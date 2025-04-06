from django.contrib import admin
from .models import InfoActe

@admin.register(InfoActe)
class InfoActeAdmin(admin.ModelAdmin):
    list_display = ('numero_assure', 'medecin', 'acte', 'affection', 'rc')
    search_fields = ('numero_assure', 'medecin', 'affection')
    list_filter = ('medecin', 'affection') 