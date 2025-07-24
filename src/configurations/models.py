import datetime
from pprint import pprint

from django.contrib.auth.models import AbstractUser, Group
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum, Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django_currentuser.middleware import (get_current_user, get_current_authenticated_user)
from django.core.exceptions import ValidationError

from shared.enum import StatutReversementCompagnie, StatutEncaissementCommission, BaseCalculTM, Statut, PasswordType, \
    StatutValidite, TypeAlerte, TypeBonConsultation, TypeEtape, StatutReversementApporteur, StatutQuittance


class FloatRangeField(models.FloatField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        validators = kwargs.pop('validators', [])
        if min_value is not None:
            validators.append(MinValueValidator(min_value))
        super().__init__(verbose_name, name, validators=validators, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class TypeApporteur(models.Model):
    code = models.CharField(max_length=10, blank=True, null=True)
    libelle = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'type_apporteur'
        verbose_name = "Type d'apporteurs"
        verbose_name_plural = "Types d'apporteurs"


class PeriodeComptable(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True)
    mois = models.IntegerField(null=True)
    annee = models.IntegerField(null=True)
    date_debut = models.DateField(blank=False, null=True)
    date_fin = models.DateField(blank=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'periode_comptable'
        verbose_name = 'Période comptable'
        verbose_name_plural = 'Périodes comptables'


class TypeRemboursement(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'type_remboursement'
        verbose_name = 'Type de remboursement'
        verbose_name_plural = 'Types de remboursement'


class TypeTarif(models.Model):
    libelle = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'type_tarifs'
        verbose_name = 'Type de tarif'
        verbose_name_plural = "Types de tarifs"


class Secteur(models.Model):
    libelle = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'secteur'
        verbose_name = 'Secteur'
        verbose_name_plural = "Secteurs"


class Taxe(models.Model):
    libelle = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'taxes'
        verbose_name = 'Taxe'
        verbose_name_plural = "taxes"


class Devise(models.Model):
    libelle = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.libelle} - {self.code} "

    class Meta:
        db_table = 'devises'
        verbose_name = 'Devise'
        verbose_name_plural = "devises"


class Pays(models.Model):
    nom = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=5, blank=True, null=True)
    indicatif = models.CharField(max_length=5, blank=True, null=True)
    poligamie = models.BooleanField(default=False)
    devise = models.ForeignKey(Devise, null=True, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

    class Meta:
        db_table = 'pays'
        verbose_name = 'Pays'
        verbose_name_plural = 'Pays'


def upload_location_bureau(instance, filename):
    filebase, extension = filename.rsplit('.', 1)
    file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return 'bureaux/tarifs/%s.%s' % (file_name, extension)


def upload_logo_bureau(instance, filename):
    filebase, extension = filename.rsplit('.', 1)
    file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return 'bureaux/logos/%s.%s' % (file_name, extension)


class Bureau(models.Model):
    CA_TYPE = (
        ('EMISSION', 'EMISSION'),
        ('REVERSEMENT', 'REVERSEMENT'),
    )
    pays = models.ForeignKey(Pays, null=True, on_delete=models.RESTRICT)
    nom = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    code_courtier = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=255, blank=True, default=None, null=True)
    fax = models.CharField(max_length=255, blank=True, default=None, null=True)
    email = models.EmailField(max_length=255, blank=True, default=None, null=True)
    addresse = models.CharField(max_length=255, blank=True, default=None, null=True)
    ville = models.CharField(max_length=255, blank=True, default=None, null=True)
    situation_geographique = models.CharField(max_length=255, blank=True, default=None, null=True)
    whatsapp = models.CharField(max_length=50, blank=True, default=None, null=True)
    mention_legale = models.TextField(blank=True, null=True)
    tarfile = models.FileField(upload_to=upload_location_bureau, blank=True, default=None, null=True)
    logo = models.FileField(upload_to=upload_logo_bureau, blank=True, default=None, null=True)
    cachet = models.ImageField(upload_to='bureaux/cachets', blank=True, default='', null=True)
    taxes = models.ManyToManyField(Taxe, through='BureauTaxe')
    option_export_beneficiaires = models.BooleanField(default=True)
    option_assurance_universelle = models.BooleanField(default=False)
    ca_type = models.CharField('CA', choices=CA_TYPE, max_length=50, blank=True, null=True, default='REVERSEMENT')
    type_bon_consultation = models.fields.CharField(choices=TypeBonConsultation.choices, default=TypeBonConsultation.AUTO_CARBONE, max_length=15, null=True)
    fuseau_horaire=models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

    @property
    def tarif_bureau(self):
        if self.tarfile and hasattr(self.tarfile, 'url'):
            return mark_safe('<a href="{0}" download>{1}</a>'.format(self.tarfile.url, 'Télécharger'))
        else:
            return ""


    class Meta:
        db_table = 'bureau'
        verbose_name = 'Bureau'
        verbose_name_plural = 'Bureaux'


class BureauTaxe(models.Model):
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    taxe = models.ForeignKey(Taxe, null=True, on_delete=models.RESTRICT)
    taux = models.FloatField(blank=True, null=True)
    montant = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bureau_taxes'
        verbose_name = 'Taxe appliquée'
        verbose_name_plural = 'Taxes appliquées'


# une sorte de taxe qui vient prelever comme l'AIB au Benin au lieu d'ajouter comme la TVA
class Retenue(models.Model):
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    secteur = models.ForeignKey(Secteur, on_delete=models.RESTRICT, blank=True, null=True)
    libelle = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=10, blank=True, null=True)
    taux = models.FloatField(blank=True, null=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'retenues'
        verbose_name = 'Retenue'
        verbose_name_plural = 'Retenues'


class TypeGarant(models.Model):
    libelle = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'type_garants'
        verbose_name = 'Type de garant'
        verbose_name_plural = "Types de garant"


class TypeCompagnie(models.Model):
    libelle = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'type_compagnies'
        verbose_name = 'Type de compagnie'
        verbose_name_plural = "Types de compagnie"


class Compagnie(models.Model):
    type_garant = models.ForeignKey(TypeGarant, on_delete=models.RESTRICT, null=True)
    nom = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)
    code_courtier = models.CharField(max_length=25, blank=True, null=True)
    telephone = models.CharField(max_length=255, blank=True, default=None, null=True)
    fax = models.CharField(max_length=255, blank=True, default=None, null=True)
    email = models.EmailField(max_length=255, blank=True, default=None, null=True)
    adresse = models.CharField(max_length=255, blank=True, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    status = models.BooleanField(default=True)

    @classmethod
    def par_bureau(cls, bureau):
        return cls.objects.filter(bureau=bureau)

    def __str__(self):
        return self.nom

    @property
    def has_taux_com(self):
        params = ParamProduitCompagnie.objects.filter(compagnie_id=self.pk)

        return True if params else False


    @property
    def nombre_reglements(self):
        return self.reglements.filter(statut_validite=StatutValidite.VALIDE).count()


    @property
    def nombre_reglements_a_reverser_cie(self):
        #reglements = self.reglement.objects.filter(quittance__compagnie=self, statut_reversement_compagnie=StatutReversementCompagnie.NON_REVERSE)

        return self.reglements.filter(statut_reversement_compagnie=StatutReversementCompagnie.NON_REVERSE).exclude(quittance__type_quittance_id=2).count()


    @property
    def nombre_reglements_a_recevoir_com(self):
        return self.reglements.filter(statut_reversement_compagnie=StatutReversementCompagnie.REVERSE,
                                      statut_commission=StatutEncaissementCommission.NON_ENCAISSEE).count()

    @property
    def nombre_reglements_a_recevoir_com_court(self):
        reglements = self.reglements.filter(statut_reversement_compagnie=StatutReversementCompagnie.REVERSE,
                                      statut_commission=StatutEncaissementCommission.NON_ENCAISSEE, statut_validite=StatutValidite.VALIDE)

        for reglement in reglements:
            if reglement.montant_com_courtage_solde() != 0 and reglement.montant_com_courtage_solde() != (reglement.montant_journal_debit_courtage() - reglement.montant_journal_credit_courtage()):
                pass
            else:
                reglements = reglements.exclude(id=reglement.id)

        return reglements.count()

    @property
    def nombre_reglements_a_recevoir_com_gest(self):
        reglements = self.reglements.filter(statut_reversement_compagnie=StatutReversementCompagnie.REVERSE,
                                      statut_commission=StatutEncaissementCommission.NON_ENCAISSEE, statut_validite=StatutValidite.VALIDE)

        for reglement in reglements:
            if reglement.montant_com_gestion_solde() != 0 and reglement.montant_com_gestion_solde() != (reglement.montant_journal_debit_gestion() - reglement.montant_journal_credit_gestion()):
                pass
            else:
                reglements = reglements.exclude(id=reglement.id)

        return reglements.count()

    @property
    def sum_reglements(self):
        return self.reglements.aggregate(montant_total=Sum('montant'))['montant_total'] or 0


    @property
    def sum_reglements_a_reverser_cie(self):
        return self.reglements.filter(statut_reversement_compagnie=StatutReversementCompagnie.NON_REVERSE).aggregate(montant_total=Sum('montant'))['montant_total'] or 0


    @property
    def sum_commissions(self):
        total_montant_com_courtage = self.reglements.aggregate(montant_total=Sum('montant_com_courtage'))[
                                         'montant_total'] or 0
        total_montant_com_gestion = self.reglements.aggregate(montant_total=Sum('montant_com_gestion'))[
                                        'montant_total'] or 0

        return total_montant_com_courtage + total_montant_com_gestion

    @property
    def total_montant_com_courtage(self):
        total_montant_com_courtage = self.reglements.filter(statut_reversement_compagnie=StatutReversementCompagnie.REVERSE,
                                      statut_commission=StatutEncaissementCommission.NON_ENCAISSEE).aggregate(montant_total=Sum('montant_com_courtage'))[
                                         'montant_total'] or 0

        return total_montant_com_courtage

    @property
    def total_montant_com_gestion(self):
        total_montant_com_gestion = self.reglements.filter(statut_reversement_compagnie=StatutReversementCompagnie.REVERSE,
                                      statut_commission=StatutEncaissementCommission.NON_ENCAISSEE).aggregate(montant_total=Sum('montant_com_gestion'))[
                                        'montant_total'] or 0

        return total_montant_com_gestion

    @property
    def solde_montant_com_courtage(self):
        solde = 0
        for reglement in self.reglements.filter(statut_reversement_compagnie=StatutReversementCompagnie.REVERSE, statut_validite=StatutValidite.VALIDE):
            solde += reglement.montant_com_courtage_solde()
        return solde


    @property
    def solde_montant_com_gestion(self):
        solde = 0
        for reglement in self.reglements.filter(statut_reversement_compagnie=StatutReversementCompagnie.REVERSE, statut_validite=StatutValidite.VALIDE):
            solde += reglement.montant_com_gestion_solde()
        return solde


    @property
    def sum_commissions_a_reverser_cie(self):
        total_montant_com_courtage = \
            self.reglements.filter(statut_reversement_compagnie=StatutReversementCompagnie.NON_REVERSE).aggregate(
                montant_total=Sum('montant_com_courtage'))['montant_total'] or 0
        total_montant_com_gestion = \
            self.reglements.filter(statut_reversement_compagnie=StatutReversementCompagnie.NON_REVERSE).aggregate(
                montant_total=Sum('montant_com_gestion'))['montant_total'] or 0

        return total_montant_com_courtage + total_montant_com_gestion

    class Meta:
        db_table = 'compagnies'
        verbose_name = 'Compagnie'
        verbose_name_plural = 'Assureurs'

class Prestataire(models.Model):
    id_per = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)
    veos_code_soc = models.CharField(max_length=255, blank=True, default=None, null=True)
    veos_type_pres = models.CharField(max_length=255, blank=True, default=None, null=True)
    telephone = models.CharField(max_length=255, blank=True, default=None, null=True)
    fax = models.CharField(max_length=255, blank=True, default=None, null=True)
    email = models.EmailField(max_length=255, blank=True, default=None, null=True)
    addresse = models.CharField(max_length=255, blank=True, default=None, null=True)
    ville = models.CharField(max_length=255, blank=True, default=None, null=True)
    logo = models.FileField(upload_to='prestataires/logos', blank=True, default=None, null=True)
    fichier_tarification = models.FileField(upload_to='prestataires/tarifs', blank=True, default=None, null=True)
    liste_prescripteurs = models.FileField(upload_to='prescripteurs/liste', blank=True, default=None, null=True)
    secteur = models.ForeignKey(Secteur, on_delete=models.RESTRICT, null=True)
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    rb_ordre = models.CharField(max_length=255, blank=True, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    has_tarif_prestataire = models.BooleanField(default=False)

    latitude = models.DecimalField(max_digits=40, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=40, decimal_places=10, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def fichier_tarifs(self):
        return mark_safe('<a href="{0}" download>{1}</a>'.format(self.fichier_tarification.url,
                                                                 'Télécharger')) if self.fichier_tarification else ""

    # tarif_download.short_description = 'Tarif'

    class Meta:
        db_table = 'prestataires'
        verbose_name = 'Prestataire'
        verbose_name_plural = 'Prestataires'


class Prescripteur(models.Model):
    bureau = models.ForeignKey(Bureau, on_delete=models.RESTRICT, null=True)
    veos_code_specialite = models.CharField(max_length=50, blank=True, null=True)
    veos_id_per = models.CharField(max_length=50, blank=True, null=True)
    nom = models.CharField(max_length=50, blank=True, null=True)
    prenoms = models.CharField(max_length=50, blank=True, null=True)
    numero_ordre = models.CharField(max_length=50, blank=True, null=True)
    telephone = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.nom + ' ' + self.prenoms

    class Meta:
        db_table = 'prescripteur'
        verbose_name = 'Prescripteur'
        verbose_name_plural = 'Prescripteurs'


class TypePriseencharge(models.Model):
    libelle = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    statut_selectable = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'type_priseencharge'
        verbose_name = 'Types de prise en charge'
        verbose_name_plural = 'Types de prise en charge'


class Rubrique(models.Model):
    type_priseencharge = models.ForeignKey(TypePriseencharge, null=True, on_delete=models.RESTRICT, )
    libelle = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True, default=None, null=True)
    base_calcul_tm = models.CharField(choices=BaseCalculTM.choices, max_length=20, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'rubriques'
        verbose_name = 'Rubrique'
        verbose_name_plural = 'Rubriques'


class SousRubrique(models.Model):
    rubrique = models.ForeignKey(Rubrique, null=True, on_delete=models.RESTRICT, )
    libelle = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.code:
            # Generate the code based on the inserted ID
            rubrique_name = self.rubrique.libelle if self.rubrique else ''
            self.code = f"SR{slugify(rubrique_name)[:3]}{str(self.pk).zfill(4)}".upper()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'sous_rubriques'
        verbose_name = 'Sous-rubrique'
        verbose_name_plural = 'Sous-rubriques'


class RegroupementActe(models.Model):
    rubrique = models.ForeignKey(Rubrique, null=True, on_delete=models.RESTRICT)
    libelle = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.code:
            # Generate the code based on the inserted ID
            self.code = f"RA{slugify(self.libelle)[:4]}{str(self.pk).zfill(4)}".upper()

        super().save(*args, **kwargs)


    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'regroupement_acte'
        verbose_name = "Regroupement d'acte"
        verbose_name_plural = "Regroupements d'actes"


class SousRegroupementActe(models.Model):
    rubrique = models.ForeignKey(Rubrique, null=True, on_delete=models.RESTRICT)
    libelle = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.code:
            # Generate the code based on the inserted ID
            self.code = f"SRA{slugify(self.libelle)[:4]}{str(self.pk).zfill(4)}".upper()

        super().save(*args, **kwargs)


    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'sous_regroupement_acte'
        verbose_name = "Sous-regroup. d'acte"
        verbose_name_plural = "Sous-regroup. d'actes"


class SousRubriqueRegroupementActe(models.Model):
    sous_rubrique = models.ForeignKey(SousRubrique, null=True, on_delete=models.RESTRICT)
    regroupement_acte = models.ForeignKey(RegroupementActe, null=True, on_delete=models.RESTRICT)
    statut = models.BooleanField(default=True)

    class Meta:
        db_table = 'sous_rubrique_regroupement_acte'
        verbose_name = "Contenu de la sous-rubrique"
        verbose_name_plural = "Contenus de la sous-rubrique"


class Acte(models.Model):
    rubrique = models.ForeignKey(Rubrique, null=True, on_delete=models.RESTRICT)
    regroupement_acte = models.ForeignKey(RegroupementActe, null=True, on_delete=models.RESTRICT)
    libelle = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True, blank=True, default=None, null=True)
    lettre_cle = models.CharField(max_length=5, blank=True, null=True)
    delais_carence = models.IntegerField(blank=True, null=True) #pas utilisé
    delais_controle = models.IntegerField(blank=True, null=True)
    base_calcul_tm = models.CharField(choices=BaseCalculTM.choices, default=BaseCalculTM.FRAIS_REEL, max_length=20, null=True)
    option_seance = models.BooleanField(default=False)
    option_quantite = models.BooleanField(default=False)
    accord_automatique = models.BooleanField(default=False)
    specialiste_uniquement = models.BooleanField(default=False)
    est_gratuit = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    statut_validite = models.fields.CharField(choices=StatutValidite.choices, default=StatutValidite.VALIDE, max_length=15, null=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'actes'
        verbose_name = 'Acte'
        verbose_name_plural = 'Actes'


    @property
    def entente_prealable(self):
        current_user = get_current_authenticated_user()
        param_acte = ParamActe.objects.filter(acte=self, bureau=current_user.bureau).first()
        return param_acte.entente_prealable if param_acte else False


class SousRegroupementActeActe(models.Model):
    sous_regroupement_acte = models.ForeignKey(SousRegroupementActe, null=True, on_delete=models.RESTRICT)
    acte = models.ForeignKey(Acte, null=True, on_delete=models.RESTRICT)
    statut = models.BooleanField(default=True)

    class Meta:
        db_table = 'sous_regroupement_acte_acte'
        verbose_name = "Contenu du sous-regroupement d'actes"
        verbose_name_plural = "Contenus du sous-regroupement d'actes"


class Medicament(models.Model):
    rubrique = models.ForeignKey(Rubrique, null=True, on_delete=models.RESTRICT)
    libelle = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True, default=None, null=True)
    accord_automatique = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'medicaments'
        verbose_name = 'Medicament'
        verbose_name_plural = 'Medicaments'


class Civilite(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=5, blank=True, null=True, )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'civilites'
        verbose_name = 'Civilite'
        verbose_name_plural = 'Civilites'


class TypeAssure(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'type_assures'
        verbose_name = 'TypeAssure'
        verbose_name_plural = 'TypeAssures'


class TypePersonne(models.Model):
    libelle = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=1, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'type_personnes'
        verbose_name = 'Type de personne'
        verbose_name_plural = 'Types de personne'


class TypeClient(models.Model):
    code = models.CharField(max_length=50, blank=True, null=True)
    libelle = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'type_clients'
        verbose_name = 'Type de client'
        verbose_name_plural = 'Types de client'


class TypeProduit(models.Model):
    nom = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom} - {self.created_at}"

    class Meta:
        db_table = 'type_produit'
        verbose_name = 'Type Produit'
        verbose_name_plural = 'Type Produit'


class TauxCommission(models.Model):
    libelle = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    taux= FloatRangeField(blank=True, default=None, null=True, min_value=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = "taux_commission"
        verbose_name = "Taux de commission"
        verbose_name_plural = "Taux de commission"


class Branche(models.Model):
    code = models.CharField(max_length=10, blank=True, null=True)
    nom = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.status} - {self.nom} "

    class Meta:
        db_table = 'branche'
        verbose_name = 'Branche'
        verbose_name_plural = 'Branches'


class Produit(models.Model):
    branche = models.ForeignKey(Branche, null=True, on_delete=models.RESTRICT)
    type_produit = models.ForeignKey(TypeProduit, null=True, on_delete=models.RESTRICT)
    taux_commission = models.ForeignKey(TauxCommission, null=True, on_delete=models.RESTRICT)
    code = models.CharField(max_length=10, blank=True, null=True)
    nom = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.code} - {self.nom} - {self.branche} - {self.type_produit}'

    class Meta:
        db_table = 'produit'
        verbose_name = 'Produits'
        verbose_name_plural = 'Produits'


class ParamProduitCompagnie(models.Model):
    compagnie = models.ForeignKey(Compagnie, related_name="taux_com", on_delete=models.RESTRICT)
    produit = models.ForeignKey(Produit, null=True, on_delete=models.RESTRICT)
    taux_com_courtage = FloatRangeField(blank=True, default=None, null=True, min_value=0)
    taux_com_courtage_terme = FloatRangeField(blank=True, default=None, null=True, min_value=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.compagnie} - {self.produit} {self.taux_com_courtage} - {self.taux_com_courtage_terme}'

    class Meta:
        db_table = 'param_produit_compagnie'
        verbose_name = 'Paramétrage des taux de com'
        verbose_name_plural = 'Paramétrage des taux de com'
        

class Langue(models.Model):
    code = models.CharField(max_length=10, blank=True, null=True)
    libelle = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'langues'
        verbose_name = 'Langue'
        verbose_name_plural = 'Langues'


class Fractionnement(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True)
    duree_en_mois = models.IntegerField(null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'fractionnements'
        verbose_name = 'Fractionnement'
        verbose_name_plural = 'Fractionnements'


class ModeReglement(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'mode_reglements'
        verbose_name = 'Mode de règlement'
        verbose_name_plural = 'Modes de règlement'


class NatureOperation(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=10, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'nature_operations'
        verbose_name = "Nature de l'operation"
        verbose_name_plural = 'Natures des operations'


class Regularisation(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'regularisations'
        verbose_name = 'Régularisation'
        verbose_name_plural = 'Régularisations'


class TypePrefinancement(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=10, blank=True, null=True)
    statut = models.fields.CharField(choices=Statut.choices, default=Statut.ACTIF, max_length=15, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'type_prefinancement'
        verbose_name = 'Type de préfinancement'
        verbose_name_plural = 'Types de préfinancement'


class ModeCreation(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    statut = models.fields.CharField(choices=Statut.choices, default=Statut.ACTIF, max_length=15, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'mode_creation'
        verbose_name = 'Mode de création'
        verbose_name_plural = 'Modes de création'


class Duree(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True)
    nombre_mois = models.IntegerField(blank=True, null=True)
    nombre_jours = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'durees'
        verbose_name = 'Durée'
        verbose_name_plural = 'Durées'


class AuthGroup(Group):
    # Add your custom field(s) here
    code = models.CharField(max_length=50)
    libelle = models.CharField(max_length=255, null=True)
    status = models.BooleanField(default=True)


class TypeUtilisateur(models.Model):
    code = models.CharField(max_length=100, blank=True, null=True)
    libelle = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'type_utilisateurs'
        verbose_name = 'Type utilisateur'
        verbose_name_plural = 'Types utilisateurs'


class User(AbstractUser):
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    type_utilisateur = models.ForeignKey(TypeUtilisateur, null=True, on_delete=models.RESTRICT)
    password_type = models.fields.CharField(choices=PasswordType.choices, default=PasswordType.DEFAULT, null=True, max_length=20)
    is_admin_group = models.BooleanField(verbose_name='Statut admin groupe', default=False)

    @property
    def is_production(self):
        if self.groups.filter(name__contains='PRODUCTION').first() is not None:
            return True
        return False


    @property
    def is_comptable(self):
        if self.groups.filter(name__contains='COMPTABLE').first() is not None:
            return True
        return False


    @property
    def is_manager(self):
        if self.groups.filter(name__contains='MANAGER').first() is not None:
            return True
        return False


    @property
    def is_commercial(self):
        if self.groups.filter(name__contains='COMMERCIAL').first() is not None:
            return True
        return False


    @property
    def is_sinistre(self):
        if self.groups.filter(name__contains='SINISTRE').first() is not None:
            return True
        return False


    @property
    def user_groups(self):
        #Return a list of group names the user belongs to.
        return (group.name for group in self.groups.all())


class ParamActe(models.Model):
    created_by = models.ForeignKey(User, related_name="pa_created_by", null=True, on_delete=models.RESTRICT)
    updated_by = models.ForeignKey(User, related_name="pa_updated_by", null=True, on_delete=models.RESTRICT)
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    acte = models.ForeignKey(Acte, null=True, on_delete=models.RESTRICT)
    delais_controle = models.IntegerField(blank=True, null=True)
    delais_carence = models.IntegerField(blank=True, null=True)
    accord_automatique = models.BooleanField(default=False)
    entente_prealable = models.BooleanField(default=False)
    specialiste_uniquement = models.BooleanField(default=False)
    est_gratuit = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True,)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = 'param_actes'
        verbose_name = "Paramétrage de l'acte"
        verbose_name_plural = "Paramétrages de l'acte"


class Apporteur(models.Model):
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    id_per = models.CharField(max_length=25, blank=True, null=True)
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    pays = models.ForeignKey(Pays, null=True, on_delete=models.RESTRICT)
    type_apporteur = models.ForeignKey(TypeApporteur, null=True, on_delete=models.RESTRICT)
    type_personne = models.ForeignKey(TypePersonne, null=True, on_delete=models.RESTRICT)
    nom = models.CharField(max_length=100, blank=True, default=None, null=True)
    prenoms = models.CharField(max_length=100, blank=True, default=None, null=True)
    code = models.CharField(max_length=25, blank=True, default=None, null=True, unique=True)
    telephone = models.CharField(max_length=25, blank=True, default=None, null=True)
    email = models.EmailField(max_length=50, blank=True, default=None, null=True)
    adresse = models.CharField(max_length=255, blank=True, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    @property
    def nombre_reglements_a_recevoir_retrocession(self):
        reglements = self.app_reglements.filter(
            statut_reversement_apporteur=StatutReversementApporteur.NON_REVERSE,
            statut_commission=StatutEncaissementCommission.ENCAISSEE,
            quittance__statut=StatutQuittance.PAYE,
        ).exclude(
            Q(montant_com_intermediaire=0) | Q(montant_com_intermediaire__isnull=True)
        )

        return reglements.count()

    @property
    def total_montant_retrocession_apporteur(self):
        total_montant_retrocession_apporteur = \
        self.app_reglements.filter(statut_reversement_apporteur=StatutReversementApporteur.NON_REVERSE,
                               statut_commission=StatutEncaissementCommission.ENCAISSEE).aggregate(
            montant_total=Sum('montant_com_intermediaire'))[
            'montant_total'] or 0

        return total_montant_retrocession_apporteur

    @property
    def solde_montant_retrocession_apporteur(self):
        solde = 0
        for reglement in self.app_reglements.filter(statut_reversement_apporteur=StatutReversementApporteur.NON_REVERSE,
                                                    statut_validite=StatutValidite.VALIDE):
            solde += reglement.montant_retrocession_apporteur_solde()

        return solde

    @property
    def sum_reglements(self):
        return self.app_reglements.aggregate(montant_total=Sum('montant_com_courtage'))['montant_total'] or 0

    @property
    def sum_reglements_a_reverser_apporteur(self):
        return self.app_reglements.filter(statut_reversement_apporteur=StatutReversementApporteur.NON_REVERSE).aggregate(
            montant_total=Sum('montant_com_courtage'))['montant_total'] or 0

    class Meta:
        db_table = 'apporteurs'
        verbose_name = 'Apporteurs'
        verbose_name_plural = 'Intermediaires'


class BaseCalcul(models.Model):
    libelle = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'base_calculs'
        verbose_name = 'Base de calcul'
        verbose_name_plural = "Bases de calcul"


class Banque(models.Model):
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    libelle = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    nom_complet = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'banques'
        verbose_name = 'Banque'
        verbose_name_plural = "Banques"


class CompteTresorerie(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'compte_tresorerie'
        verbose_name = 'Compte de trésorerie'
        verbose_name_plural = "Comptes de trésorerie"


class NatureQuittance(models.Model):
    libelle = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    code_veos = models.CharField(max_length=50, blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'nature_quittances'
        verbose_name = 'Nature de quittance'
        verbose_name_plural = "Natures de quittances"


class TypeQuittance(models.Model):
    libelle = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    code_veos = models.CharField(max_length=50, blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'type_quittances'
        verbose_name = 'Type de quittance'
        verbose_name_plural = "Types de quittances"


class CategorieVehicule(models.Model):
    libelle = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'categorie_vehicule'
        verbose_name = 'Catégorie de véhicule'
        verbose_name_plural = "Catégories de véhicule"


class TypeCarosserie(models.Model):
    libelle = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'type_carosserie'
        verbose_name = 'Type de carosserie'
        verbose_name_plural = "Types de carosserie"


class Carosserie(models.Model):
    libelle = models.CharField(max_length=50, blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'carosserie'
        verbose_name = 'Carosseries'
        verbose_name_plural = "Carosseries"


class Carburant(models.Model):
    libelle = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'carburant'
        verbose_name = 'Carburants'
        verbose_name_plural = "Energies"


class Usage(models.Model):
    libelle = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'usage'
        verbose_name = 'Usages'
        verbose_name_plural = "Usages"


class Tarif(models.Model):
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    validated_by = models.ForeignKey(User, related_name="validated_by", null=True, on_delete=models.RESTRICT)
    deleted_by = models.ForeignKey(User, related_name="tarif_deleted_by", null=True, on_delete=models.RESTRICT)
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    prestataire = models.ForeignKey(Prestataire, null=True, on_delete=models.RESTRICT)
    #police = models.ForeignKey(Police, null=True, on_delete=models.RESTRICT)


    acte = models.ForeignKey(Acte, null=True, on_delete=models.RESTRICT)
    code_acte = models.CharField(max_length=50, blank=True, null=True)


    lettre_cle_public_hg = models.CharField(max_length=50, blank=True, null=True)
    coef_public_hg = models.IntegerField(null=True)
    pu_public_hg = models.IntegerField(null=True)
    cout_public_hg = models.IntegerField(null=True)

    lettre_cle_public_chu = models.CharField(max_length=50, blank=True, null=True)
    coef_public_chu = models.IntegerField(null=True)
    pu_public_chu = models.IntegerField(null=True)
    cout_public_chu = models.IntegerField(null=True)

    lettre_cle_public_ica = models.CharField(max_length=50, blank=True, null=True)
    coef_public_ica = models.IntegerField(null=True)
    pu_public_ica = models.IntegerField(null=True)
    cout_public_ica = models.IntegerField(null=True)

    lettre_cle_mutuelle = models.CharField(max_length=50, blank=True, null=True)
    coef_mutuelle = models.IntegerField(null=True)
    pu_mutuelle = models.IntegerField(null=True)
    cout_mutuelle = models.IntegerField(null=True)

    lettre_cle_classique = models.CharField(max_length=50, blank=True, null=True)
    coef_classique = models.IntegerField(null=True)
    pu_classique = models.IntegerField(null=True)
    cout_classique = models.IntegerField(null=True)

    lettre_cle_prestataire = models.CharField(max_length=50, blank=True, null=True)
    coef_prestataire = models.IntegerField(null=True)
    pu_prestataire = models.IntegerField(null=True)
    cout_prestataire = models.IntegerField(null=True)


    statut = models.fields.CharField(choices=Statut.choices, default=Statut.ACTIF, max_length=15, null=True)
    statut_validite = models.fields.CharField(choices=StatutValidite.choices, default=StatutValidite.VALIDE, max_length=15, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tarifs'
        verbose_name = 'Tarif'
        verbose_name_plural = 'Tarifs'


class TarifExcel(models.Model):
    CODE_REGROUPEMENT_OLEA = models.CharField(max_length=100, null=True)
    LIBELLE_ACTE = models.CharField(max_length=100, null=True)
    CODE_ACTE = models.CharField(max_length=100, null=True)
    REGROUPEMENT_ACTE = models.CharField(max_length=100, null=True)

    LETTRE_CLE_CLASSIQUE = models.CharField(max_length=100, null=True)
    COEF_CLASSIQUE = models.CharField(max_length=100, null=True)
    PU_CLASSIQUE = models.CharField(max_length=100, null=True)
    COUT_CLASSIQUE = models.CharField(max_length=100, null=True)

    LETTRE_CLE_MUTUELLE = models.CharField(max_length=100, null=True)
    COEF_MUTUELLE = models.CharField(max_length=100, null=True)
    PU_MUTUELLE = models.CharField(max_length=100, null=True)
    COUT_MUTUELLE = models.CharField(max_length=100, null=True)

    LETTRE_CLE_PUBLIC_HG = models.CharField(max_length=100, null=True)
    COEF_PUBLIC_HG = models.CharField(max_length=100, null=True)
    PU_PUBLIC_HG = models.CharField(max_length=100, null=True)
    COUT_PUBLIC_HG = models.CharField(max_length=100, null=True)

    LETTRE_CLE_PUBLIC_CHU = models.CharField(max_length=100, null=True)
    COEF_PUBLIC_CHU = models.CharField(max_length=100, null=True)
    PU_PUBLIC_CHU = models.CharField(max_length=100, null=True)
    COUT_PUBLIC_CHU = models.CharField(max_length=100, null=True)

    LETTRE_CLE_PUBLIC_ICA = models.CharField(max_length=100, null=True)
    COEF_PUBLIC_ICA = models.CharField(max_length=100, null=True)
    PU_PUBLIC_ICA = models.CharField(max_length=100, null=True)
    COUT_PUBLIC_ICA = models.CharField(max_length=100, null=True)



    class Meta:
        db_table = 'tarif_excels'


class ActionLog(models.Model):
    done_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    action = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    table = models.CharField(max_length=100, blank=True, null=True)
    row = models.IntegerField(blank=True, null=True)
    data_before = models.JSONField(blank=True, null=True)
    data_after = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.action} data into {self.table} on {self.created_at}"

    class Meta:
        db_table = 'actionlog'
        verbose_name = 'action log'
        verbose_name_plural = 'action logs'


class CronLog(models.Model):
    action = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    table = models.CharField(max_length=100, blank=True, null=True)
    row = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.action} data into {self.table} on {self.created_at}"

    class Meta:
        db_table = 'cronlog'
        verbose_name = 'cron error log'
        verbose_name_plural = 'cron error logs'


class KeyValueData(models.Model):
    key = models.CharField(max_length=100, blank=False, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    statut = models.BooleanField(default=True)
    data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(verbose_name='Date de creation', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Date mise à jour', auto_now=True)

    def __str__(self):
        return self.key

    class Meta:
        db_table = 'keyvaluedata'
        verbose_name = 'Configuration'
        verbose_name_plural = 'Configurations'


class WsBoby(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True, unique=True)
    request = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'ws_boby'
        verbose_name = 'WS Boby'
        verbose_name_plural = 'WS Boby'


class ParamWsBoby(models.Model):
    ws_boby = models.ForeignKey(WsBoby, null=True, on_delete=models.RESTRICT)
    name = models.CharField(max_length=100, blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'param_ws_boby'
        verbose_name = 'Param WS Boby'
        verbose_name_plural = 'Param WS Boby'


class BackgroundQueryTask(models.Model):
    STATUS = (
        ('ENATT', 'EN ATTENTE'),
        ('ENCOURS', 'EN COURS'),
        ('ECHOUEE', 'ECHOUEE'),
        ('ANNULLEE', 'ANNULLEE'),
        ('TERMINEE', 'TERMINEE'),
    )
    name = models.CharField(verbose_name='Libellé requête', max_length=255, blank=True, null=True)
    query = models.TextField(verbose_name='Requête', blank=True, null=True)
    file = models.FileField(verbose_name='Fichier excel', upload_to='background_query', blank=True, null=True)
    status = models.CharField(verbose_name='Statut', choices=STATUS, default='ENATT', max_length=15, null=True)
    error_message = models.TextField(verbose_name="Message d'erreur",blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(verbose_name='Date de creation', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Date de modification', auto_now=True)

    @property
    def fichier_excel(self):
        if self.file:
            download_url = reverse('download_background_query_result', args=[self.id])
            return mark_safe('<a href="##" data-url="{}" class="download_background_query_result"><span class="badge btn-sm btn-details rounded-pill"><i class="fa fa-download"></i> Télécharger</span></a>'.format(download_url))
        return ""

    @property
    def statut(self):
        badge = 'success' if self.status == 'TERMINEE' else 'danger' if self.status == 'ECHOUEE' else 'info' if self.status == 'ENCOURS' else 'warning' if self.status == 'ENATT' else 'secondary'
        return mark_safe(f'<span class="badge badge-{badge}">{self.get_status_display()}</span>')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'background_query_task'
        verbose_name = 'Requête en arrière-plan'
        verbose_name_plural = 'Requête en arrière-plan'


class AdminGroupeBureau(models.Model):
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    user = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.bureau}'

    class Meta:
        db_table = 'admin_groupe_permission'
        verbose_name = 'Admin Groupe Bureau'
        verbose_name_plural = 'Admin Groupes Bureaux'


class MailingList(models.Model):
    bureau = models.ForeignKey(Bureau, on_delete=models.RESTRICT, null=True)
    mail_de_diffusion = models.CharField(max_length=100, blank=False, null=True)
    nombre_alerte = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    type_alerte = models.fields.CharField(choices=TypeAlerte.choices,max_length=15, null=True)
    statut = models.BooleanField(default=False) # On envoie le mail ou non
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, blank=True, related_name="ml_created_by", on_delete=models.RESTRICT)
    updated_by = models.ForeignKey(User, null=True, blank=True, related_name="ml_updated_by", on_delete=models.RESTRICT)

    def __str__(self):
        return self.mail_de_diffusion

    @classmethod
    def par_bureau(cls, bureau):
        return cls.objects.filter(bureau=bureau)
    
    @classmethod # sera utile pour la tâche cron / alerte activé
    def actifs(cls, bureau):
        return cls.objects.filter(status=True)

    class Meta:
        db_table = 'mailing_lists'
        verbose_name = 'Liste de diffusion'
        verbose_name_plural = 'Liste de diffusion'


class ModelLettreCheque(models.Model):
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    banque = models.ForeignKey(Banque, null=True, on_delete=models.RESTRICT)
    libelle = models.CharField(max_length=100, blank=False, null=True)
    model = models.CharField('Modèle', max_length=100, blank=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, related_name="model_lettre_cheque_created_by", on_delete=models.RESTRICT)
    statut = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.libelle} | {self.banque}"

    class Meta:
        db_table = 'model_lettre_cheque'
        verbose_name = 'Modèle lettre cheque'
        verbose_name_plural = 'Modèles lettre cheque'


class BordereauLettreCheque(models.Model):
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    model_lettre_cheque = models.ForeignKey(ModelLettreCheque, null=True, on_delete=models.RESTRICT)
    libelle = models.CharField('libellé',max_length=100, blank=False, null=True)
    nombre = models.IntegerField(null=True, blank=True)
    fichier = models.FileField(upload_to='bordereau_lettre_cheque', blank=True, null=True)
    created_at = models.DateTimeField("date d’édition", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, related_name="bordereau_lettre_cheque_created_by", on_delete=models.RESTRICT)

    @property
    def fichier_pdf(self):
        if self.fichier:
            return mark_safe(
                '<a href="{}" target="_blank"><span class="badge btn-sm btn-details rounded-pill"><i class="fa fa-download"></i> Consulter</span></a>'.format(
                    self.fichier.url))
        return ""


    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'bordereau_lettre_cheque'
        verbose_name = 'Historique des lettres Chèques'
        verbose_name_plural = 'Historique des lettres Chèques'


class StatExcelWsBoby(models.Model):
    libelle_fr = models.CharField(max_length=255, blank=True, null=True, unique=True)
    libelle_en = models.CharField(max_length=255, blank=True, null=True, unique=True)
    libelle_pt = models.CharField(max_length=255, blank=True, null=True, unique=True)
    code_ws = models.CharField(max_length=100, blank=True, null=True, unique=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle_fr

    class Meta:
        db_table = 'stat_excel_ws_boby'
        verbose_name = 'Stat Excel Ws Boby'
        verbose_name_plural = 'Stats Excel Ws Boby' 


class BusinessUnit(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True, unique=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.libelle} - {self.status} - {self.created_at} - {self.updated_at}"

    class Meta:
        db_table = 'business_unit'
        verbose_name = 'Business Unit'
        verbose_name_plural = 'Business Unit'


class Formule(models.Model):
    code = models.CharField(max_length=10, blank=True, null=True)
    libelle = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.code} - {self.libelle} - {self.status} - {self.created_at}'

    class Meta:
        db_table = 'formules'
        verbose_name = 'Formules'
        verbose_name_plural = 'Formules'


class Garantie(models.Model):
    code = models.CharField(max_length=10, blank=True, null=True)
    nom = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.nom}"

    class Meta:
        db_table = 'garanties'
        verbose_name = 'Garantie'
        verbose_name_plural = 'Garanties'


class GarantieBranche(models.Model):
    branche = models.ForeignKey(Branche, null=True, on_delete=models.RESTRICT)
    garantie = models.ForeignKey(Garantie, null=True, on_delete=models.RESTRICT)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.created_at}'

    class Meta:
        db_table = 'garantie_branche'
        verbose_name = 'Garanties / Branche'
        verbose_name_plural = 'Garanties / Branche'


class GarantieFormule(models.Model):
    formule = models.ForeignKey(Formule, null=True, on_delete=models.RESTRICT)
    garantie = models.ForeignKey(Garantie, null=True, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.formule} - {self.created_at}'

    class Meta:
        db_table = 'garantie_formule'
        verbose_name = 'Garanties / Formules'
        verbose_name_plural = 'Garanties / Formules'


class ConditionsAssurance(models.Model):
    code = models.CharField(max_length=10, blank=True, null=True)
    libelle = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.code} - {self.libelle} - {self.status} - {self.created_at}'

    class Meta:
        db_table = 'conditions_assurance'
        verbose_name = "Conditions d'assurance"
        verbose_name_plural = "Conditions d'assurance"


class MoyensTransport(models.Model):
    code = models.CharField(max_length=10, blank=True, null=True)
    libelle = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.code} - {self.libelle} - {self.status} - {self.created_at}'

    class Meta:
        db_table = 'moyens_transport'
        verbose_name = 'Moyens de transport'
        verbose_name_plural = 'Moyens de transport'


class TypeCourrier(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(null=True, auto_now_add=False)
    updated_at = models.DateTimeField(null=True, auto_now=False)

    class Meta:
        db_table = 'type_courrier'
        verbose_name = 'Type de courrier'
        verbose_name_plural = 'Type de courrier'


class TypeFichier(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    statut = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'type_fichier'
        verbose_name = 'Type de fichier'
        verbose_name_plural = 'Type de fichier'


class Groupe(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    statut = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'groupes'
        verbose_name = 'Groupes'
        verbose_name_plural = 'Groupes'


class TypeSinistre(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    statut = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'type_sinistre'
        verbose_name = 'Type de sinistre'
        verbose_name_plural = 'Type de sinistre'


class TypeIntervenant(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    statut = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'type_intervenant'
        verbose_name = "Type d'intervenant"
        verbose_name_plural = "Type d'intervenant"


class TauxResponsabilite(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True)
    taux_responsabilite = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    statut = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.libelle} - {self.taux_responsabilite} - {self.statut} - {self.created_at}'

    class Meta:
        db_table = 'taux_responsabilites'
        verbose_name = "Taux de responsabilite"
        verbose_name_plural = "Taux de responsabilite"

    constraints = [
        models.UniqueConstraint(fields=['libelle', 'taux_responsabilite'], name='unique_responsabilite')
    ]


class TypeMouvement(models.Model):
    libelle = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    statut = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'type_mouvement'
        verbose_name = "Type de mouvement"
        verbose_name_plural = "Type de mouvement"


class Circonstance(models.Model):
    branche = models.ForeignKey(Branche, null=True, on_delete=models.RESTRICT, blank=True)
    code = models.CharField(max_length=100, blank=True, null=True)
    libelle = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    statut = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'circonstance'
        verbose_name = "Circonstances"
        verbose_name_plural = "Circonstances"


class PosteDommage(models.Model):
    code = models.CharField(max_length=100, blank=True, null=True)
    libelle = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    statut = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'poste_dommage'
        verbose_name = "Postes de dommages"
        verbose_name_plural = "Postes de dommages"


class GarantieCirconstance(models.Model):
    circonstance = models.ForeignKey(Circonstance, null=True, on_delete=models.RESTRICT)
    garantie = models.ForeignKey(Garantie, null=True, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.circonstance} - {self.created_at}'

    class Meta:
        db_table = 'garantie_circonstance'
        verbose_name = 'Garanties / Circonstances'
        verbose_name_plural = 'Garanties / Circonstances'

