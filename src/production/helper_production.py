import datetime

from production.models import Aliment, AlimentFormule, Carte, Mouvement
from shared.enum import Statut, StatutEnrolement, StatutIncorporation, StatutValidite, StatutTraitement
from sqlite3 import Date

from shared.helpers import generate_numero_famille, generer_nombre_famille_du_mois, generer_numero_ordre, \
    generate_numero_carte, generer_qrcode_carte
from django.utils import timezone
from django.db import transaction


@transaction.atomic
def create_alimet_helper(prospect, request, date_affiliation=None):
    qualite_beneficiaire = prospect.qualite_beneficiaire
    aliment = Aliment.objects.create(bureau=prospect.bureau,
                                     pays_naissance=prospect.pays_naissance,
                                     pays_residence=prospect.pays_residence,
                                     pays_activite_professionnelle=prospect.pays_activite_professionnelle,
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
    carte = None

    return aliment, carte