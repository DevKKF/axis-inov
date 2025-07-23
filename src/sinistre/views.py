import datetime
import json
import os
from ast import literal_eval
from collections import defaultdict
from copy import deepcopy
from datetime import datetime as datetimeJsdecode, timedelta
from decimal import Decimal
from functools import reduce
from pprint import pprint
from sqlite3 import Date

import PyPDF2
import openpyxl
import requests
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.core import serializers
# Create your views here.
from django.core.files.base import File
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import Count
from django.db.models import Q, Subquery, OuterRef
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.db.models import Value, F
from django.db.models.functions import Concat
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import get_template
#
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView, ListView
from num2words import num2words
from xhtml2pdf import pisa
import re
from uuid import uuid4

from configurations.helper_config import execute_query, create_query_background_task
from configurations.models import Compagnie, User, Rubrique, \
    TypePriseencharge, Pays, TypeIntervenant, TauxResponsabilite, TypeSinistre, Circonstance, Garantie, GarantieCirconstance, PosteDommage, \
    ActionLog, PeriodeComptable, TypeRemboursement, ModeCreation, TypePrefinancement
from production.models import Statut, TypeDocument, Client
#
from production.models import Police, HistoriquePolice, HistoriqueAliment, PoliceAssureur, Mouvement, Motif, AlimentPolice, Document, AutreRisque, Marchandise, \
    Vehicule
from production.forms import DocumentForm
from production.templatetags.my_filters import money_field, supprimer_espaces
from shared.enum import StatutPolice
from shared.enum import StatutSinistre, StatutSinistreBordereau, StatutSinistrePrestation, StatutValidite, \
    StatutRemboursement, StatutRemboursementSinistre, DesignationRemboursementSinistre, SatutBordereauDossierSinistres, \
    StatutPaiementSinistre, TypeBonConsultation
from sinistre.helper_sinistre import exportation_en_excel_avec_style, \
    extraction_demandes_accords_prealables_traitees_par_medecins_conseil, extraction_des_sinistres_traites_valides, \
    requete_demandes_accords_prealables_traitees_par_les_medecins_conseil, requete_liste_des_sp_client_par_filiale, \
    requete_liste_paiement_sinistre_sante_entre_deux_dates, \
    requete_liste_sinistre_ordonnancee_par_period_par_beneficiaire, \
    requete_liste_sinistre_ordonnancee_par_period_par_prestataire, \
    requete_liste_sinistre_ordonnancee_par_period, requete_liste_sinistre_entre_2date, requete_analyse_prime_compta, \
    requete_liste_sinistre_saisies_entre_2date, requete_sinistres_traites_et_valides_par_les_gestionnaires, \
    requete_analyse_prime_compta_apporteur, get_retenue_selon_contexte
# Create your views here.
from sinistre.models import PaiementComptable, Sinistre, HistoriqueSinistre, Intervenant, SinistreIntervenant, SinistreGarantie, HistoriqueSinistreGarantie, DossierSinistre, MouvementSinistre, \
    RemboursementSinistre, BordereauOrdonnancement, HistoriqueOrdonnancementSinistre

from sinistre.forms import SinistreForm



@method_decorator(login_required, name='dispatch')
class DossierSinistresTraitesView(TemplateView):
    template_name = 'liste_dossiers_traites.html'
    model = Sinistre

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        clients = Client.objects.order_by('-nom')

        today = timezone.now().date()
        context['today'] = today
        context['clients'] = clients

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


def dossiersinistre_traites_datatable(request):
    items_per_page = 10
    page_number = request.GET.get('page')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', items_per_page))
    sort_column_index = int(request.GET.get('order[0][column]'))
    sort_direction = request.GET.get('order[0][dir]')

    search_numero_assure = request.GET.get('num_assure', '')
    search_numero_dossier_sinistre = request.GET.get('num_feuille_soins', '')
    search_date_survenance = request.GET.get('date_prestation', '')
    search_prestataire = request.GET.get('prestataire', '')

    today = datetime.datetime.now(tz=timezone.utc)
    yesterday = datetime.datetime.now(tz=timezone.utc) - timedelta(days=3)
    queryset = DossierSinistre.objects.filter(statut_validite=StatutValidite.VALIDE, bureau=request.user.bureau, has_sinistre_traite_bymedecin=True, date_traitement_sinistre_bymedecin__date__gte=yesterday).order_by('-id')
    # dd(queryset)

    # la recherche
    if search_numero_assure:
        cartes = Carte.objects.filter(numero=search_numero_assure)
        carte = cartes.first() if cartes else None
        aliment = carte.aliment if carte else None
        queryset = queryset.filter(aliment_id=aliment.pk) if aliment else queryset.filter(numero="nexisterajamais")

    if search_numero_dossier_sinistre:
        queryset = queryset.filter(numero__contains=search_numero_dossier_sinistre)

    if search_date_survenance:
        queryset = queryset.filter(date_survenance__contains=search_date_survenance)

    if search_prestataire:
        queryset = queryset.filter(prestataire=search_prestataire)

    # Map column index to corresponding model field for sorting
    sort_columns = {
        0: '-numero',
        1: 'aliment__nom',
        2: 'statut',
        # Add more columns as needed
    }

    # Default sorting by 'id' if column index is not found
    sort_column = sort_columns.get(sort_column_index, 'id')

    if sort_direction == 'desc':
        sort_column = '-' + sort_column  # For descending order

    # Apply sorting
    # add condition to avoid list has no attribute order_by
    # if not request.user.is_med and not request.user.is_pharm:
    # queryset = queryset.order_by(sort_column)

    paginator = Paginator(queryset, length)
    page_obj = paginator.get_page(page_number)

    # Prepare the data in the expected format
    data = []
    for c in page_obj:
        detail_url = reverse('details_dossier_sinistre', args=[c.id])  # URL to the detail view# URL to the detail view
        actions_html = f'<a href="{detail_url}"><span class="badge btn-sm btn-details rounded-pill"><i class="fa fa-eye"></i> Détails</span></a>&nbsp;&nbsp;'

        if request.user.is_pharm:
            type_or_numero_carte = aliment.carte_active if aliment else ''
        else:
            if request.user.is_med and c.type_priseencharge.code == "CONSULT":
                type_or_numero_carte = "PHARMACIE"
            else:
                type_or_numero_carte = c.type_priseencharge.libelle if c.type_priseencharge else ''

        if not c.aliment:
            c.aliment.nom = ''
        if not c.aliment:
            c.aliment.prenoms = ''


        if request.user.is_pharm:
            total_frais_reel = c.total_frais_reel_medicament
            total_part_compagnie = c.total_part_compagnie_medicament
            total_part_assure = c.total_part_assure_medicament
        elif request.user.is_prestataire:
            total_frais_reel = c.new_total_frais_reel
            total_part_compagnie = c.new_total_part_compagnie_prestataire
            total_part_assure = c.new_total_part_assure_prestataire
        else:
            total_frais_reel = c.new_total_frais_reel
            total_part_compagnie = c.new_total_part_compagnie_gestionnaire
            total_part_assure = c.new_total_part_assure_gestionnaire


        statut_html = f'<span class="badge badge-{c.statut.lower().replace(" ", "-")}">{c.statut}</span>'

        cartes = c.aliment.cartes.filter(statut=Statut.ACTIF) if c.aliment else None
        numero_carte = cartes.first().numero if cartes else None

        nom_prestataire = c.prestataire.name if c.prestataire else ""

        data_iten = {
            "id": c.id,
            "numero": c.numero if c.numero else "",
            "type_or_numero_carte": type_or_numero_carte,
            "nom": c.aliment.nom + ' ' + c.aliment.prenoms,
            "numero_carte": numero_carte,
            "prestataire": nom_prestataire,
            "total_frais_reel": money_field(total_frais_reel),
            "total_part_compagnie": money_field(total_part_compagnie),
            "total_part_assure": money_field(total_part_assure),
            "date_prestation": c.date_survenance.strftime("%d/%m/%Y %H:%M") if c.date_survenance else "",
            "date_traitement_bymedecin": c.date_traitement_sinistre_bymedecin.strftime("%d/%m/%Y %H:%M") if c.date_traitement_sinistre_bymedecin else "",
            "statut": statut_html,
            "actions": actions_html,
        }

        if request.user.is_med:
            statut_prorogation_html = f'<span class="badge badge-{c.statut_prorogation.replace(" ", "-").lower()}">{c.statut_prorogation}</span>' if c.statut_prorogation else ""
            data_iten["statut_prorogation"] = statut_prorogation_html

        data.append(data_iten)

    return JsonResponse({
        "data": data,
        "recordsTotal": queryset.count(),
        "recordsFiltered": paginator.count,
        "draw": int(request.GET.get('draw', 1)),
    })


