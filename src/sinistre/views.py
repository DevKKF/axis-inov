import datetime
import json
import io
import os
from ast import literal_eval
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from django.utils.timezone import now
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
from django.db.models import Sum, Q, ExpressionWrapper, F, DurationField, Max, Subquery, OuterRef
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.db.models import Value, F
from django.db.models.functions import Concat
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import get_template
from django.db import IntegrityError
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
from django.core.exceptions import ObjectDoesNotExist
import re
from uuid import uuid4
import uuid
from django.templatetags.static import static

from configurations.helper_config import execute_query
from configurations.models import Compagnie, User, Rubrique, ModeReglement, Bureau, \
    TypePriseencharge, Pays, TypeIntervenant, TauxResponsabilite, TypeSinistre, Circonstance, Garantie, GarantieCirconstance, PosteDommage, \
    PeriodeComptable, TypeRemboursement, ModeCreation, TypePrefinancement
from production.models import Statut, TypeDocument, Client
#
from production.models import Police, HistoriquePolice, HistoriqueAliment, PoliceAssureur, PeriodeCouverture, Mouvement, Motif, AlimentPolice, Document, AutreRisque, Marchandise, \
    Vehicule, PoliceGarantie
from production.forms import DocumentForm
from production.templatetags.my_filters import money_field, supprimer_espaces, normalize_text
from shared.enum import StatutPolice
from shared.enum import StatutSinistre, StatutSinistreBordereau, StatutSinistrePrestation, StatutValidite, \
    StatutRemboursement, StatutRemboursementSinistre, DesignationRemboursementSinistre, SatutBordereauDossierSinistres, \
    StatutPaiementSinistre, TypeBonConsultation
from sinistre.helper_sinistre import exportation_en_excel_avec_style, \
    extraction_demandes_accords_prealables_traitees_par_medecins_conseil, extraction_des_sinistres_traites_valides, \
    requete_demandes_accords_prealables_traitees_par_les_medecins_conseil, requete_liste_des_sp_client_par_filiale, \
    requete_liste_paiement_sinistre_sante_entre_deux_dates, \
    requete_liste_sinistre_entre_2date, requete_analyse_prime_compta, \
    requete_liste_sinistre_saisies_entre_2date, requete_sinistres_traites_et_valides_par_les_gestionnaires, \
    requete_analyse_prime_compta_apporteur, get_retenue_selon_contexte
# Create your views here.
from sinistre.models import PaiementComptable, Sinistre, HistoriqueSinistre, Intervenant, SinistreIntervenant, SinistreGarantie, HistoriqueSinistreGarantie, DossierSinistre, MouvementSinistre, \
    RemboursementSinistre, BordereauOrdonnancement, VentilationProvision, VentilationRecour, ReglementSinistre

from sinistre.forms import SinistreForm

from shared.helpers import renderpdf


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

    today = datetime.now(tz=timezone.utc)
    yesterday = datetime.now(tz=timezone.utc) - timedelta(days=3)
    queryset = DossierSinistre.objects.filter(statut_validite=StatutValidite.VALIDE, bureau=request.user.bureau, has_sinistre_traite_bymedecin=True, date_traitement_sinistre_bymedecin__date__gte=yesterday).order_by('-id')

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
            total_frais_reel = ""
            total_part_compagnie = ""
            total_part_assure = ""
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

        print("🔁 Lancement du chargement des intervenants")

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


