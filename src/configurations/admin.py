from pprint import pprint

import pandas as pd
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from django_json_widget.widgets import JSONEditorWidget
from import_export.admin import ImportExportModelAdmin
from django import forms
from admin_custom.admin import custom_admin_site
from configurations.forms import ActionLogForm, PermissionForm, SousRubriqueForm, TarifForm, \
    CompagnieAdminForm, BanqueAdminForm, ApporteurInternationalForm, GroupeInterForm, GarantieBrancheForm, \
    GarantieFormuleForm
from configurations.models import *
from production.models import Quittance, SecteurActivite, TypeDocument, Mouvement, Motif

from production.models import Client

admin.site = custom_admin_site
admin.site.site_header = 'INOV'


class AdminGroupeBureauAdmInLine(admin.TabularInline):
    model = AdminGroupeBureau

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "bureau":
            kwargs["queryset"] = Bureau.objects.filter(status=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class TaxeInline(admin.TabularInline):
    model = BureauTaxe
    extra = 1


class FonctionAdmin(admin.ModelAdmin):
    list_display = ('libelle',)
    search_fields = ('libelle',)
    list_filter = ('libelle',)
    list_per_page = 10


class BureauTaxeAdmin(admin.ModelAdmin):
    list_display = ('bureau_id', 'taxe_id', 'taux', 'montant')
    list_filter = ('bureau_id', 'taxe_id', 'taux', 'montant')
    search_fields = ('bureau_id', 'taxe_id', 'taux', 'montant')
    list_per_page = 10


class TarifAdmin(admin.ModelAdmin):
    form: TarifForm

    list_per_page = 30
    list_display = (
    'acte', 'lettre_cle_classique', 'coef_classique', 'pu_classique', 'cout_classique', 'pu_mutuelle', 'cout_mutuelle',
    'pu_public_hg', 'cout_public_hg', 'pu_public_chu', 'cout_public_chu', 'pu_public_ica', 'cout_public_ica')
    list_filter = ('acte',)  # Vous pouvez ajouter d'autres champs de filtrage si nécessaire
    search_fields = ('acte',)  # Vous pouvez ajouter d'autres champs de recherche si nécessaire


class TarifExcelAdmin(ImportExportModelAdmin):
    list_display = (
    'CODE_REGROUPEMENT_INOV', 'LIBELLE_ACTE', 'CODE_ACTE', 'LETTRE_CLE_CLASSIQUE', 'COEF_CLASSIQUE', 'PU_CLASSIQUE',
    'COUT_CLASSIQUE', 'PU_MUTUELLE', 'COUT_MUTUELLE', 'PU_PUBLIC_HG', 'COUT_PUBLIC_HG')
    list_filter = ('CODE_REGROUPEMENT_INOV', 'LIBELLE_ACTE',
                   'CODE_ACTE')  # Vous pouvez ajouter d'autres champs de filtrage si nécessaire
    search_fields = ('CODE_REGROUPEMENT_INOV', 'LIBELLE_ACTE',
                     'CODE_ACTE')  # Vous pouvez ajouter d'autres champs de recherche si nécessaire
    list_per_page = 10


class SecteurActiviteAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'status', 'created_at')


class AlimentBaobabAdmin(ImportExportModelAdmin):
    list_display = ('num_benef', 'nom', 'prenom', 'formule', 'formule_id')
    list_filter = ('num_benef', 'nom', 'prenom', 'formule', 'formule_id')
    search_fields = ('num_benef', 'nom', 'prenom', 'formule', 'formule_id')
    list_per_page = 10


class ChangementFormuleAdmin(ImportExportModelAdmin):
    list_display = ('NOM', 'PRENOMS', 'NUMERO_CARTE', 'QUALITE_BENEFICIAIRE',
                    'LIB_FORMULE', 'CD_FORMULE', 'DATE_DEBUT')

    search_fields = ('NOM', 'PRENOMS', 'NUMERO_CARTE', 'QUALITE_BENEFICIAIRE',
                     'LIB_FORMULE', 'CD_FORMULE', 'DATE_DEBUT')
    list_per_page = 10