@method_decorator(login_required, name='dispatch')
class SaisieSinistreView(TemplateView):
    template_name = 'form_saisie_sinistre.html'
    model = Sinistre

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        today = timezone.now().date()
        clients = Client.objects.order_by('-nom')

        pays = Pays.objects.all().order_by('nom')
        typeintervenants = TypeIntervenant.objects.filter(statut=1).order_by('libelle')

        context['today'] = today
        context['clients'] = clients
        context['pays'] = pays
        context['typeintervenants'] = typeintervenants

        intervenants = request.session.get('intervenants', None)
        # Vider les intervenants enregistrés en session
        if 'intervenants' in request.session:
            del request.session['intervenants']

        garanties = request.session.get('garanties', None)
        # Vider les garanties enregistrées en session
        if 'garanties' in request.session:
            del request.session['garanties']

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@csrf_exempt
def recherche_client_police(request):
    if request.method == 'POST':
        client_id = request.POST.get('search_client_id', '').strip().upper()
        numero_police = request.POST.get('search_numero_police', '').strip().upper()

        if not client_id and not numero_police:
            return JsonResponse({'success': False, 'message': 'Aucun champ de recherche saisi.'})

        # Recherche stricte par id
        if client_id:

            client = Client.objects.filter(id=client_id).first()

            polices_qs = (Police.objects.filter(client=client))

            # Vérification si des polices existent
            if not polices_qs.exists():
                return JsonResponse({'success': False, 'message': 'Aucune police active trouvée pour ce client.'})

            polices = []
            for plc in polices_qs:
                dernier_historique = HistoriquePolice.objects.filter(police_id=plc.id).order_by('-date_du_jour').first()
                assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id, type_compagnie_id=1).first() if dernier_historique else []
                polices.append({
                    'id': plc.id,
                    'numero': plc.numero,
                    'produit': plc.produit.nom,
                    'assureur': assureur_police.compagnie.nom,
                    'date_debut': plc.date_debut_effet.strftime("%d/%m/%Y") if plc.date_debut_effet else '',
                    'date_echeance': plc.date_fin_effet.strftime("%d/%m/%Y") if plc.date_fin_effet else (plc.date_fin_police.strftime("%d/%m/%Y") if plc.date_fin_police else None),
                })

            return JsonResponse({'success': True, 'polices': polices})
        if numero_police:
            polices_qs = (Police.objects.filter(numero=numero_police))

            # Vérification si des polices existent
            if not polices_qs.exists():
                return JsonResponse({'success': False, 'message': 'Aucune police active trouvée pour ce client.'})

            polices = []
            for plc in polices_qs:
                dernier_historique = HistoriquePolice.objects.filter(police_id=plc.id).order_by('-date_du_jour').first()
                assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id,
                                                                type_compagnie_id=1).first() if dernier_historique else []
                polices.append({
                    'id': plc.id,
                    'numero': plc.numero,
                    'produit': plc.produit.nom,
                    'assureur': assureur_police.compagnie.nom,
                    'date_debut': plc.date_debut_effet.strftime("%d/%m/%Y") if plc.date_debut_effet else '',
                    'date_echeance': plc.date_fin_effet.strftime("%d/%m/%Y") if plc.date_fin_effet else (
                        plc.date_fin_police.strftime("%d/%m/%Y") if plc.date_fin_police else None),
                })

            return JsonResponse({'success': True, 'polices': polices})

        if client_id and numero_police:
            client = Client.objects.filter(id=client_id).first()

            polices_qs = (Police.objects.filter(client=client, numero=numero_police))

            # Vérification si des polices existent
            if not polices_qs.exists():
                return JsonResponse({'success': False, 'message': 'Aucune police active trouvée pour ce client.'})

            polices = []
            for plc in polices_qs:
                dernier_historique = HistoriquePolice.objects.filter(police_id=plc.id).order_by('-date_du_jour').first()
                assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id,
                                                                type_compagnie_id=1).first() if dernier_historique else []
                polices.append({
                    'id': plc.id,
                    'numero': plc.numero,
                    'produit': plc.produit.nom,
                    'assureur': assureur_police.compagnie.nom,
                    'date_debut': plc.date_debut_effet.strftime("%d/%m/%Y") if plc.date_debut_effet else '',
                    'date_echeance': plc.date_fin_effet.strftime("%d/%m/%Y") if plc.date_fin_effet else (
                        plc.date_fin_police.strftime("%d/%m/%Y") if plc.date_fin_police else None),
                })

            return JsonResponse({'success': True, 'polices': polices})
        else:
            return JsonResponse({'success': False, 'message': 'Aucune recherche initiée.'})

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})