@login_required
@transaction.atomic
def save_session_garanties(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            garanties_existantes = request.session.get('garanties', [])
            today = timezone.now().date()

            # Extraire les IDs existants pour vérifier les doublons
            existing_ids = {g['garantie_id'] for g in garanties_existantes if g.get('garantie_id') is not None}

            duplicates_count = 0
            for g in data.get('garanties', []):
                garantie_id = g.get('id')
                if not garantie_id:  # Ignorer si garantie_id est None ou vide
                    continue

                if garantie_id in existing_ids:
                    duplicates_count += 1
                    continue  # Ignorer les doublons

                # Vérifier la présence des champs obligatoires
                if not all(k in g for k in ['nom', 'franchise', 'capital']):
                    continue  # Ignorer si les champs essentiels sont manquants

                nouvelle_garantie = {
                    'id': str(uuid.uuid4()),
                    'sinistre_id': None,  # À remplir plus tard si nécessaire
                    'garantie_id': f'{garantie_id}',
                    'nom': g.get('nom'),
                    'franchise': g.get('franchise'),
                    'capital': g.get('capital'),
                    'mouvement': "Ouverture Sinistre",
                    'date_ajout': today.isoformat(),
                    'action_mouvement': "Ajout",
                }
                garanties_existantes.append(nouvelle_garantie)
                existing_ids.add(garantie_id)  # Ajout au set pour les prochains tours

            request.session['garanties'] = garanties_existantes
            request.session.modified = True

            message = "Ajout de garantie effectué avec succès !"
            if duplicates_count > 0:
                message += f" {duplicates_count} doublon(s) ignoré(s)."

            return JsonResponse({
                'success': True,
                'message': message,
                'data': garanties_existantes
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Erreur : Données JSON invalides.'
            }, status=400)
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

    print("Garanties récupérées :", formatted_garanties)

    return JsonResponse({"garanties": formatted_garanties})


@login_required
def recuperer_garantie_session(request):
    poste_dommages = PosteDommage.objects.filter(statut=1).order_by('numero_ordre')
    garantie_sinistres = request.session.get("garanties", [])

    formatted_garanties = []
    for garantie in garantie_sinistres:
        formatted_garanties.append({
            "id": garantie.get('id'),
            "garantie_id": garantie.get('garantie_id'),
            "nom": garantie.get('nom'),
        })

    context = {
        'poste_dommages': poste_dommages,
        'garantie_sinistres': formatted_garanties,
    }
    return render(request, 'sinistre_garantie_session.html', context)


#Save Sinistre by Gestionnaire
@login_required
@transaction.atomic
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
            aliment_police = ''
            if autre_risque_id:
                autre_risque = AlimentPolice.objects.filter(autre_risque_id=autre_risque_id).first()
                aliment_police = autre_risque.id if autre_risque else None
            if marchandise_id:
                marchandise = AlimentPolice.objects.filter(marchandise_id=marchandise_id).first()
                aliment_police = marchandise.id if marchandise else None
            if vehicule_id:
                vehicule = AlimentPolice.objects.filter(vehicule_id=vehicule_id).first()
                aliment_police = vehicule.id if vehicule else None

            dernier_historique = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()

            if not date_survenance:
                return JsonResponse({
                    'statut': 0,
                    'message': "Veuillez renseigner la date de survenance du sinistre !",
                })

            fractionnement_code = dernier_historique.fractionnement.code
            intervalle = None
            if fractionnement_code == "ANNUEL":
                intervalle = timedelta(days=4 * 365)  # 4 ans
            elif fractionnement_code == "SEMESTRIEL":
                intervalle = timedelta(days=2 * 365)  # 2 ans
            elif fractionnement_code == "TRIMESTRIEL":
                intervalle = timedelta(days=1 * 365)  # 1 an
            elif fractionnement_code == "MENSUEL":
                intervalle = timedelta(days=4 * 30)  # 4 mois
            else:
                intervalle = 0

            date_survenance_conv = datetime.strptime(date_survenance, "%Y-%m-%d")
            date_recherche_debut = ''
            if isinstance(intervalle, int):
                date_recherche_debut = date_survenance_conv - timedelta(days=intervalle)
            elif isinstance(intervalle, timedelta):
                date_recherche_debut = date_survenance_conv - intervalle

            date_debut = date_recherche_debut if fractionnement_code else police.date_debut_effet
            date_fin = datetime.strptime(date_survenance, "%Y-%m-%d")

            # Construire la requête avec les nouvelles contraintes de date
            q_filter = Q(
                police_id=police.id,
                date_debut_effet__lte=date_fin,
            ) & (
               Q(date_fin_effet__gte=date_debut) | Q(date_fin_effet__isnull=True)
            )

            # Rechercher une période de couverture correspondante
            periode_valide = PeriodeCouverture.objects.filter(q_filter).first()

            if periode_valide:
                sinistre_created = Sinistre(
                    client_id=client.id,
                    police_id=police.id,
                    aliment_police_id=aliment_police if aliment_police else None,
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
                    aliment_police_id=aliment_police if aliment_police else None,
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
                ms.mouvement = Mouvement.objects.get(code=mouvement_id)
                ms.motif = Motif.objects.get(code=motif_mouvement_id)
                ms.date_effet = sinistre.date_ouverture
                ms.created_by = request.user
                ms.save()

                # Récupérer les intervenants de la session
                intervenants = request.session.get('intervenants', [])
                for intervenant_data in intervenants:
                    # Récupérer les champs de portable et téléphone
                    portable = intervenant_data.get('portable')
                    telephone = intervenant_data.get('telephone')

                    # Vérifier si un intervenant existe déjà avec le même portable ou téléphone
                    intervenant = None
                    if portable:
                        try:
                            intervenant = Intervenant.objects.get(portable=portable)
                        except ObjectDoesNotExist:
                            pass
                    if not intervenant and telephone:
                        try:
                            intervenant = Intervenant.objects.get(telephone=telephone)
                        except ObjectDoesNotExist:
                            pass

                    # Si aucun intervenant n'existe, créer un nouvel intervenant
                    if not intervenant:
                        intervenant_created = Intervenant(
                            type_intervenant_id=intervenant_data.get('type_intervenant_id'),
                            pays_id=intervenant_data.get('pays_id'),
                            nom=intervenant_data.get('nom'),
                            prenoms=intervenant_data.get('prenoms'),
                            portable=portable,
                            telephone=telephone,
                            fax=intervenant_data.get('fax'),
                            email=intervenant_data.get('email'),
                            code_postal=intervenant_data.get('code_postal'),
                            boite_postale=intervenant_data.get('boite_postale'),
                            ville=intervenant_data.get('ville'),
                            created_by_id=request.user.id,
                        )
                        intervenant_created.save()
                        intervenant = intervenant_created

                    # Créer l'entrée dans SinistreIntervenant avec l'intervenant existant ou nouvellement créé
                    sinistre_intervenant = SinistreIntervenant(
                        sinistre=sinistre,
                        historique_sinistre=historique_sinistre,
                        intervenant=intervenant,
                        created_by_id=request.user.id,
                    )
                    sinistre_intervenant.save()

                # Récupérer les garanties de la session
                garanties_sinistre = request.session.get("garanties", [])
                for garantie_sinistre in garanties_sinistre:
                    garantie_sinistre_created = SinistreGarantie.objects.create(
                        sinistre=sinistre,
                        garantie_id=garantie_sinistre.get('garantie_id'),
                        franchise=supprimer_espaces(garantie_sinistre.get('franchise', 0)) or None,
                        capital=supprimer_espaces(garantie_sinistre.get('capital', 0)) or None,
                        prime_nette=supprimer_espaces(garantie_sinistre.get('prime_net', 0)) or None,
                        prime_ttc=supprimer_espaces(garantie_sinistre.get('prime_ttc', 0)) or None,
                        created_by=request.user,
                    )

                    historique_garantie_sinistre_created = HistoriqueSinistreGarantie.objects.create(
                        sinistre_garantie=garantie_sinistre_created,
                        historique_sinistre=historique_sinistre,
                        mouvement=Mouvement.objects.get(code=mouvement_id),
                        motif=Motif.objects.get(code=motif_mouvement_id),
                        date_mouvement=today,
                        created_by=request.user,
                    )

                    # Associe directement l'objet sans refaire un .get()
                    garantie_sinistre_created.historique_sinistre_garantie = historique_garantie_sinistre_created
                    garantie_sinistre_created.save()

                motif_return = Motif.objects.get(code=motif_mouvement_id)

                import re

                ventilations_struct = {}
                for key, value in request.POST.items():
                    if key.startswith('montant_ventilation_provisions['):
                        try:
                            parts = key.split('[')
                            poste_id = parts[1].rstrip(']')
                            garantie_id = parts[2].rstrip(']')
                            champ = parts[3].rstrip(']')  # montant_provision, montant_regle, provisionne

                            # 🔹 Nettoyage : enlever tous les espaces (y compris \u202f, \xa0, etc.)
                            montant_nettoye = re.sub(r'\s+', '', value) if value.strip() else '0'
                            montant_valeur = float(montant_nettoye)

                            ventilations_struct.setdefault(poste_id, {}).setdefault(garantie_id, {})[
                                champ] = montant_valeur

                        except Exception as e:
                            print(f"Erreur parsing {key}: {e}")

                # Dictionnaire pour cumuler les provisions par garantie
                garantie_prov_totaux = {}

                for poste_id, garanties in ventilations_struct.items():
                    for garantie_id, champs in garanties.items():
                        montant_provision = champs.get('montant_provision', 0)
                        montant_regle = champs.get('montant_regle', 0)

                        if montant_provision != 0:
                            obj, created = VentilationProvision.objects.update_or_create(
                                sinistre=sinistre,
                                poste_dommage_id=poste_id,
                                garantie_id=garantie_id,
                                defaults={
                                    'montant_provision': montant_provision,
                                    'montant_regle': montant_regle,
                                    'created_by': request.user
                                }
                            )

                            # Cumuler les montants de provision par garantie
                            garantie_prov_totaux[garantie_id] = garantie_prov_totaux.get(garantie_id,
                                                                                         0) + montant_provision

                # Mise à jour des SinistreGarantie avec le cumul par garantie
                for garantie_id, total_provision in garantie_prov_totaux.items():
                    garantie = SinistreGarantie.objects.filter(
                        garantie_id=garantie_id,
                        sinistre_id=sinistre.id
                    ).first()
                    if garantie:
                        garantie.montant_provision = total_provision if total_provision > 0 else None
                        garantie.save(update_fields=["montant_provision"])

                return JsonResponse({
                    'statut': 1,
                    'message': "Sinistre enregistré avec succès !",
                    'url_return': reverse('mouvement_sinistre', args=[sinistre.id, motif_return.id])
                })
            else:
                return JsonResponse({
                    'statut': 0,
                    'message': "La date de survenance n'est pas comprise dans une période de couverture valide.",
                })

        else:
            return JsonResponse({
                'statut': 0,
                'message': "Veuillez renseigner correctement le formulaire",
                'errors': form.errors,
            })
    else:
        return JsonResponse({
            'statut': 0,
            'message': "Cette méthode n'est pas reconnue !",
        })


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
            statut_html = '<span class="badge badge-success">En cours</span>'

        data.append({
            "id": sin.id,
            "numero": numero_html,
            "client": f"{sin.police.client.nom or ''} {sin.police.client.prenoms or ''}",
            "type_sinistre": sin.type_sinistre.libelle if sin.type_sinistre else "",
            "circonstance": sin.circonstance.libelle if sin.circonstance else "",
            "date_declaration": sin.date_declaration.strftime("%d/%m/%Y") if sin.date_declaration else "",
            "date_survenance": sin.date_survenance.strftime("%d/%m/%Y") if sin.date_survenance else "",
            "etat_sinistre": sin.etat_actu_sinistre,
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
                total_frais_reel = dossier_sinistre.total_frais_reel
                total_part_compagnie = dossier_sinistre.total_part_compagnie
                total_part_assure = dossier_sinistre.total_part_assure
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

    queryset = DossierSinistre.objects.filter(bureau=request.user.bureau, statut_validite=StatutValidite.VALIDE, of_gestionnaire=1).order_by('id')

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
            total_frais_reel = ""
            total_part_compagnie = ""
            total_part_assure = ""
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


@login_required
@transaction.atomic
def add_document_sinistre(request, sinistre_id):
    if request.method == "POST":

        form = DocumentForm(request.POST, request.FILES)

        if form.is_valid():

            sinistre = Sinistre.objects.get(id=sinistre_id)
            type_document_id = request.POST.get('type_document')

            document = form.save(commit=False)
            document.sinistre = sinistre
            document.historique_sinistre_id = sinistre.historique_sinistre_id
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

        mouvements_sinistre = MouvementSinistre.objects.filter(sinistre_id=sinistre.id).order_by('-id')

        mouvements = Mouvement.objects.filter(type_mouvement_id=2).order_by('id')

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


@method_decorator(login_required, name='dispatch')
class DetailMouvementDossierSinistreView(TemplateView):
    template_name = 'historique_sinistre_detail.html'
    model = HistoriqueSinistre

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        sinistre_id = kwargs['sinistre_id']
        hist_sinistre_id = kwargs['historique_sinistre_id']
        hist_sinistres = HistoriqueSinistre.objects.filter(id=hist_sinistre_id)
        detail_sinistre = Sinistre.objects.filter(id=sinistre_id)

        if hist_sinistres:
            hist_sinistre = hist_sinistres.first()
            sinistre = detail_sinistre.first()

            intervenants = SinistreIntervenant.objects.filter(historique_sinistre_id=hist_sinistre_id)
            documents = Document.objects.filter(historique_sinistre_id=hist_sinistre_id)
            garanties = HistoriqueSinistreGarantie.objects.filter(historique_sinistre_id=hist_sinistre_id)

            context_perso = {
                'sinistre': sinistre,
                'historiquesinistre': hist_sinistre,
                'intervenants': intervenants,
                'documents': documents,
                'garanties': garanties,
            }
            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        else:
            # liste_dossiersinistre_url = reverse('dossiersinistre')
            return redirect("dossiersinistre")

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


def motifs_by_mouvement(request, mouvement_id):
    motifs = Motif.objects.filter(mouvement_id=mouvement_id).order_by('libelle').order_by('id')

    motifs_serialize = serializers.serialize('json', motifs)
    return HttpResponse(motifs_serialize, content_type='application/json')


@login_required
def mouvement_sinistre(request, sinistre_id, motif_id):
    sinistre = Sinistre.objects.filter(id=sinistre_id).first()

    intervenants = request.session.get('intervenants', None)
    # Vider les intervenants enregistrés en session
    if 'intervenants' in request.session:
        del request.session['intervenants']

    garanties = request.session.get('garanties', None)
    # Vider les garanties enregistrées en session
    if 'garanties' in request.session:
        del request.session['garanties']

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
        mode_reglements = ModeReglement.objects.order_by('libelle')
        responsabilites = TauxResponsabilite.objects.filter(statut=1)
        circonstances = Circonstance.objects.filter(statut=1, branche_id=police.produit.branche_id).order_by('libelle')
        intervenant_sinistres = SinistreIntervenant.objects.filter(sinistre_id=sinistre.id)
        pays = Pays.objects.all().order_by('nom')

        mouvements = Mouvement.objects.filter(id=motif.mouvement_id, type_mouvement_id=2).order_by('id')

        liste_motifs = Motif.objects.filter(mouvement_id=motif.mouvement_id).order_by('id')

        gestionnaire_sinistres = []

        utilisateur = User.objects.all().order_by('-first_name').exclude(is_admin_group=1)
        for user in utilisateur:
            if user.is_sinistre:
                gestionnaire_sinistres.append(user)

        poste_dommages = PosteDommage.objects.filter(statut=1).order_by('numero_ordre')
        garantie_sinistres = SinistreGarantie.objects.filter(sinistre_id=sinistre.id, date_cloture=None)
        ventilation_provision_existantes = VentilationProvision.objects.filter(sinistre=sinistre).values('id', 'poste_dommage_id', 'garantie_id', 'montant_provision', 'montant_regle')
        ventilation_recours_existantes = VentilationRecour.objects.filter(sinistre=sinistre).values('poste_dommage_id', 'garantie_id', 'montant_recours', 'montant_regle')

        # On transforme en dictionnaire pour accès rapide dans le template
        ventilations_dict_provision = {
            (v['poste_dommage_id'], v['garantie_id']): v
            for v in ventilation_provision_existantes
        }

        ventilation_reglement_map = {
            (v["poste_dommage_id"], v["garantie_id"]): v["montant_provision"] or 0
            for v in ventilation_provision_existantes
        }

        ventilations_dict_recours = {
            (v['poste_dommage_id'], v['garantie_id']): v
            for v in ventilation_recours_existantes
        }

        sommes = garantie_sinistres.aggregate(
            total_provisions=Sum('montant_provision'),
            total_provisions_regle=Sum('montant_provision_regle'),
            total_recours=Sum('montant_recours'),
            total_montant_recours_regle=Sum('montant_recours_regle'),
            total_montant_garantie=Sum('montant_garantie'),
        )

        police_garanties = PoliceGarantie.objects.filter(police_id=sinistre.police_id)
        police_garanties_ids = police_garanties.values_list("garantie_id", flat=True)

        garantie_recours = garantie_sinistres.filter(garantie_id__in=police_garanties_ids)

        context = {
            'sinistre': sinistre,
            'check_motif': motif,
            'police': police,
            'client': client,
            'dernier_historique': dernier_historique,
            'assureur_police': assureur_police,
            'today': today,
            'typesinistres': typesinistres,
            'typeintervenants': typeintervenants,
            'typedocuments': typedocuments,
            'responsabilites': responsabilites,
            'mode_reglements': mode_reglements,
            'circonstances': circonstances,
            'pays': pays,
            'mouvements': mouvements,
            'liste_motifs': liste_motifs,
            'gestionnaire_sinistres': gestionnaire_sinistres,
            'poste_dommages': poste_dommages,
            'garantie_sinistres': garantie_sinistres,
            'garantie_recours': garantie_recours,
            'ventilations_dict_provision': ventilations_dict_provision,
            'ventilations_dict_recours': ventilations_dict_recours,
            'intervenant_sinistres': intervenant_sinistres,
            'ventilation_reglement_map': ventilation_reglement_map,
            'total_provisions': sommes['total_provisions'],
            'total_provisions_regle': sommes['total_provisions_regle'],
            'total_recours': sommes['total_recours'],
            'total_montant_recours_regle': sommes['total_montant_recours_regle'],
            'total_montant_garantie': sommes['total_montant_garantie'],
        }

        return render(request, 'mouvement_sinistre.html', context)

    return redirect('dossiersinistre')


def recuperer_intervenant_sinistre(request):
    sinistre_id = request.GET.get('sinistre_id')

    try:
        sinistre_intervenants = SinistreIntervenant.objects.filter(sinistre_id=sinistre_id)
        intervenants_existant = list(request.session.get('intervenants', []))

        # Liste pour stocker les numéros de portable déjà présents
        portables_existant = {intervenant['portable'] for intervenant in intervenants_existant if intervenant['portable']}

        for sinistre_interv in sinistre_intervenants:
            # Vérifier si le numéro de portable existe déjà
            if sinistre_interv.intervenant.portable and sinistre_interv.intervenant.portable in portables_existant:
                continue  # Ignorer l'ajout si le portable est déjà présent

            nouveau_intervenant = {
                'id': str(uuid4()),
                'sinistre_id': sinistre_id,
                'nom': sinistre_interv.intervenant.nom,
                'prenoms': sinistre_interv.intervenant.prenoms,
                'telephone': sinistre_interv.intervenant.telephone,
                'fax': sinistre_interv.intervenant.fax,
                'email': sinistre_interv.intervenant.email,
                'portable': sinistre_interv.intervenant.portable,
                'pays_id': sinistre_interv.intervenant.pays_id,
                'type_intervenant_id': sinistre_interv.intervenant.type_intervenant.id,
                'type_intervenant': sinistre_interv.intervenant.type_intervenant.libelle,
                'boite_postale': sinistre_interv.intervenant.boite_postale,
                'code_postal': sinistre_interv.intervenant.code_postal,
                'ville': sinistre_interv.intervenant.ville,
            }

            intervenants_existant.append(nouveau_intervenant)
            portables_existant.add(sinistre_interv.intervenant.portable)  # Ajouter le nouveau portable à la liste
            request.session['intervenants'] = intervenants_existant
            request.session.modified = True

        intervenants_existants = list(request.session.get('intervenants', []))

        return JsonResponse({
            'success': True,
            'message': "Ajout d'intervenant effectué avec succès !",
            'data': intervenants_existants
        }, status=200)

    except SinistreIntervenant.DoesNotExist:
        return JsonResponse({'error': 'Sinistre non trouvé.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def recuperer_garantie_sinistre(request):
    sinistre_id = request.GET.get('sinistre_id')
    try:
        sinistre_garanties = SinistreGarantie.objects.filter(sinistre_id=sinistre_id, deleted_at=None)
        garanties_existantes = list(request.session.get('garanties', []))

        for nouvelle_garan in sinistre_garanties:
            montant = (
                    nouvelle_garan.montant_provision
                    or nouvelle_garan.montant_provision_regle
                    or nouvelle_garan.montant_recours
                    or nouvelle_garan.montant_recours_regle
                    or 0
            )
            print(f'montant {montant}')
            nouvelle_garantie = {
                'id': f'{nouvelle_garan.garantie_id}',
                'sinistre_id': sinistre_id,
                'garantie_id': f'{nouvelle_garan.garantie_id}',
                'nom': nouvelle_garan.garantie.nom,
                'franchise': money_field(nouvelle_garan.franchise),
                'capital': money_field(nouvelle_garan.capital),
                'montant': money_field(montant),
                'mouvement': nouvelle_garan.sinistre_garantie_premier_historique.motif.libelle,
                'date_ajout': nouvelle_garan.created_at.strftime('%Y-%m-%d'),
                'action_mouvement': "Aucun"
            }

            garanties_existantes.append(nouvelle_garantie)
            request.session['garanties'] = garanties_existantes
            request.session.modified = True

        garanties_existantes = list(request.session.get('garanties', []))

        return JsonResponse({
            'success': True,
            'message': "Ajout de garantie effectué avec succès !",
            'data': garanties_existantes
        }, status=200)

    except SinistreGarantie.DoesNotExist:
        return JsonResponse({'error': 'Sinistre non trouvé.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def cloture_garantie(request, garantie_id):
    if request.method == 'POST':
        garanties = list(request.session.get('garanties', []))

        # Parcourir les garanties et modifier action_mouvement pour celle correspondant à garantie_id
        modified = False
        for g in garanties:
            if str(g["garantie_id"]) == f'{garantie_id}':
                g["action_mouvement"] = "Cloture"
                modified = True
                break

        if modified:
            request.session["garanties"] = garanties
            request.session.modified = True
            request.session.save()

            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "message": "Garantie non trouvée."}, status=404)

    return JsonResponse({"success": False, "message": "Méthode non autorisée."}, status=405)



@login_required
@transaction.atomic
def update_sinistre_gestionnaire(request, sinistre_id):
    sinistre = Sinistre.objects.filter(id=sinistre_id).first()
    today = timezone.now().date()
    if sinistre:
        if request.method == 'POST':
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
            recours_possible = request.POST.get('recours_possible')
            reg_intervenant_id = request.POST.get('reg_intervenant_id')
            mode_reglement_id = request.POST.get('mode_reglement')
            numero_piece = request.POST.get('numero_piece')
            date_reglement = request.POST.get('date_reglement')

            if tva_recuperee_str == "1":
                tva_recuperee = True
            elif tva_recuperee_str == "0":
                tva_recuperee = False
            else:
                tva_recuperee = None

            sinistre.type_sinistre_id = type_sinistre_id
            sinistre.taux_responsabilite_id = taux_responsabilite_id
            sinistre.circonstance_id = circonstance_id
            sinistre.gestionnaire_sinistre_id = gestionnaire_sinistre_id
            sinistre.operateur_de_saisie_id = request.user.id
            sinistre.numero = numero
            sinistre.risque_sinistre = risque_sinistre
            sinistre.date_survenance = date_survenance if date_survenance else None
            sinistre.date_declaration = date_declaration if date_declaration else None
            sinistre.date_ouverture = date_ouverture if date_ouverture else None
            sinistre.date_cloture = date_cloture if date_cloture else None
            sinistre.date_reouverture = date_reouverture if date_reouverture else None
            sinistre.lieu_survenance = lieu_survenance
            sinistre.tva_recuperee = tva_recuperee if tva_recuperee else 0
            sinistre.fait_generateur = fait_generateur
            sinistre.point_de_choc = point_de_choc
            sinistre.commentaires = commentaires
            sinistre.recours_possible = recours_possible
            sinistre.franchise = supprimer_espaces(franchise) if franchise else 0
            sinistre.updated_by = request.user
            sinistre.save()

            historique_sinistre_created = HistoriqueSinistre(
                sinistre=sinistre,
                aliment_police_id=sinistre.aliment_police_id,
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
                mouvement=Mouvement.objects.get(id=mouvement_id),
                motif_mouvement=Motif.objects.get(id=motif_mouvement_id),

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

            # Mise à jour de l'ancien mouvement sinistre
            mouvement_sinistre = MouvementSinistre.objects.filter(sinistre_id=sinistre.id, historique_sinistre_id=None).first()
            print(mouvement_sinistre)
            mouvement_sinistre.historique_sinistre_id = historique_sinistre.id if historique_sinistre else None
            mouvement_sinistre.save()

            # Mettre à jour l'historique du sinistre
            sinistre.historique_sinistre = historique_sinistre
            sinistre.save()

            # Créer une ligne de mouvement_sinistre avec le mouvement ouverture sinistre et le motif ouverture sinistre
            ms = MouvementSinistre()
            ms.sinistre = sinistre
            ms.mouvement = Mouvement.objects.get(id=mouvement_id)
            ms.motif = Motif.objects.get(id=motif_mouvement_id)
            ms.date_effet = sinistre.date_ouverture
            ms.created_by = request.user
            ms.save()

            # Précharger les garanties existantes avec des clés int pour éviter les problèmes de comparaison
            garanties_existantes = {
                int(g.garantie_id): g
                for g in SinistreGarantie.objects.filter(sinistre=sinistre, deleted_at=None)
            }

            # Récupérer la liste depuis la session
            garanties_sinistre = request.session.get("garanties", [])
            print(garanties_sinistre)
            try:
                # Si mouvement_id est un id numérique :
                mouvement_obj = Mouvement.objects.get(pk=mouvement_id)
            except Mouvement.DoesNotExist:
                mouvement_obj = None

            for garantie_sinistre in garanties_sinistre:
                raw_gid = garantie_sinistre.get('garantie_id')
                raw_action_mouvement = garantie_sinistre.get('action_mouvement')

                # Normaliser la clé en int (skip si invalide)
                try:
                    gid = int(raw_gid)
                except (TypeError, ValueError):
                    print(f"garantie_id invalide dans la session: {raw_gid!r} — on l'ignore")
                    continue

                # Nettoyage des champs (ex: supprimer espaces)
                franchise = supprimer_espaces(garantie_sinistre.get('franchise', 0)) or None
                capital = supprimer_espaces(garantie_sinistre.get('capital', 0)) or None
                prime_nette = supprimer_espaces(garantie_sinistre.get('prime_net', 0)) or None
                prime_ttc = supprimer_espaces(garantie_sinistre.get('prime_ttc', 0)) or None

                if gid in garanties_existantes:
                    # --- Mise à jour
                    garantie_obj = garanties_existantes[gid]

                    # Mettre à jour les champs uniquement si besoin (optionnel)
                    changed = False
                    if garantie_obj.franchise != franchise:
                        garantie_obj.franchise = franchise
                        changed = True
                    if garantie_obj.capital != capital:
                        garantie_obj.capital = capital
                        changed = True
                    if garantie_obj.prime_nette != prime_nette:
                        garantie_obj.prime_nette = prime_nette
                        changed = True
                    if garantie_obj.prime_ttc != prime_ttc:
                        garantie_obj.prime_ttc = prime_ttc
                        changed = True

                    # Normaliser l'action et gérer la clôture
                    action_norm = normalize_text(raw_action_mouvement)
                    if action_norm == 'cloture':
                        garantie_obj.date_cloture = today
                        garantie_obj.deleted_by = request.user
                        garantie_obj.deleted_at = timezone.now()
                        changed = True

                    if changed:
                        garantie_obj.save(update_fields=['franchise', 'capital', 'prime_nette', 'prime_ttc', 'date_cloture', 'deleted_by', 'deleted_at'])

                    # Création historique si besoin
                    if mouvement_obj:
                        historique_garantie = HistoriqueSinistreGarantie.objects.create(
                            sinistre_garantie=garantie_obj,
                            historique_sinistre=historique_sinistre,
                            mouvement=mouvement_obj,
                            motif=Motif.objects.get(id=motif_mouvement_id),
                            date_mouvement=today,
                            created_by=request.user,
                        )
                        # Liaison (si le modèle a ce champ)
                        garantie_obj.historique_sinistre_garantie = historique_garantie
                        garantie_obj.save(update_fields=['historique_sinistre_garantie'])

                else:
                    # --- Création
                    garantie_obj = SinistreGarantie.objects.create(
                        sinistre=sinistre,
                        garantie_id=gid,
                        franchise=franchise,
                        capital=capital,
                        prime_nette=prime_nette,
                        prime_ttc=prime_ttc,
                        created_by=request.user,
                    )

                    # Ajouter au cache local pour éviter une recréation si la session contient des doublons
                    garanties_existantes[gid] = garantie_obj

                    if mouvement_obj:
                        historique_garantie = HistoriqueSinistreGarantie.objects.create(
                            sinistre_garantie=garantie_obj,
                            historique_sinistre=historique_sinistre,
                            mouvement=mouvement_obj,
                            motif=Motif.objects.get(id=motif_mouvement_id),
                            date_mouvement=today,
                            created_by=request.user,
                        )
                        garantie_obj.historique_sinistre_garantie = historique_garantie
                        garantie_obj.save(update_fields=['historique_sinistre_garantie'])

            # Récupérer tous les intervenants existants indexés par portable ou téléphone
            intervenants_existants = {
                i.portable: i for i in Intervenant.objects.exclude(portable__isnull=True).exclude(portable__exact='')
            }
            intervenants_existants.update({
                i.telephone: i for i in Intervenant.objects.exclude(telephone__isnull=True).exclude(telephone__exact='')
            })

            # Récupérer les intervenants de la session
            intervenants_session = request.session.get('intervenants', [])

            for data in intervenants_session:
                portable = data.get('portable')
                telephone = data.get('telephone')

                intervenant = None

                # Chercher par portable ou téléphone
                if portable and portable in intervenants_existants:
                    intervenant = intervenants_existants[portable]
                elif telephone and telephone in intervenants_existants:
                    intervenant = intervenants_existants[telephone]

                # Si aucun intervenant trouvé → créer
                if not intervenant:
                    intervenant = Intervenant.objects.create(
                        type_intervenant_id=data.get('type_intervenant_id'),
                        pays_id=data.get('pays_id'),
                        nom=data.get('nom'),
                        prenoms=data.get('prenoms'),
                        portable=portable,
                        telephone=telephone,
                        fax=data.get('fax'),
                        email=data.get('email'),
                        code_postal=data.get('code_postal'),
                        boite_postale=data.get('boite_postale'),
                        ville=data.get('ville'),
                        created_by_id=request.user.id,
                    )

                    # Mettre à jour le cache local pour éviter de recréer si on le retrouve plus tard
                    if portable:
                        intervenants_existants[portable] = intervenant
                    if telephone:
                        intervenants_existants[telephone] = intervenant

                # Lier à ce sinistre
                SinistreIntervenant.objects.create(
                    sinistre=sinistre,
                    historique_sinistre=historique_sinistre,
                    intervenant=intervenant,
                    created_by_id=request.user.id,
                )

            ventilations_struct = {}
            for key, value in request.POST.items():
                if key.startswith('montant_ventilation_provisions['):
                    try:
                        parts = key.split('[')
                        poste_id = parts[1].rstrip(']')
                        garantie_id = parts[2].rstrip(']')
                        champ = parts[3].rstrip(']')  # montant_provision, montant_regle, provisionne

                        montant_nettoye = value.replace(' ', '') if value.strip() else '0'
                        montant_valeur = float(montant_nettoye)

                        ventilations_struct.setdefault(poste_id, {}).setdefault(garantie_id, {})[champ] = montant_valeur

                    except Exception as e:
                        print(f"Erreur parsing {key}: {e}")

            # Dictionnaire pour cumuler les provisions par garantie
            garantie_totaux = {}

            for poste_id, garanties in ventilations_struct.items():
                for garantie_id, champs in garanties.items():
                    montant_provision = champs.get('montant_provision', 0)
                    montant_regle = champs.get('montant_regle', 0)

                    if montant_provision != 0:
                        obj, created = VentilationProvision.objects.update_or_create(
                            sinistre=sinistre,
                            poste_dommage_id=poste_id,
                            garantie_id=garantie_id,
                            defaults={
                                'montant_provision': montant_provision,
                                'montant_regle': montant_regle,
                                'created_by': request.user
                            }
                        )

                        # Cumuler les provisions de chaque garantie
                        garantie_totaux[garantie_id] = garantie_totaux.get(garantie_id, 0) + montant_provision

            # Mise à jour des SinistreGarantie avec le cumul par garantie
            for garantie_id, total_provision in garantie_totaux.items():
                garantie = SinistreGarantie.objects.filter(
                    garantie_id=garantie_id,
                    sinistre_id=sinistre.id
                ).first()
                if garantie:
                    garantie.montant_provision = total_provision
                    garantie.save(update_fields=["montant_provision"])

            ventilations_rec_struct = {}
            for key, value in request.POST.items():
                if key.startswith('montant_ventilation_recours['):
                    try:
                        parts = key.split('[')
                        poste_id = parts[1].rstrip(']')
                        garantie_id = parts[2].rstrip(']')
                        champ = parts[3].rstrip(']')  # montant_recours, montant_regle, recours

                        montant_nettoye = value.replace(' ', '') if value.strip() else '0'
                        montant_valeur = float(montant_nettoye)

                        ventilations_rec_struct.setdefault(poste_id, {}).setdefault(garantie_id, {})[
                            champ] = montant_valeur

                    except Exception as e:
                        print(f"Erreur parsing {key}: {e}")

            # Dictionnaire pour cumuler les recours par garantie
            garantie_rec_totaux = {}

            for poste_id, garanties in ventilations_rec_struct.items():
                for garantie_id, champs in garanties.items():
                    montant_recours = champs.get('montant_recours', 0)
                    montant_regle = champs.get('montant_regle', 0)

                    if montant_recours != 0:
                        obj, created = VentilationRecour.objects.update_or_create(
                            sinistre=sinistre,
                            poste_dommage_id=poste_id,
                            garantie_id=garantie_id,
                            defaults={
                                'montant_recours': montant_recours,
                                'montant_regle': montant_regle,
                                'created_by': request.user
                            }
                        )

                        # Cumuler les montants de recours par garantie
                        garantie_rec_totaux[garantie_id] = garantie_rec_totaux.get(garantie_id, 0) + montant_recours

            # Mise à jour des SinistreGarantie avec le cumul par garantie
            for garantie_id, total_recours in garantie_rec_totaux.items():
                garantie = SinistreGarantie.objects.filter(
                    garantie_id=garantie_id,
                    sinistre_id=sinistre.id
                ).first()
                if garantie:
                    garantie.montant_recours = total_recours if total_recours > 0 else None
                    garantie.save(update_fields=["montant_recours"])

            # Enregistrer les règlements
            try:
                motif = Motif.objects.get(id=motif_mouvement_id)
            except Motif.DoesNotExist:
                return JsonResponse({'statut': 0, 'message': "Motif invalide"})

            code_bureau = request.user.bureau.code
            annee = timezone.now().strftime("%y")
            prefix = f"{code_bureau}R{annee}"
            # Récupérer le dernier numéro de règlement pour ce préfixe
            dernier_reglement = ReglementSinistre.objects.filter(
                numero_reglement__startswith=prefix
            ).aggregate(last_num=Max("numero_reglement"))

            dernier_numero = dernier_reglement["last_num"]

            if dernier_numero:
                compteur = int(dernier_numero[-6:]) + 1
            else:
                compteur = 1

            # Générer le nouveau numéro
            numero_reglement = f"{prefix}{str(compteur).zfill(6)}"

            if motif.code == "SAISREG":
                for key, value in request.POST.items():
                    if key.startswith("montant_reglements[") and key.endswith("][montant_reglement]"):
                        try:
                            # Extraire proprement
                            inner = key[len("montant_reglements["):-len("][montant_reglement]")]
                            # Exemple: "5][3"
                            poste_id, garantie_id = inner.split("][")
                        except ValueError:
                            print(f"Clé ignorée (format inattendu): {key}")
                            continue

                        montant_str = value.strip().replace(" ", "").replace(",", ".")
                        try:
                            montant = Decimal(montant_str) if montant_str else Decimal("0")
                        except Exception:
                            montant = Decimal("0")

                        if montant > 0:
                            ventilation = VentilationProvision.objects.filter(
                                sinistre_id=sinistre.id,
                                poste_dommage_id=poste_id,
                                garantie_id=garantie_id
                            ).first()

                            sinistre_garantie = SinistreGarantie.objects.filter(
                                sinistre_id=sinistre.id,
                                garantie_id=garantie_id
                            ).first()

                            if reg_intervenant_id and mode_reglement_id and date_reglement:
                                if ventilation:
                                    ReglementSinistre.objects.create(
                                        sinistre=sinistre,
                                        ventilation_provision=ventilation,
                                        sinistre_intervenant_id=reg_intervenant_id,
                                        mode_reglement_id=mode_reglement_id,
                                        devise=sinistre.police.client.pays.devise if sinistre.police.client.pays else None,  # idem
                                        numero_reglement=numero_reglement,
                                        montant_regle=montant,
                                        numero_piece=numero_piece,
                                        date_reglement=date_reglement,
                                        created_by=request.user
                                    )

                                    # mise à jour de ventilation provision
                                    ventilation.montant_provision = ventilation.montant_provision - montant
                                    ventilation.montant_regle += montant
                                    ventilation.save(update_fields=["montant_provision", "montant_regle"])

                                    # mise à jour de la garantie sinistre
                                    if sinistre_garantie:
                                        sinistre_garantie.montant_provision = sinistre_garantie.montant_provision - montant
                                        sinistre_garantie.montant_provision_regle += montant
                                        sinistre_garantie.montant_garantie += montant
                                        sinistre_garantie.save(update_fields=["montant_provision", "montant_provision_regle", "montant_garantie"])
                            else:
                                return JsonResponse({
                                    'statut': 0,
                                    'message': "Veuillez renseigner correctement le formulaire au niveau de l'onglet de règlement!",
                                })
            else:
                pass

            if motif.code == "SAISREG":
                response = {
                    'statut': 2,
                    'message': "Sinistre modifié avec succès et réglement enregistré!",
                    'url_return': reverse('recu_reglement_sinistre', args=[sinistre.id, numero_reglement])
                }
            else:
                response = {
                    'statut': 1,
                    'message': "Sinistre modifié avec succès !",
                    'data': {
                        'id': sinistre.pk,
                        'numero': sinistre.numero,
                    }
                }

            return JsonResponse(response)

    return redirect('dossiersinistre')


def recu_reglement_sinistre_v0(request, sinistre_id, numero_reglement):
    sinistre = Sinistre.objects.filter(id=sinistre_id).first()
    reglement_sinistre = ReglementSinistre.objects.filter(numero_reglement=numero_reglement)

    site_logo_url = request.build_absolute_uri(static(settings.JAZZMIN_SETTINGS['site_logo']))

    bureau = Bureau.objects.filter(code="CI01").first()

    rec_reglement_sinistre = ReglementSinistre.objects.filter(sinistre_id=sinistre.id, numero_reglement=numero_reglement).first()

    date_reglement_sin = rec_reglement_sinistre.date_reglement

    sommes = reglement_sinistre.aggregate(
        montant_total_reglement_sinistre=Sum('montant_regle'),
    )

    net_a_payer_lettre = num2words(sommes['montant_total_reglement_sinistre'], lang="fr")

    # Premier rendu pour compter les pages
    pdf_bytes = renderpdf('courriers/recu_reglement_sinistre.html', {
        'sinistre': sinistre,
        'reglement_sinistre': reglement_sinistre,
        'rec_reglement_sinistre': rec_reglement_sinistre,
        'date_reglement_sin': date_reglement_sin,
        'numero_reglement': numero_reglement,
        'site_logo_url': site_logo_url,
        'bureau': bureau,
        'montant_total_reglement_sinistre': sommes['montant_total_reglement_sinistre'],
        'net_a_payer_lettre': net_a_payer_lettre,
    })

    if not pdf_bytes:
        return HttpResponse("Erreur lors de la génération du PDF", status=500)

    pdf_file = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    nombre_pages = len(pdf_file.pages)

    # Refaire le rendu avec le nombre de pages
    pdf_bytes = renderpdf('courriers/recu_reglement_sinistre.html', {
        'sinistre': sinistre,
        'reglement_sinistre': reglement_sinistre,
        'rec_reglement_sinistre': rec_reglement_sinistre,
        'date_reglement_sin': date_reglement_sin,
        'numero_reglement': numero_reglement,
        'nombre_pages': nombre_pages,
        'site_logo_url': site_logo_url,
        'bureau': bureau,
        'montant_total_reglement_sinistre': sommes['montant_total_reglement_sinistre'],
        'net_a_payer_lettre': net_a_payer_lettre,
    })

    if not pdf_bytes:
        return HttpResponse("Erreur lors de la génération du PDF", status=500)

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response['Content-Disposition'] = f'inline; filename="recu_reglement_{numero_reglement}.pdf"'
    return response


def recu_reglement_sinistre(request, sinistre_id, numero_reglement):
    sinistre = Sinistre.objects.filter(id=sinistre_id).first()
    reglement_sinistre = ReglementSinistre.objects.filter(numero_reglement=numero_reglement).select_related(
        "sinistre_intervenant__intervenant",
        "ventilation_provision__garantie",
        "ventilation_provision__poste_dommage"
    )

    site_logo_url = request.build_absolute_uri(static(settings.JAZZMIN_SETTINGS['site_logo']))
    bureau = Bureau.objects.filter(code="CI01").first()

    rec_reglement_sinistre = ReglementSinistre.objects.filter(
        sinistre_id=sinistre.id,
        numero_reglement=numero_reglement
    ).first()

    date_reglement_sin = rec_reglement_sinistre.date_reglement if rec_reglement_sinistre else None

    sommes = reglement_sinistre.aggregate(
        montant_total_reglement_sinistre=Sum('montant_regle'),
    )

    montant_total = sommes['montant_total_reglement_sinistre'] or 0
    net_a_payer_lettre = num2words(montant_total, lang="fr")

    # 🔹 Regrouper les règlements par numero_reglement pour gérer le rowspan
    grouped = defaultdict(list)
    for reg in reglement_sinistre:
        grouped[reg.numero_reglement].append(reg)

    reglement_struct = []
    for num, regs in grouped.items():
        reglement_struct.append({
            "numero_reglement": num,
            "rowspan": len(regs),
            "reglements": regs
        })

    # Premier rendu pour compter les pages
    pdf_bytes = renderpdf('courriers/recu_reglement_sinistre.html', {
        'sinistre': sinistre,
        'reglement_struct': reglement_struct,
        'rec_reglement_sinistre': rec_reglement_sinistre,
        'date_reglement_sin': date_reglement_sin,
        'numero_reglement': numero_reglement,
        'site_logo_url': site_logo_url,
        'bureau': bureau,
        'montant_total_reglement_sinistre': montant_total,
        'net_a_payer_lettre': net_a_payer_lettre,
    })

    if not pdf_bytes:
        return HttpResponse("Erreur lors de la génération du PDF", status=500)

    pdf_file = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    nombre_pages = len(pdf_file.pages)

    # Deuxième rendu avec le nombre de pages
    pdf_bytes = renderpdf('courriers/recu_reglement_sinistre.html', {
        'sinistre': sinistre,
        'reglement_struct': reglement_struct,
        'rec_reglement_sinistre': rec_reglement_sinistre,
        'date_reglement_sin': date_reglement_sin,
        'numero_reglement': numero_reglement,
        'nombre_pages': nombre_pages,
        'site_logo_url': site_logo_url,
        'bureau': bureau,
        'montant_total_reglement_sinistre': montant_total,
        'net_a_payer_lettre': net_a_payer_lettre,
    })

    if not pdf_bytes:
        return HttpResponse("Erreur lors de la génération du PDF", status=500)

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response['Content-Disposition'] = f'inline; filename="recu_reglement_{numero_reglement}.pdf"'
    return response