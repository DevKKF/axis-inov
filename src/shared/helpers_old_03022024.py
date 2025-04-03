import datetime
import os
from io import BytesIO
from pprint import pprint
from sqlite3 import Date

import pandas as pd
import qrcode
import qrcode.image.svg
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.sites import requests
import requests as smsrequests
from django.contrib.staticfiles import finders
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Q
from django.template.loader import get_template
from django_dump_die.middleware import dd
from xhtml2pdf import pisa


from configurations.models import Acte, Prestataire, Prescripteur, JourFerie, Periodicite, Tarif, \
    SousRubriqueRegroupementActe
from production.models import Aliment, TarifPrestataireClient, Bareme, AlimentFormule, Carte
from shared.enum import StatutSinistre, Statut, StatutValidite
from sinistre.models import Sinistre, SinistreTemporaire
from django.core.files.base import File

def debug(bareme):
    attributes = vars(bareme)
    print("bareme:{")
    for attr, value in attributes.items():
        print(f"{attr}: {value}")
    print("}")


def today_utc():
    today = datetime.datetime.now(tz=datetime.timezone.utc)

    return today

def as_money(montant):
    if montant == "" or montant is None: montant = 0
    return intcomma(int(montant))

def is_jour_ferie(date_jour):
    jours_feries = JourFerie.objects.filter(date=date_jour)

    return jours_feries.exists()


def actes_non_autorises_prescripteur(prescripteur, acte):
    if prescripteur:
        if acte.specialiste_uniquement and not prescripteur.specialite.is_specialite:
            return True

    return False

    #return not SpecialiteActeAutorise.objects.filter(specialite=prescripteur.specialite, acte=acte).exists()



def respecte_conditions(date_survenance, bareme_srb, acte, aliment):
    cdt_respectee = True

    #A corriger avec gpt
    #si la date_survenance est compris entre la date début et la date fin du barème
    #if bareme_srb.date_debut__isnull or bareme_srb.date_debut__gt == date_survenance:
    if not bareme_srb.date_debut:
        cdt_respectee = False
        pprint("date début non renseignée")

    if bareme_srb.date_debut and bareme_srb.date_debut > date_survenance.date():
        cdt_respectee = False
        pprint("date début du barème plus grand que la date de survenance du sinistre")


    #if bareme_srb.date_fin__isnotnull and bareme_srb.date_fin__lt == date_survenance:
    if bareme_srb.date_fin and bareme_srb.date_fin < date_survenance.date():
        cdt_respectee = False
        pprint("date fin du barème plus grand que la date de survenance du sinistre")

    #si une sous-rubrique est renseignée sur le barème, elle doit conternir le regroupement_acte de l'acte en cours
    if bareme_srb.sous_rubrique:
        #récupère les regroupement_acte contenu dans la sous-rubrique
        regroupements_actes = SousRubriqueRegroupementActe.objects.filter(sous_rubrique=bareme_srb.sous_rubrique)
        for regroup in regroupements_actes:
            if acte.regroupement_acte == regroup.regroupement_acte:
                cdt_respectee = True
                break  # Sort de la boucle dès que la condition est respectée
            else :
                cdt_respectee = False


    #si un regroupement_acte est renseigné sur le barème, il doit être celui de l'acte en cours
    if (bareme_srb.regroupement_acte and bareme_srb.regroupement_acte.id != acte.regroupement_acte.id):
        cdt_respectee = False


    #si un acte est renseigné sur le barème, ça doit être celui en cours
    if (bareme_srb.acte and bareme_srb.acte.id != acte.id):
        cdt_respectee = False

    #si une qualite_beneficiaire est renseignée sur le barème, ça doit être celui de l'aliment en cours
    if (bareme_srb.qualite_beneficiaire_id and bareme_srb.qualite_beneficiaire_id != aliment.qualite_beneficiaire.id):
        cdt_respectee = False

    #si un age minimum est renseigné sur le barème, ça doit être inférieur ou égal à celui de l'aliment en cours
    if (bareme_srb.age_minimum and bareme_srb.age_minimum > aliment.age):
        cdt_respectee = False

    #si un age maximum est renseigné sur le barème, ça doit être supérieur ou égal à celui de l'aliment en cours
    if (bareme_srb.age_maximum and bareme_srb.age_maximum < aliment.age):
        cdt_respectee = False


    pprint("cdt_respectee?? = ")
    pprint(cdt_respectee)

    return cdt_respectee


def filtrer_selon_lien_parente_et_age(baremes, aliment):
    pprint("Fonction de filtrage des baremes selon le lien de parenté et l'age de l'aliment")

    #
    selected_bareme = None

    pprint("Filtrer sur le lien de parenté, puis sur l'age min et sur l'age max")
    # filtrer les baremes_selon_acte trouvés selon le lien de parente
    baremes_selon_lien_parente = [b for b in baremes if b.qualite_beneficiaire_id == aliment.qualite_beneficiaire.id]

    pprint("baremes_selon_lien_parente")
    pprint(len(baremes_selon_lien_parente))
    pprint(baremes_selon_lien_parente)

    if len(baremes_selon_lien_parente) == 0:

        # si aucune ligne ne correspond au lien de parenté, alors on filtre selon l'age minimum
        baremes_selon_age_min = [b for b in baremes if b.age_minimum <= aliment.age]

        if len(baremes_selon_age_min) == 0:
            # si aucune ligne ne correspond à l'age minimum, alors on filtre selon l'age maximum
            baremes_selon_age_max = [b for b in baremes if b.age_maximum <= aliment.age]

            if len(baremes_selon_age_max) == 0:
                # si on ne trouve rien selon l'age maximum : on prend une
                bareme = baremes.__getitem__(0)

                selected_bareme = bareme

                pprint("Doublon de ligne de barème selon l'acte: on prend une")
                pprint("bareme")
                debug(bareme)


            elif len(baremes_selon_age_max) == 1:
                bareme_elsamax = baremes_selon_age_max.__getitem__(0)

                selected_bareme = bareme_elsamax

                pprint("Une ligne selon l'age maximum'")
                pprint("bareme_elsamax")
                debug(bareme_elsamax)


            else:
                plusieurs_lignes_seleon_age_max = True
                bareme_elsamax = baremes_selon_age_max.__getitem__(0)

                selected_bareme = bareme_elsamax

                pprint("Plusieurs lignes selon l'age maximum, on prend le premier")
                pprint("bareme_elsamax")
                debug(bareme_elsamax)



        elif len(baremes_selon_age_min) == 1:
            bareme_elsamin = baremes_selon_age_min.__getitem__(0)

            selected_bareme = bareme_elsamin

            pprint("Une ligne selon l'age minimum")
            pprint("bareme_elsamin")
            debug(bareme_elsamin)


        elif len(baremes_selon_age_min) > 1:
            # si plusieiurs lignes selon l'age minimum
            # si aucune ligne ne correspond à l'age minimum, alors on filtre selon l'age maximum
            baremes_selon_age_max = [b for b in baremes_selon_age_min if b.age_maximum <= aliment.age]

            if len(baremes_selon_age_max) == 0:
                # si on ne trouve rien selon l'age maximum : on prend une
                bareme = baremes_selon_age_max.__getitem__(0)

                selected_bareme = bareme

                pprint("Doublon de ligne de barème selon l'acte: on prend 1")
                pprint("bareme")
                debug(bareme)


            elif len(baremes_selon_age_max) == 1:
                bareme_elsamax = baremes_selon_age_max.__getitem__(0)

                selected_bareme = bareme_elsamax

                pprint("Une ligne selon l'age maximum'")
                pprint("bareme_elsamax")
                debug(bareme_elsamax)


            else:
                plusieurs_lignes_seleon_age_max = True
                bareme_elsamax = baremes_selon_age_max.__getitem__(0)

                selected_bareme = bareme_elsamax

                pprint("Plusieurs lignes selon l'age maximum, on prend le premier")
                pprint("bareme_elsamax")
                debug(bareme_elsamax)





    # si une seule ligne selon le lien de parenté
    elif len(baremes_selon_lien_parente) == 1:

        bareme_slp = baremes_selon_lien_parente.__getitem__(0)

        selected_bareme = bareme_slp

        pprint("Une ligne selon le lien de parenté")
        pprint("bareme_slp")
        debug(bareme_slp)

    else:
        pprint("Plusieurs lignes selon le lien de parenté")
        pprint("Procéder comme dans le cas d'aucune ligne selon lien de parenté, sauf que cette fois c'est avec le résultat du filtre selon le lien de parenté qu'on flitre sur l'age min puis sur l'age max,")

        # si plusieurs lignes selon le lien de parenté, alors on filtre selon l'age minimum
        baremes_selon_age_min = [b for b in baremes_selon_lien_parente if b.age_minimum <= aliment.age]

        if len(baremes_selon_age_min) == 0:
            # si aucune ligne ne correspond à l'age minimum, alors on filtre selon l'age maximum
            baremes_selon_age_max = [b for b in baremes if b.age_maximum <= aliment.age]

            if len(baremes_selon_age_max) == 0:
                # si on ne trouve rien selon l'age maximum : ce sont des doublons : on prend une : #A confirmer
                bareme_acte = baremes.__getitem__(0)

                selected_bareme = bareme_acte

                pprint("Doublon de ligne de barème selon l'acte: on prend 1")  # A confirmer
                pprint("bareme_acte")
                debug(bareme_acte)


            elif len(baremes_selon_age_max) == 1:
                bareme_elsamax = baremes_selon_age_max.__getitem__(0)

                selected_bareme = bareme_elsamax

                pprint("Une ligne selon l'age maximum'")
                pprint("bareme_elsamax")
                debug(bareme_elsamax)


            else:
                plusieurs_lignes_seleon_age_max = True
                bareme_elsamax = baremes_selon_age_max.__getitem__(0)

                selected_bareme = bareme_elsamax

                pprint("Plusieurs lignes selon l'age maximum, on prend le premier")
                pprint("bareme_elsamax")
                debug(bareme_elsamax)



        elif len(baremes_selon_age_min) == 1:
            bareme_elsamin = baremes_selon_age_min.__getitem__(0)

            selected_bareme = bareme_elsamin

            pprint("Une ligne selon l'age minimum")
            pprint("bareme_elsamin")
            debug(bareme_elsamin)


        elif len(baremes_selon_age_min) > 1:
            # si plusieiurs lignes selon l'age minimum
            # si aucune ligne ne correspond à l'age minimum, alors on filtre selon l'age maximum
            baremes_selon_age_max = [b for b in baremes_selon_age_min if b.age_maximum <= aliment.age]

            if len(baremes_selon_age_max) == 0:
                # si on ne trouve rien selon l'age maximum : ce sont des doublons : on prend une : #A confirmer
                bareme = baremes_selon_age_max.__getitem__(0)

                selected_bareme = bareme

                pprint("Doublon de ligne de barème selon l'acte: on prend 1")  # A confirmer
                pprint("bareme")
                debug(bareme)


            elif len(baremes_selon_age_max) == 1:
                bareme_elsamax = baremes_selon_age_max.__getitem__(0)

                selected_bareme = bareme_elsamax

                pprint("Une ligne selon l'age maximum'")
                pprint("bareme_elsamax")
                debug(bareme_elsamax)


            else:
                plusieurs_lignes_seleon_age_max = True
                bareme_elsamax = baremes_selon_age_max.__getitem__(0)

                selected_bareme = bareme_elsamax

                pprint("Plusieurs lignes selon l'age maximum, on prend le premier")
                pprint("bareme_elsamax")
                debug(bareme_elsamax)


    return selected_bareme