@csrf_exempt
def recuperer_information_police(request):
    police_id = request.GET.get('police_id')

    try:
        police = Police.objects.get(id=police_id, bureau=request.user.bureau, statut_validite='VALIDE')

        # TODO: Vider les intervenants et des garanties du sinistre
        if 'intervenants' in request.session:
            del request.session['intervenants']

        if 'garanties_sinistre' in request.session:
            del request.session['garanties_sinistre']

        # Récupération de client
        client = Client.objects.get(id=police.client_id)

        # Récupérer le dernier historique
        dernier_historique = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()

        # Récupérer les assureurs associés à l'historique
        assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id, type_compagnie_id=1).first() if dernier_historique else None
        today = timezone.now().date()

        typesinistres = TypeSinistre.objects.filter(statut=1).order_by('libelle')
        typeintervenants = TypeIntervenant.objects.filter(statut=1).order_by('libelle')
        typedocuments = TypeDocument.objects.filter(is_sinistre=1).order_by('libelle')
        responsabilites = TauxResponsabilite.objects.filter(statut=1)
        circonstances = Circonstance.objects.filter(statut=1, branche_id=police.produit.branche_id).order_by('libelle')

        pays = Pays.objects.all().order_by('nom')

        gestionnaire_sinistres = []
        utilisateur = User.objects.all().order_by('-first_name').exclude(is_admin_group=1)
        for user in utilisateur:
            if user.is_sinistre:
                gestionnaire_sinistres.append(user)

        aliments = 0
        aliment = 0
        if police.produit.code in ['10001', '10002', '50001', '50002']:
            aliments = AlimentPolice.objects.filter(police_id=police.id)
        else:
            aliment = AlimentPolice.objects.filter(police_id=police.id).first()

        context = {
            'police': police,
            'client': client,
            'dossiers_sinistres': None,
            'sinistres': None,
            'dernier_historique': dernier_historique,
            'assureur_police': assureur_police,
            'today': today,
            'typesinistres': typesinistres,
            'typeintervenants': typeintervenants,
            'typedocuments': typedocuments,
            'responsabilites': responsabilites,
            'circonstances': circonstances,
            'pays': pays,
            'aliments': aliments,
            'aliment': aliment,
            'gestionnaire_sinistres': gestionnaire_sinistres,
        }

        return render(request, 'formulaire_sinistre.html', context)
    except Police.DoesNotExist:
        return JsonResponse({'error': 'Police non trouvée.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def recuperer_intervenant_police(request):
    police_id = request.GET.get('police_id')

    try:
        police = Police.objects.get(id=police_id, bureau=request.user.bureau, statut_validite='VALIDE')

        client = Client.objects.filter(id=police.client_id).first()

        intervenants_existant = list(request.session.get('intervenants', []))

        nouveau_intervenant = {
            'id': str(uuid4()),
            'nom': client.nom,
            'prenoms': client.prenoms,
            'telephone': client.telephone_mobile,
            'email': client.email,
            'portable': client.telephone_fixe,
            'pays_id': client.pays_id,
            'type_intervenant_id': 1,
            'type_intervenant': "Tiers Personne",
            'boite_postale': client.adresse,
            'code_postal': client.adresse_postale,
            'ville': client.ville,
        }

        intervenants_existant.append(nouveau_intervenant)
        request.session['intervenants'] = intervenants_existant
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': "Ajout d'intervenant effectué avec succès !",
            'data': intervenants_existant
        }, status=200)


    except Police.DoesNotExist:
        return JsonResponse({'error': 'Police non trouvée.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def save_session_intervenants(request):
    if request.method == 'POST':
        try:
            type_intervenant_id = request.POST.get('type_intervenant_id')
            type_intervenant = TypeIntervenant.objects.filter(id=type_intervenant_id).first()
            if not type_intervenant:
                return JsonResponse({'success': False, 'message': 'Type Intervenant non trouvé.'}, status=400)

            # Nettoyage et normalisation du numéro de téléphone
            raw_portable = request.POST.get('portable', '')
            portable = re.sub(r'\D', '', raw_portable)  # Garde uniquement les chiffres

            if not portable:
                return JsonResponse({'success': False, 'message': 'Le numéro de portable est requis.'}, status=400)

            intervenants_existant = list(request.session.get('intervenants', []))

            # Vérification d’unicité : normalise les téléphones en session aussi
            existing_numbers = [re.sub(r'\D', '', i.get('portable', '')) for i in intervenants_existant]
            print('Intervenant avant ajout : ', intervenants_existant)
            if portable in existing_numbers:
                return JsonResponse({
                    'success': False,
                    'message': f"Un intervenant avec le numéro de téléphone '{raw_portable}' existe déjà."
                }, status=400)

            nouveau_intervenant = {
                'id': str(uuid4()),
                'nom': request.POST.get('nom'),
                'prenoms': request.POST.get('prenoms'),
                'telephone': request.POST.get('telephone'),  # On garde le format d'origine pour l'affichage
                'email': request.POST.get('email'),
                'portable': raw_portable,
                'fax': request.POST.get('fax'),
                'pays_id': request.POST.get('pays_id'),
                'type_intervenant_id': type_intervenant_id,
                'type_intervenant': type_intervenant.libelle,
                'code_postal': request.POST.get('code_postal'),
                'boite_postale': request.POST.get('boite_postale'),
                'ville': request.POST.get('ville'),
            }

            intervenants_existant.append(nouveau_intervenant)
            request.session['intervenants'] = intervenants_existant
            request.session.modified = True

            return JsonResponse({
                'success': True,
                'message': "Ajout d'intervenant effectué avec succès !",
                'data': intervenants_existant
            }, status=200)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f"Erreur lors de l'enregistrement : {str(e)}"
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': 'Requête invalide ou méthode non autorisée.'
    }, status=400)


@csrf_exempt
def supprimer_intervenant(request, intervenant_id):
    print('Suppression intervenant par ID...')
    if request.method == 'POST':
        try:
            intervenants = request.session.get('intervenants', [])
            intervenants = [i for i in intervenants if str(i.get('id')) != str(intervenant_id)]
            request.session['intervenants'] = intervenants
            return JsonResponse({'success': True, 'message': 'Intervenant supprimé.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'}, status=405)


#Chargement des garanties de la circonstance
def get_garanties_by_circonstance(request):
    circonstance_id = request.GET.get('circonstance_id')
    garanties = GarantieCirconstance.objects.filter(circonstance_id=circonstance_id).values('garantie__id', 'garantie__nom')
    garanties = [{'id': g['garantie__id'], 'nom': g['garantie__nom']} for g in garanties]
    return JsonResponse({'garanties': list(garanties)})


def save_session_garanties(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            garanties_existant = list(request.session.get('garanties', []))
            today = timezone.now().date()

            # Extraire les IDs existants pour vérifier les doublons
            existing_ids = {g['garantie_id'] for g in garanties_existant}

            for g in data.get('garanties', []):
                garantie_id = g.get('id')
                if garantie_id in existing_ids:
                    continue  # ✅ Ignore les doublons

                nouvelle_garantie = {
                    'id': str(uuid4()),
                    'garantie_id': garantie_id,
                    'nom': g.get('nom'),
                    'franchise': g.get('franchise'),
                    'capital': g.get('capital'),
                    'mouvement': "Ouverture Sinistre",
                    'date_ajout': today.isoformat(),
                }
                garanties_existant.append(nouvelle_garantie)
                existing_ids.add(garantie_id)  # ✅ Ajout au set pour les prochains tours

            request.session['garanties'] = garanties_existant
            request.session.modified = True

            return JsonResponse({
                'success': True,
                'message': "Ajout de garantie effectué avec succès !",
                'data': garanties_existant
            }, status=200)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f"Erreur lors de l'enregistrement : {str(e)}"
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': 'Requête invalide ou méthode non autorisée.'
    }, status=400)


