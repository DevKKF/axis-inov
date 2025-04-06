import datetime

from production.models import Aliment, AlimentFormule, Carte, Mouvement, MouvementAliment, FormuleGarantie
from shared.enum import Statut, StatutEnrolement, StatutIncorporation, StatutValidite, StatutTraitement
from sqlite3 import Date

from shared.helpers import generate_numero_famille, generer_nombre_famille_du_mois, generer_numero_ordre, \
    generate_numero_carte, generer_qrcode_carte
from django.utils import timezone
from django.db import transaction


@transaction.atomic
def create_alimet_helper(prospect, request, date_affiliation=None):
    formule_id = prospect.formulegarantie.id
    qualite_beneficiaire = prospect.qualite_beneficiaire
    aliment = Aliment.objects.create(bureau=prospect.bureau,
                                     # adherent_principal=prospect.adherent_principal.aliment if prospect.adherent_principal else None,
                                     pays_naissance=prospect.pays_naissance,
                                     pays_residence=prospect.pays_residence,
                                     pays_activite_professionnelle=prospect.pays_activite_professionnelle,
                                     profession=prospect.profession,
                                     rib=prospect.rib,
                                     date_affiliation=date_affiliation,
                                     code_postal=prospect.code_postal,
                                     ville=prospect.ville,
                                     adresse=prospect.adresse,
                                     civilite=prospect.civilite,
                                     lieu_naissance=prospect.lieu_naissance,
                                     numero_securite_sociale=prospect.numero_securite_sociale,
                                     nom=prospect.nom,
                                     prenoms=prospect.prenoms,
                                     nom_jeune_fille=prospect.nom_jeune_fille,
                                     date_naissance=prospect.date_naissance,
                                     genre=prospect.genre,
                                     telephone_fixe=prospect.telephone_fixe,
                                     telephone_mobile=prospect.telephone_mobile,
                                     email=prospect.email,
                                     #
                                     matricule_employe=prospect.matricule_employe,
                                     # date_affiliation=prospect.date_affiliation,
                                     photo=prospect.photo,
                                     statut_familiale=prospect.statut_familiale,
                                     qualite_beneficiaire=qualite_beneficiaire,
                                     numero_piece=prospect.numero_piece,
                                     apci_ald=prospect.apci_ald,
                                     statut=Statut.ACTIF,
                                     statut_incorporation=StatutIncorporation.ENCOURS
                                     )

    aliment.save()
    prospect.aliment = aliment
    prospect.statut_enrolement = StatutEnrolement.ENCOURS
    prospect.save()
    # génération des numéros
    aliment = Aliment.objects.get(id=aliment.pk)
    aliment.numero = 'A' + str(Date.today().year) + str(aliment.pk).zfill(6)
    if qualite_beneficiaire.code == "AD":
        aliment.adherent_principal = aliment
        aliment.numero_ordre = 1
        # générer un numéro de famille
        aliment.numero_famille = generate_numero_famille()
        aliment.numero_famille_du_mois = generer_nombre_famille_du_mois()
        print("aliment.numero_ordre")
        print(aliment.numero_ordre)
    else:
        aliment.adherent_principal = prospect.adherent_principal.aliment

    aliment.save()

    if qualite_beneficiaire.code != "AD":
        # générer le numéro d'ordre dans la famille
        aliment.numero_ordre = generer_numero_ordre(aliment)
        aliment.save()
        print("aliment.numero_ordre 2")
        print(aliment.numero_ordre)

    # renseigner la table association qui lie l'aliment à la police et à la formule
    aliment_formule = AlimentFormule.objects.create(formule_id=formule_id, aliment_id=aliment.pk,
                                                    date_debut=aliment.date_affiliation, statut=Statut.ACTIF,
                                                    created_by=request.user)

    formule = FormuleGarantie.objects.filter(id=formule_id).first()
    police = formule.police if formule else None

    # créer un mouvement d'incorporation en attente
    mouvement = Mouvement.objects.filter(code="DMD-INCORPO-GRH").first()
    # Créer l'avenant
    mouvement_aliment = MouvementAliment.objects.create(created_by=request.user,
                                                        aliment=aliment,
                                                        mouvement=mouvement,
                                                        police=police,
                                                        date_effet=aliment.date_affiliation,
                                                        motif="Enrôlement validé par le GRH",
                                                        statut_validite=StatutValidite.VALIDE,
                                                        statut_traitement=StatutTraitement.NON_TRAITE
                                                        )
    mouvement_aliment.save()


    #les cartes seront générées à la validation par la gestionnaire
    '''# TODO générer une carte en même temps

    aliment = Aliment.objects.get(id=aliment.pk)

    suffixe = 'A'

    # désactiver ses cartes actives
    Carte.objects.filter(aliment_id=aliment.pk).filter(statut=Statut.ACTIF).update(statut=Statut.INACTIF,
                                                                                   date_desactivation=datetime.datetime.now(
                                                                                       tz=timezone.utc))

    # enregistrer la nouvelle carte
    carte = Carte.objects.create(aliment_id=aliment.pk,
                                 date_edition=datetime.datetime.now(tz=timezone.utc),
                                 motif_edition="Nouvelle incorporation",
                                 statut=Statut.ACTIF
                                 )

    carte = Carte.objects.get(id=carte.pk)

    # METTRE A JOUR LE NUMERO
    prefixe = request.user.bureau.code
    numero_carte = generate_numero_carte(aliment)
    carte.numero = numero_carte
    carte.save()

    # générer le qrcode
    qrcode_file = generer_qrcode_carte(numero_carte)
    print("qrcode_img")
    # print(qrcode_img)
    carte.qrcode_file.save(f'qrcode_img_{numero_carte}.png', qrcode_file)
    carte.save()
    '''

    carte = None

    return aliment, carte