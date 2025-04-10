# Create your models here.

import datetime
from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone


from configurations.models import CompteTresorerie, Devise, Medicament, Compagnie, User, TypePriseencharge, Prestataire, Prescripteur, Acte, \
    Affection, Rubrique, SousRubrique, RegroupementActe, TypePrefinancement, PeriodeComptable, ModeCreation, Bureau, Circonstance, TypeSinistre, Responsabilite, TypeIntervenant, PosteDommage, Pays, \
    TypeRemboursement, ModeReglement, Banque, BordereauLettreCheque, Garantie, TypeRecours, EtapeSinistre
from production.models import TypeDocument, Aliment, Police, PeriodeCouverture, FormuleGarantie, Bareme, Client, AlimentPolice, Mouvement, Motif
from shared.enum import StatutFacture, StatutSinistre, SatutBordereauDossierSinistres, StatutSinistreBordereau, \
    StatutSinistrePrestation, StatutValidite, StatutRemboursement, StatutRemboursementSinistre, Statut, \
    OptionRefacturation, StatutPaiementSinistre, SourceCreationSinistre

import random


#
class Sinistre(models.Model):
    client = models.ForeignKey(Client, null=True, on_delete=models.RESTRICT)
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    compagnie = models.ForeignKey(Compagnie, null=True, on_delete=models.RESTRICT)
    police = models.ForeignKey(Police, null=True, on_delete=models.RESTRICT)
    type_sinistre = models.ForeignKey(TypeSinistre, null=True, on_delete=models.RESTRICT)
    responsabilite = models.ForeignKey(Responsabilite, null=True, on_delete=models.RESTRICT)
    circonstance = models.ForeignKey(Circonstance, null=True, on_delete=models.RESTRICT)
    created_by = models.ForeignKey(User, related_name="created_by_sinistre", null=True, on_delete=models.RESTRICT)
    updated_by = models.ForeignKey(User, related_name="updated_by_sinistre", null=True, on_delete=models.RESTRICT)

    numero = models.CharField(max_length=50, blank=True, null=True)
    numero_provisoire = models.CharField(max_length=50, blank=True, null=True)
    lieu_survenance = models.TextField(blank=True, null=True)
    tva_recuperee = models.TextField(blank=True, null=True)
    fait_generateur = models.TextField(blank=True, null=True)
    point_de_choc = models.TextField(blank=True, null=True)
    commentaire = models.TextField(blank=True, null=True)

    franchise = models.BigIntegerField(null=True)

    date_survenance = models.DateTimeField(null=True)
    date_declaration = models.DateTimeField(null=True)
    date_ouverture = models.DateTimeField(null=True)
    date_reouverture = models.DateTimeField(null=True)
    date_cloture = models.DateTimeField(null=True)

    statut = models.fields.CharField(choices=StatutSinistre.choices, default=StatutSinistre.ATTENTE, max_length=15, null=True)
    statut_validite = models.fields.CharField(choices=StatutValidite.choices, default=StatutValidite.BROUILLON, max_length=15, null=True)
    statut_remboursement = models.fields.CharField(choices=StatutRemboursement.choices, default=StatutRemboursement.ATTENTE, max_length=25, null=True)
    statut_paiement = models.fields.CharField(choices=StatutPaiementSinistre.choices, default=StatutPaiementSinistre.ATTENTE, max_length=15, null=True)
    date_paiement = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'sinistres'
        verbose_name = 'Sinistres'
        verbose_name_plural = 'Sinistres'

        permissions = [
            ("can_do_saisie_gestionnaire", "Peut saisir des PEC physiques"),
            ("can_view_prestations", "Peut afficher les PEC"),
            ("can_do_generation_bordereau_facturation", "Peut générer un bordereau de facturation"),
            ("can_view_bordereaux_facturations", "Peut voir bordereaux de facturations"),
            ("can_view_remboursements_validees", "Peut voir les remboursements validées"),
            ("can_do_ordonnancement", "Peut faire un ordonnancement"),
            ("can_view_bordereaux_ordonnancement", "Peut voir les bordereaux d'ordonnancements"),
            ("can_do_annulation_sinistre", "Peut annuler des sinistres"),
            ("can_do_annulation_facture", "Peut annuler des factures"),
        ]

    @property
    def total_franchises(self):
        """Calcule la somme des franchises pour ce sinistre."""
        return self.garanties.aggregate(models.Sum('franchise'))['franchise__sum'] or 0

    @property
    def total_capitaux(self):
        """Calcule la somme des capital pour ce sinistre."""
        return self.garanties.aggregate(models.Sum('capital'))['capital__sum'] or 0

    @property
    def total_prime_nette(self):
        """Calcule la somme des prime_nette pour ce sinistre."""
        return self.garanties.aggregate(models.Sum('prime_nette'))['prime_nette__sum'] or 0

    @property
    def total_prime_ttc(self):
        """Calcule la somme des prime_ttc pour ce sinistre."""
        return self.garanties.aggregate(models.Sum('prime_ttc'))['prime_ttc__sum'] or 0

    @property
    def etat_sinistre(self):
        # tenir compte de la date du jour pour déterminer l'état du sinistre
        # today = datetime.datetime.now(tz=timezone.utc).date()
        today = timezone.now().date()

        mouvement = MouvementSinistre.objects.filter(sinistre_id=self.id, date_effet__lte=today, statut_validite=StatutValidite.VALIDE).order_by('-id').first()

        if mouvement:
            return mouvement.motif.etat_sinistre
        else:
            return "En attente"