def get_plafond_rubrique(acte, aliment, formule, date_survenance):
    pprint("Récupérer le plafond rubrique en recherchant une autre ligne de barème spécifique")

    # définir une variable critères sur les dates de façon générale
    criteres_dates = Q(date_debut__lte=date_survenance) & (Q(date_fin__gte=date_survenance) | Q(date_fin__isnull=True))

    # Vérifier si la rubrique est dans les spécificités
    baremes_rubrique = Bareme.objects.filter(
        Q(formulegarantie_id=formule.id, rubrique_id=acte.rubrique.id, sous_rubrique_id__isnull=True,
          regroupement_acte_id__isnull=True, acte_id__isnull=True) & criteres_dates)

    if baremes_rubrique:
        # si une seule ligne
        if baremes_rubrique.count() == 1:
            pprint("Une seule ligne du bareme (avec la rubrique) trouvée")
            bareme_rubrique = baremes_rubrique.first()

            plafond_rubrique = bareme_rubrique.plafond_rubrique

        else:
            pprint("Plusieurs lignes du bareme (avec la rubrique) trouvée")
            pprint("Filtrer sur le lien de parentée, puis sur l'age min et sur l'age max")

            selected_bareme = filtrer_selon_lien_parente_et_age(baremes_rubrique, aliment)

            plafond_rubrique = selected_bareme.plafond_rubrique

    else:
        plafond_rubrique = 0 #ADD ON 18092023 - POUR LEVER LERREUR local variable 'plafond_rubrique' referenced before assignment - A VERIFIER -

    return plafond_rubrique



def get_plafond_sous_rubrique(acte, aliment, date_survenance):
    criteres_dates = Q(date_debut__lte=date_survenance) & (Q(date_fin__gte=date_survenance) | Q(date_fin__isnull=True))


    return 0


def get_plafond_regroupement_acte(acte, aliment, formule, date_survenance):
    pprint("Récupérer le plafond du regroupement d'acte en recherchant une autre ligne de barème spécifique")

    criteres_dates = Q(date_debut__lte=date_survenance) & (Q(date_fin__gte=date_survenance) | Q(date_fin__isnull=True))

    plafond_regroupement_acte = 0


    # vérifier si le regroupement_acte est dans les spécificités (SANS ACTE)
    if acte.regroupement_acte:
        baremes_regroupement_acte = Bareme.objects.filter(
            Q(formulegarantie_id=formule.id, regroupement_acte_id=acte.regroupement_acte_id,
              acte_id__isnull=True) & criteres_dates)

        if baremes_regroupement_acte:
            # si une seule ligne
            if baremes_regroupement_acte.count() == 1:
                pprint("Une seule ligne du bareme (avec le regroupement_acte) trouvée")
                bareme_regroupement_acte = baremes_regroupement_acte.first()

                plafond_regroupement_acte = bareme_regroupement_acte.plafond_regroupement_acte

            else:
                pprint("Plusieurs lignes du bareme (avec le regroupement_acte) trouvée")
                pprint("Filtrer sur le lien de parentée, puis sur l'age min et sur l'age max")

                selected_bareme = filtrer_selon_lien_parente_et_age(baremes_regroupement_acte, aliment)

                plafond_regroupement_acte = selected_bareme.plafond_regroupement_acte


    return plafond_regroupement_acte




