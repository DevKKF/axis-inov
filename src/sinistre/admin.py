from django.contrib import admin

# Register your models here.
from admin_custom.admin import custom_admin_site
from django.utils.html import format_html
from sinistre.models import DossierSinistre

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