#
class HistoriqueSinistre(models.Model):
    sinistre = models.ForeignKey(Sinistre, null=True, on_delete=models.RESTRICT)
    client = models.ForeignKey(Client, null=True, on_delete=models.RESTRICT)
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    compagnie = models.ForeignKey(Compagnie, null=True, on_delete=models.RESTRICT)
    police = models.ForeignKey(Police, null=True, on_delete=models.RESTRICT)
    type_sinistre = models.ForeignKey(TypeSinistre, null=True, on_delete=models.RESTRICT)
    responsabilite = models.ForeignKey(Responsabilite, null=True, on_delete=models.RESTRICT)
    circonstance = models.ForeignKey(Circonstance, null=True, on_delete=models.RESTRICT)
    created_by = models.ForeignKey(User, related_name="histo_created_by_sinistre", null=True, on_delete=models.RESTRICT)
    updated_by = models.ForeignKey(User, related_name="histo_updated_by_sinistre", null=True, on_delete=models.RESTRICT)

    numero = models.CharField(max_length=50, blank=True, null=True)
    numero_provisoire = models.CharField(max_length=50, blank=True, null=True)
    lieu_survenance = models.TextField(blank=True, null=True)
    tva_recuperee = models.TextField(blank=True, null=True)
    fait_generateur = models.TextField(blank=True, null=True)
    point_de_choc = models.TextField(blank=True, null=True)
    commentaire = models.TextField(blank=True, null=True)

    franchise = models.BigIntegerField(null=True)

    date_survenance = models.DateTimeField(null=True)
    date_declaration = models.DateTimeField(null=True)
    date_ouverture = models.DateTimeField(null=True)
    date_reouverture = models.DateTimeField(null=True)
    date_cloture = models.DateTimeField(null=True)

    statut = models.fields.CharField(choices=StatutSinistre.choices, default=StatutSinistre.ATTENTE, max_length=15, null=True)
    statut_validite = models.fields.CharField(choices=StatutValidite.choices, default=StatutValidite.BROUILLON, max_length=15, null=True)
    statut_remboursement = models.fields.CharField(choices=StatutRemboursement.choices, default=StatutRemboursement.ATTENTE, max_length=25, null=True)
    statut_paiement = models.fields.CharField(choices=StatutPaiementSinistre.choices, default=StatutPaiementSinistre.ATTENTE, max_length=15, null=True)
    date_paiement = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'historique_sinistres'
        verbose_name = 'Historique Sinistres'
        verbose_name_plural = 'Historique Sinistres'

        permissions = [
            ("can_do_saisie_gestionnaire", "Peut saisir des PEC physiques"),
            ("can_view_prestations", "Peut afficher les PEC"),
            ("can_do_generation_bordereau_facturation", "Peut générer un bordereau de facturation"),
            ("can_view_bordereaux_facturations", "Peut voir bordereaux de facturations"),
            ("can_view_remboursements_validees", "Peut voir les remboursements validées"),
            ("can_do_ordonnancement", "Peut faire un ordonnancement"),
            ("can_view_bordereaux_ordonnancement", "Peut voir les bordereaux d'ordonnancements"),
            ("can_do_annulation_sinistre", "Peut annuler des sinistres"),
            ("can_do_annulation_facture", "Peut annuler des factures"),
        ]

    @property
    def total_franchises(self):
        """Calcule la somme des franchises pour ce sinistre."""
        return self.garanties.aggregate(models.Sum('franchise'))['franchise__sum'] or 0

    @property
    def total_capitaux(self):
        """Calcule la somme des capital pour ce sinistre."""
        return self.garanties.aggregate(models.Sum('capital'))['capital__sum'] or 0

    @property
    def total_prime_nette(self):
        """Calcule la somme des prime_nette pour ce sinistre."""
        return self.garanties.aggregate(models.Sum('prime_nette'))['prime_nette__sum'] or 0

    @property
    def total_prime_ttc(self):
        """Calcule la somme des prime_ttc pour ce sinistre."""
        return self.garanties.aggregate(models.Sum('prime_ttc'))['prime_ttc__sum'] or 0


#
class AlimentPoliceSinistre(models.Model):
    police = models.ForeignKey(Police, null=True, on_delete=models.RESTRICT, related_name='police_sinistre')
    sinistre = models.ForeignKey(Sinistre, null=True, on_delete=models.RESTRICT, related_name='aliment_police_sinistre')
    aliment_police = models.ForeignKey(AlimentPolice, null=True, on_delete=models.RESTRICT, related_name='aliment_sinistre')
    risque = models.TextField(blank=True, null=True)


    class Meta:
        db_table = 'aliment_police_sinistre'
        verbose_name = 'Sinistre aliment police'
        verbose_name_plural = 'Sinistre aliment police'


#
class HistoriqueAlimentPoliceSinistre(models.Model):
    historique_sinistre = models.ForeignKey(HistoriqueSinistre, null=True, on_delete=models.RESTRICT)
    police = models.ForeignKey(Police, null=True, on_delete=models.RESTRICT)
    sinistre = models.ForeignKey(Sinistre, null=True, on_delete=models.RESTRICT)
    aliment_police = models.ForeignKey(AlimentPolice, null=True, on_delete=models.RESTRICT)
    risque = models.TextField(blank=True, null=True)


    class Meta:
        db_table = 'historique_aliment_police_sinistre'
        verbose_name = 'Historique sinistre aliment police'
        verbose_name_plural = 'Historique sinistre aliment police'


#
class Intervenant(models.Model):
    type_intervenant = models.ForeignKey(TypeIntervenant, null=True, on_delete=models.RESTRICT)
    pays = models.ForeignKey(Pays, null=True, on_delete=models.RESTRICT)
    nom = models.TextField(blank=True, null=True)
    prenoms = models.TextField(blank=True, null=True)
    portable = models.TextField(blank=True, null=True)
    telephone = models.TextField(blank=True, null=True)
    fax = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    code_postal = models.TextField(blank=True, null=True)
    boite_postale = models.TextField(blank=True, null=True)
    ville = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'intervenant'
        verbose_name = 'Intervenants'
        verbose_name_plural = 'Intervenants'


#
class SinistreIntervenant(models.Model):
    sinistre = models.ForeignKey(Sinistre, null=True, on_delete=models.RESTRICT)
    intervenant = models.ForeignKey(Intervenant, null=True, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'sinistre_intervenant'
        verbose_name = 'Sinistre intervenant'
        verbose_name_plural = 'Sinistre intervenant'


class HistoriqueSinistreIntervenant(models.Model):
    historique_sinistre = models.ForeignKey(HistoriqueSinistre, null=True, on_delete=models.RESTRICT)
    intervenant = models.ForeignKey(Intervenant, null=True, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'historique_sinistre_intervenant'
        verbose_name = 'Historique sinistre intervenant'
        verbose_name_plural = 'Historique sinistre intervenant'


#
class GarantieSinistre(models.Model):
    sinistre = models.ForeignKey(Sinistre, related_name='garanties', null=True, on_delete=models.RESTRICT)
    garantie = models.ForeignKey(Garantie, null=True, on_delete=models.RESTRICT)
    circonstance = models.ForeignKey(Circonstance, null=True, on_delete=models.RESTRICT)

    franchise = models.BigIntegerField(null=True)
    capital = models.BigIntegerField(null=True)
    prime_nette = models.BigIntegerField(null=True)
    prime_ttc = models.BigIntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'garantie_sinistre'
        verbose_name = 'Garantie Sinistre'
        verbose_name_plural = 'Garantie Sinistre'


#
class HistoriqueGarantieSinistre(models.Model):
    historique_sinistre = models.ForeignKey(HistoriqueSinistre, related_name='garanties', null=True, on_delete=models.RESTRICT)
    garantie = models.ForeignKey(Garantie, null=True, on_delete=models.RESTRICT)
    circonstance = models.ForeignKey(Circonstance, null=True, on_delete=models.RESTRICT)

    franchise = models.BigIntegerField(null=True)
    capital = models.BigIntegerField(null=True)
    prime_nette = models.BigIntegerField(null=True)
    prime_ttc = models.BigIntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'historique_garantie_sinistre'
        verbose_name = 'Historique garantie sinistre'
        verbose_name_plural = 'Historique garantie sinistre'


#
class Provision(models.Model):
    sinistre = models.ForeignKey(Sinistre, null=True, on_delete=models.RESTRICT)
    garantie = models.ForeignKey(Garantie, null=True, on_delete=models.RESTRICT)
    poste_dommage = models.ForeignKey(PosteDommage, null=True, on_delete=models.RESTRICT)

    estimation = models.BigIntegerField(null=True)
    deja_regle = models.BigIntegerField(null=True)
    provision = models.BigIntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'provisions'
        verbose_name = 'Provisions'
        verbose_name_plural = 'Provisions'


#
class HistoriqueProvision(models.Model):
    historique_sinistre = models.ForeignKey(HistoriqueSinistre, related_name='provisions', null=True, on_delete=models.RESTRICT)
    provision = models.ForeignKey(Provision, null=True, on_delete=models.RESTRICT)
    sinistre = models.ForeignKey(Sinistre, null=True, on_delete=models.RESTRICT)
    garantie = models.ForeignKey(Garantie, null=True, on_delete=models.RESTRICT)
    poste_dommage = models.ForeignKey(PosteDommage, null=True, on_delete=models.RESTRICT)

    estimation = models.BigIntegerField(null=True)
    deja_regle = models.BigIntegerField(null=True)
    provision = models.BigIntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'historique_provisions'
        verbose_name = 'Historique provisions'
        verbose_name_plural = 'Historique provisions'


class ReglementSinistre(models.Model):
    sinistre = models.ForeignKey(Sinistre, null=True, on_delete=models.RESTRICT)
    provision = models.ForeignKey(Provision, null=True, on_delete=models.RESTRICT)
    sinistre_intervenant = models.ForeignKey(SinistreIntervenant, null=True, on_delete=models.RESTRICT)
    mode_reglement = models.ForeignKey(ModeReglement, null=True, on_delete=models.RESTRICT)
    devise = models.ForeignKey(Devise, null=True, on_delete=models.CASCADE)
    montant_regle = models.BigIntegerField(null=True)
    date_reglement = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reglement_sinistres'
        verbose_name = 'Règlement du sinistre'
        verbose_name_plural = 'Règlement du sinistre'


#
class MouvementSinistre(models.Model):
    sinistre = models.ForeignKey(Sinistre, null=True, on_delete=models.RESTRICT)
    police = models.ForeignKey(Police, null=True, on_delete=models.RESTRICT)
    mouvement = models.ForeignKey(Mouvement, null=True, on_delete=models.RESTRICT)
    motif = models.ForeignKey(Motif, null=True, on_delete=models.RESTRICT)
    historique_sinistre = models.ForeignKey(HistoriqueSinistre, null=True, on_delete=models.RESTRICT)
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT, related_name='created_by_sinistre_mouv')
    updated_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT, related_name='updated_by_sinistre_mouv')

    observation = models.CharField(max_length=255, blank=True, null=True)
    date_effet = models.DateField(blank=True, null=True)
    date_cloture_sinistre = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now=True)

    statut_validite = models.fields.CharField(choices=StatutValidite.choices, default=StatutValidite.VALIDE, max_length=15, null=True)


    def __str__(self):
        return f'Mouvement sinistre: {self.mouvement.libelle}/{self.motif.libelle} - Police N° {self.sinistre.numero}'

    class Meta:
        db_table = 'mouvements_sinistres'
        verbose_name = 'Mouvement du sinistre'
        verbose_name_plural = 'Mouvements du sinistre'