def get_tarif_acte_from_bareme(type_priseencharge_code, date_survenance, acte_id, prestataire_id, prescripteur_id,
                               aliment_id, cout_acte, quantite, consommation_individuelle, consommation_famille, session_pec=None):

    #utiliser les transactions
    with transaction.atomic():

        print("***** LES VARIABLES D'ENTREE *****")
        print("- type_priseencharge_code: " + str(type_priseencharge_code))
        print("- date_survenance: " + str(date_survenance))
        print("- acte_id: " + str(acte_id))
        print("- prestataire_id: " + str(prestataire_id))
        print("- prescripteur_id: " + str(prescripteur_id))
        print("- aliment_id: " + str(aliment_id))
        print("- cout_acte: " + str(cout_acte))
        print("- quantite: " + str(quantite))
        print("- consommation_individuelle: " + str(consommation_individuelle))
        print("- consommation_famille: " + str(consommation_famille))
        print("- session_pec: " + str(session_pec))
        print("***** FIN VARIABLES D'ENTREE *****")

        aliment = Aliment.objects.filter(id=aliment_id).first()
        acte = Acte.objects.filter(id=acte_id).first()
        prestataire = Prestataire.objects.filter(id=prestataire_id).first()

        pprint("aliment")
        pprint(aliment)

        # converti les consommation en float : à verifier si pas d'impact négétif
        consommation_famille = float(consommation_famille)
        consommation_individuelle = float(consommation_individuelle)

        cout_acte = float(cout_acte) if cout_acte else 0
        quantite = int(quantite) if quantite else 0

        if type_priseencharge_code == "HOSPIT":
            quantite = quantite if acte.option_quantite else 1
            pprint("______________________________")
            pprint("___________quantite__ OK _________________")
            pprint(quantite)
            pprint("______________________________")


        #la période de couverture :
        #added on 10112023: mettre cela en parametre de la fonction
        formule = aliment.formule_atdate(date_survenance)
        periode_couverture_encours = formule.police.periode_couverture_encours_atdate(date_survenance)
        pprint("LA FORMULE DU BÉNÉFICIAIRE LA DATE DU "+ str(date_survenance.date()) +" EST " + formule.libelle)

        #Added on 25092023
        # controle des plafond contractuels bien avant de continuer
        plafond_conso_famille = formule.plafond_conso_famille or 0
        plafond_conso_individuelle = formule.plafond_conso_individuelle or 0
        devise = formule.police.client.pays.devise.code

        plafond_conso_famille = float(plafond_conso_famille)
        plafond_conso_individuelle = float(plafond_conso_individuelle)


        pprint("plafond_conso_famille:" + str(plafond_conso_famille) + ", plafond_conso_individuelle:" + str(plafond_conso_individuelle)+ ", devise:" + str(devise))


        #Added on 27092023: utiliser une table temporaire pour controler les plafonds de consommation
        # ajouter les consommations des sinistres temporaires
        consommation_individuelle_temporaire = SinistreTemporaire.objects.filter(
            periode_couverture_id=periode_couverture_encours.pk,
            aliment_id=aliment.id,
            session_pec=session_pec
        ).aggregate(Sum('part_compagnie'))['part_compagnie__sum'] or 0

        consommation_famille_temporaire = SinistreTemporaire.objects.filter(
            periode_couverture_id=periode_couverture_encours.pk,
            adherent_principal_id=aliment.adherent_principal.id,
            session_pec=session_pec
        ).aggregate(Sum('part_compagnie'))['part_compagnie__sum'] or 0

        consommation_individuelle += float(consommation_individuelle_temporaire)
        consommation_famille += float(consommation_famille_temporaire)


        # Vérifier si la somme des consommations famille de l’individu n’est pas atteinte
        pprint("# Vérifier si la somme des consommations famille de l’individu n’est pas atteinte")
        if plafond_conso_famille > 0 and consommation_famille >= plafond_conso_famille:

            message = f"PLAFOND CONSOMMATION FAMILLE DE {as_money(int(plafond_conso_famille))} {devise} ATTEINT."

            response = {
                'statut': 0,
                'message': message,
            }
            return response

        #Vérifier si la somme des consommations individuelle n’est pas atteinte
        pprint("# Vérifier si la somme des consommations individuelle n’est pas atteinte")
        if plafond_conso_individuelle > 0 and consommation_individuelle >= plafond_conso_individuelle:

            message = f"PLAFOND CONSOMMATION INDIVIDUELLE DE {as_money(int(plafond_conso_individuelle))} {devise} ATTEINT."

            response = {
                'statut': 0,
                'message': message,
            }
            return response




        pprint("# VERIFIER SI L'ASSURÉ ET ACTE EXISTENT")

        # VERIFIER SI L'ASSURÉ ET ACTE EXISTENT
        if aliment and acte:

            # vérifier si le prescripteur peut faire l'acte : généraliste pas autorisé à faire des actes de spécialité
            if prescripteur_id != '':
                prescripteur = Prescripteur.objects.filter(id=prescripteur_id).first()

                if actes_non_autorises_prescripteur(prescripteur, acte):
                    response = {
                        'statut': 0,
                        'message': "Cet acte n'est pas autorisé selon la spécialité de ce médecin.",
                    }
                    return response

            else:
                prescripteur = None
                if acte.rubrique.type_priseencharge.code == 'CONSULT':
                    response = {
                        'statut': 0,
                        'message': "Veuillez selectionner un médecin svp",
                    }
                    return response

            # les consommations de l'assuré
            consommation_acte = 0

            consommation_acte_temporaire = SinistreTemporaire.objects.filter(
                periode_couverture_id=periode_couverture_encours.pk,
                acte_id=acte.pk,
                aliment_id=aliment.id,
                session_pec=session_pec
            ).aggregate(Sum('part_compagnie'))['part_compagnie__sum'] or 0


            consommation_regroupement_acte = 0
            consommation_regroupement_acte_temporaire = 0
            if acte.regroupement_acte:
                consommation_regroupement_acte = Sinistre.objects.filter(
                    periode_couverture_id=periode_couverture_encours.pk,
                    acte__regroupement_acte_id=acte.regroupement_acte.pk,
                    aliment_id=aliment.id,
                    statut=StatutSinistre.ACCORDE,
                    statut_validite=StatutValidite.VALIDE
                ).aggregate(Sum('part_compagnie'))['part_compagnie__sum'] or 0

                consommation_regroupement_acte_temporaire = SinistreTemporaire.objects.filter(
                    periode_couverture_id=periode_couverture_encours.pk,
                    acte__regroupement_acte_id=acte.regroupement_acte.pk,
                    aliment_id=aliment.id,
                    session_pec=session_pec
                ).aggregate(Sum('part_compagnie'))['part_compagnie__sum'] or 0


            # les consommations par sous-rubrique pour chaque sous-rubrique auxquelles appartient l'acte
            # rechercher les sous-rubriques dans lesquel le regroupement_acte de l'acte est présent
            sous_rubriques = SousRubriqueRegroupementActe.objects.filter(regroupement_acte_id=acte.regroupement_acte_id)

            #
            consommation_rubrique = Sinistre.objects.filter(
                periode_couverture_id=periode_couverture_encours.pk,
                acte__rubrique_id=acte.rubrique.pk,
                aliment_id=aliment.id,
                statut=StatutSinistre.ACCORDE,
                statut_validite=StatutValidite.VALIDE
            ).aggregate(Sum('part_compagnie'))['part_compagnie__sum'] or 0

            cconsommation_rubrique_temporaire = SinistreTemporaire.objects.filter(
                periode_couverture_id=periode_couverture_encours.pk,
                acte__rubrique_id=acte.rubrique.pk,
                aliment_id=aliment.id,
                session_pec=session_pec
            ).aggregate(Sum('part_compagnie'))['part_compagnie__sum'] or 0

            #additionner les consos déjà effectuées et les temporaires
            consommation_acte += consommation_acte_temporaire
            consommation_regroupement_acte += consommation_regroupement_acte_temporaire
            consommation_rubrique += cconsommation_rubrique_temporaire



            # convertir en float: à vérifier si pas d'impact négatif
            consommation_acte = float(consommation_acte)
            consommation_regroupement_acte = float(consommation_regroupement_acte)
            consommation_rubrique = float(consommation_rubrique)

            # RECCUPERER TOUS LES CRITERES A APPLIQUER

            # critères sur l'acte de façon générale
            delais_controle = acte.delais_controle if acte.delais_controle else 0
            delais_carence = acte.delais_carence if acte.delais_carence else 0
            base_calcul_tm = acte.base_calcul_tm

            pprint("delais_carence")
            pprint(delais_carence)

            # vérifier le delais de carrence
            if delais_carence > 0:

                # si la date de souscription de l'aliment - date du jour < delais_carrence
                aliment_formule = AlimentFormule.objects.filter(formule_id=formule.pk, aliment_id=aliment.pk).first()
                pprint("aliment_formule")
                pprint(aliment_formule)
                date_entree_police = aliment_formule.date_debut
                pprint("date_entree_police")
                pprint(date_entree_police)

                jours_anciennete = (date_survenance - date_entree_police).days

                if jours_anciennete < delais_carence:
                    response = {
                        'statut': 0,
                        'message': "Délais de carence pas encore atteint. " + str(delais_carence) + " jours requis",
                    }
                    return response

            # IDENTIFIER QUELLE LIGNE DE BAREME UTILISER POUR LE CALCUL

            # Initialisation des variables avec les valeurs par défaut
            ligne_bareme_specifique_choisie = None
            is_garanti = True
            taux_franchise = formule.taux_tm
            plafond_rubrique = 0
            plafond_sous_rubrique = 0
            plafond_regroupement_acte = 0
            plafond_acte = 0
            nombre_acte = 0
            unite_frequence = 0
            frequence = 0
            periodicite_id = 0
            bareme_id = None  # précisera la ligne bareme qui sera choisi pour faire le calcul
            take_formule_info = False

            # définir les variables qui indique sur quoi on doit faire une recherche sur les baremes
            search_bareme_selon_acte = True
            search_bareme_selon_regroupement_acte = False
            search_bareme_selon_sous_rubrique = False
            search_bareme_selon_rubrique = False

            # définir une variable critères sur les dates de façon générale
            criteres_dates = Q(date_debut__lte=date_survenance) & (
                        Q(date_fin__gte=date_survenance) | Q(date_fin__isnull=True))



            # vérifier si l'acte est dans les spécificités (et que c'est garanti)
            baremes_acte = Bareme.objects.filter(Q(formulegarantie_id=formule.id, acte_id=acte.id) & criteres_dates)
            if baremes_acte:
                if baremes_acte.count() == 1:
                    bareme_acte = baremes_acte.first()
                    pprint("Une seule ligne du bareme (avec l'acte) trouvée")

                    # vérifier qu'il ne s'agit pas d'une ligne particulière pour d'autres actes ou type de personnes
                    if respecte_conditions(date_survenance, bareme_acte, acte, aliment):

                        ligne_bareme_specifique_choisie = bareme_acte
                        bareme_id = bareme_acte.pk
                        is_garanti = bareme_acte.is_garanti
                        taux_franchise = bareme_acte.taux_tm
                        plafond_rubrique = get_plafond_rubrique(acte, aliment, formule, date_survenance)
                        # plafond_sous_rubrique =
                        plafond_regroupement_acte = get_plafond_regroupement_acte(acte, aliment, formule, date_survenance)
                        plafond_acte = bareme_acte.plafond_acte
                        nombre_acte = bareme_acte.nombre_acte
                        unite_frequence = bareme_acte.unite_frequence
                        frequence = bareme_acte.frequence
                        periodicite_id = bareme_acte.periodicite_id

                        search_bareme_selon_regroupement_acte = False
                        search_bareme_selon_sous_rubrique = False
                        search_bareme_selon_rubrique = False
                        pprint("la seule ligne du bareme (avec l'acte) trouvée correspond aux critères")
                        pprint("bareme_acte")
                        debug(bareme_acte)

                    else:
                        search_bareme_selon_regroupement_acte = True
                        pprint("la seule ligne du bareme (avec l'acte) trouvée ne correspond pas aux critères")


                else:

                    pprint("Plusieurs lignes du bareme (avec l'acte) trouvée")
                    pprint("Filtrer sur le lien de parenté, puis sur l'age min et sur l'age max")
                    # s'il existe plusieurs lignes du meme acte
                    # filtrer les baremes_selon_acte trouvés selon le lien de parente

                    selected_bareme = filtrer_selon_lien_parente_et_age(baremes_acte, aliment)

                    ligne_bareme_specifique_choisie = selected_bareme
                    bareme_id = selected_bareme.pk
                    is_garanti = selected_bareme.is_garanti
                    taux_franchise = selected_bareme.taux_tm
                    # plafond_rubrique =
                    # plafond_sous_rubrique =
                    plafond_regroupement_acte = selected_bareme.plafond_regroupement_acte
                    plafond_acte = selected_bareme.plafond_acte
                    nombre_acte = selected_bareme.nombre_acte
                    unite_frequence = selected_bareme.unite_frequence
                    frequence = selected_bareme.frequence
                    periodicite_id = selected_bareme.periodicite_id

                    pprint("selected_bareme")
                    debug(selected_bareme)


                pprint("FIN DE LA RECHERCHE SELON L'ACTE")


            else:
                search_bareme_selon_regroupement_acte = True
                pprint("Aucune ligne du bareme (avec l'acte) trouvée")
                pprint("Rechercher les baremes avec le regroupement_acte")



            # vérifier si le regroupement_acte est dans les spécificités (SANS ACTE)
            if search_bareme_selon_regroupement_acte and acte.regroupement_acte:
                baremes_regroupement_acte = Bareme.objects.filter(
                    Q(formulegarantie_id=formule.id, regroupement_acte_id=acte.regroupement_acte_id,
                      acte_id__isnull=True) & criteres_dates)

                if baremes_regroupement_acte:
                    # si une seule ligne
                    if baremes_regroupement_acte.count() == 1:
                        pprint("Une seule ligne du bareme (avec le regroupement_acte) trouvée")
                        bareme_regroupement_acte = baremes_regroupement_acte.first()

                        ligne_bareme_specifique_choisie = bareme_regroupement_acte
                        bareme_id = bareme_regroupement_acte.pk
                        is_garanti = bareme_regroupement_acte.is_garanti
                        taux_franchise = bareme_regroupement_acte.taux_tm
                        # plafond_rubrique =
                        # plafond_sous_rubrique =
                        plafond_regroupement_acte = bareme_regroupement_acte.plafond_regroupement_acte
                        plafond_acte = 0
                        nombre_acte = 0
                        unite_frequence = 0
                        frequence = 0
                        periodicite_id = None

                        search_bareme_selon_sous_rubrique = False
                        search_bareme_selon_rubrique = False
                        pprint("la seule ligne du bareme (avec le regroupement_acte) trouvé correspond aux critères")
                        pprint("bareme_regroupement_acte")
                        debug(bareme_regroupement_acte)

                    else:
                        pprint("Plusieurs lignes du bareme (avec le regroupement_acte) trouvée")
                        pprint("Filtrer sur le lien de parentée, puis sur l'age min et sur l'age max")

                        selected_bareme = filtrer_selon_lien_parente_et_age(baremes_regroupement_acte, aliment)

                        ligne_bareme_specifique_choisie = selected_bareme
                        bareme_id = selected_bareme.pk
                        is_garanti = selected_bareme.is_garanti
                        taux_franchise = selected_bareme.taux_tm
                        # plafond_rubrique =
                        # plafond_sous_rubrique =
                        plafond_regroupement_acte = selected_bareme.plafond_regroupement_acte
                        plafond_acte = 0
                        nombre_acte = 0
                        unite_frequence = 0
                        frequence = 0
                        periodicite_id = None

                        pprint("selected_bareme")
                        debug(selected_bareme)

                else:
                    search_bareme_selon_sous_rubrique = True
                    pprint("Aucune ligne du bareme (avec le regroupement_acte) trouvée")
                    pprint("Rechercher les baremes avec le sous_rubrique")



            # vérifier si la sous_rubrique est dans les spécificités
            if search_bareme_selon_sous_rubrique:
                # rechercher les sous-rubriques dans lesquel le regroupement_acte de l'acte est présent
                sous_rubriques = SousRubriqueRegroupementActe.objects.filter(regroupement_acte_id=acte.regroupement_acte_id)

                # si l'acte appartient à des sous-rubriques
                if sous_rubriques:

                    # Récupérer toutes les sous-rubriques du baremes qui appartiennent à sous_rubriques
                    baremes_sous_rubrique = Bareme.objects.filter(
                        Q(formulegarantie_id=formule.id,
                          sous_rubrique_id__in=(sous_rubriques.values_list('sous_rubrique_id', flat=True).distinct().all()),
                          regroupement_acte_id__isnull=True, acte_id__isnull=True) & criteres_dates)

                    if baremes_sous_rubrique:
                        # si une seule ligne
                        if baremes_sous_rubrique.count() == 1:
                            pprint("Une seule ligne du bareme (avec la sous-rubrique) trouvée")

                            selected_bareme = baremes_sous_rubrique.first()

                            ligne_bareme_specifique_choisie = selected_bareme
                            bareme_id = selected_bareme.pk
                            is_garanti = selected_bareme.is_garanti
                            taux_franchise = selected_bareme.taux_tm
                            # plafond_rubrique =
                            plafond_sous_rubrique = selected_bareme.plafond_sous_rubrique
                            plafond_regroupement_acte = 0
                            plafond_acte = 0
                            nombre_acte = 0
                            unite_frequence = 0
                            frequence = 0
                            periodicite_id = selected_bareme.periodicite_id

                            pprint("selected_bareme")
                            debug(selected_bareme)


                            search_bareme_selon_rubrique = False
                            pprint("la seule ligne du bareme (avec la sous-rubrique) trouvé correspond aux critères")

                        else:
                            pprint("Plusieurs lignes du bareme (avec la sous-rubrique) trouvée")
                            pprint("Filtrer sur le lien de parentée, puis sur l'age min et sur l'age max")
                            # voir la possibilité de créer une fonction pour filtrer selon le lien de parentée, puis sur l'age min et sur l'age max

                            selected_bareme = filtrer_selon_lien_parente_et_age(baremes_regroupement_acte, aliment)

                            ligne_bareme_specifique_choisie = selected_bareme
                            bareme_id = selected_bareme.pk
                            is_garanti = selected_bareme.is_garanti
                            taux_franchise = selected_bareme.taux_tm
                            # plafond_rubrique =
                            plafond_sous_rubrique = selected_bareme.plafond_sous_rubrique
                            plafond_regroupement_acte = 0
                            plafond_acte = 0
                            nombre_acte = 0
                            unite_frequence = 0
                            frequence = 0
                            periodicite_id = None

                            pprint("selected_bareme")
                            debug(selected_bareme)


                    else:
                        search_bareme_selon_rubrique = True
                        pprint("Aucune ligne du bareme (avec la sous-rubrique) trouvée")
                        pprint("Rechercher les baremes avec le rubrique")

                else:
                    search_bareme_selon_rubrique = True
                    pprint("L'acte n'appartient à aucune sous-rubrique")
                    pprint("Rechercher les baremes avec la rubrique")




            # Vérifier si la rubrique est dans les spécificités
            if search_bareme_selon_rubrique:
                baremes_rubrique = Bareme.objects.filter(
                    Q(formulegarantie_id=formule.id, rubrique_id=acte.rubrique.id, sous_rubrique_id__isnull=True,
                      regroupement_acte_id__isnull=True, acte_id__isnull=True) & criteres_dates)

                if baremes_rubrique:
                    # si une seule ligne
                    if baremes_rubrique.count() == 1:
                        pprint("Une seule ligne du bareme (avec la rubrique) trouvée")
                        bareme_rubrique = baremes_rubrique.first()

                        ligne_bareme_specifique_choisie = bareme_rubrique
                        bareme_id = bareme_rubrique.pk
                        is_garanti = bareme_rubrique.is_garanti
                        taux_franchise = bareme_rubrique.taux_tm
                        plafond_rubrique = bareme_rubrique.plafond_rubrique
                        # plafond_sous_rubrique =
                        plafond_regroupement_acte = 0
                        plafond_acte = 0
                        nombre_acte = 0
                        unite_frequence = 0
                        frequence = 0
                        periodicite_id = None

                        pprint("la seule ligne du bareme (avec la rubrique) trouvée correspond aux critères")
                        pprint("bareme_rubrique")
                        (debug)(bareme_rubrique)

                    else:
                        pprint("Plusieurs lignes du bareme (avec la rubrique) trouvée")
                        pprint("Filtrer sur le lien de parentée, puis sur l'age min et sur l'age max")

                        selected_bareme = filtrer_selon_lien_parente_et_age(baremes_regroupement_acte, aliment)

                        ligne_bareme_specifique_choisie = selected_bareme
                        bareme_id = selected_bareme.pk
                        is_garanti = selected_bareme.is_garanti
                        taux_franchise = selected_bareme.taux_tm
                        plafond_rubrique = selected_bareme.plafond_rubrique
                        # plafond_sous_rubrique =
                        plafond_regroupement_acte = 0
                        plafond_acte = 0
                        nombre_acte = 0
                        unite_frequence = 0
                        frequence = 0
                        periodicite_id = None

                        pprint("selected_bareme")
                        debug(selected_bareme)


                else:
                    take_formule_info = True
                    pprint("Aucune ligne du bareme (avec la rubrique) trouvée")
                    pprint("Prendre les données de la formule de garantie")


            # take_formule_info = False #A remettre dans le else
            pprint("FIN DE LA RECHERCHE DES DONNES DANS LE BAREME")

            # si reccupérer les critères à partir de la formule
            if take_formule_info:
                ligne_bareme_specifique_choisie = None
                bareme_id = None
                is_garanti = True
                taux_franchise = formule.taux_tm
                plafond_rubrique = 0
                plafond_acte = 0
                nombre_acte = 0
                unite_frequence = 0
                frequence = 0
                periodicite_id = 0
                delais_controle = acte.delais_controle if acte.delais_controle else 0
                base_calcul_tm = acte.base_calcul_tm

            # si l'acte n'est pas garanti alors ...
            if not is_garanti:
                # renvoyer un message
                response = {
                    'statut': 0,
                    'message': "L'ACTE " + acte.libelle + " N'EST PAS GARANTI" if acte.type_acte.code == "ACTE" else acte.libelle + " N'EST PAS GARANTI",
                }
                return response

            # sinon si l'acte est garanti alors ...
            else:

                # PARTIE CALCUL PROPREMENT DIT
                # CONTROLE PLAFOND NOMBRE D'ACTE PAR JOUR, MOIS, ANNEE, BI-ANNEE
                pprint("CONTROLE PLAFOND NOMBRE D'ACTE PAR JOUR, MOIS, ANNEE, BI-ANNEE")
                pprint("nombre_acte")
                pprint(nombre_acte)
                pprint("periodicite_id")
                pprint(periodicite_id)
                if nombre_acte > 0:
                    nbre_acte_renseigne = True
                    periodicite_obj = Periodicite.objects.filter(id=periodicite_id)
                    pprint("periodicite_obj")
                    pprint(periodicite_obj)
                    if periodicite_obj:
                        periodicite = periodicite_obj.first()
                        nombre_jour_periode = periodicite.nombre_jours

                        pprint("nombre_jour_periode")
                        pprint(nombre_jour_periode)

                        # compter le nombre d'acte effectué sur la période (depuis d, jusqu'à la date de survenance du sinistre)
                        date_fin_periode = date_survenance.date()
                        date_debut_periode = date_fin_periode - datetime.timedelta(days=nombre_jour_periode)

                        pprint("date_debut_periode")
                        pprint(date_debut_periode)
                        pprint("date_fin_periode")
                        pprint(date_fin_periode)

                        # Filter sinistres within the specified period and acte_id
                        sinistres_effectues_sur_periode = Sinistre.objects.filter(
                            aliment_id=aliment.id,
                            acte_id=acte.id,
                            date_survenance__gte=date_debut_periode,
                            date_survenance__lte=date_fin_periode,
                            statut=StatutSinistre.ACCORDE,
                            statut_validite=StatutValidite.VALIDE
                        )

                        pprint("sinistres_effectues_sur_periode")
                        pprint(sinistres_effectues_sur_periode)
                        pprint(sinistres_effectues_sur_periode.count())

                        if sinistres_effectues_sur_periode.count() > nombre_acte:
                            response = {
                                'statut': 0,
                                'message': "LE NOMBRE D'ACTES AUTORISÉS POUR CETTE PÉRIODE EST ATTEINT",
                            }
                            return response

                # FIN CONTROLE PLAFOND NOMBRE D'ACTE PAR JOUR, MOIS, ANNEE, BI-ANNEE

                # GESTION DES CAS DE CONTROLE EN CONSULTATION
                if acte.rubrique.type_priseencharge.code == 'CONSULT':

                    pprint('CONSULT')
                    # le dernier sinistre de l'aliment chez le meme prestataire et le meme prescripteur
                    latest_sinistre = Sinistre.objects.filter(
                        aliment_id=aliment.id,
                        acte_id=acte.id,
                        prestataire_id=prestataire.id,
                        prescripteur_id=prescripteur.id,
                        statut=StatutSinistre.ACCORDE,
                        statut_validite=StatutValidite.VALIDE
                    ).order_by('-date_survenance').first()

                    if latest_sinistre:
                        last_date = latest_sinistre.date_survenance

                        nombre_jours_ecoules = (date_survenance - last_date).days

                        pprint("nombre_jours_ecoules: " + str(nombre_jours_ecoules))

                        if nombre_jours_ecoules < delais_controle:
                            # cas de controle, ne doit pas etre facturé
                            frais_reel = 0
                            part_compagnie = 0
                            part_assure = 0
                            depassement = 0
                            ticket_moderateur = 0

                            # if nombre_jours_ecoules == 0 else

                            taux_couverture = 100 - taux_franchise

                            response = {
                                'statut': 1,
                                'message': "Cet acte a été réalisé le " + str(
                                    last_date.strftime("%d/%m/%Y")) + ". Il y a " + str(nombre_jours_ecoules) + " jours.",
                                'is_controle': True,
                                'data': {
                                    'id': acte.id,
                                    'code': acte.code,
                                    'libelle': acte.libelle,
                                    'option_seance': acte.option_seance,
                                    'est_gratuit': acte.est_gratuit,
                                    'frais_reel': frais_reel,
                                    'taux_franchise': taux_franchise,
                                    'taux_couverture': taux_couverture,
                                    'part_assure': part_assure,
                                    'part_compagnie': part_compagnie,
                                    'ticket_moderateur': ticket_moderateur,
                                    'base_calcul_tm': base_calcul_tm,
                                    'depassement': depassement,
                                    'nombre_acte': nombre_acte,
                                    'frequence': frequence,
                                    'unite_frequence': unite_frequence,
                                    'delais_controle': delais_controle,
                                    'plafond_acte': plafond_acte,  #
                                    # 'plafond_rubrique': plafond_rubrique,
                                    # 'plafond_individuel': plafond_individuel,
                                    # 'plafond_famille': plafond_famille,
                                    # 'consommation_acte': consommation_acte,
                                    # 'consommation_rubrique': consommation_rubrique,
                                    # 'consommation_individuel': consommation_individuel,
                                    # 'consommation_famille': consommation_famille,
                                    'garanti': is_garanti,
                                    'bareme_id': bareme_id,
                                    'quantite_demande': quantite,
                                    'prestataire_id': prestataire_id,
                                    'prescripteur_id': prescripteur_id,
                                    'aliment_id': aliment_id,
                                }
                            }

                            return response

                # FIN GESTION CAS DE CONTROLE EN CONSULTATION

                # IDENTIFIER LE TARIF A APPLIQUER

                # 2- identifier le tarif à appliquer
                tarif_prestataire_client = TarifPrestataireClient.objects.filter(formule_id=formule.id,
                                                                                 prestataire_id=prestataire_id,
                                                                                 statut=1).first()


                # if tarif_prestataire_client and tarif_prestataire_client.fichier_tarification:
                #     path_tarif_file = tarif_prestataire_client.fichier_tarification.path
                #     colonne_cout_acte = "COUT ACTE"


                #     pprint("Fichier tarif_client: " + path_tarif_file)

                # elif prestataire.fichier_tarification:
                #     path_tarif_file = prestataire.fichier_tarification.path
                #     colonne_cout_acte = "COUT ACTE"

                #     pprint("Fichier tarif_prestataire: " + path_tarif_file)


                # else:
                #     path_tarif_file = prestataire.bureau.tarfile.path
                #     if prestataire.secteur.code == "PRIVE":
                #         pprint("Fichier tarif_bureau: " + path_tarif_file)


                #         if formule.type_tarif.code == "MUTUELLE":
                #             colonne_cout_acte = "COUT MUTUELLE"
                #         else:
                #             colonne_cout_acte = "COUT CLASSIC"

                #     else:
                #         colonne_cout_acte = "COUT PUBLIC"

                '''
                # recuper le cout de l'acte depuis le fichier de tarif
                if os.path.exists(path_tarif_file):
                    print(path_tarif_file + "- --- TARIF")
    
                    # recuper le cout de l'acte depuis le fichier de tarif
                    df_tarif = get_exel_df_to_dict(path_tarif_file, 'TARIF', 'CODE ACTE', acte.code)
    
                    # vérifier si le fichier de tarification est bien configuré
                    if df_tarif is None:
                        response = {
                            'statut': 0,
                            'message': "Fichier de tarification mal configuré!",
                        }
                        return response
    
                    # recuperation des données de tarification
                    frais_reel = float(df_tarif[colonne_cout_acte])
                    frais_reel_from_xlsx = frais_reel
                '''

                #Added on 2023-12-16: filtrer sur le bureau
                # added on 2023-10-21: récupération à partir de la base de données
                pprint("récupération du tarif à partir de la base de données")
                #added on 22122023: intégration tarif prestataire
                if prestataire and prestataire.has_tarif_prestataire:
                    tarif = Tarif.objects.filter(acte_id=acte_id, statut=Statut.ACTIF, bureau=prestataire.bureau, prestataire=prestataire).first()

                else:
                    #TODO A METTRE EN LIGNE LE FAIT DE PRENDRE LES LIGNES OU LE PRESTATAIRE N'EST PAS RENSEIGNÉ
                    tarif = Tarif.objects.filter(acte_id=acte_id, statut=Statut.ACTIF, bureau=prestataire.bureau, prestataire__isnull=True).first()


                if tarif:

                    pprint("tarif trouvé")
                    pprint(tarif)

                    #added on 22122023: intégration tarif prestataire
                    if prestataire and prestataire.has_tarif_prestataire:
                        frais_reel = tarif.cout_prestataire

                    else:
                        if prestataire.secteur.code == "PRIVE":
                            pprint("Tarif privé")
                            pprint("tarif.cout_mutuelle")
                            pprint(tarif.cout_mutuelle)
                            pprint("tarif.cout_classique")
                            pprint(tarif.cout_classique)

                            #added on 16122023: appliquer à la CI01 uniquement
                            bureau_code = prestataire.bureau.code

                            #added on 18102023: si labo, appliquer tarif mutuel
                            #add on 08112023:lié ça au type du prestataire, pas au type de prise en charge
                            type_prestataire_code = prestataire.type_prestataire.code if prestataire and prestataire.type_prestataire else None
                            if formule.type_tarif.code == "MUTUELLE" or (type_prestataire_code == "PRES05" and bureau_code == "CI01"): #code_veos=LABOR
                                frais_reel = tarif.cout_mutuelle

                                pprint("TARIF MUTUALISTE APPLIQUÉ")

                            else:
                                frais_reel = tarif.cout_classique

                                pprint("TARIF CLASSIQUE APPLIQUÉ")

                            pprint("type_prestataire_code")
                            pprint(type_prestataire_code)

                        else:
                            pprint("Tarif public")
                            frais_reel = tarif.cout_public_hg

                            #si type_etablissement_code
                            if prestataire.type_etablissement.code == "ICA":
                                frais_reel = tarif.cout_public_ica
                            elif prestataire.type_etablissement.code == "CHU":
                                frais_reel = tarif.cout_public_chu
                            else:
                                frais_reel = tarif.cout_public_hg


                    # frais_reel = float(frais_reel)
                    if not frais_reel:
                        frais_reel = 0

                    frais_reel_from_xlsx = frais_reel
                    pprint("Frais réel FROM DB: " + str(frais_reel))

                    # gestion du cas de l'hospit, de l'optique et de la dentaire ou le cout de l'acte est saisi manuelement
                    '''if type_priseencharge_code == "HOSPIT":
                        frais_reel = cout_acte
                    elif (type_priseencharge_code == "OPTIQUE" or acte.rubrique.type_priseencharge.code == "OPTIQUE"):
                        frais_reel = cout_acte
                    elif (type_priseencharge_code == "DENTAIRE" or acte.rubrique.type_priseencharge.code == "DENTAIRE"):
                        frais_reel = cout_acte if frais_reel <= 0 else frais_reel
                    '''

                    # Added on 27072023: dr dit si pas tarif le laisser saisir,
                    frais_reel = cout_acte if frais_reel <= 0 else frais_reel

                else:

                    # cas de pharmacie, ou les médicaments ne sont pas dans la table tarif
                    frais_reel = cout_acte

                    frais_reel_from_xlsx = frais_reel  # juste pour fixer le bug de la variable non définie

                # gestion de la quantité, nombre de séance
                if quantite > 1:
                    frais_reel = frais_reel * quantite

                print("frais_reel")
                print(frais_reel)

                # 3- base_calcul_tm = 1 (frais_reel) ou 0 (plafond)
                depassement_initial = 0
                if base_calcul_tm == 0 and plafond_acte > 0:  # sinon si sur plafond et que plafond renseigné
                    if frais_reel > plafond_acte:
                        montant_considere = plafond_acte
                        depassement_initial = frais_reel - plafond_acte  # MARIUS OK
                    else:
                        montant_considere = frais_reel

                else:
                    montant_considere = frais_reel

                # calculer du tm
                taux_tm = taux_franchise / 100
                taux_couverture = (100 - taux_franchise) / 100

                pprint("taux_tm: " + str(taux_tm) + ", taux_couverture: " + str(taux_couverture))

                tm = montant_considere * taux_tm
                couverture_a_valider = montant_considere * taux_couverture

                pprint("tm: " + str(tm) + ", couverture_a_valider: " + str(couverture_a_valider))

                # 4 - validation du montant de la couverture
                # vérifier si l'acte a un plafond (plafond_acte > 0)

                if plafond_acte <= 0:
                    montant_tm = tm
                    depassement = 0
                    montant_couverture = couverture_a_valider
                    pprint("plafond_acte <= 0")

                elif plafond_acte > 0 and couverture_a_valider < plafond_acte:
                    montant_tm = tm
                    depassement = 0
                    montant_couverture = couverture_a_valider
                    pprint("plafond_acte > 0 and couverture_a_valider < plafond_acte")

                else:
                    montant_tm = tm
                    depassement = couverture_a_valider - plafond_acte
                    montant_couverture = plafond_acte
                    pprint("plafond_acte > 0 and couverture_a_valider > plafond_acte")

                pprint(plafond_acte)


                #CONTROLE DES PLAFONDS DE CONSOMMATION
                # rechercher les sous-rubriques dans lesquel le regroupement_acte de l'acte est présent
                sous_rubriques = SousRubriqueRegroupementActe.objects.filter(regroupement_acte_id=acte.regroupement_acte_id)

                #
                nouvelle_conso_famille = consommation_famille + montant_couverture
                nouvelle_conso_individuelle = consommation_individuelle + montant_couverture
                nouvelle_conso_rubrique = consommation_rubrique + montant_couverture
                nouvelle_conso_regroupement_acte = consommation_regroupement_acte + montant_couverture
                #nouvelle_conso_acte = montant_couverture


                #Added on 18092023:: initiation de depassement_plafond
                depassement_plafond = 0
                observation = ""

                #Added on 27092023:
                #bien définir l'ordre controle : acte, regroupement, sous-rubrique, rubrique, plafond_individuelle, plafond_famille
                if plafond_acte and montant_couverture > plafond_acte and plafond_acte > 0:
                    depassement_plafond = montant_couverture - plafond_acte



                elif plafond_regroupement_acte and nouvelle_conso_regroupement_acte > plafond_regroupement_acte and plafond_regroupement_acte > 0:
                    depassement_plafond = nouvelle_conso_regroupement_acte - plafond_regroupement_acte
                    observation = "Plafond consommation par regroupement-acte atteint. Le regroupement d'acte " + acte.regroupement_acte.libelle + " a un plafond de " + str(as_money(plafond_regroupement_acte))




                # Added on 25092023: pour un barème on aura une seule ligne de sous-rubrique qui concerne un regroupement d'acte donné. du coup on aura une seule ligne plus a chaque fois.
                # Si plusieur, on prend le premier - by Marius
                # Vérification des plafonds par sous-rubrique, pour chaque rubrique ou le regroupement de l'acte s'y trouve
                # pprint("Vérification des plafonds par sous-rubrique, pour chaque rubrique ou le regroupement de l'acte s'y trouve")
                # rechercher les sous-rubriques dans lesquel le regroupement_acte de l'acte est présent
                # sous_rubriques = SousRubriqueRegroupementActe.objects.filter(regroupement_acte_id=acte.regroupement_acte_id)

                # si l'acte appartient à des sous-rubriques
                elif sous_rubriques:

                    # Récupérer toutes les sous-rubriques du baremes qui appartiennent à sous_rubriques
                    pprint("Récupérer toutes les sous-rubriques du baremes qui appartiennent à sous_rubriques")
                    baremes_sous_rubrique = Bareme.objects.filter(
                        Q(formulegarantie_id=formule.id,
                          sous_rubrique_id__in=(sous_rubriques.values_list('sous_rubrique_id', flat=True).distinct().all()),
                          regroupement_acte_id__isnull=True, acte_id__isnull=True) & criteres_dates)


                    pprint("baremes_sous_rubrique")
                    pprint(baremes_sous_rubrique)

                    if baremes_sous_rubrique:
                        # si une seule ligne
                        if baremes_sous_rubrique.count() == 1:
                            pprint("Une seule ligne du bareme (avec la sous-rubrique) trouvée")

                            selected_bareme = baremes_sous_rubrique.first() #added on 18092023

                            pprint(selected_bareme)

                            sous_rubrique = selected_bareme.sous_rubrique
                            plafond_sous_rubrique = selected_bareme.plafond_sous_rubrique
                            libelle_sous_rubrique = selected_bareme.sous_rubrique.libelle

                            #liste des regroupements de la sous-rubrique
                            regroupements_of_sous_rubrique = SousRubriqueRegroupementActe.objects.filter(sous_rubrique_id=sous_rubrique.pk)
                            pprint("regroupements_of_sous_rubrique")
                            pprint(regroupements_of_sous_rubrique.values_list)

                            #Contrôle du plafond par sous-rubrique
                            #somme des consomations de cette sous-rubrique
                            if acte.regroupement_acte:
                                consommation_sous_rubrique = Sinistre.objects.filter(
                                    periode_couverture_id=periode_couverture_encours.pk,
                                    acte__regroupement_acte_id__in=(regroupements_of_sous_rubrique.values_list('regroupement_acte_id', flat=True).distinct().all()),
                                    aliment_id=aliment.id,
                                    statut=StatutSinistre.ACCORDE,
                                    statut_validite=StatutValidite.VALIDE
                                ).aggregate(Sum('part_compagnie'))['part_compagnie__sum'] or 0

                                consommation_sous_rubrique_temporaire = SinistreTemporaire.objects.filter(
                                    periode_couverture_id=periode_couverture_encours.pk,
                                    acte__regroupement_acte_id__in=(regroupements_of_sous_rubrique.values_list('regroupement_acte_id', flat=True).distinct().all()),
                                    aliment_id=aliment.id,
                                    session_pec=session_pec
                                ).aggregate(Sum('part_compagnie'))['part_compagnie__sum'] or 0


                                consommation_sous_rubrique += consommation_sous_rubrique_temporaire


                                pprint("session_pec: " + str(session_pec))
                                pprint("ACTE: " + acte.libelle)
                                pprint("consommation_sous_rubrique += consommation_sous_rubrique_temporaire")
                                pprint(str(consommation_sous_rubrique) + " + " + str(consommation_sous_rubrique_temporaire))

                                nouvelle_conso_sous_rubrique = float(consommation_sous_rubrique) + montant_couverture

                                if plafond_sous_rubrique and nouvelle_conso_sous_rubrique > plafond_sous_rubrique and plafond_sous_rubrique > 0:
                                    depassement_plafond = nouvelle_conso_sous_rubrique - plafond_sous_rubrique
                                    observation = "Plafond consommation par sous-rubrique atteint. La sous-rubrique " + libelle_sous_rubrique + " a un plafond de " + str(as_money(plafond_sous_rubrique))

                                    pprint("**** TODO 02 FEV 2024 ****")
                                    pprint("observation")
                                    pprint(depassement_plafond)
                                    pprint("depassement_plafond = nouvelle_conso_sous_rubrique - plafond_sous_rubrique")
                                    pprint(str(depassement_plafond) +"="+ str(nouvelle_conso_sous_rubrique) +"-"+ str(plafond_sous_rubrique))



                        else:
                            pprint("Plusieurs lignes du bareme (avec la sous-rubrique) trouvée")
                            pprint("Filtrer sur le lien de parentée, puis sur l'age min et sur l'age max")
                            # voir la possibilité de créer une fonction pour filtrer selon le lien de parentée, puis sur l'age min et sur l'age max

                            selected_bareme = filtrer_selon_lien_parente_et_age(baremes_regroupement_acte, aliment)

                            sous_rubrique = selected_bareme.sous_rubrique
                            plafond_sous_rubrique = selected_bareme.plafond_sous_rubrique
                            libelle_sous_rubrique = selected_bareme.sous_rubrique.libelle

                            # liste des regroupements de la sous-rubrique
                            regroupements_of_sous_rubrique = SousRubriqueRegroupementActe.objects.filter(sous_rubrique_id=sous_rubrique.pk)
                            pprint("regroupements_of_sous_rubrique")
                            pprint(regroupements_of_sous_rubrique.values_list)

                            # Contrôle du plafond par sous-rubrique
                            # somme des consomations de cette sous-rubrique
                            if acte.regroupement_acte:
                                consommation_sous_rubrique = Sinistre.objects.filter(
                                    periode_couverture_id=periode_couverture_encours.pk,
                                    acte__regroupement_acte_id__in=(regroupements_of_sous_rubrique.values_list('regroupement_acte_id', flat=True).distinct().all()),
                                    aliment_id=aliment.id,
                                    statut=StatutSinistre.ACCORDE,
                                    statut_validite=StatutValidite.VALIDE
                                ).aggregate(Sum('part_compagnie'))['part_compagnie__sum'] or 0

                                consommation_sous_rubrique_temporaire = SinistreTemporaire.objects.filter(
                                    periode_couverture_id=periode_couverture_encours.pk,
                                    acte__regroupement_acte_id__in=(regroupements_of_sous_rubrique.values_list('regroupement_acte_id', flat=True).distinct().all()),
                                    aliment_id=aliment.id,
                                    session_pec=session_pec
                                ).aggregate(Sum('part_compagnie'))['part_compagnie__sum'] or 0

                                consommation_sous_rubrique += consommation_sous_rubrique_temporaire

                                pprint("session_pec: " + str(session_pec))
                                pprint("ACTE: " + acte.libelle)
                                pprint("consommation_sous_rubrique += consommation_sous_rubrique_temporaire")
                                pprint (str(consommation_sous_rubrique) + " + " + str(consommation_sous_rubrique_temporaire))

                                nouvelle_conso_sous_rubrique = float(consommation_sous_rubrique) + montant_couverture

                                if plafond_sous_rubrique and nouvelle_conso_sous_rubrique > plafond_sous_rubrique and plafond_sous_rubrique > 0:
                                    depassement_plafond = nouvelle_conso_sous_rubrique - plafond_sous_rubrique
                                    observation = "Plafond consommation par sous-rubrique atteint. La sous-rubrique " + libelle_sous_rubrique + " a un plafond de " + str(as_money(plafond_sous_rubrique))
                                    # bloquer puisqu'on ne sais pas quel plafond considéré vu qu'il y a plusieurs sous rubriques dans lequel le regroupement acte de l'acte est
                                    #pour faire passer en dépassement
                                    #A BIEN VERIFIER




                elif plafond_rubrique and nouvelle_conso_rubrique > plafond_rubrique and plafond_rubrique > 0:
                    depassement_plafond = nouvelle_conso_rubrique - plafond_rubrique
                    observation = "Plafond consommation par rubrique atteint. La rubrique " + acte.rubrique.libelle + " a un plafond de " + str(as_money(plafond_rubrique))
                    pprint("observation")
                    pprint(observation)


                elif plafond_conso_individuelle and nouvelle_conso_individuelle > plafond_conso_individuelle and plafond_conso_individuelle > 0:
                    depassement_plafond = nouvelle_conso_individuelle - plafond_conso_individuelle
                    observation = "Plafond consommation individuelle de " + str(as_money(plafond_conso_individuelle)) + " atteint."
                    pprint("observation")
                    pprint(observation)



                elif plafond_conso_famille and nouvelle_conso_famille > plafond_conso_famille and plafond_conso_famille > 0:
                    depassement_plafond = nouvelle_conso_famille - plafond_conso_famille
                    observation = "Plafond consommation par famille de " + str(as_money(plafond_conso_famille)) + " atteint."
                    pprint("observation")
                    pprint(observation)


                #Added on 18092023: permettre de faire la prise en charge en ajoutant le surplus plafond au dépassement
                part_assure = montant_tm + depassement + depassement_initial + depassement_plafond
                part_compagnie = montant_couverture - depassement_plafond
                if part_compagnie < 0: part_compagnie = 0 #pour éviter montant négatif
                depassement = depassement + depassement_plafond


                print("RESULTAT BAREME: {code:" + acte.code + ", part_compagnie: " + str(part_compagnie) + ", part_assure: " + str(part_assure) + "}")

                taux_couverture = 100 - taux_franchise

                response = {
                    'statut': 1,
                    'message': "Acte trouvé !",
                    'data': {
                        'id': acte.id,
                        'code': acte.code,
                        'libelle': acte.libelle,
                        'rubrique': acte.rubrique.libelle,
                        'type_pec': acte.rubrique.type_priseencharge.code,
                        'option_seance': acte.option_seance,
                        'est_gratuit': acte.est_gratuit,
                        'frais_reel': frais_reel,
                        'frais_reel_from_xlsx': frais_reel_from_xlsx,
                        'taux_franchise': taux_franchise,
                        'taux_couverture': taux_couverture,
                        'part_assure': part_assure,
                        'part_compagnie': part_compagnie,
                        'ticket_moderateur': montant_tm,
                        'base_calcul_tm': base_calcul_tm,
                        'depassement': depassement,
                        'nombre_acte': nombre_acte,
                        'frequence': frequence,
                        'unite_frequence': unite_frequence,
                        'delais_controle': delais_controle,
                        'plafond_acte': plafond_acte,  #
                        'plafond_rubrique': plafond_rubrique,
                        'plafond_individuel': plafond_conso_individuelle,
                        'plafond_famille': plafond_conso_famille,
                        'consommation_acte': consommation_acte,
                        'consommation_rubrique': consommation_rubrique,
                        'consommation_individuel': consommation_individuelle,
                        'consommation_famille': consommation_famille,
                        'garanti': is_garanti,
                        'bareme_id': bareme_id,
                        'quantite_demande': quantite,
                        'prestataire_id': prestataire_id,
                        'prescripteur_id': prescripteur_id,
                        'aliment_id': aliment_id,
                        'observation': observation,
                    }
                }


                statut = "ACCORDE" if acte.accord_automatique == 1 else "EN ATTENTE"

                #Added on 06102023: uniquement AMBULATOIRE, OPTIQUE, DENTAIRE ou on peut sélectionner plusieurs actes

                if type_priseencharge_code != "CONSULT" and type_priseencharge_code != "HOSPIT":

                    #Added on 27092023: créer un sinistre temporaire pour gérer le calcul des plafonds pendant la sélection des actes à effectuer

                    #supprimer tout sinistre temporaire portant l'acte et l'assuré, avant de recréer le sinistre
                    SinistreTemporaire.objects.filter(
                        acte_id=acte.id,
                        aliment_id=aliment.id,
                        session_pec=session_pec
                    ).delete()

                    #créer le sinistre temporaire
                    sinistre_temporaire = SinistreTemporaire.objects.create(type_sinistre="acte",
                                                       created_by_id=1,#a remplacer par l'utilisateur connecté plus tard
                                                       prestataire_id=prestataire.id,
                                                       aliment_id=aliment.id,
                                                       adherent_principal_id=aliment.adherent_principal.id,
                                                       police_id=formule.police.id,
                                                       periode_couverture_id=periode_couverture_encours.pk,
                                                       formulegarantie_id=formule.id,
                                                       bareme_id=bareme_id,
                                                       compagnie_id=formule.police.compagnie.id,
                                                       prescripteur_id=prescripteur_id,
                                                       acte_id=acte_id,
                                                       frais_reel=frais_reel,
                                                       part_compagnie=part_compagnie,
                                                       part_assure=part_assure,
                                                       ticket_moderateur=montant_tm,
                                                       depassement=depassement,

                                                       montant_plafond=plafond_acte,
                                                       nombre_plafond=nombre_acte,
                                                       frequence=frequence,
                                                       unite_frequence=unite_frequence,

                                                       nombre_demande=nombre_acte,
                                                       nombre_accorde=0,
                                                       statut=statut,
                                                       session_pec=session_pec,
                                                       observation="acte = " + acte.libelle + ", session_pec= " + str(session_pec),
                                                       )

                    sinistre_temporaire.numero = 'STEMP' + str(Date.today().year) + str(sinistre_temporaire.pk).zfill(6)
                    sinistre_temporaire.save()




        else:

            response = {
                'statut': 0,
                'message': "Aucune tarif trouvé !",
            }

        # return JsonResponse(response)
        return response