def get_garanties_by_circonstance_clean(request):
    try:
        if 'garanties' in request.session:
            del request.session['garanties']
            request.session.modified = True

            garanties = request.session.get('garanties', None)

            return JsonResponse({
                'success': True,
                'message': 'Les garanties ont été supprimées de la session.'
            }, status=200)
        else:
            return JsonResponse({
                'success': True,
                'message': 'Aucune garantie n\'était enregistrée en session.'
            }, status=200)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la suppression des garanties : {str(e)}'
        }, status=500)


def supprimer_garantie(request, garantie_id):
    if request.method == 'POST':
        garanties = request.session.get("garanties", [])

        garanties = [g for g in garanties if str(g["id"]) != str(garantie_id)]

        request.session["garanties"] = garanties
        request.session.modified = True
        request.session.save()

        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "message": "Méthode non autorisée."}, status=405)


def recuperer_garanties_sinistre(request):
    garanties = request.session.get("garanties", [])

    formatted_garanties = []
    for garantie in garanties:
        formatted_garanties.append({
            "id": garantie.get('id'),
            "garantie_id": garantie.get('garantie_id'),
            "nom": garantie.get('nom'),
            "franchise": garantie.get('franchise', ''),
            "capital": garantie.get('capital', ''),
            "mouvement": garantie.get('mouvement', ''),
            "date_ajout": garantie.get('date_ajout', ''),
        })

    return JsonResponse({"garanties": formatted_garanties})


def afficher_provision_sinistre(request):
    postedommages = PosteDommage.objects.filter(statut=1)
    garanties = request.session.get("garanties", [])

    postedommages_list = [{
        "id": poste.id,
        "libelle": poste.libelle,
    } for poste in postedommages]

    context = {
        'postedommages': postedommages_list,
        'garanties': garanties,
    }

    return render(request, 'sinistre_provision_table.html', context)