class SinistreEtape(models.Model):
    sinistre = models.ForeignKey(Sinistre, null=True, on_delete=models.RESTRICT)
    etape_sinistre = models.ForeignKey(EtapeSinistre, null=True, on_delete=models.RESTRICT)
    numero_ordre = models.PositiveIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sinistre_etape'
        verbose_name = 'Sinistre étape'
        verbose_name_plural = 'Sinistre étape'





class DossierSinistre(models.Model):
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    type_remboursement = models.ForeignKey(TypeRemboursement, null=True, on_delete=models.RESTRICT)
    mode_creation = models.ForeignKey(ModeCreation, null=True, on_delete=models.RESTRICT)
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    updated_by = models.ForeignKey(User, related_name="updated_by", null=True, on_delete=models.RESTRICT)
    type_prefinancement = models.ForeignKey(TypePrefinancement, null=True, on_delete=models.RESTRICT)
    type_priseencharge = models.ForeignKey(TypePriseencharge, null=True, on_delete=models.RESTRICT)
    prestataire = models.ForeignKey(Prestataire, related_name="dossiers_sinistres", null=True, on_delete=models.RESTRICT)
    centre_prescripteur = models.ForeignKey(Prestataire, related_name="centre_prescripteur", null=True, on_delete=models.RESTRICT)
    pharmacie = models.ForeignKey(Prestataire, related_name="pharmacie", null=True, on_delete=models.RESTRICT)
    prescripteur = models.ForeignKey(Prescripteur, null=True, on_delete=models.RESTRICT)
    aliment = models.ForeignKey(Aliment, null=True, on_delete=models.RESTRICT)
    compagnie = models.ForeignKey(Compagnie, null=True, on_delete=models.RESTRICT)
    formulegarantie = models.ForeignKey(FormuleGarantie, null=True, on_delete=models.RESTRICT)
    police = models.ForeignKey(Police, null=True, on_delete=models.RESTRICT)
    affection = models.ForeignKey(Affection, null=True, on_delete=models.RESTRICT)
    renseignement_clinique = models.TextField(blank=False, null=True)
    commentaire = models.TextField(blank=False, null=True)
    numero = models.CharField(max_length=25, blank=False, null=False)
    libelle = models.CharField(max_length=100, blank=False, null=False)
    plafond_chambre = models.FloatField(null=True, )
    plafond_hospit = models.FloatField(null=True, )
    plafond_accouchement = models.FloatField(null=True, )
    is_closed = models.BooleanField(default=False)
    of_gestionnaire = models.BooleanField(default=False)
    has_sinistre_traite_bymedecin = models.BooleanField(default=False)
    date_traitement_sinistre_bymedecin = models.DateTimeField(blank=True, null=True)
    date_survenance = models.DateTimeField(null=True)
    reference_facture = models.CharField(max_length=50, blank=True, null=True)
    date_reception_facture = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    statut_pec = models.fields.CharField(choices=StatutSinistre.choices, default=None, max_length=15, null=True)
    statut_prorogation = models.fields.CharField(choices=StatutSinistre.choices, default=None, max_length=15, null=True)
    statut_validite = models.fields.CharField(choices=StatutValidite.choices, default=StatutValidite.VALIDE, max_length=15, null=True)
    statut_remboursement = models.fields.CharField(choices=StatutRemboursement.choices, default=StatutRemboursement.ATTENTE, max_length=25, null=True)
    soins_a_l_entrange = models.BooleanField(default=False, null=True)


    class Meta:
        db_table = 'dossier_sinistre'
        verbose_name = 'Sinistre'
        verbose_name_plural = 'Liste des sinistres'

    @property
    def total_frais_reel(self):
        #return sum(sinistre.total_frais_reel for sinistre in self.sinistres.filter(type_sinistre="acte").exclude(statut="REJETE"))

        sinistres_accorde_ou_attente = self.sinistres.filter(
            type_sinistre="acte", statut__in=["ACCORDE", "EN ATTENTE"]
        )

        #si il y a des accorde ou en attente
        if sinistres_accorde_ou_attente.exists():
            return sum(sinistre.total_frais_reel for sinistre in sinistres_accorde_ou_attente)

        else:
            # Si tous les sinistres sont "REJETE", calcule leur somme
            sinistres_rejetes = self.sinistres.filter(type_sinistre="acte", statut="REJETE")
            return sum(sinistre.total_frais_reel for sinistre in sinistres_rejetes)


    @property
    def total_part_assure(self):
        #return sum(sinistre.total_part_assure for sinistre in self.sinistres.filter(type_sinistre="acte").exclude(statut="REJETE"))

        sinistres_accorde_ou_attente = self.sinistres.filter(
            type_sinistre="acte", statut__in=["ACCORDE", "EN ATTENTE"]
        )

        #si il y a des accorde ou en attente
        if sinistres_accorde_ou_attente.exists():
            return sum(sinistre.total_part_assure for sinistre in sinistres_accorde_ou_attente)

        else:
            # Si tous les sinistres sont "REJETE", calcule leur somme
            sinistres_rejetes = self.sinistres.filter(type_sinistre="acte", statut="REJETE")
            return sum(sinistre.total_part_assure for sinistre in sinistres_rejetes)


    @property
    def total_part_compagnie(self):
        #return sum(sinistre.total_part_compagnie for sinistre in self.sinistres.filter(type_sinistre="acte").exclude(statut="REJETE"))

        sinistres_accorde_ou_attente = self.sinistres.filter(
            type_sinistre="acte", statut__in=["ACCORDE", "EN ATTENTE"]
        )

        #si il y a des accorde ou en attente
        if sinistres_accorde_ou_attente.exists():
            return sum(sinistre.total_part_compagnie for sinistre in sinistres_accorde_ou_attente)

        else:
            # Si tous les sinistres sont "REJETE", calcule leur somme
            sinistres_rejetes = self.sinistres.filter(type_sinistre="acte", statut="REJETE")
            return sum(sinistre.total_part_compagnie for sinistre in sinistres_rejetes)


    @property
    def total_frais_reel_medicament(self):
        #sinistres = self.sinistres.filter(type_sinistre="medicament").exclude(statut="REJETE")

        #return sum(sinistre.total_frais_reel for sinistre in sinistres)

        sinistres_accorde_ou_attente = self.sinistres.filter(
            type_sinistre="medicament", statut__in=["ACCORDE", "EN ATTENTE"]
        )

        #si il y a des accorde ou en attente
        if sinistres_accorde_ou_attente.exists():
            return sum(sinistre.total_frais_reel for sinistre in sinistres_accorde_ou_attente)

        else:
            # Si tous les sinistres sont "REJETE", calcule leur somme
            sinistres_rejetes = self.sinistres.filter(type_sinistre="medicament", statut="REJETE")
            return sum(sinistre.total_frais_reel for sinistre in sinistres_rejetes)




    @property
    def total_part_assure_medicament(self):
        #sinistres = self.sinistres.filter(type_sinistre="medicament").exclude(statut="REJETE")

        #return sum(sinistre.total_part_assure for sinistre in sinistres)

        sinistres_accorde_ou_attente = self.sinistres.filter(
            type_sinistre="medicament", statut__in=["ACCORDE", "EN ATTENTE"]
        )

        #si il y a des accorde ou en attente
        if sinistres_accorde_ou_attente.exists():
            return sum(sinistre.total_part_assure for sinistre in sinistres_accorde_ou_attente)

        else:
            # Si tous les sinistres sont "REJETE", calcule leur somme
            sinistres_rejetes = self.sinistres.filter(type_sinistre="medicament", statut="REJETE")
            return sum(sinistre.total_part_assure for sinistre in sinistres_rejetes)




    @property
    def total_part_compagnie_medicament(self):
        #sinistres = self.sinistres.filter(type_sinistre="medicament").exclude(statut="REJETE")

        #return sum(sinistre.total_part_compagnie for sinistre in sinistres)

        sinistres_accorde_ou_attente = self.sinistres.filter(
            type_sinistre="medicament", statut__in=["ACCORDE", "EN ATTENTE"]
        )

        #si il y a des accorde ou en attente
        if sinistres_accorde_ou_attente.exists():
            return sum(sinistre.total_part_compagnie for sinistre in sinistres_accorde_ou_attente)

        else:
            # Si tous les sinistres sont "REJETE", calcule leur somme
            sinistres_rejetes = self.sinistres.filter(type_sinistre="medicament", statut="REJETE")
            return sum(sinistre.total_part_compagnie for sinistre in sinistres_rejetes)


