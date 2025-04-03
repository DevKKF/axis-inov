
from django.urls import path

from comptabilite.views import BordereauxOrdonnancesView, BordereauxPayesView, detail_bordereau_ordonnancement_datatable
from . import views
from .views import AnnulerFactureGestionnairesView, AnnulerSinistreGestionnairesView, DossierSinistresView, \
    DetailsDossierSinistreView, DossierSinistresTraitesView, \
    FacturesPrestataireView, RemboursementAppliMobile, DossiersSinistresPhysiquesGestionnairesView, \
    FacturesPrestataireTraiteView, GenerationBrValidationView, GenerationBrOrdonnancementView, \
    DetailBordereauOrdonnancementView, SaisieSinistreView, AnnulerBordereauOrdonnancementView, \
    export_sinistres_ordonnancement, EntentesPrealablesView

urlpatterns = [

    path('dossiersinistre/', DossierSinistresView.as_view(), name='dossiersinistre'),
    path('dossiersinistre_datatable/', views.dossiersinistre_datatable, name='dossiersinistre_datatable'),

    path('ententes_prealables/', EntentesPrealablesView.as_view(), name='ententes_prealables'),
    path('ententes_prealables_datatable/', views.dossiersinistre_datatable, name='ententes_prealables_datatable'),

    path('dossierstraites/', DossierSinistresTraitesView.as_view(), name='dossierstraites'),
    path('dossiersinistre_traites_datatable/', views.dossiersinistre_traites_datatable, name='dossiersinistre_traites_datatable'),

    path('popup_choose_prestataire/', views.popup_choose_prestataire, name='popup_choose_prestataire'),
    #
    path('search_benef_by_name_datatable/', views.search_benef_by_name_datatable, name='search_benef_by_name_datatable'),










    path('saisie_sinistre/', SaisieSinistreView.as_view(), name='saisie_sinistre'),
    path('recherche_client_police/', views.recherche_client_police, name='recherche_client_police'),
    path('recuperer_information_police/', views.recuperer_information_police, name='recuperer_information_police'),
    path('recuperer_intervenant_police/', views.recuperer_intervenant_police, name='recuperer_intervenant_police'),
    path('get_intervenants_session/', views.get_intervenants_session, name='get_intervenants_session'),
















    path('saisie_prestation/<int:prestataire_id>', SaisieSinistreView.as_view(), name='saisie_prestation'),
    path('popup_add_medicament_session_gestionnaire/<int:acte_id>/<int:aliment_id>/<int:prestataire_id>/<int:prescripteur_id>', views.popup_add_medicament_session_gestionnaire, name='popup_add_medicament_session_gestionnaire'),
    path('remove_medicament_session_gestionnaire/<int:medicament_id>', views.remove_medicament_session_gestionnaire, name='remove_medicament_session_gestionnaire'),

    path('popup_add_medicament_gestionnaire/<int:dossier_sinistre_id>/', views.popup_add_medicament_gestionnaire, name='popup_add_medicament_gestionnaire'),
    path('add_medicament_gestionnaire_todossiersinistre/<int:dossier_sinistre_id>/', views.add_medicament_gestionnaire_todossiersinistre, name='add_medicament_gestionnaire_todossiersinistre'),
    path('remove_medicament_gestionnaire/<int:medicament_id>/', views.remove_medicament_gestionnaire, name='remove_medicament_gestionnaire'),
    path('add_sinistre_medicament_gestionnaire/<int:dossier_sinistre_id>/', views.add_sinistre_medicament_gestionnaire, name='add_sinistre_medicament_gestionnaire'),

    path('liste_prestations/', DossiersSinistresPhysiquesGestionnairesView.as_view(), name='liste_prestations'),
    path('dossiersinistre_physique_gestionnaire_datatable/', views.dossiersinistre_physique_gestionnaire_datatable, name='dossiersinistre_physique_gestionnaire_datatable'),
    path('annuler_sinistre/', AnnulerSinistreGestionnairesView.as_view(), name='annuler_sinistre'),
    path('change_dossier_closing_status/<int:dossier_sinistre_id>', views.change_dossier_closing_status, name='change_dossier_closing_status'),
    path('annuler_facture/', AnnulerFactureGestionnairesView.as_view(), name='annuler_facture'),
    path('annuler_bordereau_ordonnancement/', AnnulerBordereauOrdonnancementView.as_view(), name='annuler_bordereau_ordonnancement'),
    path('dossier_sinistre/<int:sinistre_id>', DetailsDossierSinistreView.as_view(), name='details_dossier_sinistre'),
    path('dossier_sinistre/<str:dossier_sinistre_id>/add_sinistre_medicament', views.add_sinistre_medicament, name='add_sinistre_medicament'),
    path('dossier_sinistre_close/<str:dossier_sinistre_id>', views.close_dossier_medication, name='close_dossier_medication'),
    path('pharmacie_details/<int:aliment_id>', views.pharmacie_details, name='pharmacie_details'),
    path('sinistre/<int:sinistre_id>', views.popup_details_sinistre, name='popup_details_sinistre'),
    path('seance/<int:sinistre_id>', views.popup_seance_done, name='popup_seance_done'),
    path('medicament/<int:sinistre_id>', views.popup_modifier_sinistre_medicament, name='popup_modifier_sinistre_medicament'),
    path('update-medicament/<int:sinistre_id>', views.update_medicament_sinistre, name='update_medicament_sinistre'),
    path('delete_sinistre_medicament/<int:sinistre_id>', views.delete_sinistre_medicament, name='delete_sinistre_medicament'),
    path('search_assure', views.search_assure, name='search_assure'),
    path('search_assure_bygestionnaire/<int:prestataire_id>', views.search_assure_bygestionnaire, name='search_assure_bygestionnaire'),
    path('search_assure_pharmacie', views.search_assure_pharmacie, name='search_assure_pharmacie'),
    path('statuer_acte/', views.statuer_acte, name='statuer_acte'),
    path('approuver_liste_acte', views.approuver_liste_acte, name='approuver_liste_acte'),
    path('rejeter_liste_acte/', views.rejeter_liste_acte, name='rejeter_liste_acte'),
    path('update_date_sortie_sinistre/', views.update_date_sortie_sinistre, name='update_date_sortie_sinistre'),
    path('update_date_sortie_nb_jour/', views.update_date_sortie_nb_jour, name='update_date_sortie_nb_jour'),
    path('update_nombre_accorde_sinistre/', views.update_nombre_accorde_sinistre, name='update_nombre_accorde_sinistre'),

    path('get_infos_selected_actes', views.get_infos_selected_actes, name='get_infos_selected_actes'),
    path('get_infos_selected_actes_consultation_ls', views.get_infos_selected_actes_consultation_ls, name='get_infos_selected_actes_consultation_ls'),
    path('get_infos_selected_actes_hospitalisation', views.get_infos_selected_actes_hospitalisation, name='get_infos_selected_actes_hospitalisation'),
    path('get_infos_selected_actes_soins_ambulatoires', views.get_infos_selected_actes_soins_ambulatoires, name='get_infos_selected_actes_soins_ambulatoires'),
    path('get_infos_selected_actes_gestionnaire', views.get_infos_selected_actes_gestionnaire, name='get_infos_selected_actes_gestionnaire'),
    path('get_infos_selected_actes_optiques', views.get_infos_selected_actes_optiques, name='get_infos_selected_actes_optiques'),
    path('get_infos_selected_actes_optiques_search', views.get_infos_selected_actes_optiques_search, name='get_infos_selected_actes_optiques_search'),

    path('add_sinistre', views.add_sinistre, name='add_sinistre'),#les autres
    path('add_sinistre_optique', views.add_sinistre_optique, name='add_sinistre_optique'),
    path('add_sinistre_soins_ambulatoire', views.add_sinistre_soins_ambulatoire, name='add_sinistre_soins_ambulatoire'),
    path('add_sinistre_gestionnaire', views.add_sinistre_gestionnaire, name='add_sinistre_gestionnaire'),
    path('add_medicament_session_gestionnaire', views.add_medicament_session_gestionnaire, name='add_medicament_session_gestionnaire'),

    path('update_sinistre_hospitalisation/<int:dossier_sinistre_id>', views.update_sinistre_hospitalisation, name='update_sinistre_hospitalisation'),
    path('demande_prorogation/<int:sinistre_id>', views.demande_prorogation, name='demande_prorogation'),
    path('approuver_prorogation', views.approuver_prorogation, name='approuver_prorogation'),
    path('rejeter_prorogation', views.rejeter_prorogation, name='rejeter_prorogation'),

    path('sinistre/pdf/<int:id>', views.render_pdf_view, name='render_pdf_view'),
    path('sinistre/pdf/<int:id>/general', views.render_pdf_view_general, name='render_pdf_view_general'),
    ##
    path('sinistre/pdf/<int:id>/pharmacie', views.render_pdf_view_pharmacie, name='render_pdf_view_pharmacie'),
    ##
    path('dossier_sinistre/<int:dossier_sinistre_id>/add_document',views.dossier_sinistre_add_document,name='dossier_sinistre_add_document'),
    path("dossier_sinistre_document/delete", views.supprimer_document, name='supprimer_document'),

    path("generation_bordereau", views.GenerateFactureView.as_view(), name='generation_bordereau'),
    path("generation_bordereau_datatable", views.generate_facture_datatable, name='generation_bordereau_datatable'),
    path("search_prestataires_generate_facture_by_name_datatable", views.search_prestataires_generate_facture_by_name_datatable, name='search_prestataires_generate_facture_by_name_datatable'),
    path("search_assures_generate_facture_by_name_datatable", views.search_assures_generate_facture_by_name_datatable, name='search_assures_generate_facture_by_name_datatable'),
    path("search_adherents_generate_facture_by_name_datatable", views.search_adherents_generate_facture_by_name_datatable,
         name='search_adherents_generate_facture_by_name_datatable'),

    path('update_add_affection/<int:dossier_sinistre_id>', views.update_add_affection, name='update_add_affection'),

    path('factures_prestataires/', FacturesPrestataireView.as_view(), name='facturesprestataires'),
    path('factures_prestataires_datatable/', views.factures_prestataire_datatable, name='facturesprestataires_datatable'),

    path('factures_prestataires_traitees/', FacturesPrestataireTraiteView.as_view(), name='facturesprestataires_traite'),
    path('factures_prestataires_traitees_datatable/', views.factures_prestataires_traitees_datatable, name='facturesprestataires_traitees_datatable'),


    path('bordereaux_ordonnances/', BordereauxOrdonnancesView.as_view(), name='bordereaux_ordonnances'),
    path('bordereaux_payes/', BordereauxPayesView.as_view(), name='bordereaux_payes'), #a modifier
    #path('bordereau_ordonnancement_paye_datatable/', views.bordereau_ordonnancement_paye_datatable, name='bordereau_ordonnancement_paye_datatable'),
    #path('bordereau_ordonnancement_datatable/', views.bordereau_ordonnancement_datatable, name='bordereau_ordonnancement_datatable'),
    path('bordereau_ordonnancement/<int:bordereau_id>', DetailBordereauOrdonnancementView.as_view(), name='bordereau_ordonnancement_detail'),
    path('bordereau_ordonnancement_datatable/<int:bordereau_id>', detail_bordereau_ordonnancement_datatable, name='bordereau_ordonnancement_detail_datatable'),

    path('generation-br-validation/', GenerationBrValidationView.as_view(), name='generation_br_validation'),
    path('generation-br-validation-datatable/', views.generation_br_validation_datatable, name='generation_br_validation_datatable'),
    path("submit-generation-br-validation", views.submit_generation_br_validation, name='submit_generation_br_validation'),

    path('generation-br-ordonnancement/', GenerationBrOrdonnancementView.as_view(), name='generation_br_ordonnancement'),
    path('generation-br-ordonnancement-datatable/', views.generation_br_ordonnancement_datatable, name='generation_br_ordonnancement_datatable'),
    path('generation-br-ordonnancement/<int:sinistre_id>', views.popup_rejet_ordonnancement_sinistre, name='popup_rejet_ordonnancement_sinistre'),
    path("submit-generation-br-ordonnancement", views.submit_generation_br_ordonnancement, name='submit_generation_br_ordonnancement'),
    path("get-facture-br-ordonnancement", views.get_facture_br_ordonnancement,
         name='get_facture_br_ordonnancement'),
    path("get-periode-br-ordonnancement", views.get_periode_br_ordonnancement,
         name='get_periode_br_ordonnancement'),

    path('regenerer_borderau_ordonnancement_pdf/<int:bordereau_ordonnancement_id>', views.regenerer_borderau_ordonnancement_pdf, name='regenerer_borderau_ordonnancement_pdf'),
    path('regenerer_borderau_ordonnancement_rd_pdf/<int:bordereau_ordonnancement_id>', views.regenerer_borderau_ordonnancement_rd_pdf, name='regenerer_borderau_ordonnancement_rd_pdf'),

    path('remboursement_applimobile/', RemboursementAppliMobile.as_view(), name='remboursementapplimobile'),
    path('remboursementsvalides/', RemboursementAppliMobile.as_view(), name='remboursementsvalides'),

    path('accepter_remboursement/<int:sinistre_id>', views.accepter_remboursement, name='accepter_remboursement'),
    path('refuser_remboursement/<int:sinistre_id>', views.refuser_remboursement, name='refuser_remboursement'),
    path('refuser_remboursement_ordonnancement/<int:sinistre_id>', views.refuser_remboursement_ordonnancement, name='refuser_remboursement_ordonnancement'),
    path('annuler_remboursement_ordonnancement/<int:sinistre_id>', views.annuler_remboursement_ordonnancement, name='annuler_remboursement_ordonnancement'),

    path('traiter_liste_remboursement', views.traiter_liste_remboursement, name='traiter_liste_remboursement'),
    path('refuser_liste_remboursement', views.refuser_liste_remboursement, name='refuser_liste_remboursement'),
    path('valider_facture_remboursement/<int:facture_prestataire_id>', views.valider_facture_remboursement, name='valider_facture_remboursement'),

    path('execution-requete-excel/', views.ExecutionRequeteExcelView.as_view(), name='execution_requete_excel'),
    path('verif-background-requete-excel/', views.verif_background_requete_excel, name='verif_background_execution_requete_excel'),
    #
    path('ordonnancement/', export_sinistres_ordonnancement, name='export_sinistres_ordonnancement'),

]


