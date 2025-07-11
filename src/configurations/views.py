# Create your views here.
import datetime
import os
from ast import literal_eval
from decimal import Decimal
from pprint import pprint
from sqlite3 import Date
from datetime import date

import pandas as pd
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Permission
from django.contrib.sessions.models import Session
from django.core import serializers
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.template.backends.django import Template
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django_dump_die.middleware import dd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from datetime import datetime, timezone
from django.db.models import Sum, Q, ExpressionWrapper, F, DurationField, Max
from django.utils.timezone import now

from configurations.helper_config import verify_sql_query
from configurations.models import ActionLog, Secteur, \
    Bureau ,BusinessUnit, Branche, Banque, Apporteur, ApporteurInternational,Devise,\
    User, AuthGroup, TypeEtablissement,Tarif, Rubrique, \
    BackgroundQueryTask, ParamProduitCompagnie, Compagnie, \
    TypeApporteur, TypePersonne, Pays, TypeCompagnie, TypeGarant, TauxCommission, Carosserie, \
    CategorieVehicule, Civilite, CompteTresorerie, ConditionsAssurance, Carburant, Formule, Fractionnement, Garantie, GarantieFormule, \
    Groupe, ModeReglement, Circonstance, Responsabilite, TypeIntervenant, TypeMouvement, TypeSinistre, PosteDommage, GarantieCirconstance, RegroupementActe, Prescripteur, Prestataire, Acte, WsBoby, ParamWsBoby, TypeActe, ParamActe
from inov import settings
# Create your views here.
from production.models import Client, Mouvement, \
    Quittance, Reglement, Courrier, Produit, SecteurActivite, TypeDocument, Mouvement, Motif
from production.templatetags.my_filters import money_field
from shared.enum import PasswordType, Statut, StatutValidite, BaseCalculTM, StatutPaiementSinistre, \
    SatutBordereauDossierSinistres, StatutSinistre
from django.contrib import messages
from django.db import transaction

from sinistre.models import Sinistre, PaiementComptable, HistoriqueOrdonnancementSinistre, \
    HistoriquePaiementComptableSinistre, BordereauOrdonnancement
import json
import io

from .models import PrescripteurPrestataire
from production.models import Aliment, TarifPrestataireClient, Carte

from shared.helpers import generate_numero_famille_for_existing_aliment, generer_nombre_famille_du_mois_for_existing_aliment


def generate_numero_famille_all(request):
    aliments = Aliment.objects.filter(qualite_beneficiaire__code="AD", numero_famille__isnull=True)
    if aliments:
        for aliment in aliments:
            numero_famille = generate_numero_famille_for_existing_aliment(aliment)
            aliment.numero_famille = numero_famille
            aliment.save()

        response = {
            'statut': 1,
            'message': str(aliments.count()) + ' NUMEROS DE FAMILLES GENERES AVEC SUCCÈS'
        }

    else:
        response = {
            'statut': 0,
            'message': 'AUCUN ADHERENT PRINCIPAL SANS NUMEROS DE FAMILLE TROUVE'
        }

    return JsonResponse(response)


def generer_nombre_famille_du_mois_all(request):
    aliments = Aliment.objects.filter(qualite_beneficiaire__code="AD", numero_famille_du_mois__isnull=True)

    if aliments:
        for aliment in aliments:
            aliment.numero_famille_du_mois = generer_nombre_famille_du_mois_for_existing_aliment(aliment)
            aliment.save()

        response = {
            'statut': 1,
            'message': str(aliments.count()) + ' NOMBRE FAMILLES DU MOIS GENERES AVEC SUCCÈS'
        }

    else:
        response = {
            'statut': 0,
            'message': 'AUCUN ADHERENT PRINCIPAL SANS NOMBRE FAMILLE DU MOIS TROUVE'
        }

    return JsonResponse(response)


#Recalculer les parts des
def recalculer_parts_sinistres_sucaf(request):

    sinistres = Sinistre.objects.filter(police_id=207, type_prefinancement_id=3, dossier_sinistre_id__isnull=False)

    #dd(sinistres)

    cpt = 0
    if sinistres:
        for sinistre in sinistres:

            taux_couverture = sinistre.formulegarantie.taux_couverture
            taux_tm = sinistre.formulegarantie.taux_tm
            part_compagnie = Decimal(taux_couverture/100) * sinistre.frais_reel - sinistre.depassement
            part_assure = Decimal(taux_tm/100) * sinistre.frais_reel + sinistre.depassement

            #
            sinistre.part_compagnie = part_compagnie
            sinistre.part_assure = part_assure
            sinistre.type_prefinancement_id = 1
            sinistre.observation = 'Parts recalculées, et sinistre marqué comme préfinancé'
            sinistre.save()

            cpt = cpt + 1


        response = {
            'statut': 1,
            'message': str(cpt) + " SINISTRES ONT ETE RECALCULES AVEC SUCCÈS"
        }

    else:
        response = {
            'statut': 0,
            'message': "AUCUN SINISTRE TROUVE"
        }

    return JsonResponse(response)


def corriger_param_produit_compagnie(request):
    dd("DEJA EXECUTE, PAS BESOIN DE REEXECUTER, CONSERVER POUR UN USAGE ULTERIEUR")

    '''
    #marquer les compagnies qui ont des params taux différents
    compagnies = Compagnie.objects.all().order_by('id')
    cpt = 0
    for compagnie in compagnies:

        pprint(f'------ TRAITEMENT DES PARAMS DE LA COMPAGNIE: {compagnie.nom} (id={compagnie.id}) ------')
        params = ParamProduitCompagnie.objects.filter(compagnie=compagnie).order_by('id')

        pprint('params.count()')
        pprint(f'{params.count()} lignes de paramètres trouvés')

        if params:
            taux_com_gestion_ref = params.first().taux_com_gestion
            taux_com_courtage_ref = params.first().taux_com_courtage
            taux_com_courtage_terme_ref = params.first().taux_com_courtage_terme

            pprint("taux_com_gestion_ref")
            pprint(taux_com_gestion_ref)
            pprint("taux_com_courtage_ref")
            pprint(taux_com_courtage_ref)
            pprint("taux_com_courtage_terme_ref")
            pprint(taux_com_courtage_terme_ref)

            print("COMPARAISON DES LIGNES")
            cpt = 0
            for param in params:
                cpt = cpt + 1
                taux_com_gestion = param.taux_com_gestion
                taux_com_courtage = param.taux_com_courtage
                taux_com_courtage_terme = param.taux_com_courtage_terme

                print(f"LIGNE DE PARAM PRODUIT _N° {cpt}")
                pprint("taux_com_gestion")
                pprint(taux_com_gestion)
                pprint("taux_com_courtage")
                pprint(taux_com_courtage)
                pprint("taux_com_courtage_terme")
                pprint(taux_com_courtage_terme)

                if taux_com_gestion != taux_com_gestion_ref or taux_com_courtage != taux_com_courtage_ref or taux_com_courtage_terme != taux_com_courtage_terme_ref:
                    compagnie.has_taux_multiple = True
                    compagnie.save()
                    continue

                    pprint("DIFFERENTS DE LA PREMIERE LIGNE")

                else:
                    #dd(compagnie)
                    pprint ("IDENTIQUE A LA PREMIERE LIGNE")

            pprint(f'{params.count()} LIGNE(S) DE PARAM PRODUIT TROUVEE(S)')

        else:
            pprint("AUCUNE LIGNE DE PARAM PRODUIT TROUVEE")


        pprint(f'------ FIN DE TRAITEMENT POUR LA COMPAGNIE: {compagnie.nom} (id={compagnie.id}) ------')



    #désactiver les lignes doublons des lignes params qui n'ont pas changé
    compagnies = Compagnie.objects.filter(has_taux_multiple=False).order_by('id')
    for compagnie in compagnies:

        pprint(f'------ DESCATIVATION DES DOUBLONS DE PARAMS PRODUIT DE LA COMPAGNIE: {compagnie.nom} (id={compagnie.id}) ------')
        params = ParamProduitCompagnie.objects.filter(compagnie=compagnie).order_by('id')

        pprint('params.count()')
        pprint(f'{params.count()} lignes de paramètres trouvés')

        #si plusieurs lignes, désactivers garder la première et désactiver les autres
        if params.count() > 1:
            cpt_ligne_param = 0
            for param in params:
                cpt_ligne_param = cpt_ligne_param + 1
                if cpt_ligne_param > 1:

                    param.status = False
                    param.save()
                else:
                    pprint("LIGNE A CONSERVER")
                    pprint(param)

        pprint(f'------ FIN DESCATIVATION DES DOUBLONS DE PARAMS PRODUIT DE LA COMPAGNIE ------')

    response = {
        'statut': 1,
        'message': "OPERATION EFFECTUEE AVEC SUCCES"
    }

    return JsonResponse(response)
    
    '''


def correction_affections(request):

    affections = Affection.objects.all()

    #dd(affections)

    cpt = 0
    if affections:
        for affection in affections:

            cpt = cpt + 1


        response = {
            'statut': 1,
            'message': str(cpt) + " AFFECTIONS CORRIGEES AVEC SUCCÈS"
        }

    else:
        response = {
            'statut': 0,
            'message': "AUCUN AFFECTION TROUVE"
        }

    return JsonResponse(response)


def update_matricule(request):
    #marquer les compagnies qui ont des params taux différents
    aliments_matricules = ""

    if aliments_matricules:

        for am in aliments_matricules:

            carte = Carte.objects.filter(numero=am.NUMERO_CARTE).order_by('id')

            aliment = carte.aliment
            aliment.matricule_employe = am.MATRICULE
            aliment.save()

        response = {
            'statut': 1,
            'message': "OPERATION EFFECTUEE AVEC SUCCES"
        }

    else:
        response = {
            'statut': 0,
            'message': "AUCUNE DONNEE"
        }


    return JsonResponse(response)


def disponibilite_upd(request):
    message = {}
    message['heure'] = "LE SERVEUR PREND EN COMPTES LES CHANGEMENTS EFFECTUÉS DANS LE CODE - 19/12/2023 21:00"
    dd(message)


def redirecttohome(request):
    return redirect('/')


def clear_cache(request):
    cache.clear()

    return redirect('/')


@login_required
def custom_password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Additional logic after password change if needed
            user.password_type = PasswordType.CUSTOM
            user.save()
            pprint("Password has changed")

            return redirect('/')  # Redirect to password change success page
    else:
        form = PasswordChangeForm(user=request.user)

    pprint("custom_password_change")
    return render(request, 'registration/password_change_form.html', {'form': form})


def set_bureau(request):
    if request.method == 'POST':
        user = request.user

        if user.is_superuser or user.is_admin_group:
            bureau_id = request.POST.get('bureau_id')
            bureau = Bureau.objects.get(pk=bureau_id)
            user.bureau = bureau
            user.save()

    # Get the previous URL from the 'HTTP_REFERER' header, if available
    previous_page = request.META.get('HTTP_REFERER')

    # If the 'HTTP_REFERER' header is not available or points to the same URL,
    # redirect to a default URL (e.g., homepage).
    if not previous_page or previous_page == request.build_absolute_uri():
        return HttpResponseRedirect(reverse('home'))  # Replace 'home' with the name of your homepage URL pattern.
    else:
        return HttpResponseRedirect(previous_page)


class TarifsView(PermissionRequiredMixin, TemplateView):
    permission_required = "configurations.view_prestataire"
    template_name = 'tarifs/tarifs.html'
    model = Prestataire

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        rubriques = Rubrique.objects.filter(status=True)
        regroupements_actes = RegroupementActe.objects.filter(status=True)
        #
        tarifs_exists = Tarif.objects.filter(bureau=self.request.user.bureau).exists()

        context_perso = {
            'rubriques': rubriques,
            'regroupements_actes': regroupements_actes,
            'tarifs_exists': tarifs_exists,
        }

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