#Save Sinistre by Gestionnaire
def add_sinistre_gestionnaire(request):

    if request.method == 'POST':

        form = SinistreForm(request.POST)

        today = timezone.now().date()

        if form.is_valid():

            police = Police.objects.get(id=request.POST.get('police_id'))
            client = Client.objects.get(id=police.client_id)
            vehicule_id = request.POST.get('vehicule_id')
            marchandise_id = request.POST.get('marchandise_id')
            autre_risque_id = request.POST.get('autre_risque_id')
            compagnie_id = request.POST.get('compagnie_id')
            mouvement_id = request.POST.get('mouvement_id')
            motif_mouvement_id = request.POST.get('motif_mouvement_id')
            gestionnaire_sinistre_id = request.POST.get('gestionnaire_sinistre_id')
            date_survenance = request.POST.get('date_survenance')
            date_ouverture = request.POST.get('date_ouverture')
            date_cloture = request.POST.get('date_cloture')
            date_declaration = request.POST.get('date_declaration')
            date_reouverture = request.POST.get('date_reouverture')
            circonstance_id = request.POST.get('circonstance_id')
            lieu_survenance = request.POST.get('lieu_survenance')
            tva_recuperee_str = request.POST.get('tva_recuperee')
            type_sinistre_id = request.POST.get('type_sinistre_id')
            franchise = request.POST.get('franchise').replace(' ', '')
            taux_responsabilite_id = request.POST.get('responsabilite_id')
            fait_generateur = request.POST.get('fait_generateur')
            point_de_choc = request.POST.get('point_de_choc')
            commentaires = request.POST.get('commentaires')
            risque_sinistre = request.POST.get('risque')
            numero = request.POST.get('numero')

            if tva_recuperee_str == "1":
                tva_recuperee = True
            elif tva_recuperee_str == "0":
                tva_recuperee = False
            else:
                tva_recuperee = None

            # Récupérer l'historique aliment
            historique_aliment = ''
            if autre_risque_id:
                autre_risque = AutreRisque.objects.filter(id=autre_risque_id).first()
                historique_aliment = autre_risque.autre_risque_dernier_historique.id if autre_risque.autre_risque_dernier_historique else None
            if marchandise_id:
                marchandise = Marchandise.objects.filter(id=marchandise_id).first()
                historique_aliment = marchandise.marchandise_dernier_historique.id if marchandise.marchandise_dernier_historique else None
            if vehicule_id:
                vehicule = Vehicule.objects.filter(id=vehicule_id).first()
                historique_aliment = vehicule.vehicule_dernier_historique.id if vehicule.vehicule_dernier_historique else None

            sinistre_created = Sinistre(
                client_id=client.id,
                police_id=police.id,
                historique_aliment_id=historique_aliment if historique_aliment else None,
                historique_police_id=police.police_dernier_historique.id if police else None,
                compagnie_id=compagnie_id,
                type_sinistre_id=type_sinistre_id,
                taux_responsabilite_id=taux_responsabilite_id,
                circonstance_id=circonstance_id,
                gestionnaire_sinistre_id=gestionnaire_sinistre_id,
                operateur_de_saisie_id=request.user.id,
                created_by_id=request.user.id,
                numero=numero,
                risque_sinistre=risque_sinistre,
                date_survenance=date_survenance if date_survenance else None,
                date_declaration=date_declaration if date_declaration else None,
                date_ouverture=date_ouverture if date_ouverture else None,
                date_cloture=date_cloture if date_cloture else None,
                date_reouverture=date_reouverture if date_reouverture else None,
                lieu_survenance=lieu_survenance,
                tva_recuperee=tva_recuperee if tva_recuperee else 0,
                fait_generateur=fait_generateur,
                point_de_choc=point_de_choc,
                commentaires=commentaires,
                franchise=supprimer_espaces(franchise) if franchise else 0,
            )
            sinistre_created.save()

            code_bureau = request.user.bureau.code
            sinistre_created.numero_provisoire = str(code_bureau) + 'S' + str(Date.today().year)[-2:] + str(
                sinistre_created.pk).zfill(6)
            if sinistre_created.numero == "":
                sinistre_created.numero = sinistre_created.numero_provisoire

            sinistre_created.save()

            sinistre = Sinistre.objects.get(id=sinistre_created.pk)

            historique_sinistre_created = HistoriqueSinistre(
                sinistre=sinistre,
                historique_aliment_id=historique_aliment if historique_aliment else None,
                client_id=sinistre.client_id,
                police_id=sinistre.police_id,
                historique_police_id=sinistre.police.police_dernier_historique.id if sinistre.police else None,
                compagnie_id=sinistre.compagnie_id,
                type_sinistre_id=sinistre.type_sinistre_id,
                taux_responsabilite_id=sinistre.taux_responsabilite_id,
                circonstance_id=sinistre.circonstance_id,
                gestionnaire_sinistre_id=sinistre.gestionnaire_sinistre_id,
                created_by_id=request.user.id,
                operateur_de_saisie_id=request.user.id,
                mouvement=Mouvement.objects.get(code=mouvement_id),
                motif_mouvement=Motif.objects.get(code=motif_mouvement_id),

                date_operation=today,
                date_survenance=sinistre.date_survenance if sinistre.date_survenance else None,
                date_declaration=sinistre.date_declaration if sinistre.date_declaration else None,
                date_ouverture=sinistre.date_ouverture if sinistre.date_ouverture else None,
                date_cloture=sinistre.date_cloture if sinistre.date_cloture else None,
                date_reouverture=sinistre.date_reouverture if sinistre.date_reouverture else None,

                lieu_survenance=sinistre.lieu_survenance,
                tva_recuperee=sinistre.tva_recuperee if sinistre.tva_recuperee else 0,
                fait_generateur=sinistre.fait_generateur,
                point_de_choc=sinistre.point_de_choc,
                commentaires=sinistre.commentaires,
                risque_sinistre=sinistre.risque_sinistre,
                franchise=sinistre.franchise if sinistre.franchise else 0,
            )
            historique_sinistre_created.save()

            historique_sinistre = HistoriqueSinistre.objects.get(id=historique_sinistre_created.pk)

            sinistre.historique_sinistre = historique_sinistre
            sinistre.save()

            # Créer une ligne de mouvement_sinistre avec le mouvement ouverture sinistre et le motif ouverture sinistre
            ms = MouvementSinistre()
            ms.sinistre = sinistre
            ms.police = police
            ms.mouvement = Mouvement.objects.get(code=mouvement_id)
            ms.motif = Motif.objects.get(code=motif_mouvement_id)
            ms.date_effet = sinistre.date_ouverture
            ms.created_by = request.user
            ms.save()

            # Récupérer les intervenants de la session
            intervenants = request.session.get('intervenants', [])
            for intervenant in intervenants:
                intervenant_created = Intervenant(
                    type_intervenant_id=intervenant.get('type_intervenant_id'),
                    pays_id=intervenant.get('pays_id'),
                    nom=intervenant.get('nom'),
                    prenoms=intervenant.get('prenoms'),
                    portable=intervenant.get('portable'),
                    telephone=intervenant.get('telephone'),
                    fax=intervenant.get('fax'),
                    email=intervenant.get('email'),
                    code_postal=intervenant.get('code_postal'),
                    boite_postale=intervenant.get('boite_postale'),
                    ville=intervenant.get('ville'),
                    created_by_id=request.user.id,
                )
                intervenant_created.save()

                intervenant = Intervenant.objects.get(id=intervenant_created.pk)

                intervenant_created = SinistreIntervenant(
                    sinistre=sinistre,
                    historique_sinistre=historique_sinistre,
                    intervenant=intervenant,
                    created_by_id=request.user.id,
                )
                intervenant_created.save()


            # Récupérer les garanties de la session
            garanties_sinistre = request.session.get("garanties", [])
            for garantie_sinistre in garanties_sinistre:
                garantie_sinistre_created = SinistreGarantie(
                    sinistre=sinistre,
                    garantie_id=garantie_sinistre.get('garantie_id'),
                    franchise=supprimer_espaces(garantie_sinistre.get('franchise', 0)) if garantie_sinistre.get('franchise', 0) else None,
                    capital=supprimer_espaces(garantie_sinistre.get('capital', 0)) if garantie_sinistre.get('capital', 0) else None,
                    prime_nette=supprimer_espaces(garantie_sinistre.get('prime_net', 0)) if garantie_sinistre.get('prime_net', 0) else None,
                    prime_ttc=supprimer_espaces(garantie_sinistre.get('prime_ttc', 0)) if garantie_sinistre.get('prime_ttc', 0) else None,
                    created_by_id=request.user.id,
                )
                garantie_sinistre_created.save()
                garantie_sinistre = SinistreGarantie.objects.get(id=garantie_sinistre_created.pk)

                historique_garantie_sinistre_created = HistoriqueSinistreGarantie(
                    sinistre_garantie=garantie_sinistre,
                    historique_sinistre=historique_sinistre,
                    mouvement=Mouvement.objects.get(code=mouvement_id),
                    date_mouvement=today,
                    created_by_id=request.user.id,
                )
                historique_garantie_sinistre_created.save()
                historique_garantie_sinistre = HistoriqueSinistreGarantie.objects.get(id=historique_garantie_sinistre_created.pk)

                garantie_sinistre.historique_garantie_sinistre = historique_garantie_sinistre
                garantie_sinistre.save()

            response = {
                'statut': 1,
                'message': "Sinistre enregistré avec succès !",
                'data': {
                    'id': sinistre.pk,
                    'numero': sinistre.numero,
                }
            }

            return JsonResponse(response)

        else:
            response = {
                'statut': 0,
                'message': "Veuillez renseigner correctement le formulaire",
                'errors': form.errors,
            }

            return JsonResponse(response)
    else:
        response = {
            'statut': 0,
            'message': "Cette méthode n'est pas reconnue !",
        }

        return JsonResponse(response)


@method_decorator(login_required, name='dispatch')
class DossierSinistresView(TemplateView):
    template_name = 'liste_dossiers_sinistres.html'
    model = Sinistre

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        typesinistres = TypeSinistre.objects.filter(statut=1).order_by('libelle')
        clients = Client.objects.order_by('-nom')

        context['typesinistres'] = typesinistres
        context['clients'] = clients

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