class ProfessionAdmin(ImportExportModelAdmin):
    list_filter = ('name', 'code')
    list_display = ('name', 'code')
    search_field = ('name', 'code')
    list_per_page = 10


class BureausAdmin(ImportExportModelAdmin):
    inlines = [TaxeInline]
    list_display = ('nom', 'code', 'telephone', 'fax', 'email', 'tarif_bureau')
    list_filter = ('nom', 'code', 'telephone', 'fax', 'email', ('pays', admin.RelatedOnlyFieldListFilter))
    search_field = ('nom', 'code', 'telephone', 'fax', 'email')
    list_per_page = 10

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(id=request.user.bureau.id)
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Filtrer les bureaux pour n'afficher que celui de l'utilisateur connecté
        if db_field.name == 'pays':
            kwargs['queryset'] = Pays.objects.filter(pk=request.user.bureau.pays.id)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class RetenueAdmin(admin.ModelAdmin):
    list_filter = ('code', 'libelle')
    list_display = ('code', 'libelle', 'taux', 'secteur', 'prestataires')
    fields = ['code', 'libelle', 'taux', 'secteur', 'type_prestataire']
    search_field = ('libelle', 'code')
    list_per_page = 20

    def prestataires(self, obj):
        return ', '.join(
            [type.name for type in obj.type_prestataire.all()]) if obj.type_prestataire.count() > 0 else '-'

    prestataires.allow_tags = True
    prestataires.short_description = "Types Prestataires"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(bureau=request.user.bureau)

        return queryset

    def save_model(self, request, obj, form, change):
        # Renseignez le champ bureau uniquement lors de la création d'une nouvelle compagnie
        if not change:
            obj.bureau = request.user.bureau

        # Appelez la méthode save_model de la classe parente pour effectuer l'enregistrement réel
        super().save_model(request, obj, form, change)


class ParamProduitCompagnieInline(admin.TabularInline):
    model = ParamProduitCompagnie
    extra = 1


class CompagnieAdmin(admin.ModelAdmin):
    inlines = [ParamProduitCompagnieInline]  # , Pres
    list_display = ('nom', 'code', 'type_garant', 'telephone',)
    list_filter = ('nom', 'code', 'type_garant', 'telephone', 'email')
    search_field = ('nom', 'code', 'type_garant', 'telephone', 'email')
    list_per_page = 10
    form = CompagnieAdminForm

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(bureau=request.user.bureau)

        return queryset

    def save_model(self, request, obj, form, change):
        # Renseignez le champ bureau uniquement lors de la création d'une nouvelle compagnie
        if not change:
            obj.bureau = request.user.bureau

        # Appelez la méthode save_model de la classe parente pour effectuer l'enregistrement réel
        super().save_model(request, obj, form, change)


class MotifAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle',)


class TypeEtablissementAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'code')
    list_filter = ('libelle', 'code')
    search_field = ('libelle', 'code')
    list_per_page = 10


class SpecialiteAdmin(ImportExportModelAdmin):
    list_filter = ('name', 'status')
    list_display = ('name', 'status')
    search_field = ('name', 'status')
    list_per_page = 10


class RubiqueAdmin(ImportExportModelAdmin):
    list_filter = ('libelle',)
    list_display = ('code', 'libelle',)
    search_field = ('libelle',)
    list_per_page = 20


class LangueAdmin(admin.ModelAdmin):
    list_filter = ('libelle',)
    list_display = ('libelle', 'code')
    search_field = ('libelle', 'code')
    list_per_page = 20


class PaysAdmin(admin.ModelAdmin):
    list_filter = ('nom',)
    list_display = ('nom', 'code', 'indicatif', 'poligamie', 'devise')
    search_field = ('nom', 'code')
    list_per_page = 20


class DeviseAdmin(admin.ModelAdmin):
    list_filter = ('libelle',)
    list_display = ('libelle', 'code')
    search_field = ('code', 'libelle')
    list_per_page = 20


