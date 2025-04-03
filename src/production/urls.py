
from django.urls import path

from . import views
from .views import ClientsView, ExcelFileView, FormulesUniversellesView, FormulesView, \
    DetailsClientView, PoliceClientView, ContactClientView, FilialeClientView, AcompteClientView, GEDClientView, QuittancesClientView, \
    PoliceGedView, PoliceAvenantsView, PoliceQuittancesView, \
    PoliceSinistresView, AnnulerQuittanceView, CourrierView, PolicesEncoursView, PolicesArrivantEcheanceView, PolicesNonRenouvelleesResilieesView, \
    DetailsSinistreView, SinistreGedView, SinistreAvenantsView

urlpatterns = [
    path('apporteurs/ajax_apporteurs', views.ajax_apporteurs, name='ajax_apporteurs'),
    path("compagnie/ajax_infos_compagnie/<int:compagnie_id>/<int:produit_id>/", views.ajax_infos_compagnie, name='ajax_infos_compagnie'),
    path("ajax_produits/<int:branche_id>/", views.ajax_produits, name='ajax_produits'),
    path("modification_ajax_produits/<int:branche_id>/", views.modification_ajax_produits, name='modification_ajax_produits'),
    path("actes_by_rubrique/<int:rubrique_id>/", views.actes_by_rubrique, name='actes_by_rubrique'),
    path("sous_rubriques_by_rubrique/<int:rubrique_id>/", views.sous_rubriques_by_rubrique, name='sous_rubriques_by_rubrique'),
    path("regroupements_actes_by_rubrique/<int:rubrique_id>/", views.regroupements_actes_by_rubrique, name='regroupements_actes_by_rubrique'),
    path("sous_regroupements_actes_by_rubrique/<int:rubrique_id>/", views.sous_regroupements_actes_by_rubrique, name='sous_regroupements_actes_by_rubrique'),
    path("actes_by_regroupement_acte/<int:regroupement_acte_id>/", views.actes_by_regroupement_acte, name='actes_by_regroupement_acte'),
    path("formules_by_police/<int:police_id>/", views.formules_by_police, name='formules_by_police'),
    path("polices_restantes/<int:police_id>/", views.polices_restantes, name='polices_restantes'),

    path('client/', ClientsView.as_view(), name='clients'),
    path('clients_datatable/', views.clients_datatable, name='clients_datatable'),
    path("client/add_client", views.add_client, name='add_client'),
    path('client/<int:client_id>/modifier', views.modifier_client, name='modifier_client'),
    path('client/<int:client_id>', DetailsClientView.as_view(), name='client_details'),
    path("client/delete", views.supprimer_client, name='supprimer_client'),

    path("client/<int:client_id>/liste-police", PoliceClientView.as_view(), name='client_polices'),
    path("client/<int:client_id>/add_police", views.add_police, name='add_police'),
    path('import-excel-aliments/', views.import_excel_aliments, name='import_excel_aliments'),
    path('import-formulaire-aliments/', views.import_formulaire_aliments, name='import_formulaire_aliments'),
    path('get_garanties_by_formule/', views.get_garanties_by_formule, name='get_garanties_by_formule'),
    path('get_garanties_by_police/', views.get_garanties_by_police, name='get_garanties_by_police'),
    path('get_garanties_by_formule_modification/', views.get_garanties_by_formule_modification, name='get_garanties_by_formule_modification'),
    path('get_aliments_session/', views.get_aliments_session, name='get_aliments_session'),
    path('supprimer_aliment/<int:index>/', views.supprimer_aliment, name='supprimer_aliment'),
    path('supprimer_aliment_modification/', views.supprimer_aliment_modification, name='supprimer_aliment_modification'),
    path('clear_session/', views.clear_session, name='clear_session'),
    path('get_compagnies/', views.get_compagnies, name='get_compagnies'),
    path('branche/<int:branche_id>/produits',views.produits_by_branche, name='branche_produits'),
    path('produit/<int:produit_id>/sous-menu',views.produit_sous_menu, name='produit_sous_menu'),

    path("client/<int:client_id>/liste-contact", ContactClientView.as_view(), name='client_contacts'),
    path("client/<int:client_id>/contact/add", views.add_contact, name='client_add_contact'),
    path("client/contact/<int:contact_id>/modifier", views.modifier_contact, name='modifier_contact'),
    path("client/contact/<int:contact_id>/delete", views.supprimer_contact, name='supprimer_contact'),

    path("client/<int:client_id>/liste-filiale", FilialeClientView.as_view(), name='client_filiales'),
    path("client/<int:client_id>/filiale/add", views.add_filiale, name='client_add_filiale'),
    path("client/filiale/<int:filiale_id>/modifier", views.modifier_filiale, name='modifier_filiale'),
    path("client/filiale/<int:filiale_id>/delete", views.supprimer_filiale, name='supprimer_filiale'),

    path("client/<int:client_id>/liste-documents", GEDClientView.as_view(), name='client_documents'),
    path("client/<int:client_id>/document/add", views.add_document, name='client_add_document'),
    path("document/<int:document_id>/modifier", views.modifier_document, name='modifier_document'),
    path("document/<int:document_id>/delete", views.supprimer_document, name='supprimer_document'),

    path("client/<int:client_id>/liste-acompte", AcompteClientView.as_view(), name='client_acomptes'),
    path("client/<int:client_id>/acompte/add", views.add_acompte, name='client_add_acompte'),
    path("acompte/<int:acompte_id>/modifier", views.modifier_acompte, name='modifier_acompte'),
    path("acompte/<int:acompte_id>/delete", views.supprimer_acompte, name='supprimer_acompte'),
    path('mouvement/<int:mouvement_id>/motifs',views.motifs_by_mouvement, name='mouvement_motifs'),

    path("client/<int:client_id>/quittance", QuittancesClientView.as_view(), name='client_quittances'),
    path("client/<int:client_id>/<int:police_id>/exporter-quittance", views.exporter_quittance, name='exporter_quittance'),
    path('police/generer_exportation_quittance/<int:typefichier_id>', views.generer_exportation_quittance, name='generer_exportation_quittance'),

    path('client/<int:client_id>/changement_compagnie',views.changement_compagnie, name='changement_compagnie'),

    path('polices-en-cours/', PolicesEncoursView.as_view(), name='polices_en_cours'),
    path('polices_en_cours_datatable/', views.polices_en_cours_datatable, name='polices_en_cours_datatable'),
    path('polices-a-echeance-dans-90-jours/', PolicesArrivantEcheanceView.as_view(), name='polices_arrivant_echeance'),
    path('polices_arrivant_echeance_datatable/', views.polices_arrivant_echeance_datatable, name='polices_arrivant_echeance_datatable'),

    path('polices-non-renouvellees-resiliees/', PolicesNonRenouvelleesResilieesView.as_view(), name='polices_non_renouvellees_resiliees'),
    path('polices_non_resiliees_renouvellees_datatable/', views.polices_non_renouvellees_resiliees_datatable, name='polices_non_renouvellees_resiliees_datatable'),

    path('police/<int:police_id>/details', views.DetailsPoliceView.as_view(), name='police.details'),
    path('police/<int:police_id>/<int:historique_police_id>/historique-details', views.DetailsHistoriquePoliceView.as_view(), name='police.historique.details'),
    path('police/<int:police_id>/quittances', PoliceQuittancesView.as_view(), name='police_quittances'),
    path('police/<int:police_id>/add_quittance', views.add_quittance, name='add_quittance'),
    path('quittance/<int:quittance_id>/police/<int:police_id>/add_document', views.add_document_to_quittance, name='add_document_to_quittance'),
    #
    path('police/<int:police_id>/add_reglement', views.add_reglement, name='add_reglement'),
    path('police/<int:police_id>/add_lettrage', views.add_lettrage, name='add_lettrage'),
    path('quittance/<int:quittance_id>', views.details_quittance, name='details_quittance'),
    path('quittance/<int:quittance_id>/imprimer-recu-reglement/<int:reglement_id>', views.imprimer_recu_reglement, name='imprimer_recu_reglement'),
    path('police/<int:police_id>/mouvements', PoliceAvenantsView.as_view(), name='police_avenants'),
    path('police/<int:police_id>/add_avenant', views.add_avenant, name='add_avenant'),
    path('police/<int:police_id>/ged', PoliceGedView.as_view(), name='police_ged'),
    path('police/<int:police_id>/add_document', views.police_add_document, name='police_add_document'),

    path('police/<int:police_id>/export_sinistres_police', views.export_sinistres_police, name='export_sinistres_police'),
    #
    path('police/get_formules/<int:police_id>/', views.get_formules, name='get_formules'),
    
    path('police/<int:police_id>/vehicules', views.police_vehicules, name='police_vehicules'),
    path('police/<int:police_id>/add_vehicule', views.add_vehicule, name='add_vehicule'),
    path('police/<int:police_id>/update_vehicule/<int:aliment_police_id>', views.update_vehicule, name='update_vehicule'),
    path('police/<int:police_id>/details_vehicule/<int:aliment_police_id>', views.details_vehicule, name='details_vehicule'),
    path('police/<int:vehicule_id>/details_historique_vehicule/<int:historique_id>', views.details_historique_vehicule, name='details_historique_vehicule'),
    path('police/<int:police_id>/import_vehicules', views.import_vehicules, name='import_vehicules'),
    path("police/supprimer_vehicule/<int:vehicule_id>", views.supprimer_vehicule, name='supprimer_vehicule'),
    path('police/<int:police_id>/marchandises', views.police_marchandises, name='police_marchandises'),
    path('police/<int:police_id>/add_marchandise', views.add_marchandise, name='add_marchandise'),
    path('police/<int:police_id>/details_marchandise/<int:marchandise_id>', views.details_marchandise, name='details_marchandise'),
    path('police/<int:police_id>/update_marchandise/<int:marchandise_id>', views.update_marchandise, name='update_marchandise'),
    path("police/<int:police_id>/supprimer_marchandise/<int:marchandise_id>", views.supprimer_marchandise, name='supprimer_marchandise'),

    path('police/<int:police_id>/autres-risques', views.police_autres_risques, name='police_autres_risques'),
    path('police/<int:police_id>/details_autrerisque/<int:autre_risque_id>', views.details_autrerisque,name='details_autrerisque'),
    path('police/<int:police_id>/add_autrerisque', views.add_autrerisque, name='add_autrerisque'),
    path('police/<int:police_id>/update_autrerisque/<int:autre_risque_id>', views.update_autrerisque, name='update_autrerisque'),
    path("police/<int:police_id>/supprimer_autresrisque/<int:autresrisque_id>", views.supprimer_autresrisque, name='supprimer_autresrisque'),

    path('police/<int:police_id>/modifier', views.modifier_police, name='modifier_police'),
    path('police/<int:police_id>/sinistres', PoliceSinistresView.as_view(), name='police_sinistres'),
    path('police/<int:police_id>/save-sinistre', views.police_save_sinistre, name='police_save_sinistre'),
    path('police/<int:police_id>/sinistres_datatable', views.police_sinistres_datatable, name='police_sinistres_datatable'),
    path('police/information-vehicule/<int:vehicule_id>', views.information_vehicule, name='information_vehicule'),
    path('police/information-marchandise/<int:marchandise_id>', views.information_marchandise, name='information_marchandise'),

    path('add_intervenant_session/', views.add_intervenant_session, name='add_intervenant_session'),
    path('vider_intervenants_garanties/', views.vider_intervenants_garanties_session, name='vider_intervenants_garanties_session'),
    path('get_intervenants_session/', views.get_intervenants_session, name='get_intervenants_session'),
    path('get_intervenants_session_sinistre/', views.get_intervenants_session_sinistre, name='get_intervenants_session_sinistre'),
    path('delete_intervenant_session/', views.delete_intervenant_session, name='delete_intervenant_session'),
    path('delete_intervenant_session_sinistre/', views.delete_intervenant_session_sinistre, name='delete_intervenant_session_sinistre'),

    path('add_intervenant_session_sinistre/', views.add_intervenant_session_sinistre, name='add_intervenant_session_sinistre'),

    path('charger_garanties_circonstance_session_sinistre/', views.charger_garanties_circonstance_session_sinistre, name='charger_garanties_circonstance_session_sinistre'),
    path('recuperer_garantie_circonstance/', views.recuperer_garantie_circonstance, name='recuperer_garantie_circonstance'),
    path('recuperer_garantie_circonstance_sinistre/', views.recuperer_garantie_circonstance_sinistre, name='recuperer_garantie_circonstance_sinistre'),
    path('vider_garanties_sinistre/', views.vider_garanties_sinistre, name='vider_garanties_sinistre'),

    path("enregistrer_garanties_sinistre/", views.enregistrer_garanties_sinistre, name="enregistrer_garanties_sinistre"),
    path("enregistrer_garanties_circonstance_sinistre/", views.enregistrer_garanties_circonstance_sinistre, name="enregistrer_garanties_circonstance_sinistre"),
    path("recuperer_garanties_sinistre/", views.recuperer_garanties_sinistre, name="recuperer_garanties_sinistre"),
    path('afficher_provision_sinistre/', views.afficher_provision_sinistre, name='afficher_provision_sinistre'),
    path("recuperer_garanties_circonstance_sinistre/", views.recuperer_garanties_circonstance_sinistre, name="recuperer_garanties_circonstance_sinistre"),
    path('afficher_provision_circonstance_sinistre/', views.afficher_provision_circonstance_sinistre, name='afficher_provision_circonstance_sinistre'),
    path('enregistrer_montant_garantie_sinistre/', views.enregistrer_montant_garantie_sinistre, name='enregistrer_montant_garantie_sinistre'),
    path('enregistrer_montant_garantie_circonstance_sinistre/', views.enregistrer_montant_garantie_circonstance_sinistre, name='enregistrer_montant_garantie_circonstance_sinistre'),
    path('delete_garantie_session/', views.delete_garantie_session, name='delete_garantie_session'),

    path('police/<int:police_id>/courriers', CourrierView.as_view(), name='police_courrier'),
    path('police/<int:police_id>/courrier/<int:courrier_id>/pdf/', views.generer_courrier, name='generer_pdf'),
    path('police/<int:police_id>/courrier/<int:courrier_id>/quittance/<int:quittance_id>/pdf/', views.generer_courrier, name='generer_pdf'),
    path('police/<int:police_id>/courrier/<int:courrier_id>/word/', views.generer_word, name='generer_word'),
    path('police/<int:police_id>/courrier/<int:courrier_id>/quittance/<int:quittance_id>/word/', views.generer_word, name='generer_word'),

    # path('generate-word/', generate_word, name='generate_word'),

    path('sinistre/<int:sinistre_id>/details', views.DetailsSinistreView.as_view(), name='sinistre.details'),
    path('sinistre/<int:sinistre_id>/ged', SinistreGedView.as_view(), name='sinistre_ged'),
    path('sinistre/<int:sinistre_id>/add_document', views.sinistre_add_document, name='sinistre_add_document'),
    path('sinistre/<int:sinistre_id>/mouvements', SinistreAvenantsView.as_view(), name='sinistre_avenants'),
    path('sinistre/<int:sinistre_id>/add_sinistre_avenant', views.add_sinistre_avenant, name='add_sinistre_avenant'),
    path('sinistre/<int:sinistre_id>/modifier', views.modifier_sinistre, name='modifier_sinistre'),

    path('formules_universelles', FormulesUniversellesView.as_view(), name='formules_universelles'),
    path('police/<int:police_id>/formules', FormulesView.as_view(), name='police_formules'),
    path('police/add_formule_universelle', views.add_formule_universelle, name='add_formule_universelle'),
    path('police/<int:police_id>/add_formule', views.add_formule, name='add_formule'),
    path('formule/<int:formule_id>/modifier', views.modifier_formule, name='modifier_formule'),
    path('formule/<int:formule_id>/update_formule', views.modifier_formule, name='update_formule'),


    path('download/<str:filename>', views.download, name='download'),

    # test panda excel
    path('text-excel-file/', ExcelFileView.as_view()),

    #
    path('annuler_quittance/', AnnulerQuittanceView.as_view(), name='annuler_quittance'),
    path('add_annuler_quittance/', views.add_annuler_quittance, name='add_annuler_quittance'),
]



