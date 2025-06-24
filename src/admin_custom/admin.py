#import datetime

from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Group
from datetime import datetime

from api.serializers import BureauSerializer
from configurations.models import Rubrique, User, Bureau, TypeRemboursement, AdminGroupeBureau
from production.models import Police, HistoriquePolice, MouvementPolice
from shared.enum import StatutSinistre, Statut, StatutValidite
# Register your models here.
from sinistre.models import DossierSinistre
import pandas as pd


class CustomAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):

        if(extra_context is None): extra_context = {}

        user = User.objects.get(id=request.user.id)

        if request.user.is_superuser:
            bureaux = Bureau.objects.filter(status=True)
            bureaux_serializer = BureauSerializer(bureaux, many=True).data
        elif request.user.is_admin_group:
            admin_bureaux = AdminGroupeBureau.objects.filter(user=request.user, status=True)
            bureaux = [b.bureau for b in admin_bureaux]
            bureaux_serializer = BureauSerializer(bureaux, many=True).data
        else:
            bureaux_serializer = []

        """
        if user.is_commercial:
            count_polices_en_cours = Police.objects.filter(date_fin_effet__gt=today, commercial_id=user.id).count()
            count_polices_a_echeance = Police.objects.filter(date_fin_effet__lte=in_90_days, date_fin_effet__gt=today, commercial_id=user.id).count()
            count_polices_non_renouvelees_resilies = Police.objects.filter(date_fin_effet__lt=today, commercial_id=user.id).count()
        elif user.is_production:
            count_polices_en_cours = Police.objects.filter(date_fin_effet__gt=today).count()
            count_polices_a_echeance = Police.objects.filter(date_fin_effet__lte=in_90_days, date_fin_effet__gt=today).count()
            count_polices_non_renouvelees_resilies = Police.objects.filter(date_fin_effet__lt=today).count()
        else:
            count_polices_en_cours = 0
            count_polices_a_echeance = 0
            count_polices_non_renouvelees_resilies = 0
        """

        polices_qs = Police.objects.filter(
            client__isnull=False,
            historique_polices__isnull=False,
        ).distinct()

        date_comparaison = datetime.today().date()

        nombre_police = 0
        nombre_police_en_cours = 0
        nombre_arrivant_echeance = 0
        nombre_a_echeance = 0
        nombre_resilie_annule = 0
        for plc in polices_qs:
            date_echeance_police = None
            if plc.date_fin_effet:
                date_echeance_police = plc.date_fin_effet
            elif plc.date_fin_police:
                date_echeance_police = plc.date_fin_police

            if plc.etat_police not in ["Annulé", "Résilié", "Suspendu"]:
                nombre_police += 1
                if date_echeance_police and date_echeance_police > date_comparaison:
                    difference_jours = (date_echeance_police - date_comparaison).days
                    if difference_jours <= 90:
                        nombre_arrivant_echeance += 1
                    nombre_police_en_cours += 1
                else:
                    nombre_a_echeance += 1
            else:
                nombre_resilie_annule += 1

        # Ajout au contexte
        extra_context['count_polices_en_cours'] = nombre_police_en_cours
        extra_context['count_polices_a_echeance'] = nombre_arrivant_echeance
        extra_context['count_polices_non_renouvelees_resilies'] = nombre_a_echeance
        extra_context['count_polices_annulees_resilies_suspendues'] = nombre_resilie_annule

        return super(CustomAdminSite, self).index(request, extra_context)


# django admin index template
AdminSite.index_template = 'main_index.html'

# new custom admin
custom_admin_site = CustomAdminSite(name='custom_admin')

# get back django auth group app
custom_admin_site.register(Group)