#

    #Todo: Tenir compte du fait que sur le dossier_sinistre il peut avoir des sinistres préfinancés et d'autres non.
    @property
    def new_total_part_assure_medicament_gestionnaire(self):
        sinistres_accorde_ou_attente = self.sinistres.filter(
            type_sinistre="medicament", statut__in=["ACCORDE", "EN ATTENTE"]
        )

        #si il y a des accorde ou en attente
        if sinistres_accorde_ou_attente.exists():
            return sum(sinistre.total_part_assure for sinistre in sinistres_accorde_ou_attente)

        else:
            # Si tous les sinistres sont "REJETE", calcule leur somme
            sinistres_rejetes = self.sinistres.filter(type_sinistre="medicament", statut="REJETE")
            return sum(sinistre.total_part_assure for sinistre in sinistres_rejetes)


    #Todo: Tenir compte du fait que sur le dossier_sinistre il peut avoir des sinistres préfinancés et d'autres non.
    @property
    def new_total_part_assure_medicament_prestataire(self):
        sinistres_accorde_ou_attente = self.sinistres.filter(
            type_sinistre="medicament", statut__in=["ACCORDE", "EN ATTENTE"]
        )

        #si il y a des accorde ou en attente
        if sinistres_accorde_ou_attente.exists():
            return sum(0 if sinistre.tm_prefinanced else sinistre.total_part_assure for sinistre in sinistres_accorde_ou_attente)

        else:
            # Si tous les sinistres sont "REJETE", calcule leur somme
            sinistres_rejetes = self.sinistres.filter(type_sinistre="medicament", statut="REJETE")
            return sum(0 if sinistre.tm_prefinanced else sinistre.total_part_assure for sinistre in sinistres_rejetes)


    # Todo: Tenir compte du fait que sur le dossier_sinistre il peut avoir des sinistres préfinancés et d'autres non.
    @property
    def new_total_part_compagnie_medicament_gestionnaire(self):
        sinistres_accorde_ou_attente = self.sinistres.filter(
            type_sinistre="medicament", statut__in=["ACCORDE", "EN ATTENTE"]
        )

        #si il y a des accorde ou en attente
        if sinistres_accorde_ou_attente.exists():
            return sum(sinistre.total_part_compagnie for sinistre in sinistres_accorde_ou_attente)

        else:
            # Si tous les sinistres sont "REJETE", calcule leur somme
            sinistres_rejetes = self.sinistres.filter(type_sinistre="medicament", statut="REJETE")
            return sum(sinistre.total_part_compagnie for sinistre in sinistres_rejetes)


    # Todo: Tenir compte du fait que sur le dossier_sinistre il peut avoir des sinistres préfinancés et d'autres non.
    @property
    def new_total_part_compagnie_medicament_prestataire(self):
        sinistres_accorde_ou_attente = self.sinistres.filter(
            type_sinistre="medicament", statut__in=["ACCORDE", "EN ATTENTE"]
        )

        #si il y a des accorde ou en attente
        if sinistres_accorde_ou_attente.exists():
            return sum(sinistre.total_frais_reel if sinistre.tm_prefinanced else sinistre.total_part_compagnie for sinistre in sinistres_accorde_ou_attente)

        else:
            # Si tous les sinistres sont "REJETE", calcule leur somme
            sinistres_rejetes = self.sinistres.filter(type_sinistre="medicament", statut="REJETE")
            return sum(sinistre.total_frais_reel if sinistre.tm_prefinanced else sinistre.total_part_compagnie for sinistre in sinistres_rejetes)

