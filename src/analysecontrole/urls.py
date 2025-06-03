from django.urls import path

from . import views

from .views import AnalysePortefeuilleView

urlpatterns = [

    path('analyseportefeuille/', AnalysePortefeuilleView.as_view(), name='analyseportefeuille'),

    # Portefeuille par compagnie
    path('add_portefeuille_compagnie/', views.add_portefeuille_compagnie, name='add_portefeuille_compagnie'),
    path('get_client_by_compagnie/', views.get_client_by_compagnie, name='get_client_by_compagnie'),

    #Analyse du portefeuille par commercial
    path('add_portefeuille_commercial/', views.add_portefeuille_commercial, name='add_portefeuille_commercial'),
    path('get_client_by_commercial/', views.get_client_by_commercial, name='get_client_by_commercial'),

    
]