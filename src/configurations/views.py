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
from configurations.models import ActionLog, Specialite, Secteur, \
    Bureau ,BusinessUnit, Branche, Banque, Apporteur, ApporteurInternational,Devise,\
    User, AuthGroup, TypeEtablissement,Tarif, Rubrique, \
    BackgroundQueryTask, ParamProduitCompagnie, Compagnie, \
    TypeApporteur, TypePersonne, Pays, TypeCompagnie, TypeGarant, RisqueProduit, Carosserie, \
    CategorieVehicule, Civilite, CompteTresorerie, ConditionsAssurance, Carburant, Formule, Fractionnement, Garantie, GarantieFormule, \
    Groupe, ModeReglement, Circonstance, Responsabilite, TypeIntervenant, TypeMouvement, TypeSinistre, PosteDommage, GarantieCirconstance
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

        risqueproduit = RisqueProduit.objects.all()

        for risque in risqueproduit:
            produits = Produit.objects.filter(risque_produit_id=risque.id)
            for produit in produits:
                ParamProduitCompagnie.objects.create(
                    compagnie_id=compagnie.id, produit_id=produit.id,
                    taux_com_courtage=risque.taux,
                    taux_com_courtage_terme=risque.taux,
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
            status=request.POST.get('status'),
            created_at=datetime.now(),
        )

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': fractionnement_created.pk,
                'libelle': fractionnement_created.libelle,
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
                                                    status=request.POST.get('status'),
                                                   )
        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': fractionnement.pk,
                'libelle': fractionnement.libelle,
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

        # Créer une nouveau motif
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