class ParamProduitCompagnieInline(admin.TabularInline):
    model = ParamProduitCompagnie
    extra = 1


class ProduitAdmin(admin.ModelAdmin):
    inlines = [ParamProduitCompagnieInline]
    list_display = ('code', 'nom', 'branche')
    list_per_page = 20


class BrancheAdmin(admin.ModelAdmin):
    list_filter = ('code', 'nom', 'status')
    list_display = ('code', 'nom', 'status')
    search_field = ('code', 'nom', 'status')
    list_per_page = 20


class TaxeAdmin(admin.ModelAdmin):
    list_filter = ('libelle',)
    list_display = ('libelle', 'code')
    search_field = ('libelle', 'code')
    list_per_page = 20


@admin.register(BaseCalcul)
class BaseCalculAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'code')
    list_filter = ('libelle', 'code')
    search_field = ('libelle', 'code')


@admin.register(TypeQuittance)
class TypeQuittanceAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'code')
    list_filter = ('libelle', 'code')
    search_field = ('libelle', 'code')


@admin.register(NatureQuittance)
class NatureQuittanceAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'code')
    list_filter = ('libelle', 'code')
    search_field = ('libelle', 'code')


class BanqueAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle', 'bureau')
    form = BanqueAdminForm

    def save_model(self, request, obj, form, change):
        # Renseignez le champ bureau uniquement lors de la création d'un nouvel utilisateur
        if not change:
            obj.bureau = request.user.bureau
            obj.created_by = request.user

        # Appelez la méthode save_model de la classe parente pour effectuer l'enregistrement réel
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(bureau=request.user.bureau)

        return queryset