#

    @property
    def total_frais_reel_general(self):
        return (self.total_frais_reel + self.total_frais_reel_medicament)

    @property
    def total_part_assure_general(self):
        return (self.total_part_assure + self.total_part_assure_medicament)

    @property
    def total_part_compagnie_general(self):
        return (self.total_part_compagnie + self.total_part_compagnie_medicament)
        

    #Todo: Tenir compte du fait que sur le dossier_sinistre il peut avoir des sinistres préfinancés et d'autres non.
    @property
    def new_total_frais_reel(self):
        sinistres_accorde_ou_attente = self.sinistres.filter(
            type_sinistre="acte", statut__in=["ACCORDE", "EN ATTENTE"]
        )

        #si il y a des accorde ou en attente
        if sinistres_accorde_ou_attente.exists():
            return sum(sinistre.total_frais_reel for sinistre in sinistres_accorde_ou_attente)

        else:
            # Si tous les sinistres sont "REJETE", calcule leur somme
            sinistres_rejetes = self.sinistres.filter(type_sinistre="acte", statut="REJETE")
            return sum(sinistre.total_frais_reel for sinistre in sinistres_rejetes)


    #Todo: Tenir compte du fait que sur le dossier_sinistre il peut avoir des sinistres préfinancés et d'autres non.
    @property
    def new_total_part_assure_gestionnaire(self):
        sinistres_accorde_ou_attente = self.sinistres.filter(
            type_sinistre="acte", statut__in=["ACCORDE", "EN ATTENTE"]
        )

        #si il y a des accorde ou en attente
        if sinistres_accorde_ou_attente.exists():
            return sum(sinistre.total_part_assure for sinistre in sinistres_accorde_ou_attente)

        else:
            # Si tous les sinistres sont "REJETE", calcule leur somme
            sinistres_rejetes = self.sinistres.filter(type_sinistre="acte", statut="REJETE")
            return sum(sinistre.total_part_assure for sinistre in sinistres_rejetes)


    #Todo: Tenir compte du fait que sur le dossier_sinistre il peut avoir des sinistres préfinancés et d'autres non.
    @property
    def new_total_part_assure_prestataire(self):
        sinistres_accorde_ou_attente = self.sinistres.filter(
            type_sinistre="acte", statut__in=["ACCORDE", "EN ATTENTE"]
        )

        #si il y a des accorde ou en attente
        if sinistres_accorde_ou_attente.exists():
            return sum(0 if sinistre.tm_prefinanced else sinistre.total_part_assure for sinistre in sinistres_accorde_ou_attente)

        else:
            # Si tous les sinistres sont "REJETE", calcule leur somme
            sinistres_rejetes = self.sinistres.filter(type_sinistre="acte", statut="REJETE")
            return sum(0 if sinistre.tm_prefinanced else sinistre.total_part_assure for sinistre in sinistres_rejetes)


    # Todo: Tenir compte du fait que sur le dossier_sinistre il peut avoir des sinistres préfinancés et d'autres non.
    @property
    def new_total_part_compagnie_gestionnaire(self):
        sinistres_accorde_ou_attente = self.sinistres.filter(
            type_sinistre="acte", statut__in=["ACCORDE", "EN ATTENTE"]
        )

        #si il y a des accorde ou en attente
        if sinistres_accorde_ou_attente.exists():
            return sum(sinistre.total_part_compagnie for sinistre in sinistres_accorde_ou_attente)

        else:
            # Si tous les sinistres sont "REJETE", calcule leur somme
            sinistres_rejetes = self.sinistres.filter(type_sinistre="acte", statut="REJETE")
            return sum(sinistre.total_part_compagnie for sinistre in sinistres_rejetes)


    # Todo: Tenir compte du fait que sur le dossier_sinistre il peut avoir des sinistres préfinancés et d'autres non.
    @property
    def new_total_part_compagnie_prestataire(self):
        sinistres_accorde_ou_attente = self.sinistres.filter(
            type_sinistre="acte", statut__in=["ACCORDE", "EN ATTENTE"]
        )

        #si il y a des accorde ou en attente
        if sinistres_accorde_ou_attente.exists():
            return sum(sinistre.total_frais_reel if sinistre.tm_prefinanced else sinistre.total_part_compagnie for sinistre in sinistres_accorde_ou_attente)

        else:
            # Si tous les sinistres sont "REJETE", calcule leur somme
            sinistres_rejetes = self.sinistres.filter(type_sinistre="acte", statut="REJETE")
            return sum(sinistre.total_frais_reel if sinistre.tm_prefinanced else sinistre.total_part_compagnie for sinistre in sinistres_rejetes)


    @property
    def statut(self):
        has_sinistre_enttente = self.sinistres.filter(statut=StatutSinistre.ATTENTE)
        has_sinistre_accorde = self.sinistres.filter(statut=StatutSinistre.ACCORDE)
        has_sinistre_rejete = self.sinistres.filter(statut=StatutSinistre.REJETE)

        if has_sinistre_enttente:
            statut = 'EN ATTENTE'
        elif has_sinistre_accorde:
            statut = 'ACCORDE'
        elif has_sinistre_rejete:
            statut = 'REJETE'
        else:
            statut = 'VIDE'

        return statut

    @property
    def reviewed_by(self):
        reviewer = None

        sinistres = self.sinistres.filter(Q(statut=StatutSinistre.ACCORDE) | Q(statut=StatutSinistre.REJETE))

        automatiques = sinistres.filter(approuved_by__isnull=True)
        manuels = sinistres.filter(approuved_by__isnull=False)


        if sinistres:
            if not manuels:
                reviewer = automatiques.order_by('reviewed_at').first().approuved_by

            else:
                reviewer = manuels.order_by('reviewed_at').first().approuved_by

        '''
        if sinistres_accordes:
            reviewer = sinistres_accordes.first().approuved_by

        else:
            sinistres_rejetes = self.sinistres.filter(statut=StatutSinistre.REJETE)
            if sinistres_rejetes:
                reviewer = sinistres_rejetes.first().approuved_by
        '''

        return reviewer


    @property
    def reviewed_at(self):
        review_date = None

        sinistres = self.sinistres.filter(Q(statut=StatutSinistre.ACCORDE) | Q(statut=StatutSinistre.REJETE))

        automatiques = sinistres.filter(approuved_by__isnull=True)
        manuels = sinistres.filter(approuved_by__isnull=False)

        if sinistres:
            if not manuels:
                review_date = automatiques.order_by('reviewed_at').first().reviewed_at

            else:
                review_date = manuels.order_by('reviewed_at').first().reviewed_at

        #dd(sinistres.first().numero)
        return review_date


    @property
    def has_seances(self):
        for sinistre in self.sinistres.all():
            if sinistre.acte and sinistre.acte.option_seance:
                return True

        return False


    @property
    def has_prorogation(self):
        for sinistre in self.sinistres.all():
            if sinistre.prorogations.exists():
                return True

        return False

    @property
    def has_sinistre_en_attente(self):
        if self.sinistres.filter(statut=StatutSinistre.ATTENTE).exists():
            return True

        return False

    @property
    def has_prorogation_en_attente(self):
        for sinistre in self.sinistres.all():
            if sinistre.prorogations.filter(statut=StatutSinistre.ATTENTE).exists():
                return True

        return False

    #@property
    #def statut_prorogation(self):
    #    return self.sinistres.first().statut_prorogation


    # A COMPLETER AVEC LES PREF TM UNIQUEMENT, ...
    @property
    def tm_prefinanced(self):
        return True if (self.type_prefinancement and self.type_prefinancement.code == 'PREF_TOUT') else False


def upload_location_factureprestataire(instance, filename):
    filebase, extension = filename.rsplit('.', 1)
    file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return 'dossiers_sinistres/bordereaux/%s.%s' % (file_name, extension)


