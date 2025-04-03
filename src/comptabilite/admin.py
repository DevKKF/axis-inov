from django.contrib import admin

from admin_custom.admin import custom_admin_site
from comptabilite.models import BordereauOrdonnance, EncaissementCommission, ReglementApporteurs

# Register your models here.
from production.models import Reglement

admin.site = custom_admin_site
admin.site.site_header = 'INOV - COMPTABILITE'


class ExtractionExcelAdmin(admin.ModelAdmin):
    list_filter = ('numero',)
    list_display = ('numero',)
    search_field = ('numero',)


class ReglementCieAdmin(admin.ModelAdmin):
    list_filter = ('numero',)
    list_display = ('numero',)
    search_field = ('numero',)

    '''def get_queryset(self, request):
        return super(ReglementCieAdmin, self).get_queryset(request).filter(
            Q(mode_reglement_id=200))'''


class EncaissementCommissionAdmin(admin.ModelAdmin):
    list_filter = ('numero',)
    list_display = ('numero',)
    search_field = ('numero',)


class ReglementApporteursAdmin(admin.ModelAdmin):
    list_filter = ('numero',)
    list_display = ('numero',)
    search_field = ('numero',)


#admin.site.register(BordereauOrdonnance)


#admin.site.register(Reglement)
admin.site.register(ReglementApporteurs)
#admin.site.register(EncaissementCommission)
#admin.site.register(ExtractionExcel)