# file_pah : to string => correspond au l'adresse absolue du fichier
# sheet_name : to string => correspond au nom de la feuille
# search_colum : to string => correspond au nom de la colonne de recherche
# search_value : to string => correspond à la valeur de recherche
def get_exel_df_to_dict(file_pah, sheet_name, search_colum, search_value):
    try:
        # lire le fichier excel
        df = pd.read_excel(file_pah, sheet_name=sheet_name)
        # print(df)

        # filtrer les données
        df = df[df[search_colum] == search_value]
        # print(df)

        # convertir en dictionnaire
        data = df.to_dict()
        data_key = data.keys()

        # recuperation de l'index de la ligne
        row_index = [i for i in data[search_colum] if data[search_colum][i] == search_value][0]

        # formatage des donnees au format dictionnaire
        data_format_dict = {}
        for d in list(data_key):
            data_format_dict[d] = data[d][row_index]
        return data_format_dict

    except Exception as e:
        print('error')
        print(e)
        return None


def render_pdf(template_src, context_dict={}):
    print("@@@@@@@@@@ render_pdf_view @@@@@@@")
    template_path = template_src
    context = context_dict
    # Create a Django response object, and specify content_type as pdf
    response = BytesIO()
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    print(pisa_status)
    # if error then show some funny view
    if pisa_status.err:
        return None
    return response


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