def dossier_sinistre_datatable(request):
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    draw = int(request.GET.get('draw', 1))

    sort_column_index = int(request.GET.get('order[0][column]', 0))
    sort_direction = request.GET.get('order[0][dir]', 'asc')

    search_num_sinistre = request.GET.get('num_sinistre', '')
    search_date_declaration = request.GET.get('date_declaration', '')
    search_type_sinistre = request.GET.get('type_sinistre', '')
    search_client = request.GET.get('client', '')

    queryset = Sinistre.objects.all()

    # Filtres
    if search_num_sinistre:
        queryset = queryset.filter(numero__icontains=search_num_sinistre)

    if search_date_declaration:
        queryset = queryset.filter(date_declaration=search_date_declaration)

    if search_type_sinistre:
        queryset = queryset.filter(type_sinistre_id=search_type_sinistre)

    if search_client:
        queryset = queryset.filter(police__client_id=search_client)

    # Tri
    sort_columns = {
        0: 'numero',
        1: 'police__client__nom',
        2: 'type_sinistre__libelle',
        3: 'circonstance__libelle',
        4: 'date_declaration',
        5: 'date_survenance',
        6: 'statut',
    }
    sort_column = sort_columns.get(sort_column_index, 'id')
    if sort_direction == 'desc':
        sort_column = '-' + sort_column

    queryset = queryset.order_by(sort_column)

    # Pagination
    total_records = queryset.count()

    if length == -1:
        page_queryset = queryset  # pas de pagination
    else:
        page_number = start // length + 1
        paginator = Paginator(queryset, length)
        try:
            page_queryset = paginator.page(page_number)
        except EmptyPage:
            page_queryset = paginator.page(paginator.num_pages)

    # Formatage des données
    data = []
    for sin in page_queryset:
        detail_url = reverse('details_dossier_sinistre', args=[sin.id])
        actions_html = f'<a href="{detail_url}" target="_blank"><span class="badge btn-sm btn-details rounded-pill"><i class="fa fa-eye"></i> Détails</span></a>'
        numero_html = f'<a href="{detail_url}" class="text-center bouton_action" style="color:#F16623;" target="_blank">{sin.numero}</a>'
        if sin.etat_sinistre:
            statut_html = f'<span class="badge badge-{sin.etat_sinistre.lower().replace(" ", "-")}">{sin.etat_sinistre}</span>'
        else:
            statut_html = '<span class="badge badge-secondary">En attente</span>'

        data.append({
            "id": sin.id,
            "numero": numero_html,
            "client": f"{sin.police.client.nom or ''} {sin.police.client.prenoms or ''}",
            "type_sinistre": sin.type_sinistre.libelle if sin.type_sinistre else "",
            "circonstance": sin.circonstance.libelle if sin.circonstance else "",
            "date_declaration": sin.date_declaration.strftime("%d/%m/%Y") if sin.date_declaration else "",
            "date_survenance": sin.date_survenance.strftime("%d/%m/%Y") if sin.date_survenance else "",
            "statut": statut_html,
            "actions": actions_html,
        })

    return JsonResponse({
        "data": data,
        "recordsTotal": total_records,
        "recordsFiltered": total_records,
        "draw": draw,
    })


#Liste des sinistres annulés
@method_decorator(login_required, name='dispatch')
class AnnulerSinistreGestionnairesView(TemplateView):
    template_name = 'annuler_sinistre.html'
    model = Sinistre

    #traitement à l'appel du lien en get
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        context['breadcrumbs'] = [
            {'title': 'Sinistres', 'url': ''},
            {'title': 'Annulation', 'url': ''},
        ]
        return self.render_to_response(context)

    #traitement à l'appel du lien en post pour la recherche de dossier et la suppresion de dossier ou sinistre
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        #recuperation de tout ce qui peut venir en post que ca soit pour la recherche ou la suppression
        btn_recherche = self.request.POST.get('recherche', None)
        submit_delete_item = self.request.POST.get('submit_delete_item', None)
        type_item = self.request.POST.get('type_item', None)
        id_item = self.request.POST.get('id_item', None)
        motif_delete_item = self.request.POST.get('motif_delete_item', None)
        code_dossier_sinistre = self.request.POST.get('code_dossier_sinistre', None)
        context['breadcrumbs'] = [
            {'title': 'Sinistres', 'url': ''},
            {'title': 'Annulation', 'url': ''},
        ]
        dossier_sinistre = None

        #cette condition précise que nous venons faire la recherche
        if btn_recherche and code_dossier_sinistre:
            print(code_dossier_sinistre)
            dossier_sinistre = DossierSinistre.objects.filter(numero=code_dossier_sinistre, bureau=request.user.bureau).exclude(statut_validite=StatutValidite.SUPPRIME).first()
            # dd(dossier_sinistre)if
            #si on a trouver le dossier on récupère infos liées y compris les sinistres qui le composent
            if dossier_sinistre:
                sinistres = Sinistre.objects.filter(dossier_sinistre=dossier_sinistre).exclude(statut_validite=StatutValidite.SUPPRIME)
                total_frais_reel = dossier_sinistre.total_frais_reel + dossier_sinistre.total_frais_reel_medicament
                total_part_compagnie = dossier_sinistre.total_part_compagnie + dossier_sinistre.total_part_compagnie_medicament
                total_part_assure = dossier_sinistre.total_part_assure + dossier_sinistre.total_part_assure_medicament
                cartes = dossier_sinistre.aliment.cartes.filter(statut=Statut.ACTIF) if dossier_sinistre.aliment else None
                numero_carte = cartes.first().numero if cartes else None
                has_sinistre_on_facture = sinistres.filter(facture_prestataire__isnull=False).exists()
                context['sinistres'] = sinistres
                context['total_frais_reel'] = total_frais_reel
                context['total_part_compagnie'] = total_part_compagnie
                context['total_part_assure'] = total_part_assure
                context['numero_carte'] = numero_carte
                context['has_sinistre_on_facture'] = sinistres.filter(facture_prestataire__isnull=False).exists()

        #cette condition précise que nous venons faire la suppression de soit un dossier ou un sinistre
        if submit_delete_item and type_item and id_item:
            #dd(self.request.POST)
            if type_item == "dossier": #il s'agit de la suppresion d'un et les sinistres qui le composent
                dossier_sinistre = DossierSinistre.objects.filter(id=id_item, bureau=request.user.bureau).exclude(statut_validite=StatutValidite.SUPPRIME).first()
                if dossier_sinistre: #vérification selon données postées et suppression du dossier
                    sinistres = Sinistre.objects.filter(dossier_sinistre=dossier_sinistre)
                    code_dossier_sinistre = dossier_sinistre.numero
                    has_sinistre_on_facture = sinistres.filter(facture_prestataire__isnull=False).exists()

                    if has_sinistre_on_facture is False: #assure qu'un dossier est entiermeent annulé que si aucun de ses sinistres n'est sur une facture prestataire
                        dossier_sinistre.statut_validite = StatutValidite.SUPPRIME
                        dossier_sinistre.is_closed = True
                        #dd(dossier_sinistre)
                        dossier_sinistre.save()

                    for sinistre in sinistres: #suppression des sinistres qui composent le dossier
                        if sinistre.facture_prestataire is None: #assure que le sinistre n'est pas sur une facture prestataire
                            sinistre.statut_validite = StatutValidite.SUPPRIME
                            sinistre.statut = StatutValidite.SUPPRIME
                            sinistre.motif_suppression = motif_delete_item
                            sinistre.save()
            elif type_item == "selection_sinistre": #il s'agit de la suppresion d'une selection de sinistres du dossier recherché
                selected_sinistres = Sinistre.objects.filter(id__in=id_item.split(",")).exclude(statut_validite=StatutValidite.SUPPRIME, statut=StatutValidite.SUPPRIME)
                #dd(selected_sinistres.count())
                for sinistre in selected_sinistres:
                    if sinistre.facture_prestataire is None: #assure que le sinistre n'est pas sur une facture prestataire
                        sinistre.statut_validite = StatutValidite.SUPPRIME
                        sinistre.statut = StatutValidite.SUPPRIME
                        sinistre.motif_suppression = motif_delete_item
                        sinistre.save()
                        dossier_sinistre = sinistre.dossier_sinistre
                        code_dossier_sinistre = dossier_sinistre.numero
            else: #il s'agit de la suppresion d'un sinistre du dossier recherché
                sinistre = Sinistre.objects.filter(id=id_item).exclude(statut_validite=StatutValidite.SUPPRIME, statut=StatutValidite.SUPPRIME).first()
                if sinistre and sinistre.facture_prestataire is None: #vérification selon données postées et suppression
                    sinistre.statut_validite = StatutValidite.SUPPRIME
                    sinistre.statut = StatutValidite.SUPPRIME
                    sinistre.motif_suppression = motif_delete_item
                    sinistre.save()
                    dossier_sinistre = sinistre.dossier_sinistre
                    code_dossier_sinistre = dossier_sinistre.numero


        context['code_dossier_sinistre'] = code_dossier_sinistre
        context['dossier_sinistre'] = dossier_sinistre
            #print(code_dossier_sinistre)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@method_decorator(login_required, name='dispatch')