class FacturePrestataire(models.Model):
    numero = models.CharField(max_length=255, blank=True, null=True, unique=True)
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    type_remboursement = models.ForeignKey(TypeRemboursement, null=True, on_delete=models.RESTRICT)
    prestataire = models.ForeignKey(Prestataire, null=True, on_delete=models.RESTRICT)
    adherent_principal = models.ForeignKey(Aliment, null=True, on_delete=models.RESTRICT)
    assure = models.ForeignKey(Client, null=True, on_delete=models.RESTRICT)
    periode_comptable = models.ForeignKey(PeriodeComptable, null=True, on_delete=models.RESTRICT)
    fichier = models.FileField(upload_to=upload_location_factureprestataire, blank=True, default=None, null=True)
    observation = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    fp_deleted_by = models.ForeignKey(User, related_name="fp_deleted_by", null=True, on_delete=models.RESTRICT)
    statut = models.fields.CharField(choices=SatutBordereauDossierSinistres.choices, default=SatutBordereauDossierSinistres.ATTENTE, max_length=30, null=True)
    statut_validite = models.fields.CharField(choices=StatutValidite.choices, default=StatutValidite.VALIDE, max_length=15, null=True)
    net_a_payer = models.FloatField(null=True, )

    def __str__(self):
        return f'{self.numero} | {self.prestataire}'

    class Meta:
        db_table = 'factures_prestataires'
        verbose_name = 'Facture prestataire'
        verbose_name_plural = 'Factures prestataires'

        permissions = [
            #("can_views_factures", "Can do something with this model"),
            #("can_do_another_thing", "Can do another thing with this model"),
        ]


def upload_location_bordereauordonnancement(instance, filename):
    filebase, extension = filename.rsplit('.', 1)
    file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return 'dossiers_sinistres/bordereaux/%s.%s' % (file_name, extension)