def api_send_sms(message, destinataires):
    uri = "https://app.nerhysms.com/api/send"

    data = {
        "from": "INOV",
        "content": message,
        "to": destinataires
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer 00e18ff3e67c5533f9e6f36ccf"
    }
    try:
        response = smsrequests.post(uri, json=data, headers=headers)
        output = response.text
        print(output)
        #print("output")
        return True
    except:
        return False


def generer_qrcode_carte(numero_carte):
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(numero_carte)
    qr.make()
    img = qr.make_image()
    # Convert PIL Image to Bytes
    image_bytes = BytesIO()
    img.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    return File(image_bytes)



def generate_numero_famille():

    current_date = datetime.datetime.now(tz=datetime.timezone.utc)

    year_part = str(current_date.year)[2:]
    month_part = f"{current_date.month:02d}"

    period = f"{month_part}{year_part}" # Exemple '1223' Quand on est dans la period de decembre 2023

    # On trouve le nombre actuelle a incrementer
    nombre_distinct_numero_famille = Aliment.objects.filter(numero_famille__endswith=period).values('numero_famille').distinct().count()

    current_number = nombre_distinct_numero_famille + 1 # On incremente pour prendre le numero suivant

    numero_famille = f"F{current_number:03d}{month_part}{year_part}"
    
    return numero_famille


