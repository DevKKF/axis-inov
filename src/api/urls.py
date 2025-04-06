from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import *

# router = routers.SimpleRouter()
# router.register(r'sinistres', SinistreViewSet)

url_v2 = [
    # Authentification et configuration
    path('login-global', LoginGlobalView.as_view(), name='login-global'),
    path('login', LoginUserView.as_view(), name='login'),
    path('register', RegisterUserView.as_view(), name='register'),
    path('config/<str:key>', ConfigurationView.as_view(), name='config'),
    path('config-bureau/<str:key>', ConfigurationBureauView.as_view(), name='config-bureau'),
    path('request-reset-password', RequestResetPasswordView.as_view(), name='request_reset_password'),
    path('reset-password', ResetPasswordView.as_view(), name='reset_password'),
    path('otp-request', OTPRequestView.as_view(), name='otp_request'),

    # Gestion des utilisateurs et bénéficiaires
    path('user', UserView.as_view(), name='update_user'),
    path('beneficiaries', BeneficiariesView.as_view(), name='famille_list'),
    path('beneficiary/<int:beneficiary_id>', BeneficiariesByIdView.as_view(), name='beneficiaire_by_id'),
    path('beneficiary/carte/<str:carte>', BeneficiariesByCarteView.as_view(), name='beneficiaire_by_carte'),
    path('beneficiary/<int:formul_id>/barreme', BarremeView.as_view(), name='beneficiaire_barreme'),
    path('beneficiary/<int:formul_id>/reseau', ReseauSoinsView.as_view(), name='reseau_list'),

    # Sinistres et prestataires
    path('sinistres', SinistreView.as_view(), name='sinistre_list'),
    path('typeprestataire', TypePrestataireView.as_view(), name='type_prestataire_list'),
    path('prestataire-list', PrestataireDataView.as_view(), name='prestataire_list'),
    path('acte-list', ActeDataView.as_view(), name='acte_list'),

    # Gestion des prestataires
    path('prestataire-login', LoginPrestataireView.as_view(), name='prestataire_login'),
    path('prestataire', PrestataireView.as_view(), name='prestataire_register'),
    path('test-num-carte', TestNumCartView.as_view(), name='test-num-carte'),

    # API BOBY
    path('boBy/list', WsBobyView.as_view(), name='boby_list'),

    # Remboursements et ayants droit
    path('mode-remboursement', ModeRemboursementListView.as_view(), name='mode-remboursement'),
    path('demande-remboursements', DemandeRemboursementView.as_view(), name='demande-remboursements'),
    path('ajout_ayant_droit', AddAyantDroitView.as_view(), name='ajout_ayant_droit'),
    path('liste_prospect', ListProspectsView.as_view(), name='liste_prospect'),

    # Carte digitale
    path('digital-card/fetch', FetchDigitalCard.as_view(), name='fetch_digital_card'),
    path('digital-card/create', CreateDigitalCard.as_view(), name='create_digital_card'),
    path('digital-card/update/<int:digital_card_id>', UpdateDigitalCard.as_view(), name='update_digital_card'),

    # Prise en charge
    path('prise-en-charge', PriseEnChargeView.as_view(), name='prise_en_charge'),
    path('prise-en-charge/info-acte/<int:acte_id>', PriseEnChargeActeInfoView.as_view(), name='prise_en_charge_acte'),

    # Données constantes
    path('constantes', ConstantesView.as_view(), name='constantes'),
]

# url_v2 += router.urls
from . import views

urlpatterns = [
    path('v2/', include(url_v2)),
    path('suggestions', views.suggestions, name='suggestions'),
] 