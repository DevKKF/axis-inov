
from django.urls import path

from .views import LoginView, LogoutView, DashboardView, PolicesView, PoliceOverviewView, DetailsPoliceView, \
    FormulesPoliceView, QuittancesPoliceView, DocumentsPoliceView, BeneficiairePoliceView, DetailsFormulePoliceView, \
    DetailsGarantieFormulePoliceView, BeneficiaireOverviewView, FicheBeneficiaireView, FamilleBeneficiaireView, \
    GarantiesBeneficiaireView, TarifBeneficiaireView, DocumentsBeneficiaireView, ImporterPhotoBeneficiaireView, \
    SortirBeneficiaireView, SuspendreBeneficiaireView, ReseauDeSoinView, FicheQuittanceView, \
    DetailsGarantieFormuleBeneficiaireView, \
    IncorporationByEnrolementView, AjouterDocumentBeneficiaireView, AjouterMembreFamilleBeneficiaire, \
    PrestataireMedicalView, \
    ChangeBeneficiaireIdView, OnBoardingView, DetailsCampagneView, Enrolement, FormulaireEnrolement, \
    ErrorEnrolementView, \
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, \
    IncorporationsByGrhView, AjouterBeneficiaire, export_beneficiaire, set_client, PasswordResetOtpView, \
    PasswordResetFormView, beneficiaire_police_datatable, IncorporationsByGrhView, AjouterBeneficiaire, export_beneficiaire, DetailsCampagneAppmobileView