class TypeDocumentAdmin(admin.ModelAdmin):
    list_display = ('libelle',)
    list_filter = ('libelle',)
    search_field = ('libelle',)


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'last_name', 'first_name', 'is_active', 'is_superuser')

    list_filter = ('username', 'last_name', 'first_name', 'is_active', 'is_superuser')
    # search_fields = ('username', 'last_name', 'first_name', 'email', 'is_active', 'is_superuser')
    list_per_page = 10

    inlines = [
        AdminGroupeBureauAdmInLine,
    ]

    superuser_fieldsets = (
        (None, {"fields": ("username", "password", "first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_admin_group",
                    "groups",

                ),
            },
        ),
        # ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    staff_fieldsets = (
        (None, {"fields": ("username", "password", "first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    # "is_superuser",
                    "groups",

                ),
            },
        ),
        # ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    superuser_add_fieldsets = (
        (None, {"fields": ("username", "password1", "password2", "first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_admin_group",
                    "groups",

                ),
            },
        ),
    )

    staff_add_fieldsets = (
        (None, {"fields": (
            "username", "password1", "password2", "first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    # "is_superuser",
                    # "is_admin_group",
                    "groups",

                ),
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            if request.user.is_superuser:
                return self.superuser_add_fieldsets
            else:
                return self.staff_add_fieldsets

        if request.user.is_superuser:
            return self.superuser_fieldsets
        else:
            return self.staff_fieldsets

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if request.user.is_superuser:
            print("Bureau ", request.user.bureau)
            queryset = queryset.filter(bureau=request.user.bureau)
        else:
            print("Bureau ", request.user.bureau)
            queryset = queryset.filter(bureau=request.user.bureau, is_superuser=False)

        return queryset

    def save_model(self, request, obj, form, change):
        # Renseignez le champ bureau uniquement lors de la création d'un nouvel utilisateur

        if not change:
            obj.bureau = request.user.bureau

        # Save the user first to get the primary key
        super().save_model(request, obj, form, change)


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    form = ActionLogForm
    list_per_page = 30
    list_display = ('data_before', 'data_after',)
    # list_display = ('done_by', 'table', 'row', 'action', 'description', 'data_before', 'data_after',)
    # search_fields = ('action',)
    # list_filter = ('action',)


# class TypeRemboursementAdmin(admin.ModelAdmin):
#     list_display = ('libelle', 'code')
#     list_filter = ('libelle', 'code')
#     search_field = ('libelle', 'code')
#     list_per_page = 10


# class TypePrefinancementAdmin(admin.ModelAdmin):
#     list_display = ('libelle', 'code')
#     list_filter = ('libelle', 'code')
#     search_field = ('libelle', 'code')
#     list_per_page = 10


@admin.register(PeriodeComptable)
class PeriodeComptableAdmin(ImportExportModelAdmin):
    list_display = ('libelle', 'mois', 'annee', 'date_debut', 'date_fin')
    list_filter = ('libelle', 'mois', 'annee')
    search_field = ('libelle', 'code', 'annee')
    list_per_page = 10


class KeyValueDataAdmin(ImportExportModelAdmin):
    list_display = ('key', 'description', 'statut')
    list_filter = ('key', 'statut')
    search_field = ('key', 'description', 'data')
    list_per_page = 10
    formfield_overrides = {
        # fields.JSONField: {'widget': JSONEditorWidget}, # if django < 3.1
        models.JSONField: {'widget': JSONEditorWidget(height='500px', width='100%', mode='tree')},
    }


class ModeCreationAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle',)


class NatureOperationAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle',)


class BackgroundQueryTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'auteur', 'created_at', 'updated_at', 'fichier_excel', 'statut',)
    list_filter = (
    'status', 'created_at', ('created_by__bureau', admin.RelatedOnlyFieldListFilter), 'created_by__username')
    search_field = ('name', 'status', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at', 'error_message', 'name', 'created_by', 'fichier_excel', 'statut')
    list_per_page = 10

    superuser_fieldsets = (
        ('Général', {
            'fields': ('name', 'query', 'file', 'status')
        }),
        ('Meta Donnée', {
            'fields': (
                'created_at', 'updated_at', 'error_message', 'created_by')
        }),
    )

    staff_fieldsets = (
        ('Général', {
            'fields': ('name', 'file', 'status')
        }),
        ('Meta Donnée', {
            'fields': (
                'created_at', 'updated_at', 'error_message', 'created_by')
        }),
    )

    add_fieldsets = (
        ('Général', {
            'fields': ('name', 'query', 'status')
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        if request.user.is_superuser:
            return self.superuser_fieldsets
        else:
            return self.staff_fieldsets

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(created_by=request.user, status__in=['ENATT', 'ENCOURS', 'TERMINEE', 'ECHOUEE'])
        return queryset

    def auteur(self, obj):
        return obj.created_by.username

    auteur.short_description = 'Exécuté par'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_update_permission(self, request, obj=None):
        return False

    class Media:
        js = ("configurations/js/custom.js",)


class ApporteurInternationalAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'pays')
    form = ApporteurInternationalForm


class GroupeInterAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'apporteur', 'status')
    form = GroupeInterForm

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_update_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            return False


class ModelLettreChequeAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'banque', 'auteur', 'statut',)
    list_filter = ('statut', ('bureau', admin.RelatedOnlyFieldListFilter), ('banque', admin.RelatedOnlyFieldListFilter))
    search_field = ('libelle', 'banque__libelle')
    # readonly_fields = ('created_at','updated_at','error_message','name','created_by','fichier_excel', 'statut')
    list_per_page = 10

    fieldsets = (
        ('Général', {
            'fields': ('libelle', 'banque', 'model', 'statut')
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(bureau=request.user.bureau).order_by('-created_at')
        return queryset

    def auteur(self, obj):
        return obj.created_by.username

    auteur.short_description = 'Créé par'

    def save_model(self, request, obj, form, change):
        # Renseignez le champ bureau uniquement lors de la création d'un nouvel utilisateur
        if not change:
            obj.created_by = request.user
            obj.bureau = request.user.bureau

        # Appelez la méthode save_model de la classe parente pour effectuer l'enregistrement réel
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "banque":
            kwargs["queryset"] = Banque.objects.filter(bureau=request.user.bureau, status=True).order_by('libelle')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BordereauLettreChequeAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'created_at', 'nombre', 'edite_par', 'action',)
    list_filter = ('libelle', 'created_at',)
    search_field = ('libelle', 'created_at', 'created_by')
    readonly_fields = ('created_at', 'edite_par', 'fichier_pdf',)
    list_per_page = 10

    superuser_fieldsets = (
        ('Général', {
            'fields': ('libelle', 'model_lettre_cheque', 'nombre', 'fichier_pdf')
        }),
        ('Meta Donnée', {
            'fields': (
                'created_at', 'updated_at', 'edite_par')
        }),
    )

    staff_fieldsets = (
        ('Général', {
            'fields': ('libelle', 'nombre', 'fichier_pdf', 'edite_par')
        }),
    )

    add_fieldsets = (
        ('Général', {
            'fields': ('libelle', 'model_lettre_cheque', 'nombre', 'fichier')
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        if request.user.is_superuser:
            return self.superuser_fieldsets
        else:
            return self.staff_fieldsets

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(bureau=request.user.bureau)
        return queryset

    def edite_par(self, obj):
        return f'{obj.created_by.first_name} {obj.created_by.last_name}' if obj.created_by else ''

    def action(self, obj):
        return obj.fichier_pdf

    edite_par.short_description = 'Edité par'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_update_permission(self, request, obj=None):
        return False

    # class Media:
    #     js = ("configurations/js/custom.js",)


class MailingListAdminForm(forms.ModelForm):
    class Meta:
        model = MailingList
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Si l'instance existe déjà, ne pas modifier created_by
            self.fields['created_by'].required = False
            self.fields['updated_by'].required = False
        else:
            # Si l'instance n'existe pas (donc nouvelle), définir created_by à l'utilisateur connecté
            user = self.initial.get('user')
            if user:
                self.fields['created_by'].initial = user
                self.fields['updated_by'].initial = user


class MailingListAdmin(admin.ModelAdmin):
    form = MailingListAdminForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.user = request.user  # Passe l'utilisateur connecté au formulaire
        return form

    def save_model(self, request, obj, form, change):
        if not change:  # Si l'objet est nouveau (création)
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


class BusinessUnitAdmin(admin.ModelAdmin):
    list_filter = ('libelle', 'status', 'created_at')
    list_display = ('libelle', 'status', 'created_at')
    search_field = ('libelle', 'status', 'created_at')
    list_per_page = 10


class GarantieBrancheAdmin(admin.ModelAdmin):
    form = GarantieBrancheForm

    list_display = ['branche', 'get_garanties', 'status', 'created_at', 'updated_at']
    list_filter = ['branche', 'status']
    search_fields = ['branche__nom', 'garantie__nom']

    def save_model(self, request, obj, form, change):
        """
        Gérer la sauvegarde en associant branche et garanties via IDs
        """
        branche = form.cleaned_data['branche']
        garanties_selected = form.cleaned_data['garanties']
        status = form.cleaned_data['status']

        # Supprimer les anciennes associations pour la branche
        GarantieBranche.objects.filter(branche=branche).delete()

        try:
            # Créer les nouvelles associations
            GarantieBranche.objects.bulk_create([
                GarantieBranche(
                    branche=branche,
                    garantie=garantie,
                    status=status
                ) for garantie in garanties_selected
            ])
        except Exception as e:
            self.message_user(request, f"Erreur : {e}", level='error')

    def get_garanties(self, obj):
        """
        Afficher les garanties associées à une branche
        """
        garanties = GarantieBranche.objects.filter(branche=obj.branche).values_list('garantie__nom', flat=True)
        return ', '.join(garanties)

    get_garanties.short_description = "Garanties"


class GarantieFormuleAdmin(admin.ModelAdmin):
    form = GarantieFormuleForm

    list_display = ['formule', 'get_garanties', 'status', 'created_at', 'updated_at']
    list_filter = ['formule', 'status']
    search_fields = ['formule__libelle', 'garantie__nom']

    def save_model(self, request, obj, form, change):
        """
        Gérer la sauvegarde en associant branche et garanties via IDs
        """
        formule = form.cleaned_data['formule']
        garanties_selected = form.cleaned_data['garanties']
        status = form.cleaned_data['status']

        # Supprimer les anciennes associations pour la branche
        GarantieFormule.objects.filter(formule=formule).delete()

        try:
            # Créer les nouvelles associations
            GarantieFormule.objects.bulk_create([
                GarantieFormule(
                    formule=formule,
                    garantie=garantie,
                    status=status
                ) for garantie in garanties_selected
            ])
        except Exception as e:
            self.message_user(request, f"Erreur : {e}", level='error')

    def get_garanties(self, obj):
        """
        Afficher les garanties associées à une branche
        """
        garanties = GarantieFormule.objects.filter(formule=obj.formule).values_list('garantie__nom', flat=True)
        return ', '.join(garanties)

    get_garanties.short_description = "Garanties"


class ConditionsAssuranceAdmin(admin.ModelAdmin):
    list_filter = ('libelle',)
    list_display = ('libelle', 'code', 'status')
    search_field = ('libelle', 'code', 'status')
    list_per_page = 20


class MoyensTransportAdmin(admin.ModelAdmin):
    list_filter = ('libelle',)
    list_display = ('libelle', 'code', 'status')
    search_field = ('libelle', 'code', 'status')
    list_per_page = 20


class GroupeAdmin(admin.ModelAdmin):
    list_filter = ('libelle', 'statut', 'created_at')
    list_display = ('libelle', 'statut', 'created_at')
    search_field = ('libelle', 'statut', 'created_at')
    list_per_page = 10


class TauxCommissionAdmin(admin.ModelAdmin):
    list_filter = ('libelle', 'code', 'created_at')
    list_display = ('libelle', 'code', 'taux', 'created_at')
    search_field = ('libelle', 'code', 'created_at')
    list_per_page = 10


admin.site.register(Compagnie, CompagnieAdmin)
admin.site.register(Civilite)
admin.site.register(TypeClient)
admin.site.register(TypePersonne)
admin.site.register(Pays, PaysAdmin)
admin.site.register(Branche, BrancheAdmin)
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Fractionnement, )
admin.site.register(ModeReglement, )
admin.site.register(Banque, BanqueAdmin)
admin.site.register(Devise, DeviseAdmin)
admin.site.register(Taxe, TaxeAdmin)
admin.site.register(TypeQuittance, TypeQuittanceAdmin)
admin.site.register(TypeApporteur)
admin.site.register(CompteTresorerie)
admin.site.register(BackgroundQueryTask, BackgroundQueryTaskAdmin)
admin.site.register(BordereauLettreCheque, BordereauLettreChequeAdmin)
admin.site.register(BusinessUnit, BusinessUnitAdmin)
admin.site.register(TypeProduit)
admin.site.register(CategorieVehicule)
admin.site.register(Carburant)
admin.site.register(Usage)
admin.site.register(Carosserie)
admin.site.register(Garantie)
admin.site.register(Formule)
admin.site.register(GarantieFormule, GarantieFormuleAdmin)
admin.site.register(ConditionsAssurance, ConditionsAssuranceAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Groupe, GroupeAdmin)
admin.site.register(BureauTaxe, BureauTaxeAdmin)
admin.site.register(RisqueProduit, RisqueProduitAdmin)
admin.site.register(TypeSinistre)
admin.site.register(TypeIntervenant)
admin.site.register(Responsabilite)
admin.site.register(TypeMouvement)
admin.site.register(Circonstance)
admin.site.register(PosteDommage)
admin.site.register(GarantieCirconstance)

# admin.site.register(Mouvement) #à réactiver plus tard
# admin.site.register(Motif, MotifAdmin) #à réactiver plus tard