class DossiersSinistresPhysiquesGestionnairesView(TemplateView):
    template_name = 'liste_dossiers_sinistres.html'
    model = Sinistre

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        sinistres = []
        prestataires = []
        rubriques = Rubrique.objects.all()
        # dossiers_sinistres = [x for x in DossierSinistre.objects.all().order_by('-id') if x.sinistres.filter(statut=StatutSinistre.ATTENTE).exists()]

        # context['bureaux'] = bureaux
        context['sinistres'] = sinistres
        context['prestataires'] = prestataires
        context['rubriques'] = rubriques
        context['types_remboursements'] = TypeRemboursement.objects.filter(status=True)

        context['yesterday'] = datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(days=1)
        context['today'] = datetime.datetime.now(tz=timezone.utc)

        today = datetime.datetime.now(tz=timezone.utc)
        context['today'] = today
        context['breadcrumbs'] = [
            {'title': 'Prises en charges', 'url': ''},
            {'title': 'Traités', 'url': ''},
        ]

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


def dossiersinistre_physique_gestionnaire_datatable(request):
    items_per_page = 10
    page_number = request.GET.get('page')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', items_per_page))
    sort_column_index = int(request.GET.get('order[0][column]'))
    sort_direction = request.GET.get('order[0][dir]')

    search_numero_assure = request.GET.get('num_assure', '')
    search_numero_dossier_sinistre = request.GET.get('num_feuille_soins', '')
    search_date_survenance = request.GET.get('date_prestation', '')
    prestataire = request.GET.get('prestataire', '')

    pprint("search_numero_assure")
    pprint(search_numero_assure)

    pprint("search_numero_dossier_sinistre")
    pprint(search_numero_dossier_sinistre)

    pprint("search_date_survenance")
    pprint(search_date_survenance)

    queryset = DossierSinistre.objects.filter(bureau=request.user.bureau, statut_validite=StatutValidite.VALIDE, of_gestionnaire=1).order_by('id')
    # dd(queryset)

    if prestataire:
         queryset = queryset.filter(prestataire_id=prestataire)

    if search_numero_assure:
        cartes = Carte.objects.filter(numero=search_numero_assure)
        carte = cartes.first() if cartes else None
        aliment = carte.aliment if carte else None
        queryset = queryset.filter(aliment_id=aliment.pk) if aliment else queryset.filter(numero="nexisterajamais")

    if search_numero_dossier_sinistre:
        queryset = queryset.filter(numero__contains=search_numero_dossier_sinistre)
    if search_date_survenance:
        queryset = queryset.filter(created_at__contains=search_date_survenance)



    # Map column index to corresponding model field for sorting
    sort_columns = {
        0: '-numero',
        1: 'aliment__nom',
        2: 'statut',
        # Add more columns as needed
    }

    # Default sorting by 'id' if column index is not found
    sort_column = sort_columns.get(sort_column_index, 'id')

    if sort_direction == 'desc':
        sort_column = '-' + sort_column  # For descending order

    # Apply sorting
    queryset = queryset.order_by(sort_column)

    paginator = Paginator(queryset, length)
    page_obj = paginator.get_page(page_number)

    # Prepare the data in the expected format
    data = []
    for c in page_obj:
        detail_url = reverse('details_dossier_sinistre', args=[c.id])  # URL to the detail view# URL to the detail view
        actions_html = f'<a href="{detail_url}"><span class="badge btn-sm btn-details rounded-pill"><i class="fa fa-eye"></i> Détails</span></a>&nbsp;&nbsp;'

        if request.user.is_pharm:
            type_or_numero_carte = aliment.carte_active if aliment else ''
        else:
            if request.user.is_med and c.type_priseencharge.code == "CONSULT":
                type_or_numero_carte = "PHARMACIE"
            else:
                type_or_numero_carte = c.type_priseencharge.libelle if c.type_priseencharge else ''

        if not c.aliment:
            c.aliment.nom = ''
        if not c.aliment:
            c.aliment.prenoms = ''


        if request.user.is_pharm:
            total_frais_reel = c.total_frais_reel_medicament
            total_part_compagnie = c.total_part_compagnie_medicament
            total_part_assure = c.total_part_assure_medicament
        elif request.user.is_prestataire:
            total_frais_reel = c.new_total_frais_reel
            total_part_compagnie = c.new_total_part_compagnie_prestataire
            total_part_assure = c.new_total_part_assure_prestataire
        else:
            total_frais_reel = c.new_total_frais_reel
            total_part_compagnie = c.new_total_part_compagnie_gestionnaire
            total_part_assure = c.new_total_part_assure_gestionnaire


        statut_html = f'<span class="badge badge-{c.statut.lower()}">{c.statut}</span>'

        data_iten = {
            "id": c.id,
            "numero": c.numero if c.numero else "",
            "type_or_numero_carte": type_or_numero_carte,
            "nom": c.aliment.nom + ' ' + c.aliment.prenoms,
            "total_frais_reel": money_field(total_frais_reel),
            "total_part_compagnie": money_field(total_part_compagnie),
            "total_part_assure": money_field(total_part_assure),
            "date_prestation": c.created_at.strftime("%d/%m/%Y %H:%M"),
            "statut": statut_html,
            "actions": actions_html,
        }

        if request.user.is_med:
            statut_prorogation_html = f'<span class="badge badge-{c.statut_prorogation.replace(" ", "-").lower()}">{c.statut_prorogation}</span>' if c.statut_prorogation else ''
            data_iten["statut_prorogation"] = statut_prorogation_html

        data.append(data_iten)

    return JsonResponse({
        "data": data,
        "recordsTotal": queryset.count(),
        "recordsFiltered": paginator.count,
        "draw": int(request.GET.get('draw', 1)),
    })


