from django.db import models

from configurations.models import Profession, Pays, Civilite, QualiteBeneficiaire, Bureau, User
from production.models import Police, FormuleGarantie, Aliment, Mouvement
from shared.enum import Genre, StatutFamilial, Statut, StatutEnrolement, StatutValidite


# Create your models here.

class Campagne(models.Model):
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    police = models.ForeignKey(Police, null=True, on_delete=models.RESTRICT)
    formulegarantie = models.ForeignKey(FormuleGarantie, null=True, on_delete=models.RESTRICT)
    libelle = models.CharField(max_length=255, blank=False, null=True)
    code = models.CharField(max_length=25, unique=True, blank=False, null=True) # UPDATED
    lien = models.CharField(max_length=255, blank=False, null=True)
    date_debut = models.DateTimeField() # UPDATE
    date_fin = models.DateTimeField() # UPDATED
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    statut = models.fields.CharField(choices=StatutValidite.choices, default=StatutValidite.VALIDE, max_length=15, null=True)

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'campagne'
        verbose_name = 'Campagne'
        verbose_name_plural = 'campagnes'


 #  def save(self, *args, **kwargs):
 #      if not self.code:
 #          self.code = f'COM-{self.pk}'
 #          while Campagne.objects.filter(code=self.code).exists():
 #              self.code = f'COM-{self.pk + 1}'
 #      super().save(*args, **kwargs)


class Prospect(models.Model):
    bureau = models.ForeignKey(Bureau, null=True, on_delete=models.RESTRICT)
    police = models.ForeignKey(Police, null=True, on_delete=models.RESTRICT)
    formulegarantie = models.ForeignKey(FormuleGarantie, null=True, on_delete=models.RESTRICT)
    adherent_principal = models.ForeignKey('self', null=True, on_delete=models.RESTRICT)
    qualite_beneficiaire = models.ForeignKey(QualiteBeneficiaire, null=True, on_delete=models.RESTRICT)
    civilite = models.ForeignKey(Civilite, null=True, on_delete=models.RESTRICT)
    pays_naissance = models.ForeignKey(Pays, related_name='pays_naissance_prospect', null=True, on_delete=models.RESTRICT)
    pays_residence = models.ForeignKey(Pays, related_name='pays_residence_prospect', null=True, on_delete=models.RESTRICT)
    pays_activite_professionnelle = models.ForeignKey(Pays, related_name='pays_activite_professionnelle_prospect', null=True, on_delete=models.RESTRICT)
    profession = models.ForeignKey(Profession, null=True, on_delete=models.RESTRICT)
    nom = models.CharField(max_length=50, blank=False, null=True)
    prenoms = models.CharField(max_length=50, blank=False, null=True)
    nom_jeune_fille = models.CharField(max_length=100, blank=False, null=True)
    date_naissance = models.DateField(blank=False, null=True)
    lieu_naissance = models.CharField(max_length=100, blank=False, null=True)
    genre = models.fields.CharField(choices=Genre.choices, max_length=10, null=False)
    email = models.CharField(max_length=50, blank=True, null=True)

    numero_securite_sociale = models.CharField(max_length=50, blank=True, null=True)
    numero = models.CharField(max_length=50, blank=True, null=True)
    numero_famille = models.CharField(max_length=50, blank=True, null=True)
    numero_ordre = models.CharField(max_length=50, blank=True, null=True)
    matricule_employe = models.CharField(max_length=50, blank=True, null=True)
    date_affiliation = models.DateField(blank=True, null=True)
    date_sortie = models.DateField(blank=True, null=True)
    
    photo = models.ImageField(upload_to='prospects/', max_length=255, blank=True, null=True) # UPDATED
    
    statut_familiale = models.fields.CharField(choices=StatutFamilial.choices, default=StatutFamilial.CHOISIR, max_length=15, null=True)
    numero_piece = models.CharField(max_length=50, blank=True, null=True)

    code_postal = models.CharField(max_length=20, blank=True, null=True)
    ville = models.CharField(max_length=50, blank=True, null=True)
    adresse = models.CharField(max_length=100, blank=True, null=True)
    telephone_fixe = models.CharField(max_length=50, blank=True, null=True)
    telephone_mobile = models.CharField(max_length=50, blank=True, null=True)

    rib = models.CharField(max_length=50, blank=True, null=True)
    apci_ald = models.CharField(max_length=50, blank=True, null=True)
    statut = models.fields.CharField(choices=Statut.choices, default=Statut.ACTIF, max_length=15, null=True)
    statut_enrolement = models.fields.CharField(choices=StatutEnrolement.choices, default=StatutEnrolement.ATTENTE,
                                                max_length=15, null=True)
    aliment = models.ForeignKey(Aliment, null=True, on_delete=models.RESTRICT)
    aliment_adherent_principal = models.ForeignKey(Aliment, related_name="aliment_adherent_principal", null=True, on_delete=models.RESTRICT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.nom is None and self.prenoms is None:
            return self.email
        return f'{self.nom} {self.prenoms}'

    class Meta:
        db_table = 'prospects'
        verbose_name = 'Prospect'
        verbose_name_plural = 'prospects'


class CampagneProspect(models.Model):
    campagne = models.ForeignKey(Campagne, null=True, on_delete=models.RESTRICT)
    prospect = models.ForeignKey(Prospect, null=True, on_delete=models.RESTRICT)
    lien = models.CharField(max_length=255, blank=False, null=True)
    uiid = models.CharField(max_length=64, blank=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(auto_now_add=True)
    statut_enrolement = models.fields.CharField(choices=StatutEnrolement.choices, default=StatutEnrolement.ATTENTE, max_length=15, null=True)


class CampagneAppmobile(models.Model):
    created_by = models.ForeignKey(User, null=True, on_delete=models.RESTRICT)
    police = models.ForeignKey(Police, null=True, on_delete=models.RESTRICT)
    formulegarantie = models.ForeignKey(FormuleGarantie, null=True, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    statut = models.fields.CharField(choices=StatutValidite.choices, max_length=15, null=True)

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'campagne_appmobile'
        verbose_name = 'Campagne_appmobile'
        verbose_name_plural = 'campagne_appmobile'


class CampagneAppmobileProspect(models.Model):
    campagne_appmobile = models.ForeignKey(CampagneAppmobile, on_delete=models.RESTRICT)
    prospect = models.ForeignKey(Prospect, null=True, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    statut_enrolement = models.fields.CharField(choices=StatutEnrolement.choices, default=StatutEnrolement.ATTENTE, max_length=15, null=True)
    mouvement = models.ForeignKey(Mouvement, on_delete=models.RESTRICT)
