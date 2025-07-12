import datetime
from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone


from configurations.models import CompteTresorerie, Devise, Medicament, Compagnie, User, TypePriseencharge, Prestataire, Prescripteur, Acte, \
    Rubrique, SousRubrique, RegroupementActe, TypePrefinancement, PeriodeComptable, ModeCreation, Bureau, Circonstance, TypeSinistre, Responsabilite, TypeIntervenant, PosteDommage, Pays, \
    TypeRemboursement, ModeReglement, Banque, BordereauLettreCheque, Garantie
from production.models import TypeDocument, Aliment, HistoriqueAliment, Police, HistoriquePolice, PeriodeCouverture, FormuleGarantie, Bareme, Client, AlimentPolice, Mouvement, Motif
from shared.enum import StatutFacture, StatutSinistre, SatutBordereauDossierSinistres, StatutSinistreBordereau, \
    StatutSinistrePrestation, StatutValidite, StatutRemboursement, StatutRemboursementSinistre, Statut, \
    OptionRefacturation, StatutPaiementSinistre, SourceCreationSinistre

import random


from decimal import Decimal


class Sinistre(models.Model):
    numero = models.CharField(max_length=255, unique=True, db_index=True, null=True, blank=True)

    date_ouverture = models.DateField(null=True, blank=True)
    date_cloture = models.DateField(null=True, blank=True)
    date_survenance = models.DateField(null=True, blank=True)
    date_declaration = models.DateField(null=True, blank=True)
    date_reouverture = models.DateField(null=True, blank=True)
    date_reglement = models.DateField(null=True, blank=True)

    montant_provision = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)
    montant_provision_regle = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)
    montant_recours = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)
    montant_recours_regle = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)
    montant_sinistre = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)

    point_de_choc = models.CharField(max_length=255, null=True, blank=True)
    fait_generateur = models.CharField(max_length=255, null=True, blank=True)
    commentaires = models.TextField(null=True, blank=True)
    lieu_survenance = models.CharField(max_length=255, null=True, blank=True)

    tva_recuperee = models.BooleanField(null=True, blank=True)

    police = models.ForeignKey(Police, null=True, blank=True, on_delete=models.RESTRICT, related_name='sinistres')
    historique_police = models.ForeignKey(HistoriquePolice, null=True, blank=True, on_delete=models.RESTRICT, related_name='sinistres')
    historique_aliment = models.ForeignKey(HistoriqueAliment, null=True, blank=True, on_delete=models.RESTRICT, related_name='sinistres')
    historique_sinistre = models.ForeignKey('HistoriqueSinistre', null=True, blank=True, on_delete=models.RESTRICT, related_name='sinistres')
    taux_responsabilite = models.ForeignKey(Responsabilite, null=True, on_delete=models.RESTRICT, related_name='sinistres')
    type_sinistre = models.ForeignKey(TypeSinistre, null=True, on_delete=models.RESTRICT, related_name='sinistres')
    circonstance = models.ForeignKey(Circonstance, null=True, blank=True, on_delete=models.RESTRICT, related_name='sinistres')
    compagnie = models.ForeignKey(Compagnie, null=True, blank=True, on_delete=models.RESTRICT, related_name='sinistres')

    class Meta:
        db_table = 'sinistres'
        verbose_name = 'Sinistre'
        verbose_name_plural = 'Sinistres'

    def __str__(self):
        return f"{self.numero or 'Sinistre'}"


class HistoriqueSinistre(models.Model):
    date_operation = models.DateField(null=True, blank=True)
    date_ouverture = models.DateField(null=True, blank=True)
    date_cloture = models.DateField(null=True, blank=True)
    date_survenance = models.DateField(null=True, blank=True)
    date_declaration = models.DateField(null=True, blank=True)
    date_reouverture = models.DateField(null=True, blank=True)
    date_reglement = models.DateField(null=True, blank=True)

    montant_provision = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)
    montant_provision_regle = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)
    montant_recours = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)
    montant_recours_regle = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)
    montant_sinistre = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)

    point_de_choc = models.CharField(max_length=255, null=True, blank=True)
    fait_generateur = models.CharField(max_length=255, null=True, blank=True)
    commentaires = models.TextField(null=True, blank=True)
    lieu_survenance = models.CharField(max_length=255, null=True, blank=True)

    tva_recuperee = models.BooleanField(null=True, blank=True)

    police = models.ForeignKey(Police, null=True, blank=True, on_delete=models.RESTRICT, related_name='historiques_sinistres')
    historique_police = models.ForeignKey(HistoriquePolice, null=True, blank=True, on_delete=models.RESTRICT, related_name='historiques_sinistres')
    sinistre = models.ForeignKey(Sinistre, null=True, blank=True, on_delete=models.RESTRICT, related_name='historiques')
    historique_aliment = models.ForeignKey(HistoriqueAliment, null=True, blank=True, on_delete=models.RESTRICT, related_name='historiques_sinistres')
    taux_responsabilite = models.ForeignKey(Responsabilite,null=True,  on_delete=models.RESTRICT, related_name='historiques_sinistres')
    type_sinistre = models.ForeignKey(TypeSinistre,null=True,  on_delete=models.RESTRICT, related_name='historiques_sinistres')
    circonstance = models.ForeignKey(Circonstance, null=True, blank=True, on_delete=models.RESTRICT, related_name='historiques_sinistres')
    mouvement = models.ForeignKey(Mouvement, null=True, blank=True, on_delete=models.RESTRICT, related_name='historiques_sinistres')
    motif_mouvement = models.ForeignKey(Motif, null=True, blank=True, on_delete=models.RESTRICT, related_name='historiques_sinistres')
    operateur_de_saisie = models.ForeignKey(User, null=True, blank=True, on_delete=models.RESTRICT, related_name='historiques_sinistres')
    compagnie = models.ForeignKey(Compagnie, null=True, blank=True, on_delete=models.RESTRICT, related_name='historiques_sinistres')

    class Meta:
        db_table = 'historique_sinistres'
        verbose_name = 'Historique de sinistre'
        verbose_name_plural = 'Historiques de sinistre'

    def __str__(self):
        return f"Historique {self.sinistre.numero if self.sinistre else 'N/A'} - {self.date_operation}"


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
        db_table = 'intervenants'
        verbose_name = 'Intervenants'
        verbose_name_plural = 'Intervenants'


