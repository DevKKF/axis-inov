
from django.urls import path

from . import views
from .views import SaisieSinistreView, DossierSinistresView, DossierSinistresTraitesView, DossiersSinistresPhysiquesGestionnairesView, \
    DetailsDossierSinistreView, AnnulerSinistreGestionnairesView, GEDDossierSinistreView, IntervenantDossierSinistreView, MouvementDossierSinistreView, \
    DetailMouvementDossierSinistreView


urlpatterns = [
    path('dossiersinistre/', DossierSinistresView.as_view(), name='dossiersinistre'),
    path('dossier_sinistre_datatable/', views.dossier_sinistre_datatable, name='dossier_sinistre_datatable'),

    path('dossiers-traites/', DossierSinistresTraitesView.as_view(), name='dossierstraites'),
    path('dossiersinistre_traites_datatable/', views.dossiersinistre_traites_datatable, name='dossiersinistre_traites_datatable'),

    path('dossier_sinistre/<int:sinistre_id>', DetailsDossierSinistreView.as_view(), name='details_dossier_sinistre'),
    path('dossier_sinistre/<int:sinistre_id>/ged', GEDDossierSinistreView.as_view(), name='ged_dossier_sinistre'),
    path('add_document_sinistre/<int:sinistre_id>', views.add_document_sinistre, name='add_document_sinistre'),
    path('dossier_sinistre/<int:sinistre_id>/intervenants', IntervenantDossierSinistreView.as_view(), name='intervenant_dossier_sinistre'),
    path('details_intervenant/<int:sinistre_intervenant_id>', views.details_intervenant, name='details_intervenant'),
    path('dossier_sinistre/<int:sinistre_id>/mouvements', MouvementDossierSinistreView.as_view(), name='mouvement_dossier_sinistre'),
    path('dossier_sinistre/<int:sinistre_id>/<int:historique_sinistre_id>/historique-details', DetailMouvementDossierSinistreView.as_view(), name='sinistre.historique.details'),
    path('mouvement/<int:mouvement_id>/motifs',views.motifs_by_mouvement, name='mouvement_motifs'),
    path('mouvement_sinistre/<int:sinistre_id>/<int:motif_id>', views.mouvement_sinistre, name='mouvement_sinistre'),

    path('saisie_sinistre/', SaisieSinistreView.as_view(), name='saisie_sinistre'),
    path('recherche_client_police/', views.recherche_client_police, name='recherche_client_police'),
    path('recuperer_information_police/', views.recuperer_information_police, name='recuperer_information_police'),
    path('recuperer_intervenant_police/', views.recuperer_intervenant_police, name='recuperer_intervenant_police'),
    path('ajout-intervenant-sinistre/', views.save_session_intervenants, name='save_session_intervenants'),
    path('supprimer_intervenant/<str:intervenant_id>/', views.supprimer_intervenant, name='supprimer_intervenant'),
    path('get_garanties_by_circonstance/', views.get_garanties_by_circonstance, name='get_garanties_by_circonstance'),
    path('ajout-garantie-sinistre/', views.save_session_garanties, name='save_session_garanties'),
    path('supprimer_garantie/<str:garantie_id>/', views.supprimer_garantie, name='supprimer_garantie'),
    path('get_garanties_by_circonstance_clean/', views.get_garanties_by_circonstance_clean, name='get_garanties_by_circonstance_clean'),
    path('recuperer-garanties-sinistre/', views.recuperer_garanties_sinistre, name='recuperer_garanties_sinistre'),

    path('add_sinistre_gestionnaire', views.add_sinistre_gestionnaire, name='add_sinistre_gestionnaire'),
    path('cloture_garantie/<str:garantie_id>/', views.cloture_garantie, name='cloture_garantie'),
    path('recuperer_intervenant_sinistre/', views.recuperer_intervenant_sinistre, name='recuperer_intervenant_sinistre'),
    path('recuperer_garantie_sinistre/', views.recuperer_garantie_sinistre, name='recuperer_garantie_sinistre'),
    path('update_sinistre_gestionnaire/<int:sinistre_id>', views.update_sinistre_gestionnaire, name='update_sinistre_gestionnaire'),

    path('liste-des-dossiers-sinsitres/', DossiersSinistresPhysiquesGestionnairesView.as_view(), name='liste_prestations'),
    path('dossiersinistre_physique_gestionnaire_datatable/', views.dossiersinistre_physique_gestionnaire_datatable, name='dossiersinistre_physique_gestionnaire_datatable'),
    path('annuler_sinistre/', AnnulerSinistreGestionnairesView.as_view(), name='annuler_sinistre'),
]


