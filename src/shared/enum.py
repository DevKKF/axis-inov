import pprint

from django.core import serializers
from django.db import models
from django.http import JsonResponse, HttpResponse
from django_dump_die.middleware import dd

class StatutEnrolement(models.TextChoices):
    ATTENTE = 'EN ATTENTE'
    ENCOURS = 'EN COURS'
    SOUMIS = 'SOUMIS'
    VALIDE = 'VALIDE'
    REJETE = 'REJETE'
    INCORPORE = 'INCORPORE'


class StatutIncorporation(models.TextChoices):
    ENCOURS = 'ENCOURS'
    INCORPORE = 'INCORPORE'


class StatutTraitement(models.TextChoices):
    TRAITE = 'TRAITE'
    NON_TRAITE = 'NON TRAITE'


class Etat(models.TextChoices):
    ENTRE = 'ENTRÉ'
    SUSPENDU = 'SUSPENDU'
    SORTIE = 'SORTIE'


class PasswordType(models.TextChoices):
    DEFAULT = 'DEFAULT'
    CUSTOM = 'CUSTOM'


class SatutBordereauDossierSinistres(models.TextChoices):
    ATTENTE = 'ATTENTE'
    VALIDE = 'VALIDE'
    REJETE = 'REJETE'
    ORDONNANCE = 'ORDONNANCE'
    PAYE = 'PAYE'
    ANNULE = 'ANNULE'


class StatutSinistreBordereau(models.TextChoices):
    AJOUTE_BORDEREAU = 'AJOUTE BORDEREAU'
    PAYE = 'PAYE'
    ATTENTE = 'ATTENTE DE PAIEMENT'


class StatutSinistre(models.TextChoices):
    ACCORDE = 'ACCORDE'
    ATTENTE = 'EN ATTENTE'
    REJETE = 'REJETE'
    EN_RECOURS = 'EN RECOURS'
    SOLDE = 'SOLDE'


class StatutSinistrePrestation(models.TextChoices):
    EFFECTUE = 'EFFECTUE'
    ATTENTE = 'NON EFFECTUE'


class StatutRecours(models.TextChoices):
    OUI = 'OUI'
    NON = 'NON'
    AUCUN = 'AUCUN'


class BaseCalculTM(models.TextChoices):
    FRAIS_REEL = 'FRAIS REEL'
    PLAFOND = 'PLAFOND'


class Genre(models.TextChoices):
    MASCULIN = 'M'
    FEMININ = 'F'


class StatutFamilial(models.TextChoices):
    MARIE = 'M'
    CELIBATAIRE = 'C'
    DIVORCE = 'D'
    CHOISIR = ''


class Statut(models.TextChoices):
    ACTIF = 'ACTIF'
    INACTIF = 'INACTIF'


class StatutValidite(models.TextChoices):
    VALIDE = 'VALIDE'
    SUPPRIME = 'SUPPRIME'
    BROUILLON = 'BROUILLON'
    CLOTURE = 'CLOTURE'


class StatutRemboursement(models.TextChoices):
    ATTENTE = 'EN ATTENTE'
    DEMANDE = 'DEMANDE'
    ACCEPTE = 'ACCEPTE'
    ACCEPTE_PARTIELLEMENT = 'ACCEPTE PARTIELLEMENT'
    REFUSE = 'REFUSE'
    ANNULE = 'ANNULE'


class OptionRefacturation(models.TextChoices):
    REFACTURABLE = 'REFACTURABLE'
    NON_REFACTURABLE = 'NON REFACTURABLE'


class StatutRemboursementSinistre(models.TextChoices):
    ACCEPTE = 'ACCEPTE'
    REFUSE = 'REFUSE'
    NET_A_PAYER = 'NET A PAYER'
    TAXT = 'TAXT'
    FAR_TAXE = 'TAXE FAR'


class DesignationRemboursementSinistre(models.TextChoices):
    NET_A_PAYER = 'NET A PAYER'
    TAXT = 'TAXT'
    MONTANT_REFUSE = 'MONTANT REFUSE'

class StatutPolice(models.TextChoices):
    ACTIF = 'ACTIF'
    INACTIF = 'INACTIF'
    ANNULE = 'ANNULE'


class EtatPolice(models.TextChoices):
    EN_COURS = 'EN COURS'
    SUSPENDU = 'SUSPENDU'
    RESILIE = 'RESILIE'


class StatutRelation(models.TextChoices):
    PROSPECT = 'PROSPECT'
    CLIENT = 'CLIENT'


class StatutContrat(models.TextChoices):
    PROJET = 'PROJET'
    CONTRAT = 'CONTRAT'


class EtapeProjet(models.TextChoices):
    PROSPECTION = 'PROSPECTION'
    ETUDE = 'ETUDE'
    PROPOSITION = 'PROPOSITION'
    ACCORD_CLIENT = 'ACCORD CLIENT'


class StatutQuittance(models.TextChoices):
    IMPAYE = 'IMPAYE'
    PAYE = 'PAYE'


class StatutReglement(models.TextChoices):
    REGLE = 'REGLE'
    NON_REGLE = 'NON REGLE'


class StatutValiditeQuittance(models.TextChoices):
    VALIDE = 'VALIDE'
    ANNULEE = 'ANNULEE'


class StatutFacture(models.TextChoices):
    SOLDE = 'SOLDE'
    NON_SOLDE = 'NON SOLDE'


class StatutReversementCompagnie(models.TextChoices):
    REVERSE = 'REVERSE'
    NON_REVERSE = 'NON REVERSE'


class StatutEncaissementCommission(models.TextChoices):
    ENCAISSEE = 'ENCAISSEE'
    NON_ENCAISSEE = 'NON ENCAISSEE'


class TypeEncaissementCommission(models.TextChoices):
    COURTAGE = 'COURTAGE'
    GESTION = 'GESTION'


class StatutReglementApporteurs(models.TextChoices):
    REGLE = 'REGLE'
    NON_REGLE = 'NON REGLE'


class OptionYesNo(models.TextChoices):
    OUI = 'OUI'
    NON = 'NON'
    CHOISIR = ''


class PlacementEtGestion(models.TextChoices):
    EN_LOCAL = 'LOCAL'
    PAR_LE_COURTIER_MASTER = 'PAR LE COURTIER MASTER'
    CHOISIR = ''


class ModeRenouvellement(models.TextChoices):
    TACITE_RECONDUCTION = 'Tacite Reconduction'
    SANS_TACITE_RECONDUCTION = 'Sans Tacite Reconduction'
    CHOISIR = ''


class CalculTM(models.TextChoices):
    SUR_PLAFOND = 'SUR PLAFOND'
    SUR_FRAIS_REEL = 'SUR FRAIS REEL'
    CHOISIR = ''


class TypeMajorationContrat(models.TextChoices):
        TAUX = 'TAUX'
        MONTANT = 'MONTANT'


class Energie(models.TextChoices):
        ES = 'ESSENCE'
        DL = 'DISEL'
        GPL = 'GAZ DE PETROLE LIQUEFIE'
        EL = 'ELECTRIQUE'


class MoyenPaiement(models.TextChoices):
        CHQ = 'CHÈQUE'
        ESP = 'ESPÈCE'
        VRMT = 'VIREMENT BANCAIRE'


class StatutPaiementSinistre(models.TextChoices):
    ATTENTE = 'EN ATTENTE'
    ORDONNANCE = 'ORDONNANCE'
    PAYE = 'PAYE'


class TypeBonConsultation(models.TextChoices):
    AUTO_CARBONE = 'AUTO CARBONE'
    NUMERIQUE = 'NUMERIQUE'


class TypeAlerte(models.TextChoices):
    FILIALE = 'FILIALE'
    HOLDING = 'HOLDING'


class SourceCreationSinistre(models.TextChoices):
    WEB = 'WEB'
    MOBILE = 'MOBILE'
    BACKOFFICE = 'BACKOFFICE'
    API = 'API'


class Confidentialite(models.TextChoices):
    OUI = 'OUI'
    NON = 'NON'


class TypePortefeuille(models.TextChoices):
    AUCUN = 'AUCUN'
    PAR_CIE = 'PAR COMPAGNIE'
    ALL_CIE = 'TOUTES LES COMPAGNIES'
    PAR_COM = 'PAR COMMERCIAL'
    ALL_COM = 'TOUS LES COMMERCIAUX'
    PAR_BUS = 'PAR BUSINESS UNIT'
    ALL_BUS = 'TOUS LES BUSINESS UNIT'


class TypeEtape(models.TextChoices):
    FACULTATIF = 'Facultatif'
    OBLIGATOIRE = 'Obligatoire'