def tarifs_datatable(request):
    items_per_page = 10
    page_number = request.GET.get('page')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', items_per_page))
    sort_column_index = int(request.GET.get('order[0][column]'))
    sort_direction = request.GET.get('order[0][dir]')
    search_rubrique = request.GET.get('search_rubrique', '')
    search_code = request.GET.get('search_code', '')
    search_libelle = request.GET.get('search_libelle', '')
    search_value = request.GET.get('search[value]', '')

    user = request.user
    queryset = Tarif.objects.filter(bureau=user.bureau, statut=Statut.ACTIF, prestataire__isnull=True)

    if search_libelle:
        queryset = queryset.filter(
            Q(acte__libelle__icontains=search_libelle)
        )

    if search_code:
        queryset = queryset.filter(
            Q(acte__code__icontains=search_code)
        )

    if search_rubrique:
        queryset = queryset.filter(
            Q(acte__rubrique_id=search_rubrique)
        )

    # Map column index to corresponding model field for sorting
    sort_columns = {
        0: 'acte__code',
        1: 'acte__libelle',
        2: 'acte__lettre_cle',
        3: 'acte__rubrique__libelle',
        4: 'acte__regroupement_acte__libelle',
        5: 'cout_classique',
        6: 'cout_mutuelle',
        7: 'cout_public_hg',
        8: 'cout_public_chu',
        9: 'cout_public_ica',
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
    for p in page_obj:
        detail_url = reverse('popup_detail_tarif', args=[p.id])  # URL to the detail view

        actions_html = (
            f'<span style="cursor:pointer;" class=" btn-popup_details_tarif badge btn-sm btn-details rounded-pill" data-href="{detail_url}"<span class="badge btn-sm btn-details rounded-pill"><i class="fa fa-eye"></i> Détails</span>')

        data.append({
            "id": p.id,
            "code_acte": p.acte.code,
            "libelle_acte": p.acte.libelle,
            "lettre_cle_acte": p.acte.lettre_cle,
            "rubrique": p.acte.rubrique.libelle if p.acte.rubrique else "",
            "regroupement": p.acte.regroupement_acte.libelle if p.acte.regroupement_acte else "",
            "cout_classique": f'<span style="text-align:right;">' + money_field(p.cout_classique) + '</span>',
            "cout_mutuelle": f'<span style="text-align:right;">' + money_field(p.cout_mutuelle) + '</span>',
            "cout_public_hg": f'<span style="text-align:right;">' + money_field(p.cout_public_hg) + '</span>',
            "cout_public_chu": f'<span style="text-align:right;">' + money_field(p.cout_public_chu) + '</span>',
            "cout_public_ica": f'<span style="text-align:right;">' + money_field(p.cout_public_ica) + '</span>',
            "statut": p.statut,
            "actions": actions_html,
        })

    return JsonResponse({
        "data": data,
        "recordsTotal": queryset.count(),
        "recordsFiltered": paginator.count,
        "draw": int(request.GET.get('draw', 1)),
    })


def popup_detail_tarif(request, tarif_id):
    tarif = Tarif.objects.get(id=tarif_id)

    return render(request, 'tarifs/modal_details_tarif.html', {'tarif': tarif})


def add_tarif(request):
    '''
    if request.method == 'POST':
        name = request.POST.get('name')

        lettre_cle_public_hg = models.CharField(max_length=50, blank=True, null=True)
        coef_public_hg = models.CharField(max_length=50, blank=True, null=True)
        pu_public_hg = models.IntegerField(null=True)
        cout_public_hg = models.IntegerField(null=True)

        lettre_cle_public_chu = models.CharField(max_length=50, blank=True, null=True)
        coef_public_chu = models.CharField(max_length=50, blank=True, null=True)
        pu_public_chu = models.IntegerField(null=True)
        cout_public_chu = models.IntegerField(null=True)

        lettre_cle_public_ica = models.CharField(max_length=50, blank=True, null=True)
        coef_public_ica = models.CharField(max_length=50, blank=True, null=True)
        pu_public_ica = models.IntegerField(null=True)
        cout_public_ica = models.IntegerField(null=True)

        lettre_cle_mutuelle = models.CharField(max_length=50, blank=True, null=True)
        coef_mutuelle = models.CharField(max_length=50, blank=True, null=True)
        pu_mutuelle = models.IntegerField(null=True)
        cout_mutuelle = models.IntegerField(null=True)

        lettre_cle_classique = models.CharField(max_length=50, blank=True, null=True)
        coef_classique = models.CharField(max_length=50, blank=True, null=True)
        pu_classique = models.IntegerField(null=True)
        cout_classique = models.IntegerField(null=True)

        tarif = Tarif.objects.create(
            bureau=request.user.bureau,
            acte=type_prestataire_id,
            name=name,
        )

        tarif.save()

        response = {
            'statut': 1,
            'message': "Enregistrement effectuée avec succès !",
            'data': {
            }
        }


    else:


    '''
    response = {
        'statut': 0,
        'message': "Methode non autorisée !",
        'data': {}
    }
    return JsonResponse(response)


def tarifs_prestataire_datatable(request, prestataire_id):
    items_per_page = 10
    page_number = request.GET.get('page')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', items_per_page))
    sort_column_index = int(request.GET.get('order[0][column]'))
    sort_direction = request.GET.get('order[0][dir]')
    search_rubrique = request.GET.get('search_rubrique', '')
    search_code = request.GET.get('search_code', '')
    search_libelle = request.GET.get('search_libelle', '')
    search_value = request.GET.get('search[value]', '')
    search = request.GET.get('search[value]', '')

    user = request.user
    queryset = Tarif.objects.filter(bureau=user.bureau, prestataire_id=prestataire_id, statut=Statut.ACTIF)

    if search_libelle:
        queryset = queryset.filter(
            Q(acte__libelle__icontains=search_libelle)
        )

    if search_code:
        queryset = queryset.filter(
            Q(acte__code__icontains=search_code)
        )

    if search_rubrique:
        queryset = queryset.filter(
            Q(acte__rubrique_id=search_rubrique)
        )

    if search:
        queryset = queryset.filter(
            Q(acte__libelle__icontains=search) |
            Q(acte__code__icontains=search) |
            Q(acte__rubrique__libelle__icontains=search) |
            Q(acte__regroupement_acte__libelle__icontains=search)
        )

    # Map column index to corresponding model field for sorting
    sort_columns = {
        0: 'acte__code',
        1: 'acte__libelle',
        2: 'acte__rubrique__libelle',
        3: 'acte__regroupement_acte__libelle',
        4: 'cout_classique',
        5: 'cout_mutuelle',
        6: 'cout_public_hg',
        7: 'cout_public_chu',
        8: 'cout_public_ica',
        9: 'coef_prestataire',
        10: 'pu_prestataire',
        11: 'cout_prestataire',
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
    for p in page_obj:
        detail_url = reverse('popup_detail_tarif', args=[p.id])  # URL to the detail view

        actions_html = (
            f'<span style="cursor:pointer;" class=" btn-popup_details_tarif badge btn-sm btn-details rounded-pill" data-href="{detail_url}"<span class="badge btn-sm btn-details rounded-pill"><i class="fa fa-eye"></i> Détails</span>')

        data.append({
            "id": p.id,
            "code_acte": p.acte.code,
            "libelle_acte": p.acte.libelle,
            "lettre_cle_acte": p.acte.lettre_cle,
            "rubrique": p.acte.rubrique.libelle if p.acte.rubrique else "",
            "regroupement": p.acte.regroupement_acte.libelle if p.acte.regroupement_acte else "",
            "cout_classique": f'<span style="text-align:right;">' + money_field(p.cout_classique) + '</span>',
            "cout_mutuelle": f'<span style="text-align:right;">' + money_field(p.cout_mutuelle) + '</span>',
            "cout_public_hg": f'<span style="text-align:right;">' + money_field(p.cout_public_hg) + '</span>',
            "cout_public_chu": f'<span style="text-align:right;">' + money_field(p.cout_public_chu) + '</span>',
            "cout_public_ica": f'<span style="text-align:right;">' + money_field(p.cout_public_ica) + '</span>',
            "coef_prestataire": f'<span style="text-align:right;">' + money_field(p.coef_prestataire) + '</span>',
            "pu_prestataire": f'<span style="text-align:right;">' + money_field(p.pu_prestataire) + '</span>',
            "cout_prestataire": f'<span style="text-align:right;">' + money_field(p.cout_prestataire) + '</span>',
            "statut": p.statut,
            "actions": actions_html,
        })

    return JsonResponse({
        "data": data,
        "recordsTotal": queryset.count(),
        "recordsFiltered": paginator.count,
        "draw": int(request.GET.get('draw', 1)),
    })


# Génère un fichier model avec les actes déjà en base pour que le gestionnaire puisse renseigner les coûts des actes
def generate_modele_tarifs_excel(request, prestataire_id):
    prestataire = Prestataire.objects.get(id=prestataire_id)

    # Données à inclure dans le DataFrame
    actes = Acte.objects.filter(type_acte__code="acte", status=True).order_by('rubrique_id')

    # Créer un Workbook et accéder à la première feuille
    wb = Workbook()
    ws = wb.active

    # Données à inclure dans le DataFrame
    data = {
        'CODE_RUBRIQUE': [],
        'LIBELLE_ACTE': [],
        'CODE_ACTE': [],
        'LETTRE_CLE': [],
        # 'LETTRE_CLE_CLASSIQUE': [],
        'COEF_CLASSIQUE': [],
        'PRIX_UNIT_CLASSIQUE': [],
        'TARIF_CLASSIQUE': [],
        # 'LETTRE_CLE_MUTUELLE': [],
        'COEF_MUTUELLE': [],
        'PRIX_UNIT_MUTUELLE': [],
        'TARIF_MUTUELLE': [],
        # 'LETTRE_CLE_HG': [],
        'COEF_HG': [],
        'PRIX_UNIT_HG': [],
        'TARIF_HG': [],
        # 'LETTRE_CLE_CHU': [],
        'COEF_CHU': [],
        'PRIX_UNIT_CHU': [],
        'TARIF_CHU': [],
        # 'LETTRE_CLE_ICA': [],
        'COEF_ICA': [],
        'PRIX_UNIT_ICA': [],
        'TARIF_ICA': [],
        # 'LETTRE_CLE_PRESTATAIRE': [],
        'COEF_PRESTATAIRE': [],
        'PRIX_UNIT_PRESTATAIRE': [],
        'TARIF_PRESTATAIRE': [],
    }

    # Ajouter les actes au DataFrame
    for acte in actes:
        # renseigner avec le tarif existant de ce prestataire --
        tarif_existant = Tarif.objects.filter(acte__code=acte.code, bureau=request.user.bureau,
                                              statut=Statut.ACTIF).first()
        tarif_existant_prestataire = Tarif.objects.filter(acte__code=acte.code, bureau=request.user.bureau,
                                                          prestataire=prestataire, statut=Statut.ACTIF).first()

        data['CODE_RUBRIQUE'].append(acte.rubrique.libelle)
        data['LIBELLE_ACTE'].append(acte.libelle)
        data['CODE_ACTE'].append(acte.code)
        data['LETTRE_CLE'].append(acte.lettre_cle)

        # data['LETTRE_CLE_CLASSIQUE'].append(tarif_existant.lettre_cle_classique)
        data['COEF_CLASSIQUE'].append(tarif_existant.coef_classique if tarif_existant else 1)
        data['PRIX_UNIT_CLASSIQUE'].append(tarif_existant.pu_classique if tarif_existant else 0)
        data['TARIF_CLASSIQUE'].append(tarif_existant.cout_classique if tarif_existant else 0)

        # data['LETTRE_CLE_MUTUELLE'].append(tarif_existant.lettre_cle_classique)
        data['COEF_MUTUELLE'].append(tarif_existant.coef_mutuelle if tarif_existant else 1)
        data['PRIX_UNIT_MUTUELLE'].append(tarif_existant.pu_mutuelle if tarif_existant else 0)
        data['TARIF_MUTUELLE'].append(tarif_existant.cout_mutuelle if tarif_existant else 0)

        # data['LETTRE_CLE_HG'].append(tarif_existant.lettre_cle_public_hg if tarif_existant else 0)
        data['COEF_HG'].append(tarif_existant.coef_public_hg if tarif_existant else 0)
        data['PRIX_UNIT_HG'].append(tarif_existant.pu_public_hg if tarif_existant else 0)
        data['TARIF_HG'].append(tarif_existant.cout_public_hg if tarif_existant else 0)

        # data['LETTRE_CLE_CHU'].append(tarif_existant.lettre_cle_public_chu if tarif_existant else 0)
        data['COEF_CHU'].append(tarif_existant.coef_public_chu if tarif_existant else 0)
        data['PRIX_UNIT_CHU'].append(tarif_existant.pu_public_chu if tarif_existant else 0)
        data['TARIF_CHU'].append(tarif_existant.cout_public_chu if tarif_existant else 0)

        # data['LETTRE_CLE_ICA'].append(tarif_existant.lettre_cle_public_ica if tarif_existant else 0)
        data['COEF_ICA'].append(tarif_existant.coef_public_ica if tarif_existant else 0)
        data['PRIX_UNIT_ICA'].append(tarif_existant.pu_public_ica if tarif_existant else 0)
        data['TARIF_ICA'].append(tarif_existant.cout_public_ica if tarif_existant else 0)

        # data['LETTRE_CLE_PRESTATAIRE'].append('')
        data['COEF_PRESTATAIRE'].append(
            tarif_existant_prestataire.coef_prestataire if tarif_existant_prestataire else 1)
        data['PRIX_UNIT_PRESTATAIRE'].append(
            tarif_existant_prestataire.pu_prestataire if tarif_existant_prestataire else 0)
        data['TARIF_PRESTATAIRE'].append(
            tarif_existant_prestataire.cout_prestataire if tarif_existant_prestataire else 0)

    # Créer un DataFrame avec Pandas
    df = pd.DataFrame(data)

    filename = 'INOV_V1-TARIF_DU_PRESTATAIRE_' + slugify(str(prestataire.name)).upper() + '.xlsx'

    # Créer une réponse HTTP avec le type MIME approprié
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    # Enregistrer le DataFrame dans le fichier Excel
    df.to_excel(response, index=False, engine='openpyxl')

    return response


# une que le gestionnaire à renseigner les coûts des actes, on l'importe
def import_tarif_pestataire(request, prestataire_id):
    # try:

    # Charger le fichier Excel depuis la requête
    file = request.FILES['fichier_import_tarif']

    # Lire le fichier Excel avec pandas
    df = pd.read_excel(file)

    rows_count = 0
    # Parcourir les lignes du DataFrame
    for index, row in df.iterrows():

        # Récupérer le code de l'acte
        code_acte = row['CODE_ACTE']

        # Récupérer l'objet Acte correspondant au code
        acte = Acte.objects.filter(code=code_acte).first()

        if acte:
            pprint("L'acte existe, donc on insère le tarif")

            # désactiver l'ancien tarif si existant
            Tarif.objects.filter(acte=acte, prestataire_id=prestataire_id).update(statut=Statut.INACTIF,
                                                                                  statut_validite=StatutValidite.CLOTURE)

            # Insérer une ligne dans la table Tarif avec les coefficients, prix unitaire, etc.
            tarif = Tarif.objects.create(
                acte=acte,
                code_acte=code_acte,
                coef_prestataire=row['COEF_PRESTATAIRE'],
                pu_prestataire=row['PRIX_UNIT_PRESTATAIRE'],
                cout_prestataire=row['TARIF_PRESTATAIRE'],
                statut=Statut.ACTIF,
                statut_validite=StatutValidite.VALIDE,
                bureau=request.user.bureau,
                prestataire_id=prestataire_id,
                created_by=request.user
            )

    # Indiquer que le prestataire a son propre tarif
    Prestataire.objects.filter(id=prestataire_id).update(has_tarif_prestataire=True)

    response = {
        'statut': 1,
        'message': "Tarifs importés avec succès !",
        'data': {}
    }

    '''except Exception as e:
        response = {
            'statut': 0,
            'message': f"Erreur lors de l'importation des tarifs : {str(e)}",
            'data': {}
        }
    '''

    return JsonResponse(response)


class PrestatairesView(PermissionRequiredMixin, TemplateView):
    permission_required = "configurations.view_prestataire"
    template_name = 'prestataires/prestataires.html'
    model = Prestataire

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        secteurs = Secteur.objects.all()
        bureaux = Bureau.objects.filter(id=request.user.bureau.pk)
        types_etablissements = TypeEtablissement.objects.all()

        context_perso = {
            'bureaux': bureaux,
            'secteurs': secteurs,
            'types_etablissements': types_etablissements,
        }

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


def prestataires_datatable(request):
    items_per_page = 10
    page_number = request.GET.get('page')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', items_per_page))
    sort_column_index = int(request.GET.get('order[0][column]'))
    sort_direction = request.GET.get('order[0][dir]')
    search_nom = request.GET.get('search_nom', '')
    search_code = request.GET.get('search_code', '')
    search_type = request.GET.get('search_type', '')
    search_value = request.GET.get('search[value]', '')

    user = request.user
    if request.user.is_superuser:
        queryset = Prestataire.objects.filter(bureau_id=user.bureau_id)
    else:
        queryset = Prestataire.objects.filter(status=True, bureau_id=user.bureau_id)

    if search_nom:
        queryset = queryset.filter(
            Q(name__icontains=search_nom)
        )

    if search_code:
        queryset = queryset.filter(
            Q(code__icontains=search_code)
        )

    if search_type:
        queryset = queryset.filter(
            Q(type_prestataire_id=search_type)
        )

    # Map column index to corresponding model field for sorting
    sort_columns = {
        0: 'name',
        1: 'code',
        2: 'type_prestataire__name',
        3: 'secteur__libelle',
        4: 'telephone',
        5: 'status',
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
    for p in page_obj:
        detail_url = reverse('detail_prestataire', args=[p.id])  # URL to the detail view
        update_url = reverse('popup_modifier_prestataire', args=[p.id])  # URL to the detail view

        actions_html = (
            f'<a href="{detail_url}"><span class="badge btn-sm btn-details rounded-pill"><i class="fa fa-eye"></i> {_("Détails")}</span></a>&nbsp;'
            f'<span style="cursor:pointer;" class="btn_modifier_prestataire badge btn-sm btn-modifier rounded-pill" data-href="{update_url}"><i class="fa fa-edit"></i> {_("Modifier")}</span>')

        data.append({
            "id": p.id,
            "name": p.name,
            "code": p.code,
            "type_prestataire": p.type_prestataire.name if p.type_prestataire else "",
            "secteur": p.secteur.libelle if p.secteur else "",
            "ville": p.ville,
            "telephone": p.telephone,
            "statut": "ACTIF" if p.status else " INACTIF",
            "actions": actions_html,
        })

    return JsonResponse({
        "data": data,
        "recordsTotal": queryset.count(),
        "recordsFiltered": paginator.count,
        "draw": int(request.GET.get('draw', 1)),
    })


def export_prestaitaires(request):
    if request.method == 'POST':
        # Récupérer les paramètres de filtre

        search_nom = request.GET.get('search_nom', '')
        search_code = request.GET.get('search_code', '')
        search_type = request.GET.get('search_type', '')
        search_value = request.GET.get('search[value]', '')

        # Filtrer les données selon les paramètres
        prestataires = Prestataire.objects.filter(bureau=request.user.bureau)

        if search_nom:
            prestataires = prestataires.filter(name__icontains=search_nom)
        if search_code:
            prestataires = prestataires.filter(code__icontains=search_code)
        if search_type:
            prestataires = prestataires.filter(type_prestataire_id=search_type)

        # Préparation de l'exportation Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Liste_Prestataire.xlsx"'

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'LISTE PRESTATAIRE'

        # Définir les en-têtes

        # Personnalisation de l'en-tête
        bold_font = Font(bold=True, color="FF0000")  # Rouge et en gras
        header_fill = PatternFill(start_color='FFEBCD', end_color='FFEBCD',
                                  fill_type='solid')  # Couleur de remplissage pour les entêtes
        headers = ['Id Prestataire', 'Nom prestataire', 'Type de prestataire', 'Ville', 'Contact', 'Date de création',
                   'E-mail']
        for col_num, column_title in enumerate(headers, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.value = column_title
            cell.font = bold_font
            cell.fill = header_fill

        # Remplissage du tableau avec les données
        for row_num, prestataire in enumerate(prestataires, 2):
            row = [
                prestataire.code,
                prestataire.name,
                prestataire.type_prestataire.name if prestataire.type_prestataire else '',
                prestataire.ville,
                prestataire.telephone,
                prestataire.created_at.strftime("%d/%m/%Y %H:%M"),
                prestataire.email,
            ]
            for col_num, cell_value in enumerate(row, 1):
                cell = worksheet.cell(row=row_num, column=col_num)
                cell.value = cell_value

        # Ajuster la largeur des colonnes en fonction du contenu pour faciliter la lecture du tableau
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if cell.value is not None:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            worksheet.column_dimensions[column].width = adjusted_width

        workbook.save(response)
        return response
    else:
        return HttpResponse(status=405)


def ajouter_prescripteur_prestataire(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        rb_ordre = request.POST.get('rb_ordre')
        code = request.POST.get('code')
        telephone = request.POST.get('telephone')
        fax = request.POST.get('fax')
        email = request.POST.get('email')
        fax = request.POST.get('fax')
        ville = request.POST.get('ville')
        addresse = request.POST.get('addresse')
        secteur_id = request.POST.get('secteur_id')
        type_prestataire_id = request.POST.get('type_prestataire_id')
        reseaux_soins_ids = request.POST.getlist('reseaux_soins_ids')
        reseaux_soins = ""

        latitude = None
        longitude = None
        try:
            latitude = float(request.POST.get('latitude').replace(",", ".").replace(" ", ""))
            longitude = float(request.POST.get('longitude').replace(",", ".").replace(" ", ""))
        except Exception as e:
            print(e)

        pprint(reseaux_soins)

        prestataire = Prestataire.objects.filter(bureau=request.user.bureau).latest('id')

        code = "P" + str(prestataire.pk + 1)

        if request.user.bureau:
            bureau = request.user.bureau

            fs = FileSystemStorage()

            '''
            logo = request.FILES['logo']
            if logo:
                fichier = request.FILES['logo']
                file_name_renamed = fichier.name.replace(" ", "_")
                logo_filename = fs.save(file_name_renamed, fichier)

            '''

            prestataire = Prestataire.objects.create(
                name=name,
                rb_ordre=rb_ordre,
                code=code,
                telephone=telephone,
                fax=fax,
                email=email,
                ville=ville,
                addresse=addresse,
                # logo=logo_filename,
                status=True,
                bureau_id=bureau.pk,
                type_prestataire_id=type_prestataire_id,
                secteur_id=secteur_id,
                latitude=latitude,
                longitude=longitude,
            )

            # Mettre a jour le code
            code_bureau = request.user.bureau.code
            prestataire.code = str(code_bureau) + str(Date.today().year)[-2:] + '-' + str(prestataire.pk).zfill(
                7) + '-P'
            # prestataire.code = 'P' + str(prestataire.pk).zfill(6)
            prestataire.save()

            # enregistrer ses réseaux de soins
            for reseau_soin in reseaux_soins:
                pass

            response = {
                'statut': 1,
                'message': "Enregistrement effectuée avec succès !",
                'data': {
                }
            }


        else:
            response = {
                'statut': 0,
                'message': "Vous n'êtes lié à aucun bureau !",
                'data': {}
            }

    else:

        response = {
            'statut': 0,
            'message': "Methode non autorisée !",
            'data': {}
        }

    return JsonResponse(response)


def modifier_prestataire(request, prestataire_id):
    prestataire = Prestataire.objects.get(id=prestataire_id)

    secteurs = Secteur.objects.all()
    types_etablissements = TypeEtablissement.objects.all()

    return render(request, 'prestataires/modal_modifier_prestataire.html', {
        'prestataire': prestataire,
        'secteurs': secteurs,
        'types_etablissements': types_etablissements
    })


# TO_DO_ISMAEL
def supprimer_prestataire(request, prestataire_id):
    if request.method == 'POST':

        prestataire = Prestataire.objects.filter(id=prestataire_id).first()

        type_prestataire_id = request.POST.get('type_prestataire_id')
        secteur_id = request.POST.get('secteur_id')
        type_etablissement_id = request.POST.get('type_etablissement_id')

        prestataire.name = request.POST.get('name')
        prestataire.rb_ordre = request.POST.get('rb_ordre')
        prestataire.telephone = request.POST.get('telephone')
        prestataire.email = request.POST.get('email')
        prestataire.fax = request.POST.get('fax')
        prestataire.addresse = request.POST.get('addresse')
        prestataire.ville = request.POST.get('ville')

        prestataire.secteur_id = secteur_id
        prestataire.type_prestataire_id = type_prestataire_id
        prestataire.type_etablissement_id = type_etablissement_id

        try:
            prestataire.latitude = float(request.POST.get('latitude').replace(",", ".").replace(" ", ""))
            prestataire.longitude = float(request.POST.get('longitude').replace(",", ".").replace(" ", ""))
        except Exception as e:
            print(e)
            prestataire.latitude = None
            prestataire.longitude = None

        if request.user.bureau:
            prestataire.bureau = request.user.bureau

            fs = FileSystemStorage()

            '''
            logo = request.FILES['logo']
            fichier_tarification = request.FILES['fichier_tarification']

            if logo:
                fichier = request.FILES['logo']
                file_name_renamed = fichier.name.replace(" ", "_")
                logo_filename = fs.save(file_name_renamed, fichier)

            if fichier_tarification:
                fichier = request.FILES['fichier_tarification']
                file_name_renamed = fichier.name.replace(" ", "_")
                fichier_tarification_filename = fs.save(file_name_renamed, fichier)
            '''

            prestataire.save()
            response = {
                'statut': 1,
                'message': "Modification du prestataire effectuée avec succès !",
                'data': {
                }
            }


        else:

            response = {
                'statut': 0,
                'message': "Vous n'êtes lié à aucun bureau !",
                'data': {}
            }

    else:

        response = {
            'statut': 0,
            'message': "Methode non autorisée !",
            'data': {}
        }

    return JsonResponse(response)


def add_reseau_soin_prestataire(request, prestataire_id):
    if request.method == 'POST':
        reseaux_soins_ids = request.POST.getlist('reseaux_soins_ids')
        reseaux_soins = ""

        # enregistrer ses réseaux de soins
        for reseau_soin in reseaux_soins:
            pass

        response = {
            'statut': 1,
            'message': "Enregistrement effectuée avec succès !",
            'data': {
            }
        }

    else:

        response = {
            'statut': 0,
            'message': "Methode non autorisée !",
            'data': {}
        }

    return JsonResponse(response)


def retirer_reseau_soin_prestataire(request, prs_id):
    if request.method == 'POST':

        response = {
            'statut': 1,
            'message': "Enregistrement effectuée avec succès !",
            'data': {
            }
        }

    else:

        response = {
            'statut': 0,
            'message': "Methode non autorisée !",
            'data': {}
        }

    return JsonResponse(response)


def add_prescripteur(request):
    if request.method == 'POST':

        pprint(request.POST)

        nom = request.POST.get('nom')
        prenoms = request.POST.get('prenoms')
        numero_ordre = request.POST.get('numero_ordre')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        prestataire_id = request.POST.get('prestataire_id')

        prestataire = Prestataire.objects.get(id=prestataire_id)

        # dd(prestataire)
        prescripteur = Prescripteur.objects.create(
            nom=nom,
            prenoms=prenoms,
            telephone=telephone,
            numero_ordre=numero_ordre,
            email=email,
        )

        PrescripteurPrestataire.objects.create(
            prescripteur_id=prescripteur.pk,
            prestataire_id=prestataire.pk
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectuée avec succès !",
            'data': {
                'id': prescripteur.pk,
                'nom': prescripteur.nom,
                'prenoms': prescripteur.prenoms,
            }
        }

    else:

        response = {
            'statut': 0,
            'message': "Methode non autorisée !",
            'data': {}
        }

    return JsonResponse(response)


# @transaction.atomic
def import_prescripteurs(request, prestataire_id):
    if request.method == 'POST':
        # get file and use excel to import in prescripteur table

        fichier = request.FILES['fichier_import_prescripteurs']

        fs = FileSystemStorage(location='prestataires/upload_prescripteurs/')
        file_name_renamed = fichier.name.replace(" ", "_")

        filename = fs.save(file_name_renamed, fichier)
        uploaded_file_url = fs.url(filename)
        uploaded_file_full_path = fs.path(filename)
        prestataire = Prestataire.objects.get(id=prestataire_id)

        cpt_all = 0
        cpt_success = 0

        # df = pd.read_excel("." + uploaded_file_url)
        df = pd.read_excel(uploaded_file_full_path)
        for index, row in df.iterrows():
            cpt_all = cpt_all + 1
            # Valeur du tableau
            # Access row values using column names
            # try:
            numero_ordre = row['NUMERO_ORDRE_MEDECIN']
            nom = row['NOM']
            prenoms = row['PRENOMS']
            telephone = row['TELEPHONE']

            if Prescripteur.objects.filter(numero_ordre=numero_ordre, bureau=request.user.bureau).exists():
                # Ne retournera pas d'erreur si le prescripteur existe
                prescripteur = Prescripteur.objects.filter(numero_ordre=numero_ordre,
                                                           bureau=request.user.bureau).first()
                # dd(prescripteur)
            else:
                # Le prescripteur n'existe pas, on le créé
                prescripteur = Prescripteur.objects.create(
                    nom=nom,
                    prenoms=prenoms,
                    numero_ordre=numero_ordre,
                    telephone=telephone,
                    bureau=request.user.bureau,
                )
                # dd(prescripteur)

            # On tente de trouver l'enregistrement de du prescripteur sinon on l'enregistre
            prescripteur_prestataire = PrescripteurPrestataire.objects.filter(prescripteur_id=prescripteur.id,
                                                                              prestataire_id=prestataire.pk).first()

            if not prescripteur_prestataire:
                PrescripteurPrestataire.objects.create(
                    prescripteur_id=prescripteur.pk,
                    prestataire_id=prestataire.pk,
                    created_at=datetime.datetime.now(tz=timezone.utc)
                )

                cpt_success = cpt_success + 1

            else:
                response = {
                    'statut': 0,
                    'message': "Veilleez entrez une specialité existant dans la base de données !",
                    'data': {
                    }
                }

            # except KeyError:
            #    response = {
            #        'statut': 0,
            #        'message': "Erreur sur le mot clé " + KeyError.args.index,
            #        'data': {
            #        }
            #    }
        if cpt_success == cpt_all:
            response = {
                'statut': 1,
                'message': "Importation effectuée avec succès",
                'data': {
                }
            }
        else:
            response = {
                'statut': 0,
                'message': "Echec de l'importation, veuillez renseigner correctement le fichier svp",
                'data': {
                }
            }

        return JsonResponse(response)


# get Prestataire detail
class DetailsPrestatairesView(TemplateView):
    permission_required = "production.view_prestataires"
    template_name = 'prestataires/prestataire_details.html'
    model = Prestataire

    def get(self, request, prestataire_id, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        prestataire = Prestataire.objects.filter(id=prestataire_id, bureau=request.user.bureau).first()
        if prestataire:

            clients = Client.objects.all()

            prescripteurs = PrescripteurPrestataire.objects.filter(prestataire_id=prestataire.pk,
                                                                   statut_validite=StatutValidite.VALIDE)
            utilisateurs = User.objects.filter(prestataire_id=prestataire.pk)

            tarifs_prestataire_clients = TarifPrestataireClient.objects.filter(prestataire_id=prestataire.pk)

            reseaux_soins_prestataire = ""

            prestataire_reseausoin_ids = ""

            rubriques = Rubrique.objects.filter(status=True)
            regroupements_actes = RegroupementActe.objects.filter(status=True)

            context_perso = {
                'clients': clients,
                'prestataire': prestataire,
                'utilisateurs': utilisateurs,
                'prescripteurs': prescripteurs,
                'reseaux_soins_prestataire': reseaux_soins_prestataire,
                'tarifs_prestataire_clients': tarifs_prestataire_clients,
                'rubriques': rubriques,
                'regroupements_actes': regroupements_actes,
            }

            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        else:
            return redirect('')

    def post(self):
        pass

    def get_context_data(self, **kwargs):

        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def prescripteurs_by_prestataire(request, prestataire_id):
    prestataire_prescripteur = PrescripteurPrestataire.objects.filter(prestataire_id=prestataire_id)
    prescripteurs = []
    for pp in prestataire_prescripteur:
        if pp.prescripteur not in prescripteurs:
            prescripteurs.append(pp.prescripteur)
    prescripteurs_serialize = serializers.serialize('json', prescripteurs)
    return HttpResponse(prescripteurs_serialize, content_type='application/json')


# PRESCRIPTEUR
def prescripteurs_prestataires_datatable(request, prestataire_id):
    items_per_page = 10
    page_number = request.GET.get('page')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', items_per_page))
    sort_column_index = int(request.GET.get('order[0][column]'))
    sort_direction = request.GET.get('order[0][dir]')
    #   search_nom = request.GET.get('search_nom', '')
    search_numero_ordre = request.GET.get('search_numero_ordre', '')
    search_value = request.GET.get('search[value]', '')

    prestataire_prescripteurs_ids = PrescripteurPrestataire.objects.filter(
        prestataire=prestataire_id,
        statut_validite=StatutValidite.VALIDE
    ).values_list('prescripteur_id', flat=True).order_by('id')

    queryset = Prescripteur.objects.filter(id__in=prestataire_prescripteurs_ids)

    # if search_nom:
    #     queryset = queryset.filter(
    #         Q(nom__icontains=search_nom)
    #     )

    if search_numero_ordre:
        queryset = queryset.filter(
            Q(numero_ordre__icontains=search_numero_ordre)
        )

    sort_columns = {
        0: 'nom',
        1: 'prenoms',
        2: 'numero_ordre',
        3: 'telephone',
    }

    sort_column = sort_columns.get(sort_column_index, 'id')

    if sort_direction == 'desc':
        sort_column = '-' + sort_column

    queryset = queryset.order_by(sort_column)

    paginator = Paginator(queryset, length)
    page_obj = paginator.get_page(page_number)

    data = []
    for p in page_obj:
        modifier_prescripteur_url = reverse('popup_modifier_prescripteur', args=[p.id])  # url modifier prescripteur
        retirer_prescripteur_url = reverse('retirer_prescripteur_prestataire',
                                           args=[prestataire_id, p.id])  # url retirer prescripteur

        actions_html = (
            f'<span style="cursor:pointer;" class="btn_modifier_prescripteur badge btn-sm btn-modifier rounded-pill" data-href="{modifier_prescripteur_url}"><i class="fa fa-edit"></i> Modifier</span>&nbsp;'
            f'<span style="cursor:pointer;" class="btn_retirer_prescripteur badge btn-sm btn-danger rounded-pill" data-href="{retirer_prescripteur_url}"><i class="fa fa-minus"></i> Retirer</span>')

        data.append({
            "id": p.id,
            "nom": p.nom,
            "prenoms": p.prenoms,
            "numero_ordre": p.numero_ordre,
            "telephone": p.telephone,
            "actions": actions_html,
        })

    return JsonResponse({
        "data": data,
        "recordsTotal": queryset.count(),
        "recordsFiltered": paginator.count,
        "draw": int(request.GET.get('draw', 1)),
    })


def popup_modifier_prescripteur(request, prescripteur_id):
    prescripteur = Prescripteur.objects.filter(id=prescripteur_id).first()

    prestataires = Prestataire.objects.filter(status=True, bureau=request.user.bureau)

    return render(request, 'prestataires/modal_modifier_prescripteur.html', {
        'prescripteur': prescripteur,
        'prestataires': prestataires
    })


def update_prescripteur(request, prescripteur_id):
    if request.method == 'POST':

        prescripteur = Prescripteur.objects.filter(id=prescripteur_id).first()

        prescripteur.nom = request.POST.get('nom')
        prescripteur.prenoms = request.POST.get('prenoms')
        prescripteur.numero_ordre = request.POST.get('numero_ordre')
        prescripteur.telephone = request.POST.get('telephone')

        prescripteur.save()

        response = {
            'statut': 1,
            'message': "Modification effectuée ss avec succès !",
            'data': {
            }
        }

    else:

        response = {
            'statut': 0,
            'message': "Methode non autorisée !",
            'data': {}
        }

    return JsonResponse(response)


def retirer_prescripteur_prestataire(request, prestataire_id, prescripteur_id):
    if request.method == 'POST':
        prescripteur_prestataire = PrescripteurPrestataire.objects.filter(prescripteur_id=prescripteur_id,
                                                                          prestataire_id=prestataire_id,
                                                                          statut_validite=StatutValidite.VALIDE).update(
            statut_validite=StatutValidite.CLOTURE,
            deleted_by=request.user,
            deleted_at=datetime.datetime.now(tz=timezone.utc),
        )

        response = {
            'statut': 1,
            'message': "Prescripteur retiré avec succès !",
            'data': {
            }
        }

    return JsonResponse(response)


# FIN PRESCRIPTEUR

# POPUP JOINDRE DES PRESTATAIRES
def popup_joindre_prestataires(request, reseau_soin_id):
    reseau_soin = ""

    return render(request, 'reseaux_soins/popup_joindre_prestataires.html',
                  {'reseau_soin': reseau_soin})


def reseau_soin_prestataires_restants_datatable(request, reseau_soin_id):
    items_per_page = 10
    page_number = request.GET.get('page')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', items_per_page))
    sort_column_index = int(request.GET.get('order[0][column]'))
    sort_direction = request.GET.get('order[0][dir]')
    search_nom = request.GET.get('search_nom', '')
    search_code = request.GET.get('search_code', '')
    search_type = request.GET.get('search_type', '')
    search_value = request.GET.get('search[value]', '')

    prestataire_reseausoin_ids = ""

    if search_nom:
        queryset = queryset.filter(
            Q(name__icontains=search_nom)
        )

    if search_code:
        queryset = queryset.filter(
            Q(code__icontains=search_code)
        )

    if search_type:
        queryset = queryset.filter(
            Q(type_prestataire_id=search_type)
        )

    # Map column index to corresponding model field for sorting
    sort_columns = {
        0: 'name',
        1: 'code',
        2: 'type_prestataire__name',
        3: 'secteur__libelle',
        4: 'telephone',
        5: 'status',
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
    for p in page_obj:
        detail_url = reverse('detail_prestataire', args=[p.id])  # URL to the detail view
        integrer_prestataire_url = reverse('joindre_prestataire_reseau',
                                           args=[reseau_soin_id, p.id, ])  # URL to the detail view

        actions_html = (
            f'<span style="cursor:pointer;font-weight:normal;" class="btn_integrer_prestataire badge btn-sm btn-warning rounded-pill" data-href="{integrer_prestataire_url}"><i class="fa fa-plus" ></i> Intégrer</span>')

        checkbox_button = f'<input type="checkbox" name="checkbox_button" class="checkbox_button" value="' + str(
            p.id) + '"/>'

        data.append({
            "id": p.id,
            "checkbox": checkbox_button,
            "name": p.name,
            "code": p.code,
            "type_prestataire": p.type_prestataire.name if p.type_prestataire else "",
            "secteur": p.secteur.libelle if p.secteur else "",
            "ville": p.ville,
            "telephone": p.telephone,
            "statut": "ACTIF" if p.status else " INACTIF",
            "actions": actions_html,
        })

    return JsonResponse({
        "data": data,
        "recordsTotal": queryset.count(),
        "recordsFiltered": paginator.count,
        "draw": int(request.GET.get('draw', 1)),
    })


def joindre_prestataires_reseau(request, reseau_soin_id):
    if request.method == 'POST':

        reseau_soin = ""

        prestataires_ids = literal_eval(request.POST.get('selectedItems'))
        print("prestataires_ids")
        print(prestataires_ids)

        prestataires = Prestataire.objects.filter(id__in=prestataires_ids)

        for prestataire in prestataires:
            pass

        response = {
            'statut': 1,
            'message': "Prestataires intégrés au réseau de soins avec succès !",
            'data': {
            }
        }

    else:

        response = {
            'statut': 0,
            'message': "Not found",
            'data': {}
        }

    return JsonResponse(response)


def joindre_prestataire_reseau(request, reseau_soin_id, prestataire_id):
    if request.method == 'POST':

        reseau_soin = ""
        prestataire = Prestataire.objects.filter(id=prestataire_id).first()

        if reseau_soin and prestataire:
            pass

            response = {
                'statut': 1,
                'message': "Prestataire intégré au réseau de soins avec succès !",
                'data': {
                }
            }


        else:

            response = {
                'statut': 0,
                'message': "Prestataire ou réseau de soins introuvable",
                'data': {}
            }

    return JsonResponse(response)


def retirer_prestataire_reseau(request, reseau_soin_id, prestataire_id):
    if request.method == 'POST':
        response = {
            'statut': 1,
            'message': "Prestataire intégré au réseau de soins avec succès !",
            'data': {
            }
        }

    return JsonResponse(response)


#
class GroupePermissionsView(TemplateView):
    template_name = 'groupes/groupes_permissions.html'
    model = Permission

    def get(self, request, groupe_id, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        groupes = AuthGroup.objects.all()
        permissions = Permission.objects.all().order_by('content_type_id')

        context_perso = {
            'groupes': groupes,
            'permissions': permissions
        }

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required()
# modiifie le statut d'un prestataire depuis le toggle sur la page détail du prestataire
def change_prestataire_status(request, prestataire_id):
    response = None

    if request.method == 'POST':

        prestataire = Prestataire.objects.get(id=prestataire_id)

        if prestataire.status == True:
            prestataire.status = False

        else:
            prestataire.status = True
        prestataire.save()
        # gardons des traces
        if prestataire.status == False:
            ActionLog.objects.create(done_by=request.user, action="update",
                                     description="Désactivation d'un prestataire", table="prestataire",
                                     row=prestataire.pk,
                                     # data_before=json.dumps(model_to_dict(formule_before)),
                                     # data_after=json.dumps(model_to_dict(formule))
                                     )
        else:
            ActionLog.objects.create(done_by=request.user, action="update",
                                     description="Activation d'un prestataire", table="prestataire",
                                     row=prestataire.pk,
                                     # data_before=json.dumps(model_to_dict(formule_before)),
                                     # data_after=json.dumps(model_to_dict(formule))
                                     )

        response = {
            'statut': 1,
            'message': "Statut Prestataire changé avec succès !",
            'data': {
            }
        }
        print(prestataire.status)

    return JsonResponse(response)


class WsBobyView(TemplateView):
    # permission_required = "configurations.view_prestataire"
    template_name = 'ws_bobys/bobys.html'
    model = WsBoby

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)
        try:
            del request.session['name']
            del request.session['query']
            del request.session['params']
            del request.session['value_params']
        except:
            pass
        context = {**context_original}
        return self.render_to_response(context)


def ws_boby_datatable(request):
    items_per_page = 10
    page_number = request.GET.get('page')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', items_per_page))
    sort_column_index = int(request.GET.get('order[0][column]'))
    sort_direction = request.GET.get('order[0][dir]')
    search = request.GET.get('search[value]', '')
    print('search')
    print(search)

    queryset = WsBoby.objects.all()

    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(request__icontains=search)
        )

    # Map column index to corresponding model field for sorting
    sort_columns = {
        0: 'id',
        1: 'name',
        2: 'status',
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
    for ws_boby in page_obj:
        update_url = reverse('ws_boby_edite', args=[ws_boby.id])  # URL to the detail view

        actions_html = f'<a style="cursor:pointer;" class="badge btn-sm btn-modifier rounded-pill" href="{update_url}"><i class="fa fa-edit"></i> Modifier</a>'

        data.append({
            "id": ws_boby.id,
            "name": ws_boby.name,
            "status": '<span class="badge badge-actif">Actif</span>' if ws_boby.status else '<span class="badge badge-inactif">Inactif</span>',
            "actions": actions_html,
        })

    return JsonResponse({
        "data": data,
        "recordsTotal": queryset.count(),
        "recordsFiltered": paginator.count,
        "draw": int(request.GET.get('draw', 1)),
    })


class WsBobyCreateView(TemplateView):
    # permission_required = "configurations.view_prestataire"
    template_name = 'ws_bobys/add_boby.html'
    model = WsBoby

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }

    def post(self, request, *args, **kwargs):
        print(request.POST)
        query_data = request.POST
        name = query_data.get('name', '')
        query = query_data.get('query', '')
        params = []
        params = query_data.getlist('params[]', [])
        value_params = query_data.getlist('value_params[]', [])

        print('params')
        print(params)

        request.session['name'] = name if name else ""
        request.session['query'] = query if query else ""
        request.session['params'] = params if params else []
        request.session['value_params'] = value_params if value_params else []
        with transaction.atomic():
            try:
                verify_sql_query(query)

                ws_boby = WsBoby.objects.create(name=name, request=query, status=True)
                ws_boby.save()

                for i in range(len(params)):
                    param_ws_boby = ParamWsBoby.objects.create(ws_boby=ws_boby, name=params[i], value=value_params[i])
                    param_ws_boby.save()

                # request.session['message'] = "Bobys ajouté avec succès !"
                del request.session['name']
                del request.session['query']
                del request.session['params']
                del request.session['value_params']
                messages.success(request, "Boby ajouté avec succès !")
                return redirect('ws_bobys')

            except Exception as e:
                print(e)
                # request.session['message'] =
                messages.error(request, "ERREUR: " + str(e))
                return redirect('ws_boby_create')


class WsBobyEditeView(TemplateView):
    # permission_required = "configurations.view_prestataire"
    template_name = 'ws_bobys/edite_boby.html'
    model = WsBoby

    def get(self, request, ws_boby_id, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        ws_boby = WsBoby.objects.get(id=ws_boby_id)

        context_perso = {
            'ws_boby': ws_boby
        }

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self, request, ws_boby_id, *args, **kwargs):
        print(request.POST)
        query_data = request.POST
        name = query_data.get('name', '')
        query = query_data.get('query', '')
        status = query_data.get('status', False)
        params = query_data.getlist('params[]', [])
        value_params = query_data.getlist('value_params[]', [])

        print('params')
        print(params)

        request.session['name'] = name if name else ""
        request.session['query'] = query if query else ""
        request.session['params'] = params if params else []
        request.session['value_params'] = value_params if value_params else []
        request.session['status'] = status
        with transaction.atomic():
            try:
                verify_sql_query(query)

                ws_boby = WsBoby.objects.get(id=ws_boby_id)
                ws_boby.name = name
                ws_boby.request = query
                ws_boby.status = status
                ws_boby.save()

                for j in ws_boby.paramwsboby_set.all():
                    j.delete()

                for i in range(len(params)):
                    param_ws_boby = ParamWsBoby.objects.create(ws_boby=ws_boby, name=params[i], value=value_params[i])
                    param_ws_boby.save()

                # request.session['message'] = "Bobys ajouté avec succès !"
                del request.session['name']
                del request.session['query']
                del request.session['params']
                del request.session['value_params']
                del request.session['status']

                messages.success(request, "Boby modifié avec succès !")
                return redirect('ws_bobys')

            except Exception as e:
                print(e)
                # request.session['message'] =
                messages.error(request, "ERREUR: " + str(e))
                return redirect('ws_boby_edite', ws_boby_id)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


# ACTE
class ActesView(PermissionRequiredMixin, TemplateView):
    permission_required = "configurations.view_acte"
    template_name = 'acte/actes.html'
    model = Acte

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        # rubriques = Rubrique.objects.filter(status=True)
        # liste_regroupements_actes = RegroupementActe.objects.filter(status=True)
        # regroupements_actes = {
        #     rubrique.pk: [
        #         {'name': regroupements_acte.pk, 'value': regroupements_acte.libelle}
        #         for regroupements_acte in RegroupementActe.objects.filter(rubrique_id=rubrique.pk, status=True)
        #     ]
        #     for rubrique in rubriques
        # }

        all_type_actes = TypeActe.objects.all()
        type_actes = json.dumps(list(all_type_actes.values('id', 'libelle')))

        acte = Acte.objects.all()

        base_calcul_tm_choices = BaseCalculTM.choices

        context_perso = {
            'actes': acte,
            'type_actes': type_actes,
            'base_calcul_tm_choices': base_calcul_tm_choices,
        }

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


def actes_datatable(request):
    items_per_page = 10
    page_number = request.GET.get('page')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', items_per_page))
    sort_column_index = int(request.GET.get('order[0][column]'))
    sort_direction = request.GET.get('order[0][dir]')
    search_rubrique = request.GET.get('search_rubrique', '')
    search_code = request.GET.get('search_code', '')
    search_libelle = request.GET.get('search_libelle', '')
    search_entente_prealable = request.GET.get('search_entente_prealable', '')
    search_value = request.GET.get('search[value]', '')

    queryset = Acte.objects.filter(statut_validite=StatutValidite.VALIDE)

    if search_libelle:
        queryset = queryset.filter(
            Q(libelle__icontains=search_libelle)
        )

    if search_code:
        queryset = queryset.filter(
            Q(code__icontains=search_code)
        )

    if search_rubrique:
        queryset = queryset.filter(
            Q(rubrique_id=search_rubrique)
        )

    if search_entente_prealable:
        queryset = queryset.filter(
            Q(rubrique_id=search_entente_prealable)
        )

    # Map column index to corresponding model field for sorting
    sort_columns = {
        0: 'code',
        1: 'libelle',
        2: 'rubrique__libelle',
        3: 'regroupement_acte__libelle',
        4: 'lettre_cle',
        5: 'base_calcul_tm',
        7: 'delais_controle',
        8: 'entente_prealable',
        9: 'option_seance',
        10: 'specialiste_uniquement',
        11: 'status',
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
    for acte in page_obj:
        parametre = ParamActe.objects.filter(bureau=request.user.bureau, acte=acte).first()
        detail_url = reverse('popup_detail_acte', args=[acte.id])  # url the detail view
        update_url = reverse('popup_modifier_acte', args=[acte.id])  # url to update view

        actions_html = (
            f'<span style="cursor:pointer;" class="btn-popup_details_acte badge btn-sm btn-details rounded-pill" data-href="{detail_url}"<span class="badge btn-sm btn-details rounded-pill"><i class="fa fa-eye"></i> Détails</span>&nbsp;'
            f'<span style="cursor:pointer;" class="btn_modifier_acte badge btn-sm btn-modifier rounded-pill" data-href="{update_url}"><i class="fa fa-edit"></i> Modifier</span>')

        data.append({
            "id": acte.id,
            "code": acte.code,
            "libelle": acte.libelle,
            "type": acte.type_acte.libelle if acte.type_acte else "",
            "rubrique": acte.rubrique.libelle if acte.rubrique else "",
            "regroupement": acte.regroupement_acte.libelle if acte.regroupement_acte else "",
            "lettre_cle": acte.lettre_cle,
            "base_calcul_tm": acte.base_calcul_tm,
            "delais_controle": parametre.delais_controle if parametre else 0,
            "entente_prealable": parametre.entente_prealable if parametre else None,
            "option_seance": acte.option_seance,
            "specialiste_uniquement": parametre.specialiste_uniquement if parametre else None,
            "status": acte.status,
            "actions": actions_html,
        })

    return JsonResponse({
        "data": data,
        "recordsTotal": queryset.count(),
        "recordsFiltered": paginator.count,
        "draw": int(request.GET.get('draw', 1)),
    })


def popup_detail_acte(request, acte_id):
    acte = Acte.objects.get(id=acte_id)

    return render(request, 'acte/modal_details_acte.html', {'acte': acte})


def add_acte(request):
    if request.method == 'POST':

        bureau_id = request.POST.get('bureau_id')
        bureau = Bureau.objects.get(id=bureau_id)
        if bureau:

            rubrique_id = request.POST.get('rubrique_id')
            rubrique = Rubrique.objects.get(id=rubrique_id)
            regroupement_acte_id = request.POST.get('regroupement_acte_id')
            regroupement_acte = RegroupementActe.objects.get(id=regroupement_acte_id)
            type_acte_id = request.POST.get('type_acte')
            type_acte = TypeActe.objects.get(id=type_acte_id)
            libelle = request.POST.get('libelle', None)

            code = request.POST.get('code', None)
            if code == '':
                code = None

            lettre_cle = request.POST.get('lettre_cle', None)

            delais_carence = request.POST.get('delais_carence', None)
            if delais_carence:
                delais_carence = int(delais_carence.replace(' ', ''))
            else:
                delais_carence = None

            delais_controle = request.POST.get('delais_controle', None)
            if delais_controle:
                delais_controle = int(delais_controle.replace(' ', ''))
            else:
                delais_controle = None

            base_calcul_tm = request.POST.get('base_calcul_tm', None)
            specialiste_uniquement = 'specialiste_uniquement' in request.POST
            est_gratuit = 'est_gratuit' in request.POST
            status = 'status' in request.POST

            nouveau_acte = Acte.objects.create(
                rubrique=rubrique,
                regroupement_acte=regroupement_acte,
                type_acte=type_acte,
                libelle=libelle,
                code=code,
                lettre_cle=lettre_cle,
                delais_carence=delais_carence,
                delais_controle=delais_controle,
                base_calcul_tm=base_calcul_tm,
                specialiste_uniquement=specialiste_uniquement,
                est_gratuit=est_gratuit,
                status=status
            )
            nouveau_acte.save()

            #   coef_classique = request.POST.get('coef_classique', None)
            #   pu_classique = request.POST.get('pu_classique', None)
            #   cout_classique = request.POST.get('cout_classique', None)
            #   #
            #   coef_classique = int(coef_classique.replace(' ', '')) if coef_classique else None
            #   pu_classique = int(pu_classique.replace(' ', '')) if pu_classique else None
            #   cout_classique = int(cout_classique.replace(' ', '')) if cout_classique else None
            #
            #   coef_mutuelle = request.POST.get('coef_mutuelle', None)
            #   pu_mutuelle = request.POST.get('pu_mutuelle', None)
            #   cout_mutuelle = request.POST.get('cout_mutuelle', None)
            #   #
            #   coef_mutuelle = int(coef_mutuelle.replace(' ', '')) if coef_mutuelle else None
            #   pu_mutuelle = int(pu_mutuelle.replace(' ', '')) if pu_mutuelle else None
            #   cout_mutuelle = int(cout_mutuelle.replace(' ', '')) if cout_mutuelle else None
            #
            #   coef_hg = request.POST.get('coef_hg', None)
            #   pu_hg = request.POST.get('pu_hg', None)
            #   cout_hg = request.POST.get('cout_hg', None)
            #   #
            #   coef_hg = int(coef_hg.replace(' ', '')) if coef_hg else None
            #   pu_hg = int(pu_hg.replace(' ', '')) if pu_hg else None
            #   cout_hg = int(cout_hg.replace(' ', '')) if cout_hg else None
            #
            #   coef_chu = request.POST.get('coef_chu', None)
            #   pu_chu = request.POST.get('pu_chu', None)
            #   cout_chu = request.POST.get('cout_chu', None)
            #   #
            #   coef_chu = int(coef_chu.replace(' ', '')) if coef_chu else None
            #   pu_chu = int(pu_chu.replace(' ', '')) if pu_chu else None
            #   cout_chu = int(cout_chu.replace(' ', '')) if cout_chu else None
            #
            #   coef_ica = request.POST.get('coef_ica', None)
            #   pu_ica = request.POST.get('pu_ica', None)
            #   cout_ica = request.POST.get('cout_ica', None)
            #   #
            #   coef_ica = int(coef_ica.replace(' ', '')) if coef_ica else None
            #   pu_ica = int(pu_ica.replace(' ', '')) if pu_ica else None
            #   cout_ica = int(cout_ica.replace(' ', '')) if cout_ica else None
            #
            #   new_related_tarif = Tarif.objects.create(
            #       created_by = request.user,
            #       bureau = bureau,
            #       # #
            #       coef_classique = coef_classique,
            #       pu_classique = pu_classique,
            #       cout_classique = cout_classique,
            #       #
            #       coef_mutuelle = coef_mutuelle,
            #       pu_mutuelle = pu_mutuelle,
            #       cout_mutuelle = cout_mutuelle,
            #       #
            #       coef_public_hg = coef_hg,
            #       pu_public_hg = pu_hg,
            #       cout_public_hg = cout_hg,
            #       #
            #       coef_public_chu = coef_chu,
            #       pu_public_chu = pu_chu,
            #       cout_public_chu = cout_chu,
            #       #
            #       coef_public_ica = coef_ica,
            #       pu_public_ica = pu_ica,
            #       cout_public_ica = cout_ica
            #   )
            #   new_related_tarif.save()
            #   new_related_tarif.acte = nouveau_acte
            #   new_related_tarif.save()

            response = {
                'statut': 1,
                'message': "Enregistrement effectuée avec succès !",
                'data': {}
            }

        else:
            response = {
                'statut': 0,
                'message': "Vous n'êtes lié à aucun bureau !",
                'data': {}
            }

    else:

        response = {
            'statut': 0,
            'message': "Methode non autorisée !",
            'data': {}
        }

    return JsonResponse(response)


def modifier_acte(request, acte_id):
    #
    user = request.user

    acte = Acte.objects.get(id=acte_id)
    # identique à celui de def update_acte
    if request.user.is_superuser:  # Filtre les paramètres en fonction du statut d'administrateur
        parametres = ParamActe.objects.filter(acte=acte)  # Tous les paramètres pour les super admins
    else:
        parametres = ParamActe.objects.filter(acte=acte,
                                              bureau=request.user.bureau)  # Filtre par bureau pour les utilisateurs normaux
    tarif = Tarif.objects.filter(acte_id=acte_id).first()

    rubriques = Rubrique.objects.filter(status=True)

    selected_rubrique_id = acte.rubrique.id if acte.rubrique else None

    rubrique_regroupement_actes = []
    selected_regroupement_acte_id = None

    if selected_rubrique_id:
        selected_rubrique = Rubrique.objects.get(id=selected_rubrique_id)
        rubrique_regroupement_actes = RegroupementActe.objects.filter(rubrique=selected_rubrique)
        selected_regroupement_acte_id = acte.regroupement_acte.id if acte.regroupement_acte else None

    all_type_actes = TypeActe.objects.all()
    type_actes = json.dumps(list(all_type_actes.values('id', 'libelle')))

    base_calcul_tm_choices = BaseCalculTM.choices
    selected_base_calcul_tm = acte.base_calcul_tm

    related_tarifs = Tarif.objects.filter(acte_id=acte_id, bureau=user.bureau, prestataire__isnull=True,
                                          statut=Statut.ACTIF).all()

    return render(request, 'acte/modal_modifier_acte.html', {
        'acte': acte,
        'parametres': parametres,
        'tarif': tarif,
        'rubriques': rubriques,
        'selected_rubrique_id': selected_rubrique_id,
        'rubrique_regroupement_actes': rubrique_regroupement_actes,
        'selected_regroupement_acte_id': selected_regroupement_acte_id,
        'type_actes': type_actes,
        'base_calcul_tm_choices': base_calcul_tm_choices,
        'selected_base_calcul_tm': selected_base_calcul_tm,
        'related_tarifs': related_tarifs,
    })


def supprimer_acte(request, acte_id):
    if request.method == 'POST':
        bureau = request.user.bureau

        acte = Acte.objects.filter(id=acte_id).first()
        tarif = Tarif.objects.filter(acte_id=acte_id).first()

        # update acte
        if bureau:

            rubrique_id = request.POST.get('rubrique_id')
            acte.rubrique = Rubrique.objects.get(id=rubrique_id)

            regroupement_acte_id = request.POST.get('regroupement_acte_id')
            acte.regroupement_acte = RegroupementActe.objects.get(id=regroupement_acte_id)

            type_acte_id = request.POST.get('type_acte')
            acte.type_acte = TypeActe.objects.get(id=type_acte_id)

            acte.libelle = request.POST.get('libelle', None)

            code = request.POST.get('code', None)
            if code == '':
                code = None
            # acte.code = code

            acte.lettre_cle = request.POST.get('lettre_cle', None)

            delais_controle = request.POST.get('delais_controle', None)
            if delais_controle:
                delais_controle = int(delais_controle.replace(' ', ''))
            else:
                delais_controle = None

            acte.save()

        # Enregistrer les paramètres (particularités) de l'acte pour le bureau de l'utilisateur connecté
        # excatement le même envoyer au modal (render modal_modifier_acte)
        if request.user.is_superuser:  # Filtre les paramètres en fonction du statut d'administrateur
            parametres = ParamActe.objects.filter(acte=acte)  # Tous les paramètres pour les super admins
        else:
            parametres = ParamActe.objects.filter(acte=acte,
                                                  bureau=request.user.bureau)  # Filtre par bureau pour les utilisateurs normaux

        for i in range(1, len(parametres) + 1):
            bureau_id = request.POST.get(f'bureau_id_{i}')
            delais_controle = request.POST.get(f'delais_controle_{i}', '').replace(' ', '')
            entente_prealable = f'entente_prealable_{i}' in request.POST
            specialiste_uniquement = f'specialiste_uniquement_{i}' in request.POST
            est_gratuit = f'est_gratuit_{i}' in request.POST
            status = f'status_{i}' in request.POST

            # Récupérer ou créer l'objet ParamActe
            param_acte = ParamActe.objects.filter(bureau_id=bureau_id, acte=acte).first()
            if param_acte:
                data_before = model_to_dict(param_acte)

                param_acte.delais_controle = delais_controle
                param_acte.entente_prealable = entente_prealable
                param_acte.specialiste_uniquement = specialiste_uniquement
                param_acte.est_gratuit = est_gratuit
                param_acte.status = status
                param_acte.updated_by = request.user
                param_acte.updated_at = datetime.datetime.now(tz=timezone.utc)
                param_acte.base_calcul_tm = request.POST.get('base_calcul_tm', None)
                param_acte.save()

                data_after = model_to_dict(param_acte)

                ActionLog.objects.create(
                    done_by=request.user, action="update",
                    description="Modification du paramétrage d'un acte", table="param_acte",
                    row=param_acte.pk,
                    data_before=json.dumps(data_before),
                    data_after=json.dumps(data_after)
                )

        '''
        if tarif:
            # update related tarif
            coef_classique = request.POST.get('coef_classique', None)
            pu_classique = request.POST.get('pu_classique', None)
            cout_classique = request.POST.get('cout_classique', None)
            #
            tarif.coef_classique = int(coef_classique.replace(' ', '')) if coef_classique else None
            tarif.pu_classique = int(pu_classique.replace(' ', '')) if pu_classique else None
            tarif.cout_classique = int(cout_classique.replace(' ', '')) if cout_classique else None

            coef_mutuelle = request.POST.get('coef_mutuelle', None)
            pu_mutuelle = request.POST.get('pu_mutuelle', None)
            cout_mutuelle = request.POST.get('cout_mutuelle', None)
            #
            tarif.coef_mutuelle = int(coef_mutuelle.replace(' ', '')) if coef_mutuelle else None
            tarif.pu_mutuelle = int(pu_mutuelle.replace(' ', '')) if pu_mutuelle else None
            tarif.cout_mutuelle = int(cout_mutuelle.replace(' ', '')) if cout_mutuelle else None

            coef_hg = request.POST.get('coef_hg', None)
            pu_hg = request.POST.get('pu_hg', None)
            cout_hg = request.POST.get('cout_hg', None)
            #
            tarif.coef_public_hg = int(coef_hg.replace(' ', '')) if coef_hg else None
            tarif.pu_public_hg = int(pu_hg.replace(' ', '')) if pu_hg else None
            tarif.cout_public_hg = int(cout_hg.replace(' ', '')) if cout_hg else None

            coef_chu = request.POST.get('coef_chu', None)
            pu_chu = request.POST.get('pu_chu', None)
            cout_chu = request.POST.get('cout_chu', None)
            #
            tarif.coef_public_chu = int(coef_chu.replace(' ', '')) if coef_chu else None
            tarif.pu_public_chu = int(pu_chu.replace(' ', '')) if pu_chu else None
            tarif.cout_public_chu = int(cout_chu.replace(' ', '')) if cout_chu else None

            coef_ica = request.POST.get('coef_ica', None)
            pu_ica = request.POST.get('pu_ica', None)
            cout_ica = request.POST.get('cout_ica', None)
            #
            tarif.coef_public_ica = int(coef_ica.replace(' ', '')) if coef_ica else None
            tarif.pu_public_ica = int(pu_ica.replace(' ', '')) if pu_ica else None
            tarif.cout_public_ica = int(cout_ica.replace(' ', '')) if cout_ica else None

            tarif.save()
        '''

        response = {
            'statut': 1,
            'message': "Modification de l'acte effectuée avec succès !",
            'data': {
            }
        }

    else:

        response = {
            'statut': 0,
            'message': "Methode non autorisée !",
            'data': {}
        }

    return JsonResponse(response)


def add_acte_tarif(request, acte_id):
    if request.method == 'POST':
        #
        acte = Acte.objects.filter(id=acte_id).first()
        bureau = request.user.bureau

        if bureau:
            coef_classique = request.POST.get('coef_classique', None)
            pu_classique = request.POST.get('pu_classique', None)
            cout_classique = request.POST.get('cout_classique', None)
            #
            coef_classique = int(coef_classique.replace(' ', '')) if coef_classique else None
            pu_classique = int(pu_classique.replace(' ', '')) if pu_classique else None
            cout_classique = int(cout_classique.replace(' ', '')) if cout_classique else None

            coef_mutuelle = request.POST.get('coef_mutuelle', None)
            pu_mutuelle = request.POST.get('pu_mutuelle', None)
            cout_mutuelle = request.POST.get('cout_mutuelle', None)
            coef_mutuelle = int(coef_mutuelle.replace(' ', '')) if coef_mutuelle else None
            pu_mutuelle = int(pu_mutuelle.replace(' ', '')) if pu_mutuelle else None
            cout_mutuelle = int(cout_mutuelle.replace(' ', '')) if cout_mutuelle else None

            coef_hg = request.POST.get('coef_hg', None)
            pu_hg = request.POST.get('pu_hg', None)
            cout_hg = request.POST.get('cout_hg', None)
            coef_hg = int(coef_hg.replace(' ', '')) if coef_hg else None
            pu_hg = int(pu_hg.replace(' ', '')) if pu_hg else None
            cout_hg = int(cout_hg.replace(' ', '')) if cout_hg else None

            coef_chu = request.POST.get('coef_chu', None)
            pu_chu = request.POST.get('pu_chu', None)
            cout_chu = request.POST.get('cout_chu', None)
            coef_chu = int(coef_chu.replace(' ', '')) if coef_chu else None
            pu_chu = int(pu_chu.replace(' ', '')) if pu_chu else None
            cout_chu = int(cout_chu.replace(' ', '')) if cout_chu else None

            coef_ica = request.POST.get('coef_ica', None)
            pu_ica = request.POST.get('pu_ica', None)
            cout_ica = request.POST.get('cout_ica', None)
            coef_ica = int(coef_ica.replace(' ', '')) if coef_ica else None
            pu_ica = int(pu_ica.replace(' ', '')) if pu_ica else None
            cout_ica = int(cout_ica.replace(' ', '')) if cout_ica else None

            new_tarif = Tarif.objects.create(
                bureau=bureau,
                acte=acte,
                code_acte=acte.code,
                ##
                coef_classique=coef_classique,
                pu_classique=pu_classique,
                cout_classique=cout_classique,
                #
                coef_mutuelle=coef_mutuelle,
                pu_mutuelle=pu_mutuelle,
                cout_mutuelle=cout_mutuelle,
                #
                coef_public_hg=coef_hg,
                pu_public_hg=pu_hg,
                cout_public_hg=cout_hg,
                #
                coef_public_chu=coef_chu,
                pu_public_chu=pu_chu,
                cout_public_chu=cout_chu,
                #
                coef_public_ica=coef_ica,
                pu_public_ica=pu_ica,
                cout_public_ica=cout_ica
            )
            new_tarif.save()

            response = {
                'statut': 1,
                'message': "Ajout de tarif effectuée avec succès !",
                'data': {}
            }
        else:
            response = {
                'statut': 0,
                'message': "Vous n'êtes lié à aucun bureau !",
                'data': {}
            }
    else:
        response = {
            'statut': 0,
            'message': "Méthode non autorisée !",
            'data': {}
        }

    return JsonResponse(response)


def desactiver_tarif_acte(request, acte_id, tarif_id):
    if request.method == 'POST':
        try:
            tarif = Tarif.objects.get(id=tarif_id)
            tarif.statut = Statut.INACTIF
            tarif.statut_validite = StatutValidite.CLOTURE
            tarif.deleted_by = request.user
            tarif.updated_at = datetime.datetime.now(tz=timezone.utc)
            tarif.save()

            response = {
                'statut': 1,
                'message': "Tarif désactivé avec succès",
                'data': {}
            }
        except Tarif.DoesNotExist:
            response = {
                'statut': 0,
                'message': "Tarif non trouvé",
                'data': {}
            }
    else:
        response = {
            'statut': 0,
            'message': "Méthode non autorisée",
            'data': {}
        }

    return JsonResponse(response)


from .helper_config import send_verification_code
from django.contrib.auth import authenticate, login

#########################################
@login_required
def verify_code(request):
    if request.method == 'GET':
        print("User email:", request.user.email)

        request.session['is_verified'] = True
        return redirect('/')

        # if not request.user.email:
        #     request.session['is_verified'] = True
        #     return redirect('/')
        #
        # code = "123456" # send_verification_code(request, request.user.email)
        # if code:
        #     request.session['verification_code'] = code
        #     return render(request, '2fa/verify_code.html')


    elif request.method == 'POST':
        submitted_code = request.POST.get('code')
        stored_code = request.session.get('verification_code')

        print("Submitted code:", submitted_code)
        print("Stored code:", stored_code)

        if submitted_code == stored_code:
            del request.session['verification_code']
            request.session['is_verified'] = True
            messages.success(request, 'Verification successful. You are now logged in.')
            return redirect('/')
        else:
            messages.error(request, 'Invalid verification code. Please try again.')

    return render(request, '2fa/verify_code.html')


@login_required
def download_background_query_result(request, query_id):
    try:
        query = BackgroundQueryTask.objects.get(id=query_id)
        url = query.file.url
        query.delete()
        return redirect(url)
    except Exception as e:
        return redirect(reverse('admin:configurations_backgroundquerytask_changelist'))



    return JsonResponse(response)


def generate_modele_tarifs_bureau(request):
    # Données à inclure dans le DataFrame
    actes = Acte.objects.filter(type_acte__code="acte", status=True).order_by('rubrique_id')

    # Créer un Workbook et accéder à la première feuille
    wb = Workbook()
    ws = wb.active

    # Données à inclure dans le DataFrame
    data = {
        'CODE_RUBRIQUE': [],
        'LIBELLE_ACTE': [],
        'ID_ACTE': [],
        'CODE_ACTE': [],
        'LETTRE_CLE': [],
        # 'LETTRE_CLE_CLASSIQUE': [],
        'COEF_CLASSIQUE': [],
        'PRIX_UNIT_CLASSIQUE': [],
        'TARIF_CLASSIQUE': [],
        # 'LETTRE_CLE_MUTUELLE': [],
        'COEF_MUTUELLE': [],
        'PRIX_UNIT_MUTUELLE': [],
        'TARIF_MUTUELLE': [],
        # 'LETTRE_CLE_HG': [],
        'COEF_HG': [],
        'PRIX_UNIT_HG': [],
        'TARIF_HG': [],
        # 'LETTRE_CLE_CHU': [],
        'COEF_CHU': [],
        'PRIX_UNIT_CHU': [],
        'TARIF_CHU': [],
        # 'LETTRE_CLE_ICA': [],
        'COEF_ICA': [],
        'PRIX_UNIT_ICA': [],
        'TARIF_ICA': [],
        # 'LETTRE_CLE_PRESTATAIRE': [],
        'COEF_PRESTATAIRE': [],
        'PRIX_UNIT_PRESTATAIRE': [],
        'TARIF_PRESTATAIRE': [],
    }

    # Ajouter les actes au DataFrame
    for acte in actes:
        # renseigner avec le tarif existant de ce prestataire --
        tarif_existant = Tarif.objects.filter(acte__code=acte.code, bureau=request.user.bureau,
                                              statut=Statut.ACTIF).first()
        tarif_existant_parametre = Tarif.objects.filter(bureau=request.user.bureau, acte=acte,
                                                        prestataire_id__isnull=True, statut=Statut.ACTIF).first()

        data['CODE_RUBRIQUE'].append(acte.rubrique.libelle)
        data['LIBELLE_ACTE'].append(acte.libelle)
        data['ID_ACTE'].append(acte.id)
        data['CODE_ACTE'].append(acte.code)
        data['LETTRE_CLE'].append(acte.lettre_cle)

        # data['LETTRE_CLE_CLASSIQUE'].append(tarif_existant.lettre_cle_classique)
        data['COEF_CLASSIQUE'].append(tarif_existant.coef_classique if tarif_existant else 1)
        data['PRIX_UNIT_CLASSIQUE'].append(tarif_existant.pu_classique if tarif_existant else 0)
        data['TARIF_CLASSIQUE'].append(tarif_existant.cout_classique if tarif_existant else 0)

        # data['LETTRE_CLE_MUTUELLE'].append(tarif_existant.lettre_cle_classique)
        data['COEF_MUTUELLE'].append(tarif_existant.coef_mutuelle if tarif_existant else 1)
        data['PRIX_UNIT_MUTUELLE'].append(tarif_existant.pu_mutuelle if tarif_existant else 0)
        data['TARIF_MUTUELLE'].append(tarif_existant.cout_mutuelle if tarif_existant else 0)

        # data['LETTRE_CLE_HG'].append(tarif_existant.lettre_cle_public_hg if tarif_existant else 0)
        data['COEF_HG'].append(tarif_existant.coef_public_hg if tarif_existant else 0)
        data['PRIX_UNIT_HG'].append(tarif_existant.pu_public_hg if tarif_existant else 0)
        data['TARIF_HG'].append(tarif_existant.cout_public_hg if tarif_existant else 0)

        # data['LETTRE_CLE_CHU'].append(tarif_existant.lettre_cle_public_chu if tarif_existant else 0)
        data['COEF_CHU'].append(tarif_existant.coef_public_chu if tarif_existant else 0)
        data['PRIX_UNIT_CHU'].append(tarif_existant.pu_public_chu if tarif_existant else 0)
        data['TARIF_CHU'].append(tarif_existant.cout_public_chu if tarif_existant else 0)

        # data['LETTRE_CLE_ICA'].append(tarif_existant.lettre_cle_public_ica if tarif_existant else 0)
        data['COEF_ICA'].append(tarif_existant.coef_public_ica if tarif_existant else 0)
        data['PRIX_UNIT_ICA'].append(tarif_existant.pu_public_ica if tarif_existant else 0)
        data['TARIF_ICA'].append(tarif_existant.cout_public_ica if tarif_existant else 0)

        # data['LETTRE_CLE_PRESTATAIRE'].append('')
        data['COEF_PRESTATAIRE'].append(tarif_existant_parametre.coef_prestataire if tarif_existant_parametre else 1)
        data['PRIX_UNIT_PRESTATAIRE'].append(tarif_existant_parametre.pu_prestataire if tarif_existant_parametre else 0)
        data['TARIF_PRESTATAIRE'].append(tarif_existant_parametre.cout_prestataire if tarif_existant_parametre else 0)

    # Créer un DataFrame avec Pandas
    df = pd.DataFrame(data)

    filename = 'INOV_V1-TARIF_DU_BUREAU_' + slugify(str(request.user.bureau)).upper() + '.xlsx'
    pprint(filename)

    # Créer une réponse HTTP avec le type MIME approprié
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    # Enregistrer le DataFrame dans le fichier Excel
    df.to_excel(response, index=False, engine='openpyxl')

    return response


from django.core.exceptions import ObjectDoesNotExist
## IMPORTER LES TARIFS AU BUREAU
def import_tarifs_bureau(request):
    try:
        tarifs_existant = Tarif.objects.filter(bureau=request.user.bureau, prestataire__isnull=True, statut=Statut.ACTIF).first()

        if tarifs_existant:
            response = {
                'statut': 0,
                'message': "Vous avez déjà importé les tarifs du bureau !",
                'data': {}
            }
            return JsonResponse(response)

        file = request.FILES['fichier_import_tarif']
        df = pd.read_excel(file)
        rows_count = 0

        for index, row in df.iterrows():
            code_acte = row.get('CODE_ACTE')
            id_acte = row.get('ID_ACTE')

            try:
                acte = Acte.objects.get(id=id_acte)
                pprint("L'acte existe, donc on insère le tarif")

                # Désactiver l'ancien tarif si existant
                # Tarif.objects.filter(acte=acte).update(statut=Statut.INACTIF, statut_validite=StatutValidite.CLOTURE)

                # Insérer une ligne dans la table Tarif avec les coefficients, prix unitaire, etc.
                tarif = Tarif.objects.create(
                    acte=acte,
                    code_acte=code_acte,
                    bureau=request.user.bureau,
                    created_by=request.user,
                    statut=Statut.ACTIF,
                    statut_validite=StatutValidite.VALIDE,

                    coef_public_hg=row.get('COEF_HG'),
                    pu_public_hg=row.get('PRIX_UNIT_HG'),
                    cout_public_hg=row.get('TARIF_HG'),

                    coef_public_chu=row.get('COEF_CHU'),
                    pu_public_chu=row.get('PRIX_UNIT_CHU'),
                    cout_public_chu=row.get('TARIF_CHU'),

                    coef_public_ica=row.get('COEF_ICA'),
                    pu_public_ica=row.get('PRIX_UNIT_ICA'),
                    cout_public_ica=row.get('TARIF_ICA'),

                    coef_mutuelle=row.get('COEF_MUTUELLE'),
                    pu_mutuelle=row.get('PRIX_UNIT_MUTUELLE'),
                    cout_mutuelle=row.get('TARIF_MUTUELLE'),

                    coef_classique=row.get('COEF_CLASSIQUE'),
                    pu_classique=row.get('PRIX_UNIT_CLASSIQUE'),
                    cout_classique=row.get('TARIF_CLASSIQUE'),

                    coef_prestataire=row.get('COEF_PRESTATAIRE'),
                    pu_prestataire=row.get('PRIX_UNIT_PRESTATAIRE'),
                    cout_prestataire=row.get('TARIF_PRESTATAIRE'),
                )
            except ObjectDoesNotExist:
                continue

        response = {
            'statut': 1,
            'message': "Tarifs importés avec succès !",
            'data': {}
        }

    except Exception as e:
        response = {
            'statut': 0,
            'message': f"Erreur lors de l'importation des tarifs : {str(e)}",
            'data': {}
        }

    return JsonResponse(response)


class ConnectedUsersView(PermissionRequiredMixin, TemplateView):
    permission_required = "configurations.view_prestataire"
    template_name = 'users/connected_users.html'
    model = User

    def format_duration(self, duration):
        if duration is None:
            return "0:00:00"

        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{hours}:{minutes:02}:{seconds:02}"

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        sessions = Session.objects.filter(expire_date__gt=timezone.now())
        active_user_ids = []
        session_data = {}

        for session in sessions:
            data = session.get_decoded()
            user_id = data.get('_auth_user_id')
            last_visited = data.get('last_visited', '')
            last_ip_address = data.get('last_ip_address', '')
            last_visit_time = data.get('last_visit_time', '')
            last_visit_time_dt = (
                timezone.make_aware(datetime.datetime.fromisoformat(last_visit_time))
                if last_visit_time else None
            )
            elapsed_time = (datetime.datetime.now(tz=timezone.utc) - last_visit_time_dt) if last_visit_time_dt else None

            if user_id:
                active_user_ids.append(user_id)
                session_data[user_id] = {
                    'id': user_id,
                    'last_visited': last_visited,
                    'last_ip_address': last_ip_address,
                    'last_visit_time': datetime.datetime.fromisoformat(last_visit_time) if last_visit_time else None,
                    'elapsed_time': self.format_duration(elapsed_time),
                }

        active_users = User.objects.filter(id__in=active_user_ids)

        #merge active_users_session_data and active_users
        active_users_session_data = []
        for user in active_users:
            session = session_data.get(str(user.id), {})
            active_users_session_data.append({
                'user_data': user,
                'session_data': session,
            })

        bureaux = Bureau.objects.filter(status=True)

        context_perso = {
            'bureaux': bureaux,
            'active_users_session_data': active_users_session_data,
        }

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


def logout_user(request, user_id):
    try:
        # Récupérer l'utilisateur
        user = User.objects.get(id=user_id)

        # Récupérer toutes les sessions
        sessions = Session.objects.filter(expire_date__gte=timezone.now())

        # Parcourir les sessions
        for session in sessions:
            data = session.get_decoded()
            # Vérifier si l'utilisateur est dans cette session
            if data.get('_auth_user_id') == str(user.id):
                session.delete()  # Supprime la session
                break  # On peut arrêter après avoir trouvé la session

        return redirect(reverse('connectedusers'))

    except User.DoesNotExist:
        print("Utilisateur non trouvé.")


#---------------------BRANCHE---------------------------------------------

@method_decorator(login_required, name='dispatch')
class DbSuperAdminQueryView(TemplateView):
    template_name = 'db_query/db_super_admin_query.html'
    model = Aliment

    def get(self, request, *args, **kwargs):
        # TODO , filtrer sur le bureau : prestataire__bureau=request.user.bureau

        query_datas = [
            {
                "query_label": "MODIFICATION DE DATE D'ENTREE DE BÉNÉFICIAIRE",
                "query_name": "BENEF_ENTREE_MODIF",
            },
            {
                "query_label": "MODIFICATION DE DATE DE SORTIE DE BÉNÉFICIAIRE",
                "query_name": "BENEF_SORTI_MODIF",
            },
            {
                "query_label": "ANNULATION DE QUITTANCE SOLDÉE",
                "query_name": "ANNULATION_QUITTANCE_SOLDEE",
            },
            {
                "query_label": "ANNULATION DE BORDEREAU DE PAIEMENT",
                "query_name": "ANNULATION_BR_PAIEMENT",
            },
            {
                "query_label": "ANNULATION DE BORDEREAU D'ORDONNANCEMENT",
                "query_name": "ANNULATION_BR_ORDONNANCEMENT",
            }
            #
        ]



        context = self.get_context_data(**kwargs)
        context['query_datas'] = query_datas

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        print("----- fn= post -----")
        print(request.POST)
        print(request.POST.dict())

        query_name = request.POST.get('query_name')

        if query_name == "ANNULATION_QUITTANCE_SOLDEE":

            aq_numero = request.POST.get('aq_numero')
            aq_motif = request.POST.get('aq_motif')

            quittance = Quittance.objects.filter(numero=aq_numero, bureau=request.user.bureau).first()

            if quittance:
                # Verification si la quittance est déjà annulée
                if quittance.statut_validite == "ANNULEE":
                    return JsonResponse({
                        "message": "Erreur : Cette quittance a déjà été annulée."
                    }, status=400)

                # recuperation des reglements de la quittance
                reglement = Reglement.objects.filter(quittance=quittance)
                print("reglement", reglement)

                # Verification si reglement REVERSE ou NON
                revcomp = False
                for rgm in reglement:
                    if rgm.statut_reversement_compagnie == 'REVERSE':
                        revcomp = True
                        break

                if revcomp:
                    return JsonResponse({
                        "message": "Erreur : Impossible d'annuler la quittance car elle a déjà été reversée à la compagnie."
                    }, status=404)

                # Annulation de la quittance et de ses reglements
                date_du_jour = datetime.datetime.now()
                observation = f"Annulation de la quittance {quittance.numero} le {date_du_jour} pour motif : {aq_motif}"
                quittance.statut_validite = "ANNULEE"
                quittance.observation = observation
                quittance.save()

                # Annulation des reglements
                for rgm in reglement:
                    rgm.statut_validite = "ANNULE"
                    rgm.observation = observation
                    rgm.motif_annulation = aq_motif
                    rgm.save()

                return JsonResponse({
                    "message": f"Succès : La quittance {aq_numero} a été annulée avec succès."
                }, status=200)

            else:
                return JsonResponse({
                    "message": "Erreur : Quittance introuvable."
                }, status=404)

        ##
        elif query_name == "ANNULATION_BR_PAIEMENT":
            abrp_numero = request.POST.get('abrp_numero')
            abrp_motif = request.POST.get('abrp_motif')

            paiement_comptable = PaiementComptable.objects.filter(numero=abrp_numero, bureau=request.user.bureau).first()

            if paiement_comptable:
                # Verification si le paiement comptable est déjà annulé
                if paiement_comptable.statut_validite == StatutValidite.SUPPRIME:
                    return JsonResponse({
                        "message": "Erreur : Ce bordereau de paiement comptable a déjà été annulé."
                    }, status=400)

                date_du_jour = datetime.datetime.now()
                observation = f"Annulation de bordereau de paiement {paiement_comptable.numero} le {date_du_jour} pour motif : {abrp_motif}"

                # traitement br paiement comptable
                paiement_comptable.pc_deleted_by = request.user
                paiement_comptable.statut_validite = StatutValidite.SUPPRIME
                paiement_comptable.observation = observation
                paiement_comptable.save()

                # recuperation de borderereau associé
                paiement_comptable.bordereau_ordonnancement.statut_paiement = StatutPaiementSinistre.ORDONNANCE
                paiement_comptable.bordereau_ordonnancement.save()

                # récuperation sinistres associés
                sinistres = Sinistre.objects.filter(paiement_comptable=paiement_comptable)
                if sinistres:
                    for sinistre in sinistres:
                        sinistre.paiement_comptable = None
                        sinistre.date_paiement = None
                        sinistre.statut_paiement = StatutPaiementSinistre.ORDONNANCE
                        sinistre.save()
                        # mettre la facture à ordonnancer
                        sinistre.facture_prestataire.statut = SatutBordereauDossierSinistres.ORDONNANCE
                        sinistre.facture_prestataire.save()

                        # historiser les lignes qui étaient sur le bordereau
                        HistoriquePaiementComptableSinistre.objects.create(created_by=request.user,
                                                                        paiement_comptable=paiement_comptable,
                                                                        sinistre=sinistre,
                                                                        montant_paye=sinistre.montant_remb_accepte,
                                                                        observation=observation)

                # enregistrer dans les log
                ActionLog.objects.create(done_by=request.user, action="annulation_bordereau_paiement",
                                             description="Annulation d'un bordereau de paiement",
                                             table="paiement_comptable",
                                             row=paiement_comptable.pk)

                return JsonResponse({
                    "message": f"Succès : Le bordereau de paiement {abrp_numero} a été annulé avec succès."
                }, status=200)

            else:
                return JsonResponse({
                    "message": "Erreur : Bordereau de paiement comptable introuvable."
                }, status=404)

        elif query_name == "ANNULATION_BR_ORDONNANCEMENT":

            abro_numero = request.POST.get('abro_numero')
            abro_motif = request.POST.get('abro_motif')

            # recuperation du bordereau d'ordonnancement associé au paiement comptable
            bordereau_ordonnancement = BordereauOrdonnancement.objects.filter(numero=abro_numero, bureau=request.user.bureau).first()

            if bordereau_ordonnancement:
                # Verification si le bordereau d'ordonnancement est déjà annulé
                if bordereau_ordonnancement.statut_validite == StatutValidite.SUPPRIME:
                    return JsonResponse({
                        "message": "Erreur : Ce bordereau d'ordonnancement a déjà été annulé."
                    }, status=400)

                date_du_jour = datetime.datetime.now()
                observation = f"Annulation de bordereau d'ordonnancement {bordereau_ordonnancement.numero} le {date_du_jour} pour motif : {abro_motif}"

                # traitement facture
                bordereau_ordonnancement.bo_deleted_by = request.user
                bordereau_ordonnancement.statut_paiement = StatutPaiementSinistre.ATTENTE
                bordereau_ordonnancement.statut_validite = StatutValidite.SUPPRIME
                bordereau_ordonnancement.observation = observation
                bordereau_ordonnancement.save()

                # récuperation sinistres associés
                sinistres = Sinistre.objects.filter(bordereau_ordonnancement=bordereau_ordonnancement)
                if sinistres:
                    for sinistre in sinistres:
                        sinistre.bordereau_ordonnancement = None
                        sinistre.statut_paiement = StatutPaiementSinistre.ATTENTE
                        # sinistre.observation = str(sinistre.observation)
                        sinistre.save()

                        # mettre la facture à traitée:: faire sortir de la boucle lorsque les factures seront directement liées aux bordereau d'ordonnancement
                        sinistre.facture_prestataire.statut = SatutBordereauDossierSinistres.VALIDE
                        sinistre.facture_prestataire.save()

                        # historiser les lignes qui étaient sur le bordereau
                        HistoriqueOrdonnancementSinistre.objects.create(created_by=request.user,
                                                                        bordereau_ordonnancement=bordereau_ordonnancement,
                                                                        sinistre=sinistre,
                                                                        montant_ordonnance=sinistre.montant_remb_accepte,
                                                                        observation=observation)

                # enregistrer dans les log
                ActionLog.objects.create(done_by=request.user, action="annulation_bordereau_ordonnancement",
                                         description="Annulation d'un bordereau d'ordonnancement",
                                         table="bordereau_ordonnancement",
                                         row=bordereau_ordonnancement.pk)

                return JsonResponse({
                    "message": f"Succès : Le bordereau d'ordonnancement {abro_numero} a été annulé avec succès."
                }, status=200)
            else:
                return JsonResponse({
                    "message": "Erreur : Bordereau d'ordonnancement introuvable."
                }, status=404)
        elif query_name == "BENEF_ENTREE_MODIF":

            benefe_numero = request.POST.get('benefe_numero')
            benefe_date = request.POST.get('benefe_date')
            benefe_motif = request.POST.get('benefe_motif')



            carte = Carte.objects.filter(numero=benefe_numero, statut=Statut.ACTIF, aliment__bureau=request.user.bureau).first()

            if carte:
                aliment = carte.aliment
                aliment_formule = aliment.aliment_formule if aliment else None
                mouvement = aliment.last_mouvement if aliment else None

                # liste de sinistre lié à la carte
                sinistre = aliment.ses_sinistres.all().filter(
                    statut_validite=StatutValidite.VALIDE,
                    statut__in=[StatutSinistre.ACCORDE, StatutSinistre.ATTENTE],
                    date_survenance__lte=benefe_date
                ).order_by('-date_survenance').first() if aliment else None

                # verification si le bénéficiaire n'a pas sinistre a enterieur a la nouvelle date d'entree
                if sinistre:
                    return JsonResponse({
                        "message": "Erreur : Impossible de modifier la date d'entrée du bénéficiaire, car un sinistre antérieur à la nouvelle date d'entrée a été détecté."
                    }, status=404)


                date_du_jour = datetime.datetime.now()
                observation = f"Modification de date d'entrée de {carte.numero} le {date_du_jour} pour motif : {benefe_motif}"

                if aliment:
                    aliment.date_affiliation = benefe_date
                    aliment.save()

                    if aliment_formule:
                        aliment_formule.date_debut = benefe_date
                        aliment_formule.observation = observation
                        aliment_formule.save()

                    if mouvement:
                        if mouvement.mouvement_id == 7:  # INCORPORATION
                            mouvement.date_effet = benefe_date
                            mouvement.observation = observation
                            mouvement.save()
                else:
                    return JsonResponse({
                        "message": "Erreur : Bénéficiaire introuvable."
                    }, status=404)


                return JsonResponse({
                    "message": f"Succès : La date d'entrée du bénéficiaire {benefe_numero} a été modifié avec succès."
                }, status=200)


            else:
                return JsonResponse({
                    "message": "Erreur : Bénéficiaire introuvable."
                }, status=404)


        elif query_name == "BENEF_SORTI_MODIF":

            benefs_numero = request.POST.get('benefs_numero')
            benefs_date = request.POST.get('benefs_date')
            benefs_motif = request.POST.get('benefs_motif')

            carte = Carte.objects.filter(numero=benefs_numero, statut=Statut.ACTIF,
                                         aliment__bureau=request.user.bureau).first()

            if carte:
                aliment = carte.aliment
                aliment_formule = aliment.aliment_formule if aliment else None
                mouvement = aliment.last_mouvement if aliment else None

                # liste de sinistre lié à la carte
                sinistre = aliment.ses_sinistres.all().filter(
                    statut_validite=StatutValidite.VALIDE,
                    statut__in=[StatutSinistre.ACCORDE, StatutSinistre.ATTENTE],
                    date_survenance__gte=benefs_date
                ).order_by('-date_survenance').first() if aliment else None

                # verification si le bénéficiaire n'a pas sinistre a enterieur a la nouvelle date d'entree
                if sinistre:
                    return JsonResponse({
                        "message": "Erreur : Impossible de modifier la date d'entrée du bénéficiaire, car un sinistre posterieur à la nouvelle date de sortie a été détecté."
                    }, status=404)

                date_du_jour = datetime.datetime.now()
                observation = f"Modification de date de sortie de {carte.numero} le {date_du_jour} pour motif : {benefs_motif}"


                if aliment:
                    if aliment_formule.date_fin:
                        aliment.date_sortie = benefs_date
                        aliment.save()

                        aliment_formule.date_fin = benefs_date
                        aliment_formule.observation = observation
                        aliment_formule.save()

                        if mouvement.mouvement_id == 11:  # SORTIE-BENEF
                            mouvement.date_effet = benefs_date
                            mouvement.observation = observation
                            mouvement.save()

                        return JsonResponse({
                            "message": f"Succès : La date de sortie du bénéficiaire {benefs_numero} a été modifié avec succès."
                        }, status=200)

                    else:
                        return JsonResponse({
                            "message": "Erreur : Impossible de modifier la date de sortie du bénéficiaire, car il n'est pas encore sorti."
                        }, status=404)


                else:
                    return JsonResponse({
                        "message": "Erreur : Bénéficiaire introuvable."
                    }, status=404)

            else:
                return JsonResponse({
                    "message": "Erreur : Bénéficiaire introuvable."
                }, status=404)
        else:
            return JsonResponse({
                "message": "Erreur : Cette action n'est pas prise en charge."
            }, status=404)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }



class BrancheView(PermissionRequiredMixin,TemplateView):
    template_name = 'branches/branche.html'
    permission_required = "configurations.view_branches"
    model = Branche

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        branche = Branche.objects.all().order_by('-id')

        context_perso = {'branches': branche}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_branche(request):

    if request.method == 'POST':
        # Récupérer le dernier code dans la base de données
        dernier_branche = Branche.objects.order_by('-pk').first()
        dernier_code = int(dernier_branche.code) if dernier_branche and dernier_branche.code.isdigit() else 0

        # Ajouter 10 au dernier code
        nouveau_code = dernier_code + 10

        # Créer une nouvelle branche
        branche_created = Branche.objects.create(
            nom=request.POST.get('nom'),
            status=request.POST.get('statut'),
            created_at=datetime.now(),
            code=str(nouveau_code).zfill(2)  # Remplir avec des zéros si nécessaire
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': branche_created.pk,
                'libelle': branche_created.nom,
                'status': branche_created.status,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_branche(request, branche_id):

    branche = Branche.objects.get(id=branche_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Branche.objects.filter(id=branche_id).update(nom=request.POST.get('nom'),
                                                    status=request.POST.get('statut'),
                                                    updated_at=datetime.now(),
                                                   )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': branche.pk,
                'nom': branche.nom,
                'status': branche.status,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'branches/modal_modifier_branche.html', {'branche': branche})


@login_required
def supprimer_branche(request, branche_id):
    if request.method == "POST":

        branche_id = request.POST.get('branche_id')
        print("branche id : ", branche_id)
        branche = Branche.objects.get(id=branche_id)
        if branche.pk is not None:

            branche.delete()

            response = {
                'statut': 1,
                'message': "Branche supprimée avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Apporteur non trouvé !",
            }

        return JsonResponse(response)

#---------------------FIN BRANCHE---------------------------------------------

#------------------------------BUSINESS UNIT---------------------------------------

class BusinessUnitView(PermissionRequiredMixin,TemplateView):
    template_name = 'businessunits/businessunit.html'
    permission_required = "configurations.view_businessunit"
    model = BusinessUnit

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        businessunits = BusinessUnit.objects.all().order_by('-id')

        context_perso = {'businessunits': businessunits}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_businessunit(request):

    if request.method == 'POST':

        businessunit_created = BusinessUnit.objects.create(libelle=request.POST.get('libelle'),
                                       status=request.POST.get('statut'),
                                       created_at=datetime.now(),
                                       )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': businessunit_created.pk,
                'libelle': businessunit_created.libelle,
                'status': businessunit_created.status,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_businessunit(request, businessunit_id):

    businessunit = BusinessUnit.objects.get(id=businessunit_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        BusinessUnit.objects.filter(id=businessunit_id).update(
                                                    libelle=request.POST.get('libelle'),
                                                    status=request.POST.get('statut'),
                                                   )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': businessunit.pk,
                'nom': businessunit.libelle,
                'status': businessunit.status,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'businessunits/modal_modifier_businessunit.html', {'businessunit': businessunit})


@login_required
def supprimer_businessunit(request, businessunit_id):
    if request.method == "POST":

        businessunit_id = request.POST.get('businessunit_id')
        print("businessunit id : ", businessunit_id)
        businessunit = BusinessUnit.objects.get(id=businessunit_id)
        if businessunit.pk is not None:

            businessunit.delete()

            response = {
                'statut': 1,
                'message': "BusinessUnit supprimé avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "BusinessUnit non trouvé !",
            }

        return JsonResponse(response)

#------------------------------FIN BUSINESS UNIT---------------------------------------


#------------------------------BANQUE--------------------------------------

class BanquesView(PermissionRequiredMixin,TemplateView):
    template_name = 'banques/banque.html'
    permission_required = "configurations.view_banque"
    model = Banque

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        banque = Banque.objects.all()
        bureau = Bureau.objects.all()
        utilisateurs = User.objects.filter(bureau=request.user.bureau, type_utilisateur__code="INTERNE",
                                           is_active=True).order_by('last_name')

        context_perso = {'banques': banque, 'utilisateurs': utilisateurs, 'bureaux': bureau}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_banque(request):

    if request.method == 'POST':

        banque_created = Banque.objects.create(bureau_id=request.user.bureau_id,
                                       libelle=request.POST.get('libelle'),
                                       nom_complet=request.POST.get('nom_complet'),
                                       status=request.POST.get('statut'),
                                       created_by_id=request.user.id,
                                       created_at=datetime.now(),
                                       )

        #TODO : nomenclature du code banque a trouver
        banque_created.code = 'BQ-' + str(Date.today().year)[-2:] + '-' + str(banque_created.pk).zfill(7)
        banque_created.save()

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': banque_created.pk,
                'libelle': banque_created.libelle,
                'status': banque_created.status,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_banque(request, banque_id):

    banque = Banque.objects.get(id=banque_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Banque.objects.filter(id=banque_id).update(
                                                    libelle=request.POST.get('libelle'),
                                                    nom_complet=request.POST.get('nom_complet'),
                                                    status=request.POST.get('statut'),
                                                    updated_at=datetime.now(),
                                                   )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': banque.pk,
                'nom': banque.libelle,
                'status': banque.status,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'banques/modal_modifier_banque.html', {'banque': banque})


@login_required
def supprimer_banque(request, banque_id):
    if request.method == "POST":

        banque_id = request.POST.get('banque_id')
        print("banque id : ", banque_id)
        banque = Banque.objects.get(id=banque_id)
        if banque.pk is not None:

            banque.delete()

            response = {
                'statut': 1,
                'message': "Banque supprimée avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Banque non trouvé !",
            }

        return JsonResponse(response)

#------------------------------FIN BANQUE--------------------------------------

#------------------------APPORTEUR----------------------------------

class ApporteurView(PermissionRequiredMixin, TemplateView):
        template_name = 'apporteurs/apporteur.html'
        permission_required = "configurations.view_apporteur"
        model = Apporteur

        def get(self, request, *args, **kwargs):
            context_original = self.get_context_data(**kwargs)

            types_apporteur = TypeApporteur.objects.all()
            types_personnes = TypePersonne.objects.all()
            pays = Pays.objects.order_by('-nom')

            apporteur = Apporteur.objects.order_by('-id')

            context_perso = {'apporteurs': apporteur, 'types_apporteur': types_apporteur, 'types_personnes': types_personnes, 'pays': pays}

            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        def get_context_data(self, **kwargs):
            pprint(kwargs)
            return {
                **super().get_context_data(**kwargs),
                **admin.site.each_context(self.request),
                "opts": self.model._meta,
            }


@login_required
def add_apporteur(request):

    if request.method == 'POST':

        apporteur_created = Apporteur.objects.create(bureau_id=request.user.bureau_id,
                                       nom=request.POST.get('nom'),
                                       prenoms=request.POST.get('prenoms'),
                                       type_personne_id=request.POST.get('type_personne_id'),
                                       type_apporteur_id=request.POST.get('type_apporteur_id'),
                                       pays_id=request.POST.get('pays_id'),
                                       telephone=request.POST.get('telephone'),
                                       email=request.POST.get('email'),
                                       adresse=request.POST.get('adresse'),
                                       status=request.POST.get('status'),
                                       created_by_id=request.user.id,
                                       created_at=datetime.now(),
                                       )

        #TODO : nomenclature du code apporteur a trouver
        apporteur_created.code = 'AP-' + str(Date.today().year)[-2:] + '-' + str(apporteur_created.pk).zfill(7)
        apporteur_created.save()

        response = {
            'statut': 1,
            'message': "Enregistrement effectuée avec succès !",
            'data': {
                'id': apporteur_created.pk,
                'nom': apporteur_created.nom,
                'prenoms': apporteur_created.prenoms,
                'type_personne': apporteur_created.type_personne.libelle if apporteur_created.type_personne else "",
                'status': apporteur_created.status,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_apporteur(request, apporteur_id):

    apporteur = Apporteur.objects.get(id=apporteur_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Apporteur.objects.filter(id=apporteur_id).update(
                                                    nom=request.POST.get('nom'),
                                                    prenoms=request.POST.get('prenoms'),
                                                    type_personne_id=request.POST.get('type_personne_id'),
                                                    type_apporteur_id=request.POST.get('type_apporteur_id'),
                                                    pays_id=request.POST.get('pays_id'),
                                                    telephone=request.POST.get('telephone'),
                                                    email=request.POST.get('email'),
                                                    adresse=request.POST.get('adresse'),
                                                    status=request.POST.get('status'),
                                                    updated_at=datetime.now(),
                                                   )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': apporteur.pk,
                'nom': apporteur.nom,
                'prenoms': apporteur.prenoms,
                'type_personne': apporteur.type_personne.libelle if apporteur.type_personne else "",
                'status': apporteur.status,
            }
        }

        return JsonResponse(response)

    else:
        types_apporteur = TypeApporteur.objects.all()
        types_personnes = TypePersonne.objects.all()
        pays = Pays.objects.order_by('-nom')

        return render(request, 'apporteurs/modal_modifier_apporteur.html',
                      {'apporteur': apporteur, 'types_apporteur': types_apporteur, 'types_personnes': types_personnes, 'pays': pays})


@login_required
def supprimer_apporteur(request, apporteur_id):
    if request.method == "POST":

        apporteur_id = request.POST.get('apporteur_id')
        print("apporteur id : ", apporteur_id)
        apporteur = Apporteur.objects.get(id=apporteur_id)
        if apporteur.pk is not None:

            apporteur.delete()

            response = {
                'statut': 1,
                'message': "Apporteur supprimé avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Apporteur non trouvé !",
            }

        return JsonResponse(response)

#------------------------FIN APPORTEUR----------------------------------


#------------------------COMPAGNIE----------------------------------

class CompagnieView(PermissionRequiredMixin, TemplateView):
        template_name = 'compagnies/compagnie.html'
        permission_required = "configurations.view_compagnie"
        model = Compagnie

        def get(self, request, *args, **kwargs):
            context_original = self.get_context_data(**kwargs)

            types_garants = TypeGarant.objects.all()

            produits = Produit.objects.all().order_by('-nom')

            compagnies = Compagnie.objects.all().order_by('-id')

            context_perso = {'compagnies': compagnies, 'types_garants': types_garants}

            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        def get_context_data(self, **kwargs):
            pprint(kwargs)
            return {
                **super().get_context_data(**kwargs),
                **admin.site.each_context(self.request),
                "opts": self.model._meta,
            }


# Générer le code pour l'assureur
def generate_assureur_code():
    current_year = str(date.today().year)[-2:]

    # Trouver le dernier code créé dans la base de données
    last_code = Compagnie.objects.aggregate(Max('code'))['code__max']

    # Extraire le numéro incrémental du dernier code
    if last_code:
        last_number = int(last_code.split('-')[0])  # Ex: "0001-CP24" -> 0001
        new_number = last_number + 1
    else:
        new_number = 1  # Si aucun code n'existe encore

    # Formatage du nouveau numéro pour garder 4 chiffres
    new_code = f"{str(new_number).zfill(4)}-CP{current_year}"

    return new_code


@login_required
def add_compagnie(request):
    if request.method == "POST":
        compagnie_created = Compagnie.objects.create(bureau_id=request.user.bureau_id,
                                                        type_garant_id = request.POST.get('type_garant_id'),
                                                        nom = request.POST.get('nom'),
                                                        code_courtier = request.POST.get('code_courtier'),
                                                        telephone = request.POST.get('telephone'),
                                                        fax = request.POST.get('fax'),
                                                        email = request.POST.get('email'),
                                                        adresse = request.POST.get('adresse'),
                                                        status = request.POST.get('statut'),
                                                        code = generate_assureur_code(),
                                                        created_at = datetime.now(),
                                                    )

        compagnie = Compagnie.objects.get(id=compagnie_created.pk)

        taux_commission = TauxCommission.objects.all()

        for taux_com in taux_commission:
            produits = Produit.objects.filter(taux_commission_id=taux_com.id)
            for produit in produits:
                ParamProduitCompagnie.objects.create(
                    compagnie_id=compagnie.id, produit_id=produit.id,
                    taux_com_courtage=taux_com.taux,
                    taux_com_courtage_terme=taux_com.taux,
                ).save()

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': compagnie.pk,
                'nom': compagnie.nom,
                'status': compagnie.status,
            }
        }

        return JsonResponse(response)


@login_required
def taux_compagnie(request, compagnie_id):
    compagnie = Compagnie.objects.get(id=compagnie_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)


        response = {
            'statut': 1,
            'message': "Taux modifié avec succès !",
            'data': {}
        }

        return JsonResponse(response)

    else:
        param_produit_compagnie = ParamProduitCompagnie.objects.filter(compagnie_id=compagnie.id)

        return render(request, 'compagnies/modal_taux_compagnie.html',
                      {'compagnie': compagnie, 'param_produit_compagnie': param_produit_compagnie})


@login_required
def modifier_compagnie(request, compagnie_id):
    compagnie = Compagnie.objects.get(id=compagnie_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Compagnie.objects.filter(id=compagnie_id).update(
            type_garant_id=request.POST.get('type_garant_id'),
            nom=request.POST.get('nom'),
            code_courtier=request.POST.get('code_courtier'),
            telephone=request.POST.get('telephone'),
            fax=request.POST.get('fax'),
            email=request.POST.get('email'),
            adresse=request.POST.get('adresse'),
            status=request.POST.get('statut'),
            updated_at=datetime.now(),
        )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': compagnie.pk,
                'nom': compagnie.nom,
                'status': compagnie.status,
            }
        }

        return JsonResponse(response)

    else:
        types_garants = TypeGarant.objects.all()

        return render(request, 'compagnies/modal_modifier_compagnie.html',
                      {'compagnie': compagnie, 'types_garants': types_garants})


@login_required
def supprimer_compagnie(request, compagnie_id):
    if request.method == "POST":

        compagnie_id = request.POST.get('compagnie_id')
        print("compagnie id : ", compagnie_id)
        compagnie = Compagnie.objects.get(id=compagnie_id)
        if compagnie.pk is not None:

            paramproduitcompagnie = ParamProduitCompagnie.objects.filter(compagnie_id=compagnie.id)
            for param in paramproduitcompagnie:
                param.delete()

            compagnie.delete()

            response = {
                'statut': 1,
                'message': "Compagnie supprimée avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Compagnie non trouvée !",
            }

        return JsonResponse(response)

#------------------------FIN COMPAGNIE----------------------------------


#------------------------CAROSSERIE----------------------------------

class CarosseriesView(PermissionRequiredMixin,TemplateView):
    template_name = 'carosseries/carosserie.html'
    permission_required = "configurations.view_carosserie"
    model = Carosserie

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        carosseries = Carosserie.objects.all().order_by('-id')

        context_perso = {'carosseries': carosseries}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_carosserie(request):

    if request.method == 'POST':

        carosserie_created = Carosserie.objects.create(libelle=request.POST.get('libelle'),
                                       status=request.POST.get('statut'),
                                       created_at=datetime.now(),
                                       )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': carosserie_created.pk,
                'libelle': carosserie_created.libelle,
                'status': carosserie_created.status,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_carosserie(request, carosserie_id):

    carosserie = Carosserie.objects.get(id=carosserie_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Carosserie.objects.filter(id=carosserie_id).update(
                                                    libelle=request.POST.get('libelle'),
                                                    status=request.POST.get('statut'),
                                                   )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': carosserie.pk,
                'nom': carosserie.libelle,
                'status': carosserie.status,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'carosseries/modal_modifier_carosserie.html', {'carosserie': carosserie})


@login_required
def supprimer_carosserie(request, carosserie_id):
    if request.method == "POST":

        carosserie_id = request.POST.get('carosserie_id')
        print("carosserie id : ", carosserie_id)
        carosserie = Carosserie.objects.get(id=carosserie_id)
        if carosserie.pk is not None:

            carosserie.delete()

            response = {
                'statut': 1,
                'message': "Carosserie supprimée avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Carosserie non trouvée !",
            }

        return JsonResponse(response)

#------------------------FIN CAROSSERIE----------------------------------


#---------------------CATEGORIE VEHICULE---------------------------------------------

class CategorieVehiculeView(PermissionRequiredMixin,TemplateView):
    template_name = 'categorievehicules/categorievehicule.html'
    permission_required = "configurations.view_categorievehicule"
    model = CategorieVehicule

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        categorievehicule = CategorieVehicule.objects.all().order_by('-id')

        context_perso = {'categorievehicules': categorievehicule}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_categorievehicule(request):

    if request.method == 'POST':
        # Récupérer le dernier code dans la base de données
        dernier_categorievehicule = CategorieVehicule.objects.order_by('-pk').first()

        # Obtenir le dernier code numérique, ou 0 si aucun code ou format invalide
        dernier_code = int(dernier_categorievehicule.code.split('-')[-1]) if dernier_categorievehicule and dernier_categorievehicule.code.startswith('CAT-') else 0

        # Ajouter 1 au dernier code et formater avec des zéros
        nouveau_code = f"CAT-{dernier_code + 1:04d}"

        # Créer une nouvelle catégorie véhicule
        categorievehicule_created = CategorieVehicule.objects.create(
            libelle=request.POST.get('libelle'),
            status=request.POST.get('statut'),
            created_at=datetime.now(),
            code=str(nouveau_code).zfill(2)  # Remplir avec des zéros si nécessaire
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': categorievehicule_created.pk,
                'libelle': categorievehicule_created.libelle,
                'status': categorievehicule_created.status,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_categorievehicule(request, categorievehicule_id):

    categorievehicule = CategorieVehicule.objects.get(id=categorievehicule_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        CategorieVehicule.objects.filter(id=categorievehicule_id).update(libelle=request.POST.get('libelle'),
                                                    status=request.POST.get('statut'),
                                                    updated_at=datetime.now(),
                                                   )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': categorievehicule.pk,
                'libelle': categorievehicule.libelle,
                'status': categorievehicule.status,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'categorievehicules/modal_modifier_categorievehicule.html', {'categorievehicule': categorievehicule})


@login_required
def supprimer_categorievehicule(request, categorievehicule_id):
    if request.method == "POST":

        categorievehicule_id = request.POST.get('categorievehicule_id')
        print("categorievehicule id : ", categorievehicule_id)
        categorievehicule = CategorieVehicule.objects.get(id=categorievehicule_id)
        if categorievehicule.pk is not None:

            categorievehicule.delete()

            response = {
                'statut': 1,
                'message': "Catégorie véhicule supprimée avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Catégorie véhicule non trouvée !",
            }

        return JsonResponse(response)

#---------------------FIN CATEGORIE VEHICULE---------------------------------------------


#------------------------CIRCONSTANCE----------------------------------

class CirconstanceView(PermissionRequiredMixin,TemplateView):
    template_name = 'circonstances/circonstance.html'
    permission_required = "configurations.view_circonstance"
    model = Circonstance

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        circonstances = Circonstance.objects.all().order_by('-id')
        branches = Branche.objects.filter(status=1).order_by('nom')

        context_perso = {'circonstances': circonstances, 'branches': branches}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


# Générer le code pour la circonstance
def generate_circonstance_code():

    # Trouver le dernier code créé dans la base de données
    last_code = Circonstance.objects.aggregate(Max('code'))['code__max']
    
    # Extraire le numéro incrémental du dernier code
    if last_code:
        last_number = int(last_code[3:])  # Ex: "CIR001" -> 001
        new_number = last_number + 1
    else:
        new_number = 1  # Si aucun code n'existe encore

    # Formatage du nouveau numéro pour garder 3 chiffres
    new_code = f"CIR{str(new_number).zfill(3)}"

    return new_code


@login_required
def add_circonstance(request):

    if request.method == 'POST':

        # Créer une nouveau circonstance
        circonstance_created = Circonstance.objects.create(
            branche_id=request.POST.get('branche_id'),
            libelle=request.POST.get('libelle'),
            code=generate_circonstance_code(),
            statut=request.POST.get('statut'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': circonstance_created.pk,
                'libelle': circonstance_created.libelle,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_circonstance(request, circonstance_id):

    circonstance = Circonstance.objects.get(id=circonstance_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Circonstance.objects.filter(id=circonstance_id).update(
            branche_id=request.POST.get('branche_id'),
            libelle=request.POST.get('libelle'),
            statut=request.POST.get('statut'),
            updated_at=datetime.now(),
        )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': circonstance.pk,
                'libelle': circonstance.libelle,
            }
        }

        return JsonResponse(response)

    else:
        branches = Branche.objects.filter(status=1).order_by('nom')
        return render(request, 'circonstances/modal_modifier_circonstance.html', {'circonstance': circonstance, 'branches': branches})


@login_required
def supprimer_circonstance(request, circonstance_id):
    if request.method == "POST":

        circonstance_id = request.POST.get('circonstance_id')
        print("circonstance id : ", circonstance_id)
        circonstance = Circonstance.objects.get(id=circonstance_id)
        if circonstance.pk is not None:

            circonstance.delete()

            response = {
                'statut': 1,
                'message': "Circonstance supprimée avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Circonstance non trouvée !",
            }

            return JsonResponse(response)

#------------------------FIN CIRCONSTANCE----------------------------------


#------------------------CIVILITE----------------------------------

class CiviliteView(PermissionRequiredMixin,TemplateView):
    template_name = 'civilites/civilite.html'
    permission_required = "configurations.view_civilite"
    model = Civilite

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        civilites = Civilite.objects.all().order_by('-id')

        context_perso = {'civilites': civilites}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_civilite(request):

    if request.method == 'POST':

        civilite_created = Civilite.objects.create(name=request.POST.get('name'),
                                       status=request.POST.get('statut'),
                                       created_at=datetime.now(),
                                       )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': civilite_created.pk,
                'name': civilite_created.name,
                'status': civilite_created.status,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_civilite(request, civilite_id):

    civilite = Civilite.objects.get(id=civilite_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Civilite.objects.filter(id=civilite_id).update(
                                                    name=request.POST.get('name'),
                                                    status=request.POST.get('statut'),
                                                   )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': civilite.pk,
                'name': civilite.name,
                'status': civilite.status,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'civilites/modal_modifier_civilite.html', {'civilite': civilite})


@login_required
def supprimer_civilite(request, civilite_id):
    if request.method == "POST":

        civilite_id = request.POST.get('civilite_id')
        print("civilite id : ", civilite_id)
        civilite = Civilite.objects.get(id=civilite_id)
        if civilite.pk is not None:

            civilite.delete()

            response = {
                'statut': 1,
                'message': "Civilité supprimée avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Civilite non trouvée !",
            }

        return JsonResponse(response)

#------------------------FIN CIVILITE----------------------------------


#------------------------COMPTE TRESORERIE----------------------------------

class CompteTresorerieView(PermissionRequiredMixin,TemplateView):
    template_name = 'comptetresoreries/comptetresorerie.html'
    permission_required = "configurations.view_comptetresorerie"
    model = CompteTresorerie

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        comptetresoreries = CompteTresorerie.objects.all().order_by('-id')

        context_perso = {'comptetresoreries': comptetresoreries}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_comptetresorerie(request):

    if request.method == 'POST':

        # Créer un nouveau compte de trésorerie
        comptetresorerie_created = CompteTresorerie.objects.create(
            code=request.POST.get('code'),
            libelle=request.POST.get('libelle'),
            status=request.POST.get('statut'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': comptetresorerie_created.pk,
                'libelle': comptetresorerie_created.libelle,
                'status': comptetresorerie_created.status,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_comptetresorerie(request, comptetresorerie_id):

    comptetresorerie = CompteTresorerie.objects.get(id=comptetresorerie_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        CompteTresorerie.objects.filter(id=comptetresorerie_id).update(
                                                    code=request.POST.get('code'),
                                                    libelle=request.POST.get('libelle'),
                                                    status=request.POST.get('statut'),
                                                   )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': comptetresorerie.pk,
                'libelle': comptetresorerie.libelle,
                'status': comptetresorerie.status,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'comptetresoreries/modal_modifier_comptetresorerie.html', {'comptetresorerie': comptetresorerie})


@login_required
def supprimer_comptetresorerie(request, comptetresorerie_id):
    if request.method == "POST":

        comptetresorerie_id = request.POST.get('comptetresorerie_id')
        print("comptetresorerie id : ", comptetresorerie_id)
        comptetresorerie = CompteTresorerie.objects.get(id=comptetresorerie_id)
        if comptetresorerie.pk is not None:

            comptetresorerie.delete()

            response = {
                'statut': 1,
                'message': "Compte trésorerie supprimé avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Compte trésorerie non trouvé !",
            }

        return JsonResponse(response)

#------------------------FIN COMPTE TRESORERIE----------------------------------


#------------------------CONDITION D'ASSURANCE----------------------------------

class ConditionsAssuranceView(PermissionRequiredMixin,TemplateView):
    template_name = 'conditionsassurances/conditionsassurance.html'
    permission_required = "configurations.view_conditionsassurance"
    model = ConditionsAssurance

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        conditionsassurances = ConditionsAssurance.objects.all().order_by('-id')

        context_perso = {'conditionsassurances': conditionsassurances}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_conditionsassurance(request):

    if request.method == 'POST':
        # Récupérer le dernier code dans la base de données
        dernier_conditionsassurance = ConditionsAssurance.objects.order_by('-pk').first()

        # Obtenir le dernier code numérique, ou 0 si aucun code ou format invalide
        dernier_code = int(dernier_conditionsassurance.code.split('-')[-1]) if dernier_conditionsassurance and dernier_conditionsassurance.code.startswith('CA-') else 0

        # Ajouter 1 au dernier code et formater avec des zéros
        nouveau_code = f"CA-{dernier_code + 1:03d}"

        # Créer une nouvelle condition d'assurance
        conditionsassurance_created = ConditionsAssurance.objects.create(
            libelle=request.POST.get('libelle'),
            status=request.POST.get('statut'),
            created_at=datetime.now(),
            code=str(nouveau_code).zfill(2)  # Remplir avec des zéros si nécessaire
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': conditionsassurance_created.pk,
                'libelle': conditionsassurance_created.libelle,
                'status': conditionsassurance_created.status,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_conditionsassurance(request, conditionsassurance_id):

    conditionsassurance = ConditionsAssurance.objects.get(id=conditionsassurance_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        ConditionsAssurance.objects.filter(id=conditionsassurance_id).update(
                                                    libelle=request.POST.get('libelle'),
                                                    status=request.POST.get('statut'),
                                                   )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': conditionsassurance.pk,
                'libelle': conditionsassurance.libelle,
                'status': conditionsassurance.status,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'conditionsassurances/modal_modifier_conditionsassurance.html', {'conditionsassurance': conditionsassurance})


@login_required
def supprimer_conditionsassurance(request, conditionsassurance_id):
    if request.method == "POST":

        conditionsassurance_id = request.POST.get('conditionsassurance_id')
        print("conditionsassurance id : ", conditionsassurance_id)
        conditionsassurance = ConditionsAssurance.objects.get(id=conditionsassurance_id)
        if conditionsassurance.pk is not None:

            conditionsassurance.delete()

            response = {
                'statut': 1,
                'message': "Condition d'assurance supprimé avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Condition d'assurance non trouvé !",
            }

        return JsonResponse(response)

#------------------------FIN CONDITION D'ASSURANCE----------------------------------


#------------------------DEVISE----------------------------------

class DeviseView(PermissionRequiredMixin,TemplateView):
    template_name = 'devises/devise.html'
    permission_required = "configurations.view_devise"
    model = Devise

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        devises = Devise.objects.all().order_by('-id')

        context_perso = {'devises': devises}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_devise(request):

    if request.method == 'POST':

        # Créer une nouvelle dévise
        devise_created = Devise.objects.create(
            libelle=request.POST.get('libelle'),
            code=request.POST.get('code'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': devise_created.pk,
                'libelle': devise_created.libelle,
                'code': devise_created.code,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_devise(request, devise_id):

    devise = Devise.objects.get(id=devise_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Devise.objects.filter(id=devise_id).update(
                                                    libelle=request.POST.get('libelle'),
                                                    code=request.POST.get('code'),
                                                   )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': devise.pk,
                'libelle': devise.libelle,
                'code': devise.code,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'devises/modal_modifier_devise.html', {'devise': devise})


@login_required
def supprimer_devise(request, devise_id):
    if request.method == "POST":

        devise_id = request.POST.get('devise_id')
        print("devise id : ", devise_id)
        devise = Devise.objects.get(id=devise_id)
        if devise.pk is not None:

            devise.delete()

            response = {
                'statut': 1,
                'message': "Dévise supprimée avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Dévise non trouvée !",
            }

        return JsonResponse(response)

#------------------------FIN DEVISE----------------------------------


#------------------------CARBURANT----------------------------------

class CarburantView(PermissionRequiredMixin,TemplateView):
    template_name = 'carburants/carburant.html'
    permission_required = "configurations.view_carburant"
    model = Carburant

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        carburants = Carburant.objects.all().order_by('-id')

        context_perso = {'carburants': carburants}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_carburant(request):

    if request.method == 'POST':

        # Créer une nouveau carburant
        carburant_created = Carburant.objects.create(
            libelle=request.POST.get('libelle'),
            code=request.POST.get('code'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': carburant_created.pk,
                'libelle': carburant_created.libelle,
                'code': carburant_created.code,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_carburant(request, carburant_id):

    carburant = Carburant.objects.get(id=carburant_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Carburant.objects.filter(id=carburant_id).update(
                                                    libelle=request.POST.get('libelle'),
                                                    code=request.POST.get('code'),
                                                   )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': carburant.pk,
                'libelle': carburant.libelle,
                'code': carburant.code,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'carburants/modal_modifier_carburant.html', {'carburant': carburant})


@login_required
def supprimer_carburant(request, carburant_id):
    if request.method == "POST":

        carburant_id = request.POST.get('carburant_id')
        print("carburant id : ", carburant_id)
        carburant = Carburant.objects.get(id=carburant_id)
        if carburant.pk is not None:

            carburant.delete()

            response = {
                'statut': 1,
                'message': "Energie supprimée avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Energie non trouvée !",
            }

        return JsonResponse(response)

#------------------------FIN CARBURANT----------------------------------


#------------------------FORMULE----------------------------------

class FormuleView(PermissionRequiredMixin,TemplateView):
    template_name = 'formules/formule.html'
    permission_required = "configurations.view_formule"
    model = Formule

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        formules = Formule.objects.all().order_by('-id')

        context_perso = {'formules': formules}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_formule(request):

    if request.method == 'POST':

        # Créer une nouvelle formule
        formule_created = Formule.objects.create(
            code=request.POST.get('code'),
            libelle=request.POST.get('libelle'),
            status=request.POST.get('statut'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': formule_created.pk,
                'libelle': formule_created.libelle,
                'status': formule_created.status,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_formule(request, formule_id):

    formule = Formule.objects.get(id=formule_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Formule.objects.filter(id=formule_id).update(
                                                    code=request.POST.get('code'),
                                                    libelle=request.POST.get('libelle'),
                                                    status=request.POST.get('status'),
                                                   )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': formule.pk,
                'libelle': formule.libelle,
                'status': formule.status,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'formules/modal_modifier_formule.html', {'formule': formule})


@login_required
def supprimer_formule(request, formule_id):
    if request.method == "POST":

        formule_id = request.POST.get('formule_id')
        print("formule id : ", formule_id)
        formule = Formule.objects.get(id=formule_id)
        if formule.pk is not None:

            formule.delete()

            response = {
                'statut': 1,
                'message': "Formule supprimée avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Formule non trouvée !",
            }

        return JsonResponse(response)

#------------------------FIN FORMULE----------------------------------


#------------------------FRACTIONNEMENT----------------------------------

class FractionnementView(PermissionRequiredMixin,TemplateView):
    template_name = 'fractionnements/fractionnement.html'
    permission_required = "configurations.view_fractionnement"
    model = Fractionnement

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        fractionnements = Fractionnement.objects.all().order_by('-id')

        context_perso = {'fractionnements': fractionnements}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_fractionnement(request):

    if request.method == 'POST':

        # Créer une nouveau fractionnement
        fractionnement_created = Fractionnement.objects.create(
            libelle=request.POST.get('libelle'),
            duree_en_mois=request.POST.get('duree_en_mois'),
            status=request.POST.get('status'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': fractionnement_created.pk,
                'libelle': fractionnement_created.libelle,
                'duree_en_mois': fractionnement_created.duree_en_mois,
                'status': fractionnement_created.status,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_fractionnement(request, fractionnement_id):

    fractionnement = Fractionnement.objects.get(id=fractionnement_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Fractionnement.objects.filter(id=fractionnement_id).update(
                                                    libelle=request.POST.get('libelle'),
                                                    duree_en_mois=request.POST.get('duree_en_mois'),
                                                    status=request.POST.get('status'),
                                                   )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': fractionnement.pk,
                'libelle': fractionnement.libelle,
                'duree_en_mois': fractionnement.duree_en_mois,
                'status': fractionnement.status,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'fractionnements/modal_modifier_fractionnement.html', {'fractionnement': fractionnement})


@login_required
def supprimer_fractionnement(request, fractionnement_id):
    if request.method == "POST":

        fractionnement_id = request.POST.get('fractionnement_id')
        print("fractionnement id : ", fractionnement_id)
        fractionnement = Fractionnement.objects.get(id=fractionnement_id)
        if fractionnement.pk is not None:

            fractionnement.delete()

            response = {
                'statut': 1,
                'message': "fractionnement supprimée avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "fractionnement non trouvée !",
            }

        return JsonResponse(response)

#------------------------FIN FRACTIONNEMENT----------------------------------


#------------------------GARANTIE----------------------------------

class GarantieView(PermissionRequiredMixin,TemplateView):
    template_name = 'garanties/garantie.html'
    permission_required = "configurations.view_garantie"
    model = Garantie

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        garanties = Garantie.objects.all().order_by('-id')

        context_perso = {'garanties': garanties}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_garantie(request):

    if request.method == 'POST':

        # Créer une nouvelle garantie
        garantie_created = Garantie.objects.create(
            code=request.POST.get('code'),
            nom=request.POST.get('nom'),
            status=request.POST.get('statut'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': garantie_created.pk,
                'nom': garantie_created.nom,
                'status': garantie_created.status,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_garantie(request, garantie_id):

    garantie = Garantie.objects.get(id=garantie_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Garantie.objects.filter(id=garantie_id).update(
            code=request.POST.get('code'),
            nom=request.POST.get('nom'),
            status=request.POST.get('status'),
        )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': garantie.pk,
                'nom': garantie.nom,
                'status': garantie.status,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'garanties/modal_modifier_garantie.html', {'garantie': garantie})


@login_required
def supprimer_garantie(request, garantie_id):
    if request.method == "POST":

        garantie_id = request.POST.get('garantie_id')
        print("garantie id : ", garantie_id)
        garantie = Garantie.objects.get(id=garantie_id)
        if garantie.pk is not None:

            garantie.delete()

            response = {
                'statut': 1,
                'message': "garantie supprimée avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "garantie non trouvée !",
            }

        return JsonResponse(response)

#------------------------FIN GARANTIE----------------------------------


#------------------------GARANTIE / FORMULE----------------------------------

class GarantieFormuleView(PermissionRequiredMixin,TemplateView):
    template_name = 'garantieformules/garantieformule.html'
    permission_required = "configurations.view_garantieformule"
    model = GarantieFormule

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        garantieformules = GarantieFormule.objects.all().order_by('-id')

        garanties = Garantie.objects.filter(status=1).order_by('nom')
        formules = Formule.objects.filter(status=1).order_by('libelle')

        context_perso = {
            'garantieformules': garantieformules,
            'garanties': garanties,
            'formules': formules,
        }

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_garantieformule(request):

    if request.method == 'POST':
        garantieformules = request.POST.getlist('garantieformules')

        if len(garantieformules) > 0:
            for garantieformule in garantieformules:
                # Créer une nouvelle garantie formule
                garantie_formule = GarantieFormule(
                    garantie_id=garantieformule,
                    formule_id=request.POST.get('formule_id'),
                    status=request.POST.get('status'),
                    created_at=datetime.now(),

                )
                garantie_formule.save()

            response = {
                'statut': 1,
                'message': "Enregistrement effectué avec succès !",
                'data': {}
            }

            return JsonResponse(response)

        response = {
            'statut': 0,
            'message': "Veuillez sélectionner des garanties !",
            'data': {}
        }

        return JsonResponse(response)


@login_required
def modifier_garantieformule(request, garantieformule_id):

    garantieformule = GarantieFormule.objects.get(id=garantieformule_id)
    garanties = Garantie.objects.filter(status=1).order_by('nom')
    formulegaranties = GarantieFormule.objects.filter(formule_id=garantieformule.formule_id)
    formules = Formule.objects.filter(status=1).order_by('libelle')

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        #Suppression l'existant
        for formulegarantie in formulegaranties:
            formulegarantie.delete()

        garantieformules = request.POST.getlist('garantieformules')

        if len(garantieformules) > 0:
            for garantieformule in garantieformules:
                # Créer une nouvelle garantie formule
                garantie_formule = GarantieFormule(
                    garantie_id=garantieformule,
                    formule_id=request.POST.get('formule_id'),
                    status=request.POST.get('status'),
                    updated_at=datetime.now(),

                )
                garantie_formule.save()

            response = {
                'statut': 1,
                'message': "Modification effectuée avec succès !",
                'data': {}
            }

            return JsonResponse(response)

        response = {
            'statut': 0,
            'message': "Veuillez sélectionner des garanties !",
            'data': {}
        }

        return JsonResponse(response)

    else:
        print('garantieformule ', garantieformule)
        print('garanties ', garanties)
        print('formulegaranties ', formulegaranties)
        print('formules ', formules)

        context = {
            'garantieformule':garantieformule,
            'garanties':garanties,
            'formulegaranties':formulegaranties,
            'formules':formules,
        }

        return render(request, 'garantieformules/modal_modifier_garantieformule.html',context)


@login_required
def supprimer_garantieformule(request, garantieformule_id):
    if request.method == "POST":

        garantieformule_id = request.POST.get('garantieformule_id')
        print("garantieformule id : ", garantieformule_id)
        garantieformule = GarantieFormule.objects.get(id=garantieformule_id)
        if garantieformule.pk is not None:

            garantieformule.delete()

            response = {
                'statut': 1,
                'message': "Garantie formule supprimée avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Garantie formule non trouvée !",
            }

        return JsonResponse(response)

#------------------------FIN GARANTIE / FORMULE----------------------------------


#------------------------GARANTIE / CIRCONSTANCE----------------------------------

class GarantieCirconstanceView(PermissionRequiredMixin,TemplateView):
    template_name = 'garantiecirconstances/garantiecirconstance.html'
    permission_required = "configurations.view_garantiecirconstance"
    model = GarantieCirconstance

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        garantiecirconstances = GarantieCirconstance.objects.all().order_by('-id')

        garanties = Garantie.objects.filter(status=1).order_by('nom')
        circonstances = Circonstance.objects.filter(statut=1).order_by('libelle')

        context_perso = {
            'garantiecirconstances': garantiecirconstances,
            'garanties': garanties,
            'circonstances': circonstances,
        }

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_garantiecirconstance(request):

    if request.method == 'POST':
        garantiecirconstances = request.POST.getlist('garantiecirconstances')

        if len(garantiecirconstances) > 0:
            for garantiecirconstance in garantiecirconstances:
                # Créer une nouvelle Garantie circonstance
                garantie_circonstance = GarantieCirconstance(
                    garantie_id=garantiecirconstance,
                    circonstance_id=request.POST.get('circonstance_id'),
                    status=request.POST.get('status'),
                    created_at=datetime.now(),

                )
                garantie_circonstance.save()

            response = {
                'statut': 1,
                'message': "Enregistrement effectué avec succès !",
                'data': {}
            }

            return JsonResponse(response)

        response = {
            'statut': 0,
            'message': "Veuillez sélectionner des garanties !",
            'data': {}
        }

        return JsonResponse(response)


@login_required
def modifier_garantiecirconstance(request, garantiecirconstance_id):

    garantiecirconstance = GarantieCirconstance.objects.get(id=garantiecirconstance_id)
    garanties = Garantie.objects.filter(status=1).order_by('nom')
    circonstancegaranties = GarantieCirconstance.objects.filter(circonstance_id=garantiecirconstance.circonstance_id)
    circonstances = Circonstance.objects.filter(statut=1).order_by('libelle')

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        #Suppression l'existant
        for circonstancegarantie in circonstancegaranties:
            circonstancegarantie.delete()

        garantiecirconstances = request.POST.getlist('garantiecirconstances')

        if len(garantiecirconstances) > 0:
            for garantiecirconstance in garantiecirconstances:
                # Créer une nouvelle Garantie circonstance
                garantie_circonstance = GarantieCirconstance(
                    garantie_id=garantiecirconstance,
                    circonstance_id=request.POST.get('circonstance_id'),
                    status=request.POST.get('status'),
                    updated_at=datetime.now(),

                )
                garantie_circonstance.save()

            response = {
                'statut': 1,
                'message': "Modification effectuée avec succès !",
                'data': {}
            }

            return JsonResponse(response)

        response = {
            'statut': 0,
            'message': "Veuillez sélectionner des garanties !",
            'data': {}
        }

        return JsonResponse(response)

    else:
        print('garantiecirconstance ', garantiecirconstance)
        print('garanties ', garanties)
        print('circonstancegaranties ', circonstancegaranties)
        print('circonstances ', circonstances)

        context = {
            'garantiecirconstance':garantiecirconstance,
            'garanties':garanties,
            'circonstancegaranties':circonstancegaranties,
            'circonstances':circonstances,
        }

        return render(request, 'garantiecirconstances/modal_modifier_garantiecirconstance.html',context)


@login_required
def supprimer_garantiecirconstance(request, garantiecirconstance_id):
    if request.method == "POST":

        garantiecirconstance_id = request.POST.get('garantiecirconstance_id')
        print("garantiecirconstance id : ", garantiecirconstance_id)
        garantiecirconstance = GarantieCirconstance.objects.get(id=garantiecirconstance_id)
        if garantiecirconstance.pk is not None:

            garantiecirconstance.delete()

            response = {
                'statut': 1,
                'message': "Garantie circonstance supprimée avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Garantie circonstance non trouvée !",
            }

        return JsonResponse(response)

#------------------------FIN GARANTIE / CIRCONSTANCE----------------------------------


#------------------------GROUPE----------------------------------

class GroupeView(PermissionRequiredMixin,TemplateView):
    template_name = 'groupes/groupe.html'
    permission_required = "configurations.view_groupe"
    model = Groupe

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        groupes = Groupe.objects.all().order_by('-id')

        context_perso = {'groupes': groupes}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_groupe(request):

    if request.method == 'POST':

        # Créer une nouveau groupe
        groupe_created = Groupe.objects.create(
            libelle=request.POST.get('libelle'),
            statut=request.POST.get('status'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': groupe_created.pk,
                'libelle': groupe_created.libelle,
                'status': groupe_created.statut,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_groupe(request, groupe_id):

    groupe = Groupe.objects.get(id=groupe_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Groupe.objects.filter(id=groupe_id).update(
            libelle=request.POST.get('libelle'),
            statut=request.POST.get('status'),
        )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': groupe.pk,
                'libelle': groupe.libelle,
                'statut': groupe.statut,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'groupes/modal_modifier_groupe.html', {'groupe': groupe})


@login_required
def supprimer_groupe(request, groupe_id):
    if request.method == "POST":

        groupe_id = request.POST.get('groupe_id')
        print("groupe id : ", groupe_id)
        groupe = Groupe.objects.get(id=groupe_id)
        if groupe.pk is not None:

            groupe.delete()

            response = {
                'statut': 1,
                'message': "Groupe supprimé avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Groupe non trouvé !",
            }

        return JsonResponse(response)

#------------------------FIN GROUPE----------------------------------


#------------------------MODE REGLEMENT----------------------------------

class ModeReglementView(PermissionRequiredMixin,TemplateView):
    template_name = 'modereglements/modereglement.html'
    permission_required = "configurations.view_modereglement"
    model = ModeReglement

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        modereglements = ModeReglement.objects.all().order_by('-id')

        context_perso = {'modereglements': modereglements}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_modereglement(request):

    if request.method == 'POST':

        # Créer une nouveau modereglement
        modereglement_created = ModeReglement.objects.create(
            libelle=request.POST.get('libelle'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': modereglement_created.pk,
                'libelle': modereglement_created.libelle,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_modereglement(request, modereglement_id):

    modereglement = ModeReglement.objects.get(id=modereglement_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        ModeReglement.objects.filter(id=modereglement_id).update(
            libelle=request.POST.get('libelle'),
        )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': modereglement.pk,
                'libelle': modereglement.libelle,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'modereglements/modal_modifier_modereglement.html', {'modereglement': modereglement})


@login_required
def supprimer_modereglement(request, modereglement_id):
    if request.method == "POST":

        modereglement_id = request.POST.get('modereglement_id')
        print("modereglement id : ", modereglement_id)
        modereglement = ModeReglement.objects.get(id=modereglement_id)
        if modereglement.pk is not None:

            modereglement.delete()

            response = {
                'statut': 1,
                'message': "Mode de règlement supprimé avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Mode de règlement non trouvé !",
            }

            return JsonResponse(response)

#------------------------FIN MODE REGLEMENT----------------------------------


#------------------------PAYS----------------------------------

class PaysView(PermissionRequiredMixin,TemplateView):
    template_name = 'pays/pays.html'
    permission_required = "configurations.view_pays"
    model = Pays

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        pays = Pays.objects.all().order_by('-id')

        devises = Devise.objects.all().order_by('libelle')

        context_perso = {'pays': pays, 'devises':devises}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_pays(request):

    if request.method == 'POST':

        # Créer une nouveau pays
        pays_created = Pays.objects.create(
            code=request.POST.get('code'),
            nom=request.POST.get('nom'),
            indicatif=request.POST.get('indicatif'),
            poligamie=request.POST.get('poligamie'),
            devise_id=request.POST.get('devise_id'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': pays_created.pk,
                'libelle': pays_created.nom,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_pays(request, pays_id):

    pays = Pays.objects.get(id=pays_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Pays.objects.filter(id=pays_id).update(
            code=request.POST.get('code'),
            nom=request.POST.get('nom'),
            indicatif=request.POST.get('indicatif'),
            poligamie=request.POST.get('poligamie'),
            devise_id=request.POST.get('devise_id'),
        )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': pays.pk,
                'libelle': pays.nom,
            }
        }

        return JsonResponse(response)

    else:
        devises = Devise.objects.all().order_by('libelle')
        return render(request, 'pays/modal_modifier_pays.html', {'pays': pays, 'devises': devises})


@login_required
def supprimer_pays(request, pays_id):
    if request.method == "POST":

        pays_id = request.POST.get('pays_id')
        print("pays id : ", pays_id)
        pays = Pays.objects.get(id=pays_id)
        if pays.pk is not None:

            pays.delete()

            response = {
                'statut': 1,
                'message': "Pays supprimé avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Pays non trouvé !",
            }

            return JsonResponse(response)

#------------------------FIN PAYS----------------------------------


#------------------------RESPONSABILITE----------------------------------

class ResponsabiliteView(PermissionRequiredMixin,TemplateView):
    template_name = 'responsabilites/responsabilite.html'
    permission_required = "configurations.view_responsabilite"
    model = Responsabilite

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        responsabilites = Responsabilite.objects.all().order_by('-id')

        context_perso = {'responsabilites': responsabilites}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_responsabilite(request):

    if request.method == 'POST':

        # Créer une nouveau responsabilité
        responsabilite_created = Responsabilite.objects.create(
            libelle=request.POST.get('libelle'),
            taux_responsabilite=request.POST.get('taux_responsabilite'),
            statut=request.POST.get('statut'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': responsabilite_created.pk,
                'libelle': responsabilite_created.libelle,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_responsabilite(request, responsabilite_id):

    responsabilite = Responsabilite.objects.get(id=responsabilite_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Responsabilite.objects.filter(id=responsabilite_id).update(
            libelle=request.POST.get('libelle'),
            taux_responsabilite=request.POST.get('taux_responsabilite'),
            statut=request.POST.get('statut'),
            updated_at=datetime.now(),
        )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': responsabilite.pk,
                'libelle': responsabilite.libelle,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'responsabilites/modal_modifier_responsabilite.html', {'responsabilite': responsabilite})


@login_required
def supprimer_responsabilite(request, responsabilite_id):
    if request.method == "POST":

        responsabilite_id = request.POST.get('responsabilite_id')
        print("responsabilite id : ", responsabilite_id)
        responsabilite = Responsabilite.objects.get(id=responsabilite_id)
        if responsabilite.pk is not None:

            responsabilite.delete()

            response = {
                'statut': 1,
                'message': "Responsabilité supprimée avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Responsabilité non trouvée !",
            }

            return JsonResponse(response)

#------------------------FIN RESPONSABILITE----------------------------------


#------------------------SECTEUR D'ACTIVITE----------------------------------

class SecteurActiviteView(PermissionRequiredMixin,TemplateView):
    template_name = 'secteuractivites/secteuractivite.html'
    permission_required = "configurations.view_secteuractivite"
    model = SecteurActivite

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        secteuractivites = SecteurActivite.objects.all().order_by('-id')

        context_perso = {'secteuractivites': secteuractivites}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_secteur_activite(request):

    if request.method == 'POST':

        # Créer une nouveau secteur d'activité
        secteur_activite_created = SecteurActivite.objects.create(
            libelle=request.POST.get('libelle'),
            status=request.POST.get('status'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': secteur_activite_created.pk,
                'libelle': secteur_activite_created.libelle,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_secteur_activite(request, secteur_activite_id):

    secteuractivite = SecteurActivite.objects.get(id=secteur_activite_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        SecteurActivite.objects.filter(id=secteur_activite_id).update(
            libelle=request.POST.get('libelle'),
            status=request.POST.get('status'),
        )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': secteuractivite.pk,
                'libelle': secteuractivite.libelle,
                'statut': secteuractivite.status,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'secteuractivites/modal_modifier_secteuractivite.html', {'secteuractivite': secteuractivite})


@login_required
def supprimer_secteur_activite(request, secteur_activite_id):
    if request.method == "POST":

        secteur_activite_id = request.POST.get('secteuractivite_id')
        print("secteur activite id : ", secteur_activite_id)
        secteuractivite = SecteurActivite.objects.get(id=secteur_activite_id)
        if secteuractivite.pk is not None:

            secteuractivite.delete()

            response = {
                'statut': 1,
                'message': "Secteur d'activité supprimé avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Secteur d'activité non trouvé !",
            }

            return JsonResponse(response)

#------------------------FIN SECTEUR D'ACTIVITE----------------------------------


#------------------------TYPE DE DOCUMENT----------------------------------

class TypeDocumentView(PermissionRequiredMixin,TemplateView):
    template_name = 'typesdocuments/type_document.html'
    permission_required = "configurations.view_types_documents"
    model = TypeDocument

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        typedocuments = TypeDocument.objects.all().order_by('-id')

        context_perso = {'typedocuments': typedocuments}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_types_documents(request):

    if request.method == 'POST':

        # Créer une nouveau type de document
        typedocument_created = TypeDocument.objects.create(
            libelle=request.POST.get('libelle'),
            is_sinistre=request.POST.get('is_sinistre'),
            is_production=request.POST.get('is_production'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': typedocument_created.pk,
                'libelle': typedocument_created.libelle,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_types_documents(request, type_document_id):

    typedocument = TypeDocument.objects.get(id=type_document_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        TypeDocument.objects.filter(id=type_document_id).update(
            libelle=request.POST.get('libelle'),
            is_sinistre=request.POST.get('is_sinistre'),
            is_production=request.POST.get('is_production'),
        )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': typedocument.pk,
                'libelle': typedocument.libelle,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'typesdocuments/modal_modifier_type_document.html', {'typedocument': typedocument})


@login_required
def supprimer_types_documents(request, type_document_id):
    if request.method == "POST":

        type_document_id = request.POST.get('type_document_id')
        print("type de documemnt id : ", type_document_id)
        typedocument = TypeDocument.objects.get(id=type_document_id)
        if typedocument.pk is not None:

            typedocument.delete()

            response = {
                'statut': 1,
                'message': "Type de document supprimé avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Type de document non trouvé !",
            }

            return JsonResponse(response)

#------------------------FIN TYPE DE DOCUMENT----------------------------------

#------------------------TYPE D'INTERVENANT----------------------------------

class TypeIntervenantView(PermissionRequiredMixin,TemplateView):
    template_name = 'typeintervenants/typeintervenant.html'
    permission_required = "configurations.view_type_intervenant"
    model = TypeIntervenant

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        typeintervenants = TypeIntervenant.objects.all().order_by('-id')

        context_perso = {'typeintervenants': typeintervenants}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_typeintervenant(request):

    if request.method == 'POST':

        # Créer une nouveau type d'intervenant
        typeintervenant_created = TypeIntervenant.objects.create(
            libelle=request.POST.get('libelle'),
            statut=request.POST.get('statut'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': typeintervenant_created.pk,
                'libelle': typeintervenant_created.libelle,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_typeintervenant(request, type_intervenant_id):

    typeintervenant = TypeIntervenant.objects.get(id=type_intervenant_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        TypeIntervenant.objects.filter(id=type_intervenant_id).update(
            libelle=request.POST.get('libelle'),
            statut=request.POST.get('statut'),
            updated_at=datetime.now(),
        )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': typeintervenant.pk,
                'libelle': typeintervenant.libelle,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'typeintervenants/modal_modifier_typeintervenant.html', {'typeintervenant': typeintervenant})


@login_required
def supprimer_typeintervenant(request, type_intervenant_id):
    if request.method == "POST":

        type_intervenant_id = request.POST.get('type_intervenant_id')
        print("type d'intervenant id : ", type_intervenant_id)
        typeintervenant = TypeIntervenant.objects.get(id=type_intervenant_id)
        if typeintervenant.pk is not None:

            typeintervenant.delete()

            response = {
                'statut': 1,
                'message': "Type d'intervenant supprimé avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Type d'intervenant non trouvé !",
            }

            return JsonResponse(response)

#------------------------FIN TYPE D'INTERVENANT----------------------------------


#------------------------TYPE DE MOUVEMENT----------------------------------

class TypeMouvementView(PermissionRequiredMixin,TemplateView):
    template_name = 'typemouvements/typemouvement.html'
    permission_required = "configurations.view_type_mouvement"
    model = TypeMouvement

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        typemouvements = TypeMouvement.objects.all().order_by('-id')

        context_perso = {'typemouvements': typemouvements}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_typemouvement(request):

    if request.method == 'POST':

        # Créer une nouveau type de mouvement
        typemouvement_created = TypeMouvement.objects.create(
            libelle=request.POST.get('libelle'),
            statut=request.POST.get('statut'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': typemouvement_created.pk,
                'libelle': typemouvement_created.libelle,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_typemouvement(request, type_mouvement_id):

    typemouvement = TypeMouvement.objects.get(id=type_mouvement_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        TypeMouvement.objects.filter(id=type_mouvement_id).update(
            libelle=request.POST.get('libelle'),
            statut=request.POST.get('statut'),
            updated_at=datetime.now(),
        )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': typemouvement.pk,
                'libelle': typemouvement.libelle,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'typemouvements/modal_modifier_typemouvement.html', {'typemouvement': typemouvement})


@login_required
def supprimer_typemouvement(request, type_mouvement_id):
    if request.method == "POST":

        type_mouvement_id = request.POST.get('type_mouvement_id')
        print("type de mouvement id : ", type_mouvement_id)
        typemouvement = TypeMouvement.objects.get(id=type_mouvement_id)
        if typemouvement.pk is not None:

            typemouvement.delete()

            response = {
                'statut': 1,
                'message': "Type de mouvement supprimé avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Type de mouvement non trouvé !",
            }

            return JsonResponse(response)

#------------------------FIN TYPE DE MOUVEMENT----------------------------------


#------------------------TYPE DE SINISTRE----------------------------------

class TypeSinistreView(PermissionRequiredMixin,TemplateView):
    template_name = 'typesinistres/typesinistre.html'
    permission_required = "configurations.view_type_sinistre"
    model = TypeSinistre

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        typesinistres = TypeSinistre.objects.all().order_by('-id')

        context_perso = {'typesinistres': typesinistres}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_typesinistre(request):

    if request.method == 'POST':

        # Créer une nouveau type de sinistre
        typesinistre_created = TypeSinistre.objects.create(
            libelle=request.POST.get('libelle'),
            statut=request.POST.get('statut'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': typesinistre_created.pk,
                'libelle': typesinistre_created.libelle,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_typesinistre(request, type_sinistre_id):

    typesinistre = TypeSinistre.objects.get(id=type_sinistre_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        TypeSinistre.objects.filter(id=type_sinistre_id).update(
            libelle=request.POST.get('libelle'),
            statut=request.POST.get('statut'),
            updated_at=datetime.now(),
        )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': typesinistre.pk,
                'libelle': typesinistre.libelle,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'typesinistres/modal_modifier_typesinistre.html', {'typesinistre': typesinistre})


@login_required
def supprimer_typesinistre(request, type_sinistre_id):
    if request.method == "POST":

        type_sinistre_id = request.POST.get('type_sinistre_id')
        print("type de sinistre id : ", type_sinistre_id)
        typesinistre = TypeSinistre.objects.get(id=type_sinistre_id)
        if typesinistre.pk is not None:

            typesinistre.delete()

            response = {
                'statut': 1,
                'message': "Type de sinistre supprimé avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Type de sinistre non trouvé !",
            }

            return JsonResponse(response)

#------------------------FIN TYPE DE SINISTRE----------------------------------


#------------------------MOUVEMENT----------------------------------

class MouvementView(PermissionRequiredMixin,TemplateView):
    template_name = 'mouvements/mouvement.html'
    permission_required = "configurations.view_mouvements"
    model = Mouvement

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        mouvements = Mouvement.objects.all().order_by('-id')
        typemouvements = TypeMouvement.objects.filter(statut=1).order_by('libelle')

        context_perso = {'mouvements': mouvements, 'typemouvements': typemouvements}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_mouvement(request):

    if request.method == 'POST':

        # Créer une nouveau mouvement
        mouvement_created = Mouvement.objects.create(
            type_mouvement_id=request.POST.get('type_mouvement_id'),
            libelle=request.POST.get('libelle'),
            code=request.POST.get('code'),
            type=request.POST.get('type'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': mouvement_created.pk,
                'libelle': mouvement_created.libelle,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_mouvement(request, mouvement_id):

    mouvement = Mouvement.objects.get(id=mouvement_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Mouvement.objects.filter(id=mouvement_id).update(
            type_mouvement_id=request.POST.get('type_mouvement_id'),
            libelle=request.POST.get('libelle'),
            code=request.POST.get('code'),
            type=request.POST.get('type'),
            updated_at=datetime.now(),
        )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': mouvement.pk,
                'libelle': mouvement.libelle,
            }
        }

        return JsonResponse(response)

    else:
        typemouvements = TypeMouvement.objects.filter(statut=1).order_by('libelle')

        return render(request, 'mouvements/modal_modifier_mouvement.html', {'mouvement': mouvement, 'typemouvements': typemouvements})


@login_required
def supprimer_mouvement(request, mouvement_id):
    if request.method == "POST":

        mouvement_id = request.POST.get('mouvement_id')
        print("mouvement id : ", mouvement_id)
        mouvement = Mouvement.objects.get(id=mouvement_id)
        if mouvement.pk is not None:

            mouvement.delete()

            response = {
                'statut': 1,
                'message': "Mouvement supprimé avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Mouvement non trouvé !",
            }

            return JsonResponse(response)

#------------------------FIN MOUVEMENT----------------------------------


#------------------------MOTIF----------------------------------

class MotifView(PermissionRequiredMixin,TemplateView):
    template_name = 'motifs/motif.html'
    permission_required = "configurations.view_motifs"
    model = Motif

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        motifs = Motif.objects.all().order_by('-id')
        mouvements = Mouvement.objects.order_by('libelle')

        context_perso = {'motifs': motifs, 'mouvements': mouvements}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required
def add_motif(request):

    if request.method == 'POST':

        # Créer un nouveau motif
        motif_created = Motif.objects.create(
            mouvement_id=request.POST.get('mouvement_id'),
            libelle=request.POST.get('libelle'),
            etat_police=request.POST.get('etat_police'),
            etat_sinistre=request.POST.get('etat_sinistre'),
            code=request.POST.get('code'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': motif_created.pk,
                'libelle': motif_created.libelle,
            }
        }

        return JsonResponse(response)


@login_required
def import_motif(request):
    if request.method == 'POST':
        fichier = request.FILES.get('fichier')

        if not fichier:
            return JsonResponse({
                'statut': 0,
                'message': "Aucun fichier n'a été fourni."
            })

        try:
            # Lecture du fichier Excel
            df = pd.read_excel(fichier)

            # Compteur de lignes ignorées
            lignes_ignores = 0
            lignes_importees = 0

            for _, row in df.iterrows():
                code_mouvement = str(row['code_mouvement']).strip()

                try:
                    mouvement = Mouvement.objects.get(code=code_mouvement)
                except Mouvement.DoesNotExist:
                    lignes_ignores += 1
                    continue  # saut de la ligne

                # Création du motif
                Motif.objects.create(
                    code=row['code'],
                    libelle=row['libelle'],
                    #etat_sinistre=row['libelle'],
                    mouvement=mouvement,
                    created_at=datetime.now(),
                )
                lignes_importees += 1

            return JsonResponse({
                'statut': 1,
                'message': f"Importation terminée. {lignes_importees} lignes importées, {lignes_ignores} ignorées."
            })

        except Exception as e:
            return JsonResponse({
                'statut': 0,
                'message': f"Erreur lors de la lecture du fichier : {str(e)}"
            })


@login_required
def modifier_motif(request, motif_id):

    motif = Motif.objects.get(id=motif_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        Motif.objects.filter(id=motif_id).update(
            mouvement_id=request.POST.get('mouvement_id'),
            libelle=request.POST.get('libelle'),
            etat_police=request.POST.get('etat_police'),
            etat_sinistre=request.POST.get('etat_sinistre'),
            code=request.POST.get('code'),
            updated_at=datetime.now(),
        )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': motif.pk,
                'libelle': motif.libelle,
            }
        }

        return JsonResponse(response)

    else:
        mouvements = Mouvement.objects.order_by('libelle')
        return render(request, 'motifs/modal_modifier_motif.html', {'motif': motif, 'mouvements': mouvements})


@login_required
def supprimer_motif(request, motif_id):
    if request.method == "POST":

        motif_id = request.POST.get('motif_id')
        print("motif id : ", motif_id)
        motif = Motif.objects.get(id=motif_id)
        if motif.pk is not None:

            motif.delete()

            response = {
                'statut': 1,
                'message': "Motif supprimé avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Motif non trouvé !",
            }

            return JsonResponse(response)

#------------------------FIN MOTIF----------------------------------


#------------------------POSTE DE DOMMAGE----------------------------------

class PosteDommageView(PermissionRequiredMixin,TemplateView):
    template_name = 'postedommages/postedommage.html'
    permission_required = "configurations.view_poste_dommage"
    model = PosteDommage

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        postedommages = PosteDommage.objects.all().order_by('-id')

        context_perso = {'postedommages': postedommages}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


# Générer le code pour le poste de dommage
def generate_postedommage_code():

    # Trouver le dernier code créé dans la base de données
    last_code = PosteDommage.objects.aggregate(Max('code'))['code__max']
    
    # Extraire le numéro incrémental du dernier code
    if last_code:
        last_number = int(last_code[4:])  # Ex: "CIR001" -> 001
        new_number = last_number + 1
    else:
        new_number = 1  # Si aucun code n'existe encore

    # Formatage du nouveau numéro pour garder 3 chiffres
    new_code = f"PDOM{str(new_number).zfill(3)}"

    return new_code


@login_required
def add_postedommage(request):

    if request.method == 'POST':

        # Créer une nouveau poste de dommage
        postedommage_created = PosteDommage.objects.create(
            libelle=request.POST.get('libelle'),
            code=generate_postedommage_code(),
            statut=request.POST.get('statut'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': postedommage_created.pk,
                'libelle': postedommage_created.libelle,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_postedommage(request, postedommage_id):

    postedommage = PosteDommage.objects.get(id=postedommage_id)

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        PosteDommage.objects.filter(id=postedommage_id).update(
            libelle=request.POST.get('libelle'),
            statut=request.POST.get('statut'),
            updated_at=datetime.now(),
        )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': postedommage.pk,
                'libelle': postedommage.libelle,
            }
        }

        return JsonResponse(response)

    else:
        return render(request, 'postedommages/modal_modifier_postedommage.html', {'postedommage': postedommage})


@login_required
def supprimer_postedommage(request, postedommage_id):
    if request.method == "POST":

        postedommage_id = request.POST.get('postedommage_id')
        print("postedommage id : ", postedommage_id)
        postedommage = PosteDommage.objects.get(id=postedommage_id)
        if postedommage.pk is not None:

            postedommage.delete()

            response = {
                'statut': 1,
                'message': "Poste de dommage supprimé avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Poste de dommage non trouvé !",
            }

            return JsonResponse(response)

#------------------------FIN POSTE DE DOMMAGE----------------------------------


#--------------------------------------APPORTEUR INTERNAL----------------------------------------------------------

class ApporteurinternationalView(PermissionRequiredMixin, TemplateView):
    template_name = 'apporteur_international/apporteur_inter.html'
    permission_required = "configurations.view_apporteurinternational"
    model = ApporteurInternational

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        apporteurinternational = ApporteurInternational.objects.all()
        utilisateurs = User.objects.filter(bureau=request.user.bureau, type_utilisateur__code="INTERNE",
                                           is_active=True).order_by('last_name')

        context_perso = {'apporteur': apporteurinternational, 'utilisateurs': utilisateurs}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }

#--------------------------------------COURRIER--------------------------------------------------

class ViewCourrier(PermissionRequiredMixin, TemplateView):
    template_name = 'courriers/courrier.html'
    permission_required = "configurations.view_courrier"
    model = Courrier

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        courriers = Courrier.objects.all()
        utilisateurs = User.objects.filter(bureau=request.user.bureau, type_utilisateur__code="INTERNE",
                                           is_active=True).order_by('last_name')

        context_perso = {'courriers': courriers, 'utilisateurs': utilisateurs}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@login_required()
def add_courrier(request):
    if request.method == 'POST':
        # Récupération des données depuis la requête
        designation = request.POST.get('designation')
        service = request.POST.get('service')
        status = request.POST.get('status')

        # Vérifie que toutes les données requises sont présentes
        if not all([designation, service, status]):
            return JsonResponse({
                'statut': 0,
                'message': "Veuillez remplir tous les champs requis.",
            }, status=400)


    courrier_created = Courrier.objects.create(
            designation = request.POST.get('designation'),
            service = request.POST.get('service'),
            status = request.POST.get('status')
        )


    response = {
            'statut': 1,
            'message': "Enregistrement effectuée avec succès !",
            'data': {
                'designation': courrier_created.designation,
                'service':courrier_created.service,
                'status': courrier_created.status,
                'created_at': courrier_created.created_at,
            }
        }

    return JsonResponse(response)


def modifier_courrier(request, courrier_id):

    courrier = get_object_or_404(Courrier, id=courrier_id)

    if request.method == 'POST':

        courrier_before = courrier
        pprint(courrier_before)

        # Récupérer les champs envoyés par le formulaire
        designation = request.POST.get('designation')
        service =request.POST.get('service')
        status = request.POST.get('statut')



        # Mettre à jour les champs
        # courrier.produit = produit
        courrier.designation = designation
        # courrier.lien_fichier = lien_fichier
        courrier.service = service
        courrier.status = status

        # Sauvegarder les modifications
        courrier.save()

        # Log d'action (si nécessaire)
        ActionLog.objects.create(
            done_by=request.user,
            action="update",
            description="Modification d'un courrier",
            table="courrier",
            row=courrier.pk,
        )

        # Retourner une réponse JSON pour AJAX
        return JsonResponse({
            'statut': 1,
            'message': "Courrier modifié avec succès !"
        })

    else:
        courriers = Courrier.objects.all()  # Options pour les services et statuts
        return render(request, 'courriers/modal_courrier_update.html', {'courrier': courrier})


@login_required()
def supprimer_courrier(request):
    if request.method == "POST":
        courrier_id = request.POST.get('courrier_id')

        try:
            courrier = Courrier.objects.get(id=courrier_id)
            courrier.delete()

            response = {
                'statut': 1,
                'message': "Courrier supprimé avec succès !",
            }

        except Courrier.DoesNotExist:
            response = {
                'statut': 0,
                'message': "Courrier introuvable !",
            }

        return JsonResponse(response)

    return JsonResponse({'statut': 0, 'message': "Requête invalide !"}, status=400)