@method_decorator(login_required, name='dispatch')
class DetailsDossierSinistreView_v1(TemplateView):
    permission_required = "sinistre.view_sinistre"
    template_name = 'details_dossier_sinistre.html'
    model = Sinistre

    def get(self, request, sinistre_id, *args, **kwargs):

        sinistre = Sinistre.objects.filter(id=sinistre_id)

        if sinistre:
            print(f"Sinistre ID: {sinistre_id}")
            context = self.get_context_data(**kwargs)
            context['sinistre'] = sinistre

            return self.render_to_response(context)

        else:
            return redirect('/')

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@method_decorator(login_required, name='dispatch')
class DetailsDossierSinistreView(TemplateView):
    template_name = 'details_dossier_sinistre.html'
    model = Sinistre

    def get(self, request, sinistre_id, *args, **kwargs):
        try:
            sinistre = Sinistre.objects.get(id=sinistre_id)
        except Sinistre.DoesNotExist:
            return redirect('/')

        mouvement_sinistre = MouvementSinistre.objects.filter(sinistre_id=sinistre.id, statut_validite=StatutValidite.VALIDE).order_by('-id').first()

        context = self.get_context_data(**kwargs)
        context['sinistre'] = sinistre
        context['mouvement_sinistre'] = mouvement_sinistre
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@method_decorator(login_required, name='dispatch')
class GEDDossierSinistreView(TemplateView):
    template_name = 'ged_dossier_sinistre.html'
    model = Sinistre

    def get(self, request, sinistre_id, *args, **kwargs):
        try:
            sinistre = Sinistre.objects.get(id=sinistre_id)
        except Sinistre.DoesNotExist:
            return redirect('/')

        documents = Document.objects.filter(sinistre_id=sinistre.id)
        typedocuments = TypeDocument.objects.filter(is_sinistre=1, is_production=0)

        context = self.get_context_data(**kwargs)
        context['sinistre'] = sinistre
        context['documents'] = documents
        context['typedocuments'] = typedocuments
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


def add_document_sinistre(request, sinistre_id):
    if request.method == "POST":

        form = DocumentForm(request.POST, request.FILES)

        if form.is_valid():

            sinistre = Sinistre.objects.get(id=sinistre_id)
            type_document_id = request.POST.get('type_document')

            document = form.save(commit=False)
            document.sinistre = sinistre
            document.type_document = TypeDocument.objects.get(id=type_document_id)
            document.save()

            response = {
                'statut': 1,
                'message': "Enregistrement effectue avec succes !",
                'data': {
                    'id': document.pk,
                    'nom': document.nom,
                    'fichier': '<a href="' + document.fichier.url + '"><i class="fa fa-file" title="Aperçu"></i> Afficher</a>',
                    'type_document': document.type_document.libelle,
                    'confidentialite': document.confidentialite,
                }
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Veuillez renseigner correctement le formulaire !",
                'errors': form.errors,
            }

            return JsonResponse(response)


@method_decorator(login_required, name='dispatch')
class IntervenantDossierSinistreView(TemplateView):
    template_name = 'intervenant_dossier_sinistre.html'
    model = Sinistre

    def get(self, request, sinistre_id, *args, **kwargs):
        try:
            sinistre = Sinistre.objects.get(id=sinistre_id)
        except Sinistre.DoesNotExist:
            return redirect('/')

        intervenants = SinistreIntervenant.objects.filter(sinistre_id=sinistre.id)

        context = self.get_context_data(**kwargs)
        context['sinistre'] = sinistre
        context['intervenants'] = intervenants
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def details_intervenant(request, sinistre_intervenant_id):
    sinistre_intervenant = SinistreIntervenant.objects.get(id=sinistre_intervenant_id)

    context = {
        'sinistre_intervenant': sinistre_intervenant,
    }
    return render(request, 'details_intervenant.html', context)


@method_decorator(login_required, name='dispatch')
class MouvementDossierSinistreView(TemplateView):
    template_name = 'mouvement_dossier_sinistre.html'
    model = Sinistre

    def get(self, request, sinistre_id, *args, **kwargs):
        try:
            sinistre = Sinistre.objects.get(id=sinistre_id)
        except Sinistre.DoesNotExist:
            return redirect('/')

        mouvements_sinistre = MouvementSinistre.objects.filter(sinistre_id=sinistre.id)

        mouvements = Mouvement.objects.filter(type_mouvement_id=2)

        context = self.get_context_data(**kwargs)
        context['sinistre'] = sinistre
        context['mouvements_sinistre'] = mouvements_sinistre
        context['mouvements'] = mouvements
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


def motifs_by_mouvement(request, mouvement_id):
    motifs = Motif.objects.filter(mouvement_id=mouvement_id) #.exclude(code__in=["INCOR", "RETRAIT"])

    motifs_serialize = serializers.serialize('json', motifs)
    return HttpResponse(motifs_serialize, content_type='application/json')


@login_required
def mouvement_sinistre(request, sinistre_id, motif_id):
    sinistre = Sinistre.objects.filter(id=sinistre_id).first()
    if sinistre:
        motif = Motif.objects.filter(id=motif_id).first()
        if not motif:
            return redirect(f'/sinistre/dossier_sinistre/{sinistre_id}/mouvements')

        police = Police.objects.get(id=sinistre.police_id, bureau=request.user.bureau, statut_validite='VALIDE')

        # Récupération de client
        client = Client.objects.get(id=police.client_id)

        # Récupérer le dernier historique
        dernier_historique = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()

        # Récupérer les assureurs associés à l'historique
        assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id, type_compagnie_id=1).first() if dernier_historique else None
        today = timezone.now().date()

        typesinistres = TypeSinistre.objects.filter(statut=1).order_by('libelle')
        typeintervenants = TypeIntervenant.objects.filter(statut=1).order_by('libelle')
        typedocuments = TypeDocument.objects.filter(is_sinistre=1).order_by('libelle')
        responsabilites = TauxResponsabilite.objects.filter(statut=1)
        circonstances = Circonstance.objects.filter(statut=1, branche_id=police.produit.branche_id).order_by('libelle')

        pays = Pays.objects.all().order_by('nom')

        mouvements = Mouvement.objects.filter(id=motif.mouvement_id, type_mouvement_id=2)

        liste_motifs = Motif.objects.filter(mouvement_id=motif.mouvement_id)

        gestionnaire_sinistres = []

        utilisateur = User.objects.all().order_by('-first_name').exclude(is_admin_group=1)
        for user in utilisateur:
            if user.is_sinistre:
                gestionnaire_sinistres.append(user)

        context = {
            'sinistre': sinistre,
            'check_motif': motif,
            'police': police,
            'client': client,
            'dossiers_sinistres': None,
            'sinistres': None,
            'dernier_historique': dernier_historique,
            'assureur_police': assureur_police,
            'today': today,
            'typesinistres': typesinistres,
            'typeintervenants': typeintervenants,
            'typedocuments': typedocuments,
            'responsabilites': responsabilites,
            'circonstances': circonstances,
            'pays': pays,
            'mouvements': mouvements,
            'liste_motifs': liste_motifs,
            'gestionnaire_sinistres': gestionnaire_sinistres,
        }

        return render(request, 'mouvement_sinistre.html', context)

    return redirect('dossiersinistre')



@login_required
def update_sinistre_gestionnaire(request, sinistre_id):
    sinistre = Sinistre.objects.filter(id=sinistre_id).first()
    if sinistre:
        if request.method == 'POST':
            pass

    return redirect('dossiersinistre')

