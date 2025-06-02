from django.urls import path

from . import views

from .views import AnalysePortefeuilleView

urlpatterns = [

    path('analyseportefeuille/', AnalysePortefeuilleView.as_view(), name='analyseportefeuille'),

    #Analyse du portefeuille par commercial
    path('add_portefeuille_commercial/', views.add_portefeuille_commercial, name='add_portefeuille_commercial'),
    path('get_client_by_commercial/', views.get_client_by_commercial, name='get_client_by_commercial'),

    
]