def generate_numero_famille_for_existing_aliment(aliment):
    date_reference = aliment.date_affiliation

    year_part = str(date_reference.year)[2:]
    month_part = f"{date_reference.month:02d}"

    period = f"{month_part}{year_part}"  # Exemple '1223' Quand on est dans la period de decembre 2023

    # On trouve le nombre actuelle a incrementer
    nombre_distinct_numero_famille = Aliment.objects.filter(numero_famille__endswith=period).values(
        'numero_famille').distinct().count()

    current_number = nombre_distinct_numero_famille + 1  # On incremente pour prendre le numero suivant

    numero_famille = f"F{current_number:03d}{month_part}{year_part}"

    return numero_famille


def generer_numero_ordre(aliment):
    numero_ordre = Aliment.objects.filter(adherent_principal=aliment.adherent_principal).count() #pas necessaire de faire + 1 puisqu'il a été déjà enregistré, il est compté
    return numero_ordre


def generer_nombre_famille_du_mois():
    today = datetime.datetime.now(tz=timezone.utc)
    nombre_famille_du_mois = Aliment.objects.filter(qualite_beneficiaire__code="AD", date_affiliation__month=today.month, date_affiliation__year=today.year).count() + 1
    print("nombre_famille_du_mois")
    print(nombre_famille_du_mois)
    return nombre_famille_du_mois



