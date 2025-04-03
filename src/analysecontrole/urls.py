from django.urls import path

from . import views

from .views import AnalysePortefeuilleView, ControleComissionView

urlpatterns = [

    path('analyseportefeuille/', AnalysePortefeuilleView.as_view(), name='analyseportefeuille'),

    # Portefeuille par compagnie
    path('add_portefeuille_compagnie/', views.add_portefeuille_compagnie, name='add_portefeuille_compagnie'),
    path('get_client_by_compagnie/', views.get_client_by_compagnie, name='get_client_by_compagnie'),

    # Portefeuille par commercial
    path('add_portefeuille_commercial/', views.add_portefeuille_commercial, name='add_portefeuille_commercial'),
    path('get_client_by_commercial/', views.get_client_by_commercial, name='get_client_by_commercial'),

    # Portefeuille par business unit
    path('add_portefeuille_business_unit/', views.add_portefeuille_business_unit, name='add_portefeuille_business_unit'),
    path('get_client_by_business_unit/', views.get_client_by_business_unit, name='get_client_by_business_unit'),

    path('controlecommission/', ControleComissionView.as_view(), name='controlecommission'),
    path('controlecommission_datatable/', views.controlecommission_datatable, name='controlecommission_datatable'),
    path('importer_controle_commission/', views.importer_controle_commission, name='importer_controle_commission'),
]