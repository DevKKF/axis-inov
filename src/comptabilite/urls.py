
from django.urls import path

from . import views
from .views import BordereauxOrdonnancesView, DetailBordereauOrdonnancementView, DetailFactureGarant, \
    EncaissementCommissionsCourtGestView, FactureCompagnieView, InitialisationFondRoulementView, PaiementsRealises, \
    RefacturationAssureurView, ReversesementCompagniesView, \
    EncaissementCommissionsView, ReglementApporteursView, BordereauxPayesView, SuiviTresorerie, EditionLettreCheque, create_periode_comptable, \
    export_bordereaux_ordonnances, export_bordereaux_ordonnances_paye
from .views import DetailTresorerie

urlpatterns = [
    
    # path('bordereaux-ordonnances/', BordereauxOrdonnances.as_view(), name='bordereaux-ordonnances'),
    path('bordereauordonnance/', BordereauxOrdonnancesView.as_view(), name='bordereaux_ordonnances'),
    path('bordereaux_ordonnances_datatable/', views.bordereaux_ordonnances_datatable, name='bordereaux_ordonnances_datatable'),
    
    path('bordereaux-payes/', BordereauxPayesView.as_view(), name='bordereaux_payes_compta'),
    path('bordereaux_payes_datatable/', views.bordereaux_payes_datatable, name='bordereaux_payes_datatable'),

    path('fonds-de-roulements/', InitialisationFondRoulementView.as_view(), name='initialisation_fonds_de_roulements'),
    path('add_mise_en_initialiser_fdr_garant/',views.add_mise_en_initialiser_fdr_garant, name='add_mise_en_initialiser_fdr_garant'),
    path("edition-caution-compagnie/<int:compagnie_id>/", views.edition_caution_compagnie, name='edition_caution_compagnie'),
    path('get-fdr-data/', views.get_fdr_data, name='get_fdr_data'),
    path('fonds-de-roulements/init/', views.init_fonds_de_roulements, name='init_fonds_de_roulements'), # SCRIPT

    path('refacturation-assureur/', RefacturationAssureurView.as_view(), name='refacturation_assureur'),
    path("generation_facture_assureur/", views.generate_facture_assureur_datatable, name='generation_facture_assureur_datatable'),
    path("submit_generate_facture_assureur", views.submit_generate_facture_assureur, name='submit_generate_facture_assureur'),
    path('get-refacturation-assureur-data/', views.get_refacturation_assureur_data, name='get_refacturation_assureur_data'),
    path('get_garant_selectionne_data/<int:compagnie_id>/', views.get_garant_selectionne_data, name='get_garant_selectionne_data'),

    path('factures-compagnies/', FactureCompagnieView.as_view(), name='factures_compagnies'),
    path('factures-compagnies/datatable/', views.facture_compagnie_datatable, name='facture_compagnie_datatable'),
    path('fetch_factures', views.fetch_factures, name='fetch_factures'),
    path('factures-compagnies/details/<int:facture_id>/', DetailFactureGarant.as_view(), name='detail_facture_garant'),
    path('factures-compagnies/<int:facture_id>/regenerate', views.regenerateFactureGarantpdf, name='regenerer_facture_compagnie'),
    # path('factures-compagnies/details/<int:facture_id>/', DetailFactureGarant.as_view(), name='detail_facture_garant'),
    path("factures-compagnies/reglement_facture_simple/<int:facture_id>/", views.reglement_facture_garant_simple, name='reglement_facture_simple'),
    path("factures-compagnies/annulation_facture_simple/<int:facture_id>/", views.annulation_facture_simple, name='annulation_facture_simple'),

    path('obtenir_montant_facture/', views.obtenir_montant_sinistre, name='obtenir_montant_sinistre'),

    path('add_mise_en_reglement_factures_garant/',views.add_mise_en_reglement_factures_garant, name='add_mise_en_reglement_factures_garant'),

    path('suivi-tresorerie/', SuiviTresorerie.as_view(), name='suivi_tro'),

    path('bordereau_ordonnancement/<int:bordereau_id>/', DetailBordereauOrdonnancementView.as_view(), name='details_bordereau_ordonnancement'),

    path('update_montant_accepte_total/', views.update_montant_accepte_total, name='update_montant_accepte_total'),

    path('add_mise_en_reglement_ordonnancement',views.add_mise_en_reglement_ordonnancement, name='add_mise_en_reglement_ordonnancement'),
    path('generer_bordereau_reglement_ordonnancement_pdf/<int:operation_id>', views.generer_bordereau_reglement_ordonnancement_pdf, name='generer_bordereau_reglement_ordonnancement_pdf'),

    path('add_mise_en_reglement_ordonnancement_par_garant',views.add_mise_en_reglement_ordonnancement_par_garant, name='add_mise_en_reglement_ordonnancement_par_garant'),
    path('generer_bordereau_reglement_ordonnancement_par_garant_pdf/<int:operation_id>', views.generer_bordereau_reglement_ordonnancement_par_garant_pdf, name='generer_bordereau_reglement_ordonnancement_par_garant_pdf'),

    path("bordereau-ordonnancement-pdf/", views.bordereau_ordonnancement_pdf, name='pdf_bordereau_ordonnancement'),

    path('regenerate_bordereau_pdf/<int:paiement_comptable_id>/', views.regenerate_bordereau_pdf, name='regenerate_bordereau_pdf'),

    path('paiements-realises/', PaiementsRealises.as_view(), name='paiements-realises'),
    path('paiements_comptables_datatable/', views.paiements_comptables_datatable, name='paiements_comptables_datatable'),
    path('export_paiements_comptables/', views.export_paiements_comptables, name='export_paiements_comptables'),

    path('edition-lettre-cheque/', EditionLettreCheque.as_view(), name='edition-lettre-cheque'),
    path('edition_lettre_cheque_datatable/', views.edition_lettre_cheque_datatable, name='edition_lettre_cheque_datatable'),
    path("submit_edition_lettre_cheque", views.submit_edition_lettre_cheque, name='submit_edition_lettre_cheque'),
    path("edition-lettre-cheque-pdf", views.edition_lettre_cheque_pdf, name='edition_lettre_cheque_pdf'),

    path('create_periode_comptable/', create_periode_comptable, name='create_periode_comptable'),

    path('suivi_treso/', SuiviTresorerie.as_view(), name='suivi-tresorerie'),
    path('suivi-treso-datatable/', views.suivi_treso_datatable, name='suivi_treso_datatable'),
    path('suivi_treso/<int:compagnie_id>/', DetailTresorerie.as_view(), name='detail_suivi_treso'),
    # path('suivi_treso/<int:compagnie_id>/stats', views.get_camembert_data_detail_par_garant, name='get_camembert_data_detail_par_garant'),
    path('suivi_treso/datatable', views.datatable_facture_compagnie_specifique, name='datatable_facture_compagnie_specifique'),

    path('reglements_compagnies/', ReversesementCompagniesView.as_view(), name='reglements_compagnies'),
    path('encaissement_commissions/', EncaissementCommissionsView.as_view(), name='encaissement_commissions'),
    path('encaissement_commissions_court_gest/<str:type>', EncaissementCommissionsCourtGestView.as_view(), name='encaissement_commissions_court_gest'),
    path('encaissement_commissions_court_gest/courtage', EncaissementCommissionsCourtGestView.as_view(), name='encaissement_commissions_court_gest_courtage'),
    path('encaissement_commissions_court_gest/gestion', EncaissementCommissionsCourtGestView.as_view(), name='encaissement_commissions_court_gest_gestion'),
    path('reglements_apporteurs/', ReglementApporteursView.as_view(), name='reglements_apporteurs'),
    path('ajax_reglements_a_reverser_compagnie/<int:compagnie_id>', views.ajax_reglements_a_reverser_compagnie, name='ajax_reglements_a_reverser_compagnie'),
    path('ajax_reglements_reverses/<int:compagnie_id>', views.ajax_reglements_reverses, name='ajax_reglements_reverses'),
    path('ajax_reglements_reverses_court_gest/<int:compagnie_id>/<str:type>', views.ajax_reglements_reverses_court_gest, name='ajax_reglements_reverses_court_gest'),
    path('add_reglement_compagnie',views.add_reglement_compagnie, name='add_reglement_compagnie'),
    path('add_encaissement_commission',views.add_encaissement_commission, name='add_encaissement_commission'),
    path('add_encaissement_com_court_gest/<str:type>',views.add_encaissement_com_court_gest, name='add_encaissement_com_court_gest'),

    path('generer_bordereau_reglement_compagnie_pdf/<int:operation_id>', views.generer_bordereau_reglement_compagnie_pdf, name='generer_bordereau_reglement_compagnie_pdf'),
    
    path('generer_bordereau_encaissement_compagnie_pdf/<int:operation_id>', views.generer_bordereau_encaissement_compagnie_pdf, name='generer_bordereau_encaissement_compagnie_pdf'),

    path('execution-requete-excel-compta/', views.ExecutionRequeteExcelComptaView.as_view(), name='execution_requete_excel_compta'),

    #
    path('export_bordereaux_ordonnances/', export_bordereaux_ordonnances, name='export_bordereaux_ordonnances'),
    path('export_bordereaux_ordonnances_paye/', export_bordereaux_ordonnances_paye, name='export_bordereaux_ordonnances_paye'),



]
