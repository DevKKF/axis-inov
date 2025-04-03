from django.db import models
import datetime
from datetime import date
from pprint import pprint
from django.utils import timezone
from django.urls import reverse

from configurations.models import BusinessUnit, User, Compagnie
from production.models import Client

from shared.enum import TypePortefeuille


def upload_fichier_portefeuille(instance, filename):
    filebase, extension = filename.rsplit('.', 1)
    file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return 'portefeuilles/fichiers/%s.%s' % (file_name, extension)


class AnalysePortefeuille(models.Model):
    compagnie = models.ForeignKey(Compagnie, blank=False, null=True, on_delete=models.RESTRICT)
    business_unit = models.ForeignKey(BusinessUnit, blank=False, null=True, on_delete=models.RESTRICT)
    commercial = models.ForeignKey(User, blank=False, null=True, on_delete=models.RESTRICT)
    fichier = models.ImageField(upload_to=upload_fichier_portefeuille, null=True, blank=True, )
    type_portefeuille = models.fields.CharField(choices=TypePortefeuille.choices, default=TypePortefeuille.AUCUN, max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="portefeuille_created_by", blank=True, null=True, default=None, on_delete=models.RESTRICT)

    def __str__(self):
        return f'{self.compagnie} {self.business_unit} ({self.commercial})'

    class Meta:
        db_table = 'analyse_portefeuille'
        verbose_name = 'Analyse portefeuille'
        verbose_name_plural = 'Analyse portefeuille'


def upload_fichier_commission(instance, filename):
    filebase, extension = filename.rsplit('.', 1)
    file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return 'commissions/fichiers/%s.%s' % (file_name, extension)


class ControleCommission(models.Model):
    fichier = models.ImageField(upload_to=upload_fichier_commission, null=True, blank=True, )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="controle_commision_created_by", blank=True, null=True, default=None, on_delete=models.RESTRICT)

    def __str__(self):
        return f'{self.created_by} {self.fichier} ({self.created_at})'

    class Meta:
        db_table = 'controle_commission'
        verbose_name = 'Contrôle commissions'
        verbose_name_plural = 'Contrôle commissions'
