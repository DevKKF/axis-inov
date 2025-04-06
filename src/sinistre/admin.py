from django.contrib import admin

# Register your models here.
from admin_custom.admin import custom_admin_site
from django.utils.html import format_html
from sinistre.models import DossierSinistre, DemandeRemboursementMobile

admin.site = custom_admin_site
admin.site.site_header = 'INOV - SINISTRE'

class DossierSinistreAdmin(admin.ModelAdmin):
    list_filter = ('numero',)
    list_display = ('numero',)
    search_field = ('numero',)

class SinistreAdmin(admin.ModelAdmin):
    list_filter = ('numero',)
    list_display = ('numero',)
    search_field = ('numero',)

admin.site.register(DossierSinistre,)
#admin.site.register(Sinistre)

class DemandeRemboursementMobileAdmin(admin.ModelAdmin):
    list_display = (
        'date_sinistre', 'acte', 'prestataire', 'montant_a_rembourser',
        'beneficiaire', 'adherent_principal', 'numero_remboursement', 'statut', 'action'
    )
    list_filter = ('beneficiaire', 'acte', 'bureau', 'mode_remboursement')
    search_fields = ('beneficiaire__nom', 'acte__libelle', 'prestataire__nom', 'numero_remboursement')
    list_per_page = 10

    # Optimize database queries for related objects
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('acte', 'prestataire', 'beneficiaire', 'adherent_principal', 'bureau', 'mode_remboursement')
        return queryset

    def action(self, obj):
        action = '<a href="#"><span class="badge btn-sm btn-success rounded-pill"><i class="fa fa-check"></i> Traiter</span></a>'
        return format_html(action)

    action.short_description = 'Action'

admin.site.register(DemandeRemboursementMobile, DemandeRemboursementMobileAdmin)