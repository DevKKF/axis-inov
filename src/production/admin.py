import os
from datetime import datetime
from gettext import ngettext
from sqlite3 import Date

from django import forms
from django.contrib import admin
from django.contrib import messages
# Register your models here.
from import_export.admin import ImportExportModelAdmin
from slugify import slugify

from admin_custom.admin import custom_admin_site
from production.forms import ClientForm, PoliceForm, ApporteurAdminForm
from production.models import *

admin.site = custom_admin_site
admin.site.site_header = 'INOV - PRODUCTION'


# actions utilisable par plusieur modeladmin
@admin.action(description='Désactiver les éléments sélectionnés')
def action_desactiver(modeladmin, request, queryset):
    updated = queryset.update(statut=Statut.DESACTIVE)
    modeladmin.message_user(request, ngettext(
        '%d élément a été désactivé avec succès.',
        '%d éléments ont été désactivé avec succès.',
        updated,
    ) % updated, messages.SUCCESS)


@admin.action(description='Activer les éléments sélectionnés')
def action_activer(modeladmin, request, queryset):
    updated = queryset.update(statut=Statut.ACTIF)
    modeladmin.message_user(request, ngettext(
        '%d élément été désactivé avec succès.',
        '%d éléments ont été désactivé avec succès.',
        updated,
    ) % updated, messages.SUCCESS)


# ---------------------------------------- DEBUT DE CLIENT ------------------------------------------------#

# ---------------------------------------- FIN DE CLIENT ------------------------------------------------#


# ---------------------------------------- DEBUT DE POLICE ------------------------------------------------#

class CarteAdmin(admin.ModelAdmin):
    list_filter = ('numero', 'date_edition', 'statut',)
    list_display = ('numero', 'detenteur', 'date_edition', 'date_desactivation', 'statut')
    search_field = ('numero', 'date_edition', 'statut',)
    list_per_page = 20
    exclude = ('statut', 'date_desactivation', 'numero')

    def detenteur(self, obj):
        if obj.aliment == None:
            return obj.ayant_droit
        else:
            return obj.aliment

    detenteur.admin_order_field = 'ayant_droit'
    # detenteur.admin_order_field  = 'aliment'  #Allows column order sorting
    detenteur.short_description = 'Détenteur'  # Renames column head

    # overide save_model method to process other actions
    def save_model(self, request, obj, form, change):

        super().save_model(request, obj, form, change)

        if (obj.aliment == None):
            suffixe = 'B'
        else:
            suffixe = 'A'

        # METTRE A JOUR LE NUMERO
        obj.numero = str(obj.id).zfill(6) + suffixe

        super().save_model(request, obj, form, change)

    @admin.action(description='Désactiver les cartes sélectionnés')
    def action_desactiver(modeladmin, request, queryset):
        updated = queryset.update(statut=Statut.INACTIF, date_desactivation=datetime.now())
        modeladmin.message_user(request, ngettext(
            '%d carte a été désactivé avec succès.',
            '%d cartes ont été désactivé avec succès.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description='Activer les cartes sélectionnés')
    def action_activer(modeladmin, request, queryset):
        updated = queryset.update(statut=Statut.ACTIF)
        modeladmin.message_user(request, ngettext(
            '%d carte été désactivé avec succès.',
            '%d cartes ont été désactivé avec succès.',
            updated,
        ) % updated, messages.SUCCESS)

    actions = [action_activer, action_desactiver, ]


class MouvementAdmin(ImportExportModelAdmin):
    list_filter = ('libelle', 'police')
    list_display = ('libelle', 'police')
    search_field = ('libelle', 'police')
    list_per_page = 20


class QuittanceAdmin(ImportExportModelAdmin):
    list_filter = ('numero', 'date_emission')
    list_display = ['numero', 'prime_ttc', 'date_emission', 'get_numero_police', 'get_client','statut']
    search_field = ('numero', 'prime_ttc', 'date_emission')
    list_per_page = 20
    exclude = ('statut',)

    # accède à un champ de la table parente
    def get_numero_police(self, obj):
        return obj.police.numero

    get_numero_police.admin_order_field = 'numero'  # Allows column order sorting
    get_numero_police.short_description = 'Numéro Police'  # Renames column head

    # accéder au client
    def get_client(self, obj):
        return obj.mouvement.police.client.nom

    get_client.admin_order_field = 'nom'  # Allows column order sorting
    get_client.short_description = 'Client'  # Renames column head


class ReglementAdmin(ImportExportModelAdmin):
    list_filter = ('montant', 'date_paiement')
    list_display = ('montant', 'date_paiement')
    search_field = ('montant', 'date_paiement')
    list_per_page = 20


class AcompteAdmin(admin.ModelAdmin):
    list_filter = ('montant', 'date_versement', 'client')
    list_display = ('montant', 'date_versement', 'client')
    search_field = ('montant', 'date_versement', 'client')
    list_per_page = 20

    def has_add_permission(self, request, obj=None):
        return False


'''
def add_view(self, request, form_url='', extra_context=None):
    extra_context = extra_context or {}
    extra_context['your_custom_data'] = self.your_custom_method()
    return super().add_view(request, form_url, extra_context=extra_context)
'''


class ApporteurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenoms', 'code', 'telephone', 'email', 'adresse', 'type_apporteur', 'pays')
    search_field = ('nom', 'prenoms', 'code',  'telephone', 'email', 'adresse', 'type_apporteur', 'pays')
    list_per_page = 20
    form = ApporteurAdminForm

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(bureau=request.user.bureau)

        return queryset


    def save_model(self, request, obj, form, change):
        # Renseignez le champ bureau uniquement lors de la création d'une nouvelle compagnie
        if not change:
            #code_bureau = request.user.bureau.code
            obj.bureau = request.user.bureau
            #obj.code = f"{slugify(code_bureau)}{str(obj.pk).zfill(4)}".upper()

        # Appelez la méthode save_model de la classe parente pour effectuer l'enregistrement réel
        super().save_model(request, obj, form, change)


class GroupeAdmin(admin.ModelAdmin):
    list_filter = ('nom', 'statut', 'created_at')
    list_display = ('nom', 'statut', 'created_at')
    search_field = ('nom', 'statut', 'created_at')
    list_per_page = 10


admin.site.register(Client, )
admin.site.register(Apporteur, ApporteurAdmin)
#admin.site.register(Carte, CarteAdmin)

