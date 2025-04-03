
from django.urls import path

from shared.helpers import openai_complete
from . import views
from .views import GroupePermissionsView, ConnectedUsersView, BusinessUnitView, \
    BrancheView, BanquesView, ApporteurView, ApporteurinternationalView, ViewCourrier, CompagnieView, \
    CarosseriesView, CategorieVehiculeView, CiviliteView, CompteTresorerieView, ConditionsAssuranceView, DeviseView, CarburantView, \
    FormuleView, FractionnementView, GarantieView, GarantieFormuleView, GroupeView, ModeReglementView, PaysView, SecteurActiviteView, \
    TypeDocumentView, CirconstanceView, ResponsabiliteView, TypeIntervenantView, TypeMouvementView, TypeSinistreView, MouvementView, \
    MotifView, PosteDommageView, GarantieCirconstanceView


urlpatterns = [

    path('recalculer_parts_sinistres_sucaf/', views.recalculer_parts_sinistres_sucaf, name='recalculer_parts_sinistres_sucaf'),
    path('corriger_param_produit_compagnie/', views.corriger_param_produit_compagnie, name='corriger_param_produit_compagnie'),
    #
    #path('openai_complete/', openai_complete, name='openai_complete'),
    path('disponibilite_upd/', views.disponibilite_upd, name='disponibilite_upd'),
    path('set_bureau/', views.set_bureau, name='set_bureau'),
    #
    path('apporteur/', ApporteurView.as_view(), name='apporteurs'),
    path('apporteur/ajouter', views.add_apporteur, name='add_apporteur'),
    path('apporteur/<int:apporteur_id>/modifier', views.modifier_apporteur, name='modifier_apporteur'),
    path('apporteur/delete/<int:apporteur_id>/', views.supprimer_apporteur, name='supprimer_apporteur'),
    #
    path('apporteurinternational/', ApporteurinternationalView.as_view(), name='apporteurinternational'),
    #
    path('businessunit/', BusinessUnitView.as_view(), name='business_unit'),
    path('businessunit/ajouter', views.add_businessunit, name='add_businessunit'),
    path('businessunit/<int:businessunit_id>/modifier', views.modifier_businessunit, name='modifier_businessunit'),
    path('businessunit/delete/<int:businessunit_id>/', views.supprimer_businessunit, name='supprimer_businessunit'),
    #
    path('categorievehicule/', CategorieVehiculeView.as_view(), name='categorievehicule'),
    path('categorievehicule/ajouter', views.add_categorievehicule, name='add_categorievehicule'),
    path('categorievehicule/<int:categorievehicule_id>/modifier', views.modifier_categorievehicule, name='modifier_categorievehicule'),
    path('categorievehicule/delete/<int:categorievehicule_id>/', views.supprimer_categorievehicule, name='supprimer_categorievehicule'),
    #
    path('circonstance/', CirconstanceView.as_view(), name='circonstance'),
    path('circonstance/ajouter', views.add_circonstance, name='add_circonstance'),
    path('circonstance/<int:circonstance_id>/modifier', views.modifier_circonstance, name='modifier_circonstance'),
    path('circonstance/delete/<int:circonstance_id>/', views.supprimer_circonstance, name='supprimer_circonstance'),
    #
    path('civilite/', CiviliteView.as_view(), name='civilite'),
    path('civilite/ajouter', views.add_civilite, name='add_civilite'),
    path('civilite/<int:civilite_id>/modifier', views.modifier_civilite, name='modifier_civilite'),
    path('civilite/delete/<int:civilite_id>/', views.supprimer_civilite, name='supprimer_civilite'),
    #
    path('comptetresorerie/', CompteTresorerieView.as_view(), name='comptetresorerie'),
    path('comptetresorerie/ajouter', views.add_comptetresorerie, name='add_comptetresorerie'),
    path('comptetresorerie/<int:comptetresorerie_id>/modifier', views.modifier_comptetresorerie, name='modifier_comptetresorerie'),
    path('comptetresorerie/delete/<int:comptetresorerie_id>/', views.supprimer_comptetresorerie, name='supprimer_comptetresorerie'),
    #
    path('conditionsassurance/', ConditionsAssuranceView.as_view(), name='conditionsassurance'),
    path('conditionsassurance/ajouter', views.add_conditionsassurance, name='add_conditionsassurance'),
    path('conditionsassurance/<int:conditionsassurance_id>/modifier', views.modifier_conditionsassurance, name='modifier_conditionsassurance'),
    path('conditionsassurance/delete/<int:conditionsassurance_id>/', views.supprimer_conditionsassurance, name='supprimer_conditionsassurance'),
    #
    path('carburant/', CarburantView.as_view(), name='carburant'),
    path('carburant/ajouter', views.add_carburant, name='add_carburant'),
    path('carburant/<int:carburant_id>/modifier', views.modifier_carburant, name='modifier_carburant'),
    path('carburant/delete/<int:carburant_id>/', views.supprimer_carburant, name='supprimer_carburant'),
    #
    path('devise/', DeviseView.as_view(), name='devise'),
    path('devise/ajouter', views.add_devise, name='add_devise'),
    path('devise/<int:devise_id>/modifier', views.modifier_devise, name='modifier_devise'),
    path('devise/delete/<int:devise_id>/', views.supprimer_devise, name='supprimer_devise'),
    #
    path('branche/',BrancheView.as_view(), name='branche'),
    path('branche/ajouter', views.add_branche, name='add_branche'),
    path('branche/<int:branche_id>/modifier', views.modifier_branche, name='modifier_branche'),
    path('branche/delete/<int:branche_id>/', views.supprimer_branche, name='supprimer_branche'),
    #
    path('banque/',BanquesView.as_view(),name='banques'),
    path('banque/ajouter', views.add_banque, name='add_banque'),
    path('banque/<int:banque_id>/modifier', views.modifier_banque, name='modifier_banque'),
    path('banque/delete/<int:banque_id>/', views.supprimer_banque, name='supprimer_banque'),
    #
    path('carosserie/',CarosseriesView.as_view(),name='carosseries'),
    path('carosserie/ajouter', views.add_carosserie, name='add_carosserie'),
    path('carosserie/<int:carosserie_id>/modifier', views.modifier_carosserie, name='modifier_carosserie'),
    path('carosserie/delete/<int:carosserie_id>/', views.supprimer_carosserie, name='supprimer_carosserie'),
    #
    path('formule/', FormuleView.as_view(), name='formule'),
    path('formule/ajouter', views.add_formule, name='add_formule'),
    path('formule/<int:formule_id>/modifier', views.modifier_formule, name='modifier_formule'),
    path('formule/delete/<int:formule_id>/', views.supprimer_formule, name='supprimer_formule'),
    #
    path('fractionnement/', FractionnementView.as_view(), name='fractionnement'),
    path('fractionnement/ajouter', views.add_fractionnement, name='add_fractionnement'),
    path('fractionnement/<int:fractionnement_id>/modifier', views.modifier_fractionnement, name='modifier_fractionnement'),
    path('fractionnement/delete/<int:fractionnement_id>/', views.supprimer_fractionnement, name='supprimer_fractionnement'),
    #
    path('garantie/', GarantieView.as_view(), name='garantie'),
    path('garantie/ajouter', views.add_garantie, name='add_garantie'),
    path('garantie/<int:garantie_id>/modifier', views.modifier_garantie, name='modifier_garantie'),
    path('garantie/delete/<int:garantie_id>/', views.supprimer_garantie, name='supprimer_garantie'),
    #
    path('garantieformule/', GarantieFormuleView.as_view(), name='garantieformule'),
    path('garantieformule/ajouter', views.add_garantieformule, name='add_garantieformule'),
    path('garantieformule/<int:garantieformule_id>/modifier', views.modifier_garantieformule, name='modifier_garantieformule'),
    path('garantieformule/delete/<int:garantieformule_id>/', views.supprimer_garantieformule, name='supprimer_garantieformule'),
    #
    path('garantiecirconstance/', GarantieCirconstanceView.as_view(), name='garantiecirconstance'),
    path('garantiecirconstance/ajouter', views.add_garantiecirconstance, name='add_garantiecirconstance'),
    path('garantiecirconstance/<int:garantiecirconstance_id>/modifier', views.modifier_garantiecirconstance, name='modifier_garantiecirconstance'),
    path('garantiecirconstance/delete/<int:garantiecirconstance_id>/', views.supprimer_garantiecirconstance, name='supprimer_garantiecirconstance'),
    #
    path('groupe/', GroupeView.as_view(), name='groupe'),
    path('groupe/ajouter', views.add_groupe, name='add_groupe'),
    path('groupe/<int:groupe_id>/modifier', views.modifier_groupe, name='modifier_groupe'),
    path('groupe/delete/<int:groupe_id>/', views.supprimer_groupe, name='supprimer_groupe'),
    #
    path('modereglement/', ModeReglementView.as_view(), name='modereglement'),
    path('modereglement/ajouter', views.add_modereglement, name='add_modereglement'),
    path('modereglement/<int:modereglement_id>/modifier', views.modifier_modereglement, name='modifier_modereglement'),
    path('modereglement/delete/<int:modereglement_id>/', views.supprimer_modereglement, name='supprimer_modereglement'),
    #
    path('pays/', PaysView.as_view(), name='pays'),
    path('pays/ajouter', views.add_pays, name='add_pays'),
    path('pays/<int:pays_id>/modifier', views.modifier_pays, name='modifier_pays'),
    path('pays/delete/<int:pays_id>/', views.supprimer_pays, name='supprimer_pays'),
    #
    path('responsabilite/', ResponsabiliteView.as_view(), name='responsabilite'),
    path('responsabilite/ajouter', views.add_responsabilite, name='add_responsabilite'),
    path('responsabilite/<int:responsabilite_id>/modifier', views.modifier_responsabilite, name='modifier_responsabilite'),
    path('responsabilite/delete/<int:responsabilite_id>/', views.supprimer_responsabilite, name='supprimer_responsabilite'),
    #
    path('courriers/', ViewCourrier.as_view(), name='courrier'),
    path('courrier/add_courrier', views.add_courrier, name='add_courrier'),
    path('courrier/<int:courrier_id>/modifier_courrier', views.modifier_courrier, name='modifier_courrier'),
    path("courrier/delete", views.supprimer_courrier, name='supprimer_courrier'),
    #
    path('compagnie/', CompagnieView.as_view(), name='compagnie'),
    path('compagnie/add_compagnie', views.add_compagnie, name='add_compagnie'),
    path('compagnie/<int:compagnie_id>/taux', views.taux_compagnie, name='taux_compagnie'),
    path('compagnie/<int:compagnie_id>/modifier', views.modifier_compagnie, name='modifier_compagnie'),
    path('compagnie/delete/<int:compagnie_id>/', views.supprimer_compagnie, name='supprimer_compagnie'),
    #
    path('typeintervenant/', TypeIntervenantView.as_view(), name='typeintervenant'),
    path('typeintervenant/ajouter', views.add_typeintervenant, name='add_typeintervenant'),
    path('typeintervenant/<int:type_intervenant_id>/modifier', views.modifier_typeintervenant, name='modifier_typeintervenant'),
    path('typeintervenant/delete/<int:type_intervenant_id>/', views.supprimer_typeintervenant, name='supprimer_typeintervenant'),
    #
    path('typemouvement/', TypeMouvementView.as_view(), name='typemouvement'),
    path('typemouvement/ajouter', views.add_typemouvement, name='add_typemouvement'),
    path('typemouvement/<int:type_mouvement_id>/modifier', views.modifier_typemouvement, name='modifier_typemouvement'),
    path('typemouvement/delete/<int:type_mouvement_id>/', views.supprimer_typemouvement, name='supprimer_typemouvement'),
    #
    path('typesinistre/', TypeSinistreView.as_view(), name='typesinistre'),
    path('typesinistre/ajouter', views.add_typesinistre, name='add_typesinistre'),
    path('typesinistre/<int:type_sinistre_id>/modifier', views.modifier_typesinistre, name='modifier_typesinistre'),
    path('typesinistre/delete/<int:type_sinistre_id>/', views.supprimer_typesinistre, name='supprimer_typesinistre'),
    #
    path('secteuractivite/', SecteurActiviteView.as_view(), name='secteur_activite'),
    path('secteuractivite/ajouter', views.add_secteur_activite, name='add_secteur_activite'),
    path('secteur_activite/<int:secteur_activite_id>/modifier', views.modifier_secteur_activite, name='modifier_secteur_activite'),
    path('secteur_activite/delete/<int:secteur_activite_id>/', views.supprimer_secteur_activite, name='supprimer_secteur_activite'),
    #
    path('types_documents/', TypeDocumentView.as_view(), name='types_documents'),
    path('types_documents/ajouter', views.add_types_documents, name='add_types_documents'),
    path('types_documents/<int:type_document_id>/modifier', views.modifier_types_documents, name='modifier_types_documents'),
    path('types_documents/delete/<int:type_document_id>/', views.supprimer_types_documents, name='supprimer_types_documents'),
    #
    path('mouvements/', MouvementView.as_view(), name='mouvements'),
    path('mouvements/ajouter', views.add_mouvement, name='add_mouvement'),
    path('mouvements/<int:mouvement_id>/modifier', views.modifier_mouvement, name='modifier_mouvement'),
    path('mouvements/delete/<int:mouvement_id>/', views.supprimer_mouvement, name='supprimer_mouvement'),
    #
    path('motifs/', MotifView.as_view(), name='motifs'),
    path('motifs/ajouter', views.add_motif, name='add_motif'),
    path('motifs/<int:motif_id>/modifier', views.modifier_motif, name='modifier_motif'),
    path('motifs/delete/<int:motif_id>/', views.supprimer_motif, name='supprimer_motif'),
    #
    path('postedommage/', PosteDommageView.as_view(), name='postedommage'),
    path('postedommage/ajouter', views.add_postedommage, name='add_postedommage'),
    path('postedommage/<int:postedommage_id>/modifier', views.modifier_postedommage, name='modifier_postedommage'),
    path('postedommage/delete/<int:postedommage_id>/', views.supprimer_postedommage, name='supprimer_postedommage'),

    #
    path('groupes_permissions/<int:groupe_id>', GroupePermissionsView.as_view(), name='groupes_permissions'),
    path('clearcache/', views.clear_cache, name='clear_cache'),
    #
    path('verify-code/', views.verify_code, name='verify_code'),
    #
    path('download-background-query-result/<int:query_id>', views.download_background_query_result, name='download_background_query_result'),
    #
    path('connectedusers/', ConnectedUsersView.as_view(), name='connectedusers'),
    path('logoutuser/<int:user_id>', views.logout_user, name='logoutuser'),
]