def generate_numero_carte(aliment):
    # Nomenclature: X-NOMBRE_FAMILLE_DU_MOIS-MMAA-A*.  exemple: 1-00001-1223-A

    today = datetime.datetime.now(tz=timezone.utc)

    annee = str(today.year)[2:]
    mois = f"{today.month:02d}"

    # vérifier s'il a déjà une carte
    carte_precedente = Carte.objects.filter(aliment=aliment, numero__isnull=False).order_by('-id').first()

    if carte_precedente:
        # récupérer le dernier caractère
        lettre_precedente = carte_precedente.numero[-1]
        liste_lettres = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

        # trouver l'index de la lettre précédente dans la liste
        index_lettre = liste_lettres.index(lettre_precedente)

        # obtenir la lettre suivante en vérifiant les limites
        if index_lettre < len(liste_lettres) - 1:
            lettre_suivante = liste_lettres[index_lettre + 1]

        else:
            # si la lettre précédente est Z, revenir à A
            lettre_suivante = liste_lettres[0]

        numero_carte = carte_precedente.numero[:-1] + lettre_suivante

    else:
        # déterminer sa position dans les membres (en fonction de l'id) # après créer peut-être un champ qui sera renseigné à l'enregistrement du bénéficiaire
        position = aliment.numero_ordre
        nombre_famille_du_mois = aliment.adherent_principal.numero_famille_du_mois

        # si le nombre de famille du mois n'a pas encore ete generer pour un adherent existant
        if not nombre_famille_du_mois:
            nombre_famille_du_mois = generer_nombre_famille_du_mois()
            aliment.adherent_principal.numero_famille_du_mois = nombre_famille_du_mois
            aliment.adherent_principal.save()

        numero_carte = f"{position}{nombre_famille_du_mois}{mois}{annee}A"


    return numero_carte


