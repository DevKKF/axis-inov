from django.db import models

from configurations.models import User, ModeReglement, Banque, TypeRemboursement, Prestataire, Compagnie, Bureau, \
    Devise, CompteTresorerie
# Create your models here.
from production.models import Reglement, StatutReversementCompagnie, Aliment, Operation
from shared.enum import StatutValidite, StatutQuittance, TypeEncaissementCommission
from sinistre.models import BordereauOrdonnancement

class ReglementReverseCompagnie(Reglement):
    class Meta:
        proxy = True
        verbose_name = "Reglement compagnie"
        verbose_name_plural = "Reglements compagnie"

        permissions = [
            ("can_do_reglement_compagnie", "Peut faire des règlements compagnies"),
        ]

    def get_queryset(self):
        return super(ReglementReverseCompagnie, self).get_queryset().filter(statut_reversement_compagnie=StatutReversementCompagnie.REVERSE)


class ReglementApporteurs(Reglement):
    class Meta:
        proxy = True
        verbose_name = "Reglement apporteurs"
        verbose_name_plural = "Reglements apporteurs"

    def get_queryset(self):
        return super(ReglementApporteurs, self).get_queryset().filter(statut_reversement_compagnie=StatutReversementCompagnie.REVERSE)


class BordereauOrdonnance(BordereauOrdonnancement):
    class Meta:
        proxy = True
        verbose_name = "Bord. ordonnancé"
        verbose_name_plural = "Bordx ordonnancés"

    def get_queryset(self):
        return super(BordereauOrdonnancement, self).get_queryset().filter(statut_reversement_compagnie=StatutReversementCompagnie.REVERSE)


class EncaissementCommission(models.Model):
    operation = models.ForeignKey(Operation, null=True, on_delete=models.RESTRICT)
    reglement = models.ForeignKey(Reglement, null=True, on_delete=models.RESTRICT, related_name="encaissement_commissions", related_query_name="encaissement_commission")
    montant_com_courtage = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True)
    montant_com_gestion = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True)
    type_commission = models.fields.CharField(choices=TypeEncaissementCommission.choices, default=None, max_length=15, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.numero

    class Meta:
        db_table = 'encaissement_commission'
        verbose_name = 'Encaissement de commission'
        verbose_name_plural = 'Encaissements de commissions'

    def montant_com_encaisse(self):
        if self.type_commission == TypeEncaissementCommission.COURTAGE:
            return self.montant_com_courtage
        elif self.type_commission == TypeEncaissementCommission.GESTION:
            return self.montant_com_gestion
        else:
            return (self.montant_com_courtage + self.montant_com_gestion)

    def montant(self):
        montant = 0
        for journal in self.journals.all():
            if journal.sens == "D":
                montant = montant + journal.montant
            if journal.sens == "C":
                montant = montant - journal.montant
        if self.type_commission == TypeEncaissementCommission.COURTAGE:
            montant = montant + self.montant_com_courtage
        elif self.type_commission == TypeEncaissementCommission.GESTION:
            montant = montant + self.montant_com_gestion
        else:
            montant = montant + self.montant_com_courtage + self.montant_com_gestion
        print(f"{self.reglement.numero} {montant}")
        return montant    
    

class CompteComptable(models.Model):
    code = models.CharField(max_length=255, blank=True, null=True)
    libelle = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'compte_comptable'
        verbose_name = 'Compte comptable'
        verbose_name_plural = 'Comptes comptables'


class Journal(models.Model):
    bureau = models.ForeignKey(Bureau, null=False, on_delete=models.RESTRICT)
    compte_comptable = models.ForeignKey(CompteComptable, null=False, on_delete=models.RESTRICT)
    sens = models.CharField(max_length=1, blank=True, null=True) #D, C
    montant = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    encaissement_commission = models.ForeignKey(EncaissementCommission, null=True, on_delete=models.RESTRICT, related_name="journals", related_query_name="journal")
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.designation

    class Meta:
        db_table = 'journal'
        verbose_name = 'Journal'
        verbose_name_plural = 'Journaux'