class SinistreIntervenant(models.Model):
    sinistre = models.ForeignKey(Sinistre, null=True, blank=True, on_delete=models.RESTRICT, related_name='sinistre_intervenants')
    historique_sinistre = models.ForeignKey(HistoriqueSinistre, null=True, blank=True, on_delete=models.RESTRICT, related_name='historique_sinistre_intervenants')
    intervenant = models.ForeignKey(Intervenant, null=True, blank=True, on_delete=models.RESTRICT, related_name='intervenant_sinistres')

    class Meta:
        db_table = 'sinistre_intervenants'
        verbose_name = 'Intervenants liée au sinistre'
        verbose_name_plural = 'Intervenants liées au sinistre'


class SinistreGarantie(models.Model):
    franchise = models.BigIntegerField(null=True)
    capital = models.BigIntegerField(null=True)
    prime_nette = models.BigIntegerField(null=True)
    prime_ttc = models.BigIntegerField(null=True)

    montant_provision = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)
    montant_provision_regle = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)
    montant_recours = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)
    montant_recours_regle = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)
    montant_garantie = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)

    date_cloture = models.DateField(null=True, blank=True)

    sinistre = models.ForeignKey(Sinistre, on_delete=models.CASCADE, related_name='sinistre_garanties')
    garantie = models.ForeignKey(Garantie, on_delete=models.RESTRICT, related_name='garantie_sinistres')
    #historique_sinistre_garantie = models.ForeignKey('HistoriqueSinistreGarantie', null=True, blank=True, on_delete=models.RESTRICT, related_name='sinistres_garanties')

    class Meta:
        db_table = 'sinistre_garanties'
        verbose_name = 'Garantie liée à un sinistre'
        verbose_name_plural = 'Garanties liées à un sinistre'

    def __str__(self):
        return f"{self.garantie} (Sinistre: {self.sinistre_id})"


class VentilationRecour(models.Model):
    montant_recours = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)
    montant_regle = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)

    sinistre = models.ForeignKey(Sinistre, null=True, blank=True, on_delete=models.RESTRICT, related_name='ventilation_recours')
    garantie = models.ForeignKey(Garantie, null=True, blank=True, on_delete=models.RESTRICT, related_name='ventilation_recours')
    poste_dommage = models.ForeignKey(PosteDommage, null=True, blank=True, on_delete=models.RESTRICT, related_name='ventilation_recours')

    class Meta:
        db_table = 'ventilation_recours'
        verbose_name = 'Ventilation de recours'
        verbose_name_plural = 'Ventilations de recours'

    def __str__(self):
        return f"Recours {self.montant_recours} / {self.sinistre_id}"


class VentilationProvision(models.Model):
    montant_provision = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)
    montant_regle = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0"), null=True, blank=True)

    sinistre = models.ForeignKey(Sinistre, null=True, blank=True, on_delete=models.RESTRICT, related_name='ventilation_provision')
    garantie = models.ForeignKey(Garantie, null=True, blank=True, on_delete=models.RESTRICT, related_name='ventilation_provision')
    poste_dommage = models.ForeignKey(PosteDommage, null=True, blank=True, on_delete=models.RESTRICT, related_name='ventilation_provision')

    class Meta:
        db_table = 'ventilation_provision'
        verbose_name = 'Ventilation de provision'
        verbose_name_plural = 'Ventilations de provision'

    def __str__(self):
        return f"Provision {self.montant_provision} / {self.sinistre_id}"


class ReglementSinistre(models.Model):
    sinistre = models.ForeignKey(Sinistre, null=True, on_delete=models.RESTRICT)
    ventilation_provision = models.ForeignKey(VentilationRecour, null=True, on_delete=models.RESTRICT)
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


#historique des sinistres sur un bordereau d'ordonnancment au cas ou on doit annuler un bordereau d'ordonnancement on concerve l'historique
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'sinistres_temporaires'
        verbose_name = 'Sinistre temporaire'
        verbose_name_plural = 'Sinistres temporaires'


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