urlpatterns = [

    # DASHBOARD
    path('<int:selected_police_id>/', DashboardView.as_view(), name='grh.dashboard'),
    path('', DashboardView.as_view(), name='grh.dashboard'),
    path('', DashboardView.as_view(), name='grh.dashboard2'),

    path('set_client/', set_client, name='set_client'),


    # AUTH
    path('login/', LoginView.as_view(), name='grh.login'),
    # path('verify_codes/', VerifyCodeView.as_view(), name='grh.verify_codes'),
    

    
    
    path('logout/', LogoutView.as_view(), name='grh.logout'),
    path('password_reset/', PasswordResetView.as_view(), name='grh.password_reset'),
    path('password_reset/otp', PasswordResetOtpView.as_view(), name='grh.password_reset_otp'),
    path('password_reset/form', PasswordResetFormView.as_view(), name='grh.password_reset_form'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', PasswordResetCompleteView.as_view(), name='grh.password_reset_complete'),

    # ONBOARDING
    path('onboarding/', OnBoardingView.as_view(), name='grh.onboarding'),
    path('onboarding/details_compagne/<int:campagne_id>/', DetailsCampagneView.as_view(), name='grh.details_campagne'),
    path('onboarding/details_compagne_appmobile/<int:campagneappmobile_id>/', DetailsCampagneAppmobileView.as_view(), name='details_campagne_appmobile'),
    path('onboarding/details_compagne/<int:campagne_id>/incorporation_by_enrolement/<int:prospect_id>/', IncorporationByEnrolementView.as_view(), name='grh.incorporations_prospect'),

    # ENRÔLEMENT
    path('enrolement/<int:campagne_id>/<str:uiid>/', Enrolement.as_view(), name='grh.enrolement'),
    path('enrolement/<int:campagne_id>/<str:uiid>/<int:aliment_id>/', Enrolement.as_view(), name='grh.enrolement_by_aliment'),
    # FORMULAIRE ENRÔLEMENT
    path('enrolement/<int:campagne_id>/<str:uiid>/formulaire_enrolement/', FormulaireEnrolement.as_view(), name='grh.formulaire_enrolement'),
    path('enrolement/<int:campagne_id>/<str:uiid>/<int:aliment_id>/formulaire_enrolement/', FormulaireEnrolement.as_view(), name='grh.formulaire_enrolement_by_aliment'),
    path('enrolement/<int:campagne_id>/<str:uiid>/formulaire_enrolement/<int:prospect_id>/', FormulaireEnrolement.as_view(), name='grh.formulaire_enrolement_update'),
    path('enrolement/<int:campagne_id>/<str:uiid>/<int:aliment_id>/formulaire_enrolement/<int:prospect_id>/', FormulaireEnrolement.as_view(), name='grh.formulaire_enrolement_update_by_aliment'),
    # ERROR ENRÔLEMENT
    path('enrolement/<int:campagne_id>/<str:uiid>/error/<str:status>/', ErrorEnrolementView.as_view(), name='grh.error_enrolement'),

    # POLICES
    path('polices/', PolicesView.as_view(), name='grh.polices'),

    # POLICE OVERVIEW
    path('polices/police_overview/<int:police_id>/', PoliceOverviewView.as_view(), name='grh.police_overview'),
    path('polices/police_overview/<int:police_id>/details_police/', DetailsPoliceView.as_view(), name='grh.details_police'),
    path('polices/police_overview/<int:police_id>/formules_police/', FormulesPoliceView.as_view(), name='grh.formules_police'),
    path('polices/police_overview/<int:police_id>/formules_police/details_formule_police/<int:formule_id>/', DetailsFormulePoliceView.as_view(), name='grh.details_formule_police'),
    path('polices/police_overview/<int:police_id>/formules_police/details_formule_police/<int:formule_id>/details_garantie_formule_police/<int:bareme_id>/', DetailsGarantieFormulePoliceView.as_view(), name='grh.details_garantie_formule_police'),    
    path('polices/police_overview/<int:police_id>/formules_police/details_formule_police/<int:formule_id>/reseau_de_soin/<int:reseau_soin_id>/', ReseauDeSoinView.as_view(), name='grh.reseau_de_soin'),
    path('polices/police_overview/<int:police_id>/formules_police/details_formule_police/<int:formule_id>/reseau_de_soin/<int:reseau_soin_id>/prestataire_medical/<int:prestataire_id>/', PrestataireMedicalView.as_view(), name='grh.prestataire_medical'),
    path('polices/police_overview/<int:police_id>/quittances_police/', QuittancesPoliceView.as_view(), name='grh.quittances_police'),
    path('polices/police_overview/<int:police_id>/quittances_police/<int:quittance_id>/fiche_quittance/', FicheQuittanceView.as_view(), name='grh.fiche_quittance'),
    path('polices/police_overview/<int:police_id>/documents_police/', DocumentsPoliceView.as_view(), name='grh.documents_police'),
    path('polices/police_overview/<int:police_id>/beneficiaire/', BeneficiairePoliceView.as_view(), name='grh.beneficiaire'),
    path('polices/police_overview/<int:police_id>/beneficiaire_datatable/', beneficiaire_police_datatable, name='grh.beneficiaire_police_datatable'),

    #
    path('police/<int:police_id>/export_beneficiaire', export_beneficiaire, name='export_beneficiaire'),

    # DEMANDES BY GRH
    path('polices/police_overview/<int:police_id>/incorporations_by_grh/', IncorporationsByGrhView.as_view(), name='grh.incorporations_by_grh'),

    # BÉNÉFICIAIRE OVERVIEW
    path('polices/police_overview/<int:police_id>/beneficiaire_overview/<int:beneficiaire_id>/', BeneficiaireOverviewView.as_view(), name='grh.beneficiaire_overview'),
    path('polices/police_overview/<int:police_id>/beneficiaire_overview/<int:beneficiaire_id>/fiche_beneficiaire/', FicheBeneficiaireView.as_view(), name='grh.fiche_beneficiaire'),
    path('polices/police_overview/<int:police_id>/beneficiaire_overview/<int:beneficiaire_id>/famille_beneficiaire/', FamilleBeneficiaireView.as_view(), name='grh.famille_beneficiaire'),
    path('polices/police_overview/<int:police_id>/beneficiaire_overview/<int:beneficiaire_id>/garanties_beneficiaire/', GarantiesBeneficiaireView.as_view(), name='grh.garanties_beneficiaire'),
    path('polices/police_overview/<int:police_id>/beneficiaire_overview/<int:beneficiaire_id>/garanties_beneficiaire/<int:formule_id>/details_garantie_formule_beneficiaire/<int:bareme_id>/', DetailsGarantieFormuleBeneficiaireView.as_view(), name='grh.details_garantie_formule_beneficiaire'),    
    path('polices/police_overview/<int:police_id>/beneficiaire_overview/<int:beneficiaire_id>/tarif_beneficiaire', TarifBeneficiaireView.as_view(), name='grh.tarif_beneficiaire'),
    path('polices/police_overview/<int:police_id>/beneficiaire_overview/<int:beneficiaire_id>/documents_beneficiaire', DocumentsBeneficiaireView.as_view(), name='grh.documents_beneficiaire'),
    path('polices/police_overview/<int:police_id>/beneficiaire_overview/<int:beneficiaire_id>/importer_photo_beneficiaire', ImporterPhotoBeneficiaireView.as_view(), name='grh.importer_photo_beneficiaire'),
    path('polices/police_overview/<int:police_id>/beneficiaire_overview/<int:beneficiaire_id>/documents_beneficiaire/ajouter_document_beneficiaire', AjouterDocumentBeneficiaireView.as_view(), name='grh.ajouter_document_beneficiaire'),
    path('polices/police_overview/<int:police_id>/beneficiaire_overview/fiche_beneficiaire/<int:beneficiaire_id>/sortir_beneficiaire', SortirBeneficiaireView.as_view(), name='grh.sortir_beneficiaire'),
    path('polices/police_overview/<int:police_id>/beneficiaire_overview/fiche_beneficiaire/<int:beneficiaire_id>/suspendre_beneficiaire', SuspendreBeneficiaireView.as_view(), name='grh.suspendre_beneficiaire'),
    path('polices/police_overview/<int:police_id>/beneficiaire_overview/<int:beneficiaire_id>/formulaire_ajouter_beneficiaire_famille', AjouterMembreFamilleBeneficiaire.as_view(), name='grh.formulaire_ajouter_beneficiaire'),
    path('polices/police_overview/<int:police_id>/nouveau_beneficiaire/', AjouterBeneficiaire.as_view(), name='grh.formulaire_ajouter_beneficiaire_police'),
    path('polices/police_overview/<int:police_id>/nouveau_beneficiaire/<int:adherent_principal_id>/', AjouterBeneficiaire.as_view(), name='grh.formulaire_ajouter_beneficiaire_famille'),

    # GET / UPDATE BENEFICIAIRE ID FROM FAMILLE PAGE
    path('change_beneficiaire_id/', ChangeBeneficiaireIdView.as_view(), name='grh.change_beneficiaire_id'),

]