def bool_plafond_atteint(dossier_sinistre):
    plafond_atteint = False
    formule = dossier_sinistre.formulegarantie
    
    if formule:
        # récupérer ses consommations individuel et par famille
        periode_couverture_encours = formule.police.periode_couverture_encours_atdate(dossier_sinistre.date_survenance)
        consommation_individuelle = \
            Sinistre.objects.filter(periode_couverture_id=periode_couverture_encours.pk, aliment_id=dossier_sinistre.aliment.id,
                                    statut=StatutSinistre.ACCORDE, statut_validite=StatutValidite.VALIDE).aggregate(Sum('part_compagnie'))[
                'part_compagnie__sum'] or 0

        consommation_famille = Sinistre.objects.filter(periode_couverture_id=periode_couverture_encours.pk,
                                                        adherent_principal_id=dossier_sinistre.aliment.adherent_principal.id,
                                                        statut=StatutSinistre.ACCORDE, statut_validite=StatutValidite.VALIDE).aggregate(
            Sum('part_compagnie'))['part_compagnie__sum'] or 0


        #TODO : Tenir compte du fait que le champs formule.plafond_conso_individuelle peut être null ou contenir 0
        niveau_consommation_individuelle = consommation_individuelle * 100 / formule.plafond_conso_individuelle if formule.plafond_conso_individuelle is not None and formule.plafond_conso_individuelle > 0 else 0 
        niveau_consommation_famille = consommation_famille * 100 / formule.plafond_conso_famille if formule.plafond_conso_famille is not None and formule.plafond_conso_famille > 0 else 0
        
        if niveau_consommation_individuelle >= 80 or niveau_consommation_famille >= 80:
            plafond_atteint = True
    
    return plafond_atteint