class BordereauOrdonnancement(models.Model):
    numero = models.CharField(max_length=255, blank=True, null=True, unique=True)
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    type_remboursement = models.ForeignKey(TypeRemboursement, null=True, on_delete=models.RESTRICT)
    prestataire = models.ForeignKey(Prestataire, null=True, on_delete=models.RESTRICT)
    adherent_principal = models.ForeignKey(Aliment, null=True, on_delete=models.RESTRICT)
    assure = models.ForeignKey(Client, null=True, on_delete=models.RESTRICT)
    periode_comptable = models.ForeignKey(PeriodeComptable, null=True, on_delete=models.RESTRICT)
    fichier = models.FileField(upload_to=upload_location_bordereauordonnancement, blank=True, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    bo_deleted_by = models.ForeignKey(User, related_name="bo_deleted_by", null=True, on_delete=models.RESTRICT)
    montant_remb_total = models.FloatField(null=True, )
    montant_rejet_total = models.FloatField(null=True, )
    montant_accepte_total = models.FloatField(null=True, )
    montant_total_paye = models.FloatField(null=True, )
    montant_total_impaye = models.FloatField(null=True, )
    ordre_de = models.CharField(max_length=255, blank=True, null=True)
    par_compagnie = models.BooleanField(default=True)
    observation = models.CharField(max_length=255, blank=True, null=True)
    statut_paiement = models.fields.CharField(choices=StatutPaiementSinistre.choices, default=StatutPaiementSinistre.ORDONNANCE, max_length=15, null=True)
    statut_validite = models.fields.CharField(choices=StatutValidite.choices, default=StatutValidite.VALIDE, max_length=15, null=True)


    def __str__(self):
        return f'{self.numero} | {self.prestataire}'

    @classmethod
    def par_bureau(cls, bureau):
        return cls.objects.filter(bureau=bureau)

    class Meta:
        db_table = 'bordereau_ordonnancement'
        verbose_name = 'Bordereau de ordonnancement'
        verbose_name_plural = 'Bordereaux de ordonnancements'

        permissions = [
            #("can_views_factures", "Can do something with this model"),
            #("can_do_another_thing", "Can do another thing with this model"),
        ]
        

def upload_location_paiementcomptable(instance, filename):
    filebase, extension = filename.rsplit('.', 1)
    file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return 'dossiers_sinistres/bordereaux_paiements_comptables/%s.%s' % (file_name, extension)


class PaiementComptable(models.Model):
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    adherent_principal = models.ForeignKey(Aliment, null=True, on_delete=models.RESTRICT)
    prestataire = models.ForeignKey(Prestataire, null=True, on_delete=models.RESTRICT)
    nom_beneficiaire = models.CharField(max_length=100, blank=True, null=True)
    numero_iban = models.CharField(max_length=50, blank=True, null=True)
    bordereau_ordonnancement = models.ForeignKey(BordereauOrdonnancement, null=True, on_delete=models.RESTRICT)
    compagnie = models.ForeignKey(Compagnie, null=True, on_delete=models.RESTRICT)
    mode_reglement = models.ForeignKey(ModeReglement, null=True, on_delete=models.RESTRICT)
    banque = models.ForeignKey(Banque, null=True, on_delete=models.RESTRICT)
    banque_emettrice = models.CharField(max_length=255, blank=True, null=True)
    numero_piece = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField(max_length=100, blank=True, null=True)
    montant_total = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True)
    nombre_sinistres = models.IntegerField(blank=True, null=True)
    date_paiement = models.DateField(blank=True, null=True)
    fichier = models.FileField(upload_to=upload_location_paiementcomptable, blank=True, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uuid = models.CharField(max_length=255, null=True)
    bordereau_lettre_cheque = models.ForeignKey(BordereauLettreCheque, null=True, on_delete=models.RESTRICT)
    statut_validite = models.fields.CharField(choices=StatutValidite.choices, default=StatutValidite.VALIDE,
                                              max_length=15, null=True)
    observation = models.CharField(max_length=255, null=True)
    pc_deleted_by = models.ForeignKey(User, related_name="pc_deleted_by", null=True, on_delete=models.RESTRICT)

    def __str__(self):
        return self.numero

    class Meta:
        db_table = 'paiement_comptable'
        verbose_name = 'Paiement comptable'
        verbose_name_plural = 'Paiements comptable'


def generate_random_invoice_number():
    return ''.join(random.choices('0123456789', k=8))


class FactureCompagnie(models.Model):
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    compagnie = models.ForeignKey(Compagnie, null=True, on_delete=models.RESTRICT)
    devise = models.ForeignKey(Devise, null=True, on_delete=models.RESTRICT)
    numero = models.CharField(max_length=20, blank=True, default=generate_random_invoice_number, unique=True)
    montant_total = models.BigIntegerField(null=False)
    montant_regle = models.BigIntegerField(null=True, default=0)
    montant_restant = models.BigIntegerField(null=True)
    date_emission = models.DateField(blank=True, null=True)
    fichier = models.FileField(upload_to='factures/fact_compagnies', blank=True, default=None, null=True)
    statut = models.fields.CharField(choices=StatutFacture.choices, default=StatutFacture.NON_SOLDE, max_length=15, null=True)
    statut_validite = models.fields.CharField(choices=StatutValidite.choices, default=StatutValidite.VALIDE, max_length=15, null=True)
    observation = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'N°{self.numero} - Montant: {self.montant} {self.devise.code} '

    @classmethod
    def par_bureau(cls, bureau):
        return cls.objects.filter(bureau=bureau)

    class Meta:
        db_table = "facture_compagnie"
        verbose_name = "Facture d'une compagnie"
        verbose_name_plural = "Factures des compagnies"


class ReglementCompagnie(models.Model):
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    compagnie = models.ForeignKey(Compagnie, null=True, on_delete=models.RESTRICT)
    numero = models.CharField(max_length=50, blank=True, null=True)
    numero_piece = models.CharField(max_length=50, blank=True, null=True)
    banque_emettrice = models.CharField(max_length=255, blank=True, null=True)
    mode_reglement = models.ForeignKey(ModeReglement, null=True, on_delete=models.RESTRICT)
    banque = models.ForeignKey(Banque, null=True, on_delete=models.RESTRICT)
    compte_tresorerie = models.ForeignKey(CompteTresorerie, null=True, on_delete=models.RESTRICT)
    devise = models.ForeignKey(Devise, null=True, on_delete=models.RESTRICT)
    montant = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True)
    date_reglement = models.DateField(blank=True, null=True)
    observation = models.CharField(max_length=255, null=True)
    motif_annulation = models.CharField(max_length=255, null=True)
    statut_validite = models.fields.CharField(choices=StatutValidite.choices, default=StatutValidite.VALIDE, max_length=15, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reglement_compagnie'
        verbose_name = 'Reglement compagnie'
        verbose_name_plural = 'Reglements faits par les compagnies'


class ReglementFactureCompagnie(models.Model):
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    reglement_compagnie = models.ForeignKey(ReglementCompagnie, on_delete=models.RESTRICT)
    facture_compagnie = models.ForeignKey(FactureCompagnie, on_delete=models.RESTRICT)
    montant_regle = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True)
    observation = models.CharField(max_length=255, null=True)
    statut_validite = models.fields.CharField(choices=StatutValidite.choices, default=StatutValidite.VALIDE, max_length=15, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reglement_facture_compagnie'
        verbose_name = 'Reglement facture'
        verbose_name_plural = 'Reglement facture'


class RemboursementSinistre(models.Model):
    created_by = models.ForeignKey(User, related_name="remboursements_crees", null=True, on_delete=models.RESTRICT)
    designation = models.CharField(max_length=255, blank=True, null=True)
    sinistre = models.ForeignKey(Sinistre, related_name="remboursements", on_delete=models.RESTRICT)
    montant = models.DecimalField(max_digits=50, decimal_places=16, null=True)
    motif = models.CharField(max_length=255, blank=True, null=True)
    observation = models.CharField(max_length=255, blank=True, null=True)
    statut = models.fields.CharField(choices=StatutRemboursementSinistre.choices, default=StatutRemboursementSinistre.REFUSE, max_length=15, null=True)
    option_refacturation = models.fields.CharField(choices=OptionRefacturation.choices, default=OptionRefacturation.NON_REFACTURABLE, max_length=20, null=True)
    is_invalid = models.BooleanField(default=False)
    is_invalid_by = models.ForeignKey(User, related_name="remboursements_rejetes", null=True, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'remboursement_sinistre'
        verbose_name = 'Remboursement'
        verbose_name_plural = 'Remboursements'

    @property
    def is_accepted(self):
        if self.statut == StatutRemboursementSinistre.ACCEPTE:
            return True
        return False

    @property
    def is_refused(self):
        if self.statut == StatutRemboursementSinistre.REFUSE:
            return True
        return False


class ProrogationSinistre(models.Model):
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    reviewed_by = models.ForeignKey(User, null=True, related_name='reviewed_by', on_delete=models.RESTRICT)
    sinistre = models.ForeignKey(Sinistre, related_name="prorogations", on_delete=models.RESTRICT)
    motif_demande = models.CharField(max_length=255, blank=True, null=True)
    motif_rejet = models.CharField(max_length=255, blank=True, null=True)
    jour_demande = models.IntegerField(default=0)
    jour_accorde = models.IntegerField(default=0)
    date_entree = models.DateTimeField(null=True)
    date_sortie = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    statut = models.fields.CharField(choices=StatutSinistre.choices, default=StatutSinistre.ATTENTE, max_length=15, null=True)

    def __str__(self):
        return f' Demande de prorogation de {self.jour_demande} jour(s)'

    class Meta:
        db_table = 'prorogation_sinistre'
        verbose_name = 'Prorogation'
        verbose_name_plural = 'Prorogations'


#historique des sinistre sur un bordereau d'ordonnancment au cas ou on doit annuler un bordereau d'ordonnancement on concerve l'historique
class HistoriqueOrdonnancementSinistre(models.Model):
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    bordereau_ordonnancement = models.ForeignKey(BordereauOrdonnancement, on_delete=models.RESTRICT)
    sinistre = models.ForeignKey(Sinistre, on_delete=models.RESTRICT)
    montant_ordonnance = models.DecimalField(max_digits=50, decimal_places=16, null=True)
    observation = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'historique_ordonnancement_sinistre'
        verbose_name = 'Historique ordonnancement sinistre'
        verbose_name_plural = 'Historique ordonnancement sinistre'


def upload_location_documentdossiersinistre(instance, filename):
    filebase, extension = filename.rsplit('.', 1)
    file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return 'dossiers_sinistres/documents/%s.%s' % (file_name, extension)


class DocumentDossierSinistre(models.Model):
    dossier_sinistre = models.ForeignKey(DossierSinistre, related_name="documents", on_delete=models.RESTRICT)
    type_document = models.ForeignKey(TypeDocument, on_delete=models.RESTRICT)
    nom = models.CharField(max_length=255, blank=True, null=True)
    fichier = models.FileField(upload_to=upload_location_documentdossiersinistre, blank=True, default=None, null=True)
    commentaire = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    statut = models.fields.CharField(choices=Statut.choices, default=Statut.ACTIF, max_length=15, null=True)

    def __str__(self):
        return self.nom

    class Meta:
        db_table = 'documents_dossiers_sinistres'
        verbose_name = 'Document prise en charge'
        verbose_name_plural = 'Documents prises en charge'


class ControlePlafond(models.Model):
    session_pec = models.CharField(max_length=255, blank=True, null=True)
    plafond_conso_famille = models.CharField(max_length=255, blank=True, null=True)
    plafond_conso_individuel = models.CharField(max_length=255, blank=True, null=True)
    plafond_conso_sous_rubrique = models.CharField(max_length=255, blank=True, null=True)
    plafond_conso_regroupement_acte = models.CharField(max_length=255, blank=True, null=True)
    plafond_conso_acte = models.CharField(max_length=255, blank=True, null=True)
    rubrique = models.ForeignKey(Rubrique, on_delete=models.RESTRICT)
    sous_rubrique = models.ForeignKey(SousRubrique, null=True, on_delete=models.RESTRICT)
    regroupement_acte = models.ForeignKey(RegroupementActe, null=True, on_delete=models.RESTRICT)
    acte = models.ForeignKey(Acte, null=True, on_delete=models.RESTRICT)
    aliment = models.ForeignKey(Aliment, null=True, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'controle_plafond'
        verbose_name = 'Controle plafond'
        verbose_name_plural = 'Controle plafonds'


#pour permettre le calcul de plafond pendant les ambulatoires
class SinistreTemporaire(models.Model):
    session_pec = models.CharField(max_length=100, blank=True, null=True)
    observation = models.CharField(max_length=255, blank=True, null=True)

    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    updated_price_by = models.ForeignKey(User, related_name="st_updated_price_by", null=True, on_delete=models.RESTRICT)
    approuved_by = models.ForeignKey(User, related_name="st_approbateur", null=True, on_delete=models.RESTRICT)
    served_by = models.ForeignKey(User, related_name="st_serveur", null=True, on_delete=models.RESTRICT)
    dossier_sinistre = models.ForeignKey(DossierSinistre, related_name="st_sinistres", null=True, on_delete=models.RESTRICT)
    aliment = models.ForeignKey(Aliment, null=True, on_delete=models.RESTRICT)
    adherent_principal = models.ForeignKey(Aliment, related_name="st_famille", null=True, on_delete=models.RESTRICT)
    compagnie = models.ForeignKey(Compagnie, null=True, on_delete=models.RESTRICT)
    police = models.ForeignKey(Police, null=True, on_delete=models.RESTRICT)
    periode_couverture = models.ForeignKey(PeriodeCouverture, null=True, on_delete=models.RESTRICT)
    formulegarantie = models.ForeignKey(FormuleGarantie, null=True, on_delete=models.RESTRICT)
    bareme = models.ForeignKey(Bareme, null=True, blank=True, on_delete=models.RESTRICT)
    acte = models.ForeignKey(Acte, null=True, on_delete=models.RESTRICT)
    medicament = models.ForeignKey(Medicament, null=True, on_delete=models.RESTRICT)
    affection = models.ForeignKey(Affection, null=True, on_delete=models.RESTRICT)
    prestataire = models.ForeignKey(Prestataire, null=True, on_delete=models.RESTRICT)
    prescripteur = models.ForeignKey(Prescripteur, null=True, on_delete=models.RESTRICT)
    numero = models.CharField(max_length=50, blank=True, null=True)
    type_sinistre = models.CharField(max_length=100, blank=False, null=True)
    prix_unitaire = models.IntegerField(default=0, null=True)
    frais_reel = models.DecimalField(max_digits=50, decimal_places=16, null=True)
    ticket_moderateur = models.DecimalField(max_digits=50, decimal_places=16, null=True)
    depassement = models.DecimalField(max_digits=50, decimal_places=16, null=True)

    nombre_demande = models.IntegerField(null=True, )
    nombre_accorde = models.IntegerField(null=True, )

    plafond_chambre = models.DecimalField(max_digits=50, decimal_places=16, null=True)
    plafond_hospit = models.DecimalField(max_digits=50, decimal_places=16, null=True)

    montant_plafond = models.DecimalField(max_digits=50, decimal_places=16, null=True)
    nombre_plafond = models.IntegerField(null=True, )
    nature = models.IntegerField(null=True, )
    frequence = models.IntegerField(null=True, )
    unite_frequence = models.IntegerField(null=True, )
    franchise_min = models.FloatField(null=True, )
    franchise_max = models.FloatField(null=True, )
    delai_controle = models.IntegerField(null=True, )

    part_assure = models.DecimalField(max_digits=50, decimal_places=16, null=True)
    part_compagnie = models.DecimalField(max_digits=50, decimal_places=16, null=True)

    date_survenance = models.DateTimeField(null=True)
    date_entree = models.DateTimeField(null=True)
    date_sortie = models.DateTimeField(null=True)
    reference_facture = models.CharField(max_length=50, blank=True, null=True)
    date_reception_facture = models.DateTimeField(blank=True, null=True)
    motif_rejet = models.CharField(max_length=255, blank=True, null=True)
    statut = models.fields.CharField(choices=StatutSinistre.choices, default=StatutSinistre.ACCORDE, max_length=15, null=True)
    statut_prestation = models.fields.CharField(choices=StatutSinistrePrestation.choices, default=StatutSinistrePrestation.ATTENTE, max_length=15, null=True)
    statut_bordereau = models.fields.CharField(choices=StatutSinistreBordereau.choices, default=StatutSinistreBordereau.ATTENTE, max_length=20, null=True)
    statut_synchro_veos = models.fields.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'sinistres_temporaires'
        verbose_name = 'Sinistre temporaire'
        verbose_name_plural = 'Sinistres temporaires'


class DemandeRemboursementMobile(models.Model):
    date_sinistre = models.DateField(blank=True)
    acte = models.ForeignKey(Acte, on_delete=models.RESTRICT)
    prestataire = models.ForeignKey(Prestataire, on_delete=models.RESTRICT)
    beneficiaire = models.ForeignKey(Aliment, related_name='beneficiaire_remboursements', on_delete=models.RESTRICT)
    adherent_principal = models.ForeignKey(Aliment, null=True, on_delete=models.RESTRICT)
    bureau = models.ForeignKey(Bureau,  null=True, on_delete=models.RESTRICT)
    montant_a_rembourser = models.DecimalField(max_digits=20, decimal_places=2)
    mode_remboursement = models.ForeignKey(ModeReglement, on_delete=models.RESTRICT)
    numero_remboursement = models.CharField(max_length=100, null=True, blank=True)
    prescription_medical = models.FileField(upload_to='sinistre/documents/prescription_medical/', blank=True, default=None)
    facture_normalisee = models.FileField(upload_to='sinistre/documents/facture_normalisee/', blank=True, default=None)
    acquittee_laboratoire = models.FileField(upload_to='sinistre/documents/acquittee_laboratoire/', blank=True, default=None, null=True)
    autre_document = models.FileField(upload_to='sinistre/documents/autres/', null=True, blank=True)
    statut = models.fields.CharField(choices=StatutRemboursement.choices, default=StatutRemboursement.ATTENTE, max_length=25)

    def _str_(self):
        return f"Demande de remboursement {self.id}"

    class Meta:
        db_table = 'demande_remboursement_mobile'
        verbose_name = "Demande de remboursement mobile"
        verbose_name_plural = "Demandes de remboursement mobiles"


#suivi du traitement des factures prestataires
class TrackFacture(models.Model):
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    prestataire = models.ForeignKey(Prestataire, null=True, on_delete=models.RESTRICT)
    code_systeme = models.CharField(max_length=255, blank=True, null=True)
    reference_facture_prestataire = models.CharField(max_length=255, blank=True, null=True)
    montant_facture = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    nombre_feuilles_soins = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    date_reception = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'track_facture'
        verbose_name = 'track_facture'
        verbose_name_plural = 'track_facture'


class TrackEtape(models.Model):
    code = models.CharField(max_length=50, blank=True, null=True)
    libelle = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'track_etape'
        verbose_name = 'Etape'
        verbose_name_plural = 'Etape'


class TrackEtapeFacture(models.Model):
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    track_facture = models.ForeignKey(TrackFacture, on_delete=models.RESTRICT)
    etape = models.ForeignKey(TrackEtape, null=True, on_delete=models.RESTRICT)
    observation = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'track_etape_facture'
        verbose_name = 'Etape Facture'
        verbose_name_plural = 'Etapes Factures'


# Historique des sinistres payés
class HistoriquePaiementComptableSinistre(models.Model):
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    paiement_comptable = models.ForeignKey(PaiementComptable, on_delete=models.RESTRICT)
    sinistre = models.ForeignKey(Sinistre, on_delete=models.RESTRICT)
    montant_paye = models.DecimalField(max_digits=50, decimal_places=16, null=True)
    observation = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'historique_paiement_comptable_sinistre'
        verbose_name = 'Historique paiement comptable sinistre'
        verbose_name_plural = 'Historique paiement comptable sinistre'