
from datetime import date, datetime
from decimal import Decimal
from pprint import pprint

from django.core.paginator import Paginator
from django.db.models.functions import Concat
from django.urls import reverse
from django.views.generic import TemplateView
from django.views import View
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout,authenticate
from django.contrib.auth import get_user_model
from django_dump_die.middleware import dd
import openpyxl

from grh.models import Campagne
from production.helper_production import create_alimet_helper
from shared.helpers import generate_numero_famille, generer_nombre_famille_du_mois
from sinistre.models import Sinistre


User = get_user_model()

from production.models import Aliment, AlimentFormule, Bareme, Document, Mouvement, \
    MouvementPolice, Police, Quittance, Reglement, TypeDocument, Client
from configurations.models import Civilite, Pays, Prestataire, User
from shared.enum import Statut, StatutQuittance, Genre, StatutEnrolement, StatutValidite, StatutIncorporation, \
    StatutTraitement


from django.db.models import ExpressionWrapper, F, DurationField, Q, Value
from django.db.models import Count

from .helper import generate_uiid, send_email, format_phone_number,export_beneficiaire,send_otp_mail
from django.db.models import Count, Sum
import json

from django.utils import formats
from django.utils import timezone

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView

from django.db import transaction
from django.db import connection

import pyotp
#

from django_otp.util import random_number_token
from inov import settings
from django.core.mail import send_mail

#
from django.contrib.humanize.templatetags.humanize import intcomma

# Create your views here.


#LOGIN

class LoginView(TemplateView):
    template_name = "grh/auth/login.html"

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            error_message = "Cet utilisateur n'existe pas !"
            messages.error(request, error_message)
            return render(request, self.template_name, {'error': error_message})
        if user.check_password(password):
            if user.utilisateur_grh is None:
                error_message = "Cet utilisateur n'est pas autorisé à accéder !"
                messages.error(request, error_message)
                return render(request, self.template_name, {'error': error_message})
            else:
                #authenticated_user = User.objects.get(username=user.username)
                login(request, user)
                return redirect('grh.dashboard')

                # if not user.email:
                #     login(request, user)
                #     return redirect('grh.dashboard')
                #
                # email = user.email
                #
                # # generate the code
                # hotp = pyotp.HOTP(settings.OTP_SECRET_KEY, digits=6)
                # code_verification = int(datetime.now().strftime("%Y%m%d%H%M%S"))
                # code = hotp.at(code_verification)
                #
                #
                # request.session['code'] = "123456" # code
                # request.session['email'] = email
                # request.session['username'] = user.username
                #
                # # send_otp_mail(email, code)

                # return redirect('grh.verify_codes')
        else:
            error_message = 'Mot de passe incorrect !'
            messages.error(request, error_message)
            return render(request, self.template_name, {'error': error_message})


# LOGOUT
class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('grh.login')


# DASHBOARD
class DashboardView(TemplateView):
    template_name = "grh/dashboard.html"

    ######################################################
    
    def get(self, request, *args, **kwargs):

        selected_police_id = kwargs.get('selected_police_id')
        client = request.user.utilisateur_grh

        # CHECK PAGE FIRST LOAD
        if not request.session.get('page_loaded', False):

            # SET SESSION FLAG
            request.session['page_loaded'] = True
            if not selected_police_id and client:

                # POLICES-CLIENT
                police_clients = Police.objects.filter(client=client)

                # POLICES-CLIENT EN COURS
                police_clients_encours = [p for p in police_clients if p.etat_police == "En cours"]
                if police_clients_encours:
                    selected_police_id = police_clients_encours[0].id
                    return HttpResponseRedirect(reverse('grh.dashboard', kwargs={'selected_police_id': selected_police_id}))

        # CLEAR SESSION FLAG
        if selected_police_id:
            request.session['page_loaded'] = True

        return super().get(request, *args, **kwargs)

    ######################################################

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # CLIENT
        client = self.request.user.utilisateur_grh

        # POLICES-CLIENT
        if client:

            police_clients = Police.objects.filter(client=client)
            context['police_clients'] = police_clients

            # POLICES-CLIENT EN COURS
            police_clients_encours = [p for p in police_clients if p.etat_police == "En cours"]
            context['police_clients_encours'] = police_clients_encours
    
            # POPULATION TOTALE
            total_aliments_all_police = sum(p.nombre_total_beneficiaires for p in police_clients)
            context['total_aliments_all_police'] = total_aliments_all_police

            # POPULATION ACTIVE
            total_aliments_entres_all_police = sum(p.nombre_beneficiaires_entres for p in police_clients_encours)
            context['total_aliments_entres_all_police'] = total_aliments_entres_all_police

            # PRIME TOTAL
            quittances_for_all_polices = Quittance.objects.filter(police__in=police_clients_encours, statut_validite=StatutValidite.VALIDE)
            total_prime_ttc_all_polices = quittances_for_all_polices.aggregate(Sum('prime_ttc'))['prime_ttc__sum']
            if total_prime_ttc_all_polices is None:
                total_prime_ttc_all_polices = 0
            formatted_total_prime_ttc = "{:,}".format(total_prime_ttc_all_polices).replace(",", " ")
            context['total_prime_ttc_all_polices'] = formatted_total_prime_ttc

            # SOLDE DU CLIENT
            total_reglements = Reglement.objects.filter(quittance__police__in=police_clients).aggregate(total_reglements=Sum('montant'))['total_reglements'] or 0
            total_quittances = Quittance.objects.filter(police__in=police_clients).aggregate(total_quittances=Sum('prime_ttc'))['total_quittances'] or 0
            solde_total_client = total_reglements - total_quittances
            context['solde_total_client'] = intcomma(solde_total_client)

            # GRAPHE - TOTAL EVOLUTION POPULATION
            current_year = timezone.now().year
            current_month = timezone.now().month
            previous_year = current_year - 1

            # PREPARE THE MONTH LABELS FOR THE CHART
            months = [datetime(current_year, month, 1).strftime('%b %Y') for month in range(1, current_month + 1)]

            # GET THE TOTAL BENEFICIARIES AT THE END OF THE PREVIOUS YEAR
            total_aliments_previous_year = Aliment.objects.filter(
                historique_formules__formule__police__in=police_clients,
                date_affiliation__lte=datetime(previous_year, 12, 31),
                statut_incorporation=StatutIncorporation.INCORPORE,
            )

            # EXCLUDE BENEFICIARIES WITH THE SPECIFIED STATES IN THE QUERYSET
            excluded_states = ["SORTI", "SORTIE EN COURS", "ENTREE EN COURS"]
            total_aliments_previous_year = total_aliments_previous_year.exclude(
                id__in=[aliment.id for aliment in total_aliments_previous_year if aliment.etat_beneficiaire in excluded_states]
            ).count()

            total_progression = {}
            previous_total = total_aliments_previous_year

            # LOOP THROUGH EACH MONTH OF THE CURRENT YEAR TO UPDATE THE CUMULATIVE TOTAL
            for month in range(1, current_month + 1):
                # GET NEWLY ADDED BENEFICIARIES FOR THE CURRENT MONTH
                aliment_counts = Aliment.objects.filter(
                    historique_formules__formule__police__in=police_clients,
                    date_affiliation__month=month,
                    date_affiliation__year=current_year,
                )

                # EXCLUDE BENEFICIARIES WITH THE SPECIFIED STATES
                aliment_counts = aliment_counts.exclude(
                    id__in=[aliment.id for aliment in aliment_counts if aliment.etat_beneficiaire in excluded_states]
                ).count()

                previous_total += aliment_counts  # UPDATE THE CUMULATIVE TOTAL.
                total_progression[month] = previous_total  # STORE THE CUMULATIVE TOTAL FOR THIS MONTH

            # PREPARE CHART DATA
            chart_data = [{
                'name': 'Aliments',
                'data': [total_progression.get(month, 0) for month in range(1, current_month + 1)]
            }]
            chart_data_json = json.dumps(chart_data)
            context['chart_data_json'] = chart_data_json
            context['months'] = months

        ####################################################################################

        # SELECTED POLICE - SESSION
        selected_police_id = self.kwargs.get('selected_police_id')
        self.request.session['selected_police_id'] = selected_police_id
        try:
            selected_police = Police.objects.get(id=selected_police_id)
        except Police.DoesNotExist:
            selected_police = None
        context['selected_police'] = selected_police

        # SELECTED POLICE - CHECK
        if selected_police:

            # SELECTED POLICE - POPULATION
            total_police_active_id = selected_police.nombre_total_beneficiaires

            # SELECTED POLICE - POPULATION ACTIVE
            print(selected_police.nombre_beneficiaires_entres)

            # FILTER BY POLICE - PRIME
            quittances_for_selected_police = Quittance.objects.filter(police=selected_police,statut_validite=StatutValidite.VALIDE)
            total_prime_ttc_result = quittances_for_selected_police.aggregate(total_prime_ttc=Sum('prime_ttc'))
            total_prime_ttc = total_prime_ttc_result['total_prime_ttc']
            if total_prime_ttc is None:
                total_prime_ttc = 0
            formatted_total_prime_ttc = "{:,}".format(total_prime_ttc).replace(",", " ")
            context['total_prime_ttc'] = formatted_total_prime_ttc

            # FILTER BY POLICE - SOLDE DU CLIENT
            total_reglements = Reglement.objects.filter(quittance__police=selected_police).aggregate(total_reglements=Sum('montant'))['total_reglements'] or 0
            total_quittances = Quittance.objects.filter(police=selected_police).aggregate(total_quittances=Sum('prime_ttc'))['total_quittances'] or 0
            solde_police_client = total_reglements - total_quittances
            context['solde_police_client'] = solde_police_client

            # FILTER BY POLICE - TOTAL CONSOMMATION SINISTRE / TYPE ALIMENT
            aliments_for_selected_police = Aliment.objects.filter(historique_formules__formule__police=selected_police)
            total_sums_selected_police = {}
            context['total_sums_selected_police'] = json.dumps(total_sums_selected_police)
            context['total_police_active_id'] = total_police_active_id

            # FILTER BY POLICE - GRAPHE LINEAIRE POPULATION                 
            current_year = timezone.now().year
            current_month = timezone.now().month
            previous_year = current_year - 1

            # PREPARE THE MONTH LABELS FOR THE CHART
            months_filter = [datetime(current_year, month, 1).strftime('%b %Y') for month in range(1, current_month + 1)]

            # GET THE TOTAL BENEFICIARIES AT THE END OF THE PREVIOUS YEAR FOR THE SELECTED POLICE
            total_aliments_previous_year = Aliment.objects.filter(
                historique_formules__formule__police=selected_police,
                date_affiliation__lte=datetime(previous_year, 12, 31),
                statut_incorporation=StatutIncorporation.INCORPORE,
            )

            # EXCLUDE BENEFICIARIES WITH THE SPECIFIED STATES IN THE QUERYSET
            excluded_states = ["SORTI", "SORTIE EN COURS", "ENTREE EN COURS"]
            total_aliments_previous_year = total_aliments_previous_year.exclude(
                id__in=[aliment.id for aliment in total_aliments_previous_year if aliment.etat_beneficiaire in excluded_states]
            ).count()

            total_progression = {}
            previous_total = total_aliments_previous_year

            # LOOP THROUGH EACH MONTH OF THE CURRENT YEAR TO UPDATE THE CUMULATIVE TOTAL
            for month in range(1, current_month + 1):
                # GET NEWLY ADDED BENEFICIARIES FOR THE CURRENT MONTH
                aliment_counts = Aliment.objects.filter(
                    historique_formules__formule__police=selected_police,
                    date_affiliation__month=month,
                    date_affiliation__year=current_year,
                )

                # EXCLUDE BENEFICIARIES WITH THE SPECIFIED STATES
                aliment_counts = aliment_counts.exclude(
                    id__in=[aliment.id for aliment in aliment_counts if aliment.etat_beneficiaire in excluded_states]
                ).count()

                previous_total += aliment_counts  # UPDATE THE CUMULATIVE TOTAL
                total_progression[month] = previous_total  # STORE THE CUMULATIVE TOTAL FOR THIS MONTH

            # FILTER BY POLICE - PREPARE CHART DATA
            chart_data_filter = [{
                'name': 'Aliments',
                'data': [total_progression.get(month, 0) for month in range(1, current_month + 1)]  
            }]
            chart_data_json_filter = json.dumps(chart_data_filter)
            context['chart_data_json_filter'] = chart_data_json_filter
            context['months_filter'] = months_filter

        return context


def set_client(request):
    if request.method == 'POST':
        user = request.user

        if user.client_grh is not None:
            client_id = request.POST.get('client_id')
            utilisateur_grh = Client.objects.get(pk=client_id)
            user.utilisateur_grh = utilisateur_grh
            user.save()

    # Get the previous URL from the 'HTTP_REFERER' header, if available
    previous_page = request.META.get('HTTP_REFERER')

    # If the 'HTTP_REFERER' header is not available or points to the same URL,
    # redirect to a default URL (e.g., homepage).
    if not previous_page or previous_page == request.build_absolute_uri():
        return HttpResponseRedirect(reverse('grh.dashboard'))  # Replace 'home' with the name of your homepage URL pattern.
    else:
        for url in ['polices/police_overview/', 'polices/']:
            if url in previous_page:
                return HttpResponseRedirect(reverse('grh.polices'))

        for url in ['onboarding/details_compagne/', 'onboarding/']:
            if url in previous_page:
                return HttpResponseRedirect(reverse('grh.onboarding'))
        # print(previous_page)
        return HttpResponseRedirect(reverse('grh.dashboard'))


# ONBOARDING
class OnBoardingView(TemplateView):
    template_name = "grh/onboarding.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        admin_grh = self.request.user
        today = formats.date_format(date.today(), "Y-m-d")

        related_client = admin_grh.utilisateur_grh

        if related_client:

            related_polices = Police.objects.filter(client=related_client)
            context['related_polices'] = related_polices

            campagnes = Campagne.objects.filter(police__in=related_polices, created_by=admin_grh)
            for campagne in campagnes:
                if campagne.date_debut > timezone.now():
                    campagne.statut = StatutValidite.BROUILLON
                    campagne.save()
                if campagne.date_fin < timezone.now().replace(hour=0, minute=0, second=0, microsecond=0):
                    campagne.statut = StatutValidite.CLOTURE
                    campagne.save()

            context['campagnes'] = campagnes
            context['today'] = today

            for police in related_polices:
                etat_police = police.etat_police
                context['etat_police'] = etat_police

        return context

    def post(self, request, *args, **kwargs):

        #   base_url = 'https://preprod.inov.com'
        #   base_url = 'https://inov.com'
        #   base_url ='http://127.0.0.1:8000'

        if request.META.get('HTTP_HOST') == 'preprod.inov.com':
            base_url = 'https://preprod.inov.com'

        elif request.META.get('HTTP_HOST') == 'inov.com':
            base_url = 'https://inov.com'

        else:
            base_url = 'http://127.0.0.1:8000'

        libelle_campagne = request.POST.get('libelle', None)
        date_debut_str = request.POST.get('date_debut', None)
        date_fin_str = request.POST.get('date_fin', None)

        selected_police = request.POST.get('police', None)
        police = get_object_or_404(Police, id=selected_police)
        selected_formule = request.POST.get('formule', None)

        date_debut = None
        date_fin = None

        if date_debut_str:
            date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d')
        if date_fin_str:
            date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d')

        email_group = request.POST.get('list_email', None)
        destinataires = email_group.split(';')

        today = timezone.now().date()

        if date_debut and date_debut.date() == today:
            default_statut = StatutValidite.VALIDE
        else:
            default_statut = StatutValidite.BROUILLON

        admin_grh = self.request.user
        bureau = admin_grh.utilisateur_grh.bureau

        campagne = Campagne(
            created_by=admin_grh,
            libelle=libelle_campagne,
            police=police,
            date_debut=date_debut,
            date_fin=date_fin,
            statut=default_statut
        )
        campagne.save()

        for email in destinataires:
            email = email.strip()
            if email:
                pass

        return redirect('grh.onboarding')


class DetailsCampagneView(TemplateView):
    template_name = "grh/details_campagne.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        campagne_id = kwargs.get('campagne_id')
        campagne = get_object_or_404(Campagne, id=campagne_id)

        admin_grh = self.request.user

        return context


class IncorporationByEnrolementView(TemplateView):
    template_name = "grh/incorporations_by_enrolement.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        today = formats.date_format(date.today(), "Y-m-d")
        print("today")
        print(today)

        campagne_id = kwargs.get('campagne_id')
        prospect_id = kwargs.get('prospect_id')

        pprint("campagne_id")
        pprint(campagne_id)

        pprint("prospect_id")
        pprint(prospect_id)

        campagne = get_object_or_404(Campagne, id=campagne_id)
        admin_grh = self.request.user

        context['campagne'] = campagne
        context['today'] = today

        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # TODO : CREATE ALIMENT
        opened_campagne_id = kwargs.get('campagne_id')
        opened_prospect_id = kwargs.get('prospect_id')
        post_data = request.POST
        date_affiliation = post_data.get('date_affiliation')
        valide_option = post_data.get('valide_option')


        print("@@@@@@@@@@@@@@")
        print(request.POST)

        print("@@@@@@@@@@@@@@")
        print(request.POST.get('date_affiliation'))

        opened_campagne = get_object_or_404(Campagne, id=opened_campagne_id)

        prospect_id = None

        if valide_option.startswith('valider_'):
            action = 'valider'
            prospect_id = valide_option.split('_')[1]
        elif valide_option.startswith('rejeter_'):
            action = 'rejeter'
            prospect_id = valide_option.split('_')[1]

        if valide_option == 'valider_tous':
            pass

        elif prospect_id:
            pass
        context = self.get_context_data(**kwargs)

        return self.render_to_response(context)


# POLICE
class PolicesView(TemplateView):
    template_name = "grh/polices.html"

    def get(self, request, *args, **kwargs):

        client = request.user.utilisateur_grh
        if client:
            polices = Police.objects.filter(client=client)
            return render(request, self.template_name, {'polices': polices})
        else:
            return redirect('grh.login')


class PoliceOverviewView(TemplateView):
    template_name = "grh/police_overview.html"

    def dispatch(self, request, *args, **kwargs):

        police_id = kwargs.get('police_id')
        client = request.user.utilisateur_grh
        self.police = get_object_or_404(Police, id=police_id, client=client)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['police'] = self.police

        return context


class DetailsPoliceView(TemplateView):
    template_name = "grh/details_police.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        police_id = kwargs.get('police_id')
        police = get_object_or_404(Police, id=police_id)
        mouvements = MouvementPolice.objects.filter(police=police)
        duree_police_en_mois = Police.objects.filter(id=police.id).annotate(
            duree_police_en_mois=ExpressionWrapper(
                F('date_fin_effet') - F('date_debut_effet'),
                output_field=DurationField()
            )
        ).values('id', 'duree_police_en_mois').first()['duree_police_en_mois']
        nombre_total_mois = duree_police_en_mois.days // 30
        duree = f"{nombre_total_mois}"

        context['police'] = police
        context['mouvements'] = mouvements
        context['duree_police'] = duree

        return context


class FormulesPoliceView(TemplateView):
    template_name = "grh/formules_police.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        police_id = kwargs.get('police_id')
        police = get_object_or_404(Police, id=police_id)

        context['police'] = police

        return context


class DetailsFormulePoliceView(TemplateView):
    template_name = "grh/details_formule_police.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        police_id = kwargs.get('police_id')
        formule_id = kwargs.get('formule_id')

        police = get_object_or_404(Police, id=police_id)
        reseau_soins = []

        context['police'] = police
        context['reseau_soins'] = reseau_soins

        return context


class DetailsGarantieFormulePoliceView(TemplateView):
    template_name = "grh/details_garantie_formule_police.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        police_id = kwargs.get('police_id')
        formule_id = kwargs.get('formule_id')
        bareme_id = kwargs.get('bareme_id')

        police = get_object_or_404(Police, id=police_id)
        bareme = get_object_or_404(Bareme, id=bareme_id)

        context['police'] = police
        context['bareme'] = bareme

        return context


class ReseauDeSoinView(TemplateView):
    template_name = "grh/reseau_de_soin.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        police_id = kwargs.get('police_id')

        police = get_object_or_404(Police, id=police_id)

        context['police'] = police

        return context


class PrestataireMedicalView(TemplateView):
    template_name = "grh/prestataire_medical.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        police_id = kwargs.get('police_id')
        formule_id = kwargs.get('formule_id')
        prestataire_id = kwargs.get('prestataire_id')
        
        police = get_object_or_404(Police, id=police_id)
        prestataire = get_object_or_404(Prestataire, id=prestataire_id)

        context['police'] = police
        context['formule'] = formule
        context['prestataire'] = prestataire

        return context


class QuittancesPoliceView(TemplateView):
    template_name = "grh/quittances_police.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        police_id = kwargs.get('police_id')

        police = get_object_or_404(Police, id=police_id)

        quittances = Quittance.objects.filter(police=police)
        quittances_impayees = Quittance.objects.filter(police=police, statut=StatutQuittance.IMPAYE)

        context['police'] = police
        context['quittances'] = quittances
        context['quittances_impayees'] = quittances_impayees

        return context


class FicheQuittanceView(TemplateView):
    template_name = "grh/fiche_quittance.html"
    
    def dispatch(self, request, *args, **kwargs):
        police_id = kwargs.get('police_id')
        client = request.user.utilisateur_grh
        self.police = get_object_or_404(Police, id=police_id, client=client)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        police_id = kwargs.get('police_id')
        quittance_id = kwargs.get('quittance_id')

        police = get_object_or_404(Police, id=police_id)
        quittance = get_object_or_404(Quittance, id=quittance_id)

        context['police'] = police
        context['quittance'] = quittance

        return context


class DocumentsPoliceView(TemplateView):
    template_name = "grh/documents_police.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        police_id = kwargs.get('police_id')
        police = get_object_or_404(Police, id=police_id)
        documents = Document.objects.filter(police=police)
        
        context['police'] = police
        context['documents'] = documents

        return context


class BeneficiairePoliceView(TemplateView):
    template_name = "grh/beneficiaire.html"

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        police_id = kwargs.get('police_id')
        police = get_object_or_404(Police, id=police_id)

        aliment_formule_ids = AlimentFormule.objects.filter(formule_id__in=[p.id for p in police.formules], 
                                                            statut=Statut.ACTIF).values_list('aliment_id', 
                                                                                             flat=True).order_by('-id')
        beneficiaires = Aliment.objects.filter(id__in=aliment_formule_ids)[:100]

        option_export_beneficiaire = export_beneficiaire

        context['police'] = police
        context['beneficiaires'] = beneficiaires

        context['option_export_beneficiaire'] = option_export_beneficiaire

        return context


def beneficiaire_police_datatable(request, police_id):
    items_per_page = 10
    page_number = request.GET.get('page')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', items_per_page))
    sort_column_index = int(request.GET.get('order[0][column]'))
    sort_direction = request.GET.get('order[0][dir]')
    search = request.GET.get('search[value]', '')
    search_etat = request.GET.get('search_etat', '')

    police = get_object_or_404(Police, id=police_id)

    queryset = Aliment.objects.all()


    # Map column index to corresponding model field for sorting
    sort_columns = {
        # 1: '-numero_carte',
        2: 'created_at',
        3: 'nom',
        4: 'genre',
        5: 'qualite_beneficiaire__libelle',
        # Add more columns as needed
    }

    # Default sorting by 'id' if column index is not found
    sort_column = sort_columns.get(sort_column_index, 'id')

    if sort_direction == 'desc':
        sort_column = '-' + sort_column  # For descending order
        queryset = queryset.order_by(sort_column)


    if search:
        queryset = queryset.annotate(full_name=Concat(F('nom'), Value(' '), F('prenoms'))).filter(
            Q(full_name__icontains=search) |
            Q(qualite_beneficiaire__libelle__icontains=search) |
            Q(qualite_beneficiaire__code__icontains=search) |
            Q(cartes__numero__icontains=search),
            cartes__statut=Statut.ACTIF
        )

    if search_etat:

        print("search_etat")
        print(search_etat)
        filtered_qs_ids = [obj.id for obj in queryset if obj.etat_beneficiaire == search_etat]
        queryset = queryset.filter(id__in=filtered_qs_ids)

    paginator = Paginator(queryset, length)
    page_obj = paginator.get_page(page_number)

    # Prepare the data in the expected format
    data = []
    for c in page_obj:
        detail_url = reverse('grh.beneficiaire_overview', args=[police_id,c.id])  # URL to the detail view# URL to the detail view
        actions_html = f'<div class="flex justify-center items-center"><a href="{detail_url}"><i data-feather="eye" class="title"></i></a></div>'
        statut_html = f'<div class="flex items justify-center status status-{c.etat_beneficiaire.lower()} badge-{c.etat_beneficiaire.lower()}">{c.etat_beneficiaire}</div>'

        data_iten = {
            "id": c.id,
            "numero_carte": f'{c.carte_active()}' if c.carte_active else "",
            "date_ajout": c.created_at.strftime("%d/%m/%Y"),
            "nom_prenoms": f"{c.nom} {c.prenoms}",
            "sexe": c.genre if c.genre else "",
            "lien": c.qualite_beneficiaire.libelle if c.qualite_beneficiaire else "",
            "date_entree": c.date_affiliation.strftime("%d/%m/%Y") if c.date_affiliation else "",
            "etat": statut_html,
            "motif": c.last_mouvement.motif if c.last_mouvement else "",
            "actions": actions_html,
        }

        data.append(data_iten)

    return JsonResponse({
        "data": data,
        "recordsTotal": queryset.count() if not request.user.is_med else len(queryset),
        "recordsFiltered": paginator.count,
        "draw": int(request.GET.get('draw', 1)),
    })



# BÉNÉFICIAIRE
class BeneficiaireOverviewView(TemplateView):
    template_name = "grh/beneficiaire_overview.html"

    def dispatch(self, request, *args, **kwargs):
        police_id = kwargs.get('police_id')
        client = request.user.utilisateur_grh
        
        # Ensure the police belongs to the client
        self.police = get_object_or_404(Police, id=police_id, client=client)
        
        # Call the parent class's dispatch method
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        police_id = kwargs.get('police_id')
        beneficiaire_id = kwargs.get('beneficiaire_id')

        # Fetch the police and beneficiaire objects
        police = get_object_or_404(Police, id=police_id)
        beneficiaire = get_object_or_404(Aliment, id=beneficiaire_id)

        # Add data to context
        etat_police = police.etat_police
        context['etat_police'] = etat_police
        context['police'] = police
        context['beneficiaire'] = beneficiaire

        return context


class FicheBeneficiaireView(TemplateView):
    template_name = "grh/fiche_beneficiaire.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        police_id = kwargs.get('police_id')
        beneficiaire_id = kwargs.get('beneficiaire_id')

        police = get_object_or_404(Police, id=police_id)
        beneficiaire = get_object_or_404(Aliment, id=beneficiaire_id)
        adherent = beneficiaire.adherent_principal
        aliment_formule = AlimentFormule.objects.filter(aliment=beneficiaire).first()
        formule = aliment_formule.formule

        date_entree_police = beneficiaire.historique_formules.first().date_debut if beneficiaire.historique_formules else None

        context['date_entree_police'] = date_entree_police
        context['police'] = police
        context['beneficiaire'] = beneficiaire
        context['adherent'] = adherent
        context['formule'] = formule
        context['photo_identite'] = beneficiaire.photo

        return context


class SortirBeneficiaireView(TemplateView):
    template_name = "grh/sortir_beneficiaire.html"
    def dispatch(self, request, *args, **kwargs):
        # Retrieve police_id from kwargs
        police_id = kwargs.get('police_id')
        client = request.user.utilisateur_grh
        self.police = get_object_or_404(Police, id=police_id, client=client)

        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        police_id = kwargs.get('police_id')
        beneficiaire_id = kwargs.get('beneficiaire_id')

        today = formats.date_format(date.today(), "Y-m-d")

        police = get_object_or_404(Police, id=police_id)
        beneficiaire = get_object_or_404(Aliment, id=beneficiaire_id)

        context['police'] = police
        context['beneficiaire'] = beneficiaire
        context['today'] = today

        return context

    def post(self, request, *args, **kwargs):

        beneficiaire_id = kwargs.get('beneficiaire_id')
        police_id = kwargs.get('police_id')

        police = get_object_or_404(Police, id=police_id)
        aliment = get_object_or_404(Aliment, id=beneficiaire_id)

        date_sortie = request.POST.get('date_sortie', None)
        motif = request.POST.get('motif', None)

        mouvement = Mouvement.objects.filter(code="DMDSORTIE").first()

        return redirect('grh.police_overview', police_id=police_id)


class SuspendreBeneficiaireView(TemplateView):
    template_name = "grh/suspendre_beneficiaire.html"

    def dispatch(self, request, *args, **kwargs):
        # Retrieve police_id from kwargs
        police_id = kwargs.get('police_id')
        client = request.user.utilisateur_grh
        self.police = get_object_or_404(Police, id=police_id, client=client)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        police_id = kwargs.get('police_id')
        beneficiaire_id = kwargs.get('beneficiaire_id')

        today = formats.date_format(date.today(), "Y-m-d")

        # Ensure that the police belongs to the current user
        police = get_object_or_404(Police, id=police_id, client=self.police.client)
        beneficiaire = get_object_or_404(Aliment, id=beneficiaire_id)

        context['police'] = police
        context['beneficiaire'] = beneficiaire
        context['today'] = today

        return context

    def post(self, request, *args, **kwargs):

        beneficiaire_id = kwargs.get('beneficiaire_id')
        police_id = kwargs.get('police_id')

        police = get_object_or_404(Police, id=police_id)
        aliment = get_object_or_404(Aliment, id=beneficiaire_id)
        mouvement = Mouvement.objects.filter(code='DMDSUSPENSION').first()
        admin_grh = self.request.user

        date_suspension = request.POST.get('date_suspension', None)
        motif = request.POST.get('motif', None)

        return redirect('grh.police_overview', police_id=police_id)


class FamilleBeneficiaireView(TemplateView):
    template_name = "grh/famille_beneficiaire.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        police_id = kwargs.get('police_id')
        beneficiaire_id = kwargs.get('beneficiaire_id')
        police = get_object_or_404(Police, id=police_id)
        aliment = get_object_or_404(Aliment, id=beneficiaire_id)
        adherent = aliment.adherent_principal
        famille = Aliment.objects.filter(adherent_principal=adherent).all()

        #
        etat_police = police.etat_police
        context['etat_police'] = etat_police

        context['police'] = police
        context['beneficiaire'] = adherent
        context['famille'] = famille

        return context


class GarantiesBeneficiaireView(TemplateView):
    template_name = "grh/garanties_beneficiaire.html"
    def dispatch(self, request, *args, **kwargs):
        police_id = kwargs.get('police_id')
        client = request.user.utilisateur_grh
        self.police = get_object_or_404(Police, id=police_id, client=client)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        police_id = kwargs.get('police_id')
        beneficiaire_id = kwargs.get('beneficiaire_id')
        police = get_object_or_404(Police, id=police_id)
        beneficiaire = get_object_or_404(Aliment, id=beneficiaire_id)
        aliment_formule = AlimentFormule.objects.filter(aliment=beneficiaire).first()
        formule = aliment_formule.formule

        context['police'] = police
        context['formule'] = formule
        context['beneficiaire'] = beneficiaire

        return context


class DetailsGarantieFormuleBeneficiaireView(TemplateView):
    template_name = "grh/details_garantie_formule_beneficiaire.html"
    def dispatch(self, request, *args, **kwargs):
        police_id = kwargs.get('police_id')
        client = request.user.utilisateur_grh
        self.police = get_object_or_404(Police, id=police_id, client=client)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        police_id = kwargs.get('police_id')
        beneficiaire_id = kwargs.get('beneficiaire_id')
        formule_id = kwargs.get('formule_id')
        bareme_id = kwargs.get('bareme_id')
        police = get_object_or_404(Police, id=police_id)
        beneficiaire = get_object_or_404(Aliment, id=beneficiaire_id)
        bareme = get_object_or_404(Bareme, id=bareme_id)

        context['police'] = police
        context['beneficiaire'] = beneficiaire
        context['bareme'] = bareme

        return context


class TarifBeneficiaireView(TemplateView):
    template_name = "grh/tarif_beneficiaire.html"

    #   def get_context_data(self, **kwargs):
    #       context = super().get_context_data(**kwargs)
    #       police_id = kwargs.get('police_id')
    #       beneficiaire_id = kwargs.get('beneficiaire_id')
    #       police = get_object_or_404(Police, id=police_id)
    #       beneficiaire = get_object_or_404(Aliment, id=beneficiaire_id)
    #       context['police'] = police
    #       context['beneficiaire'] = beneficiaire
    #       return context


class DocumentsBeneficiaireView(TemplateView):
    template_name = "grh/documents_beneficiaire.html"
    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        police_id = kwargs.get('police_id')
        beneficiaire_id = kwargs.get('beneficiaire_id')
        police = get_object_or_404(Police, id=police_id)
        beneficiaire = get_object_or_404(Aliment, id=beneficiaire_id)
        documents = Document.objects.filter(aliment=beneficiaire)
        
        #
        etat_police = police.etat_police
        context['etat_police'] = etat_police


        context['police'] = police
        context['beneficiaire'] = beneficiaire
        context['documents'] = documents
        
        return context


class AjouterDocumentBeneficiaireView(TemplateView):
    template_name = "grh/ajouter_document_beneficiaire.html"
    
    def dispatch(self, request, *args, **kwargs):
        police_id = kwargs.get('police_id')
        client = request.user.utilisateur_grh
        self.police = get_object_or_404(Police, id=police_id, client=client)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        police_id = kwargs.get('police_id')
        beneficiaire_id = kwargs.get('beneficiaire_id')
        police = get_object_or_404(Police, id=police_id)
        beneficiaire = get_object_or_404(Aliment, id=beneficiaire_id)
        types_documents = TypeDocument.objects.all()
        
        #
        etat_police = police.etat_police
        context['etat_police'] = etat_police

        context['police'] = police
        context['beneficiaire'] = beneficiaire
        context['types'] = types_documents
        
        return context
    
    def post(self, request, *args, **kwargs):

        beneficiaire_id = kwargs.get('beneficiaire_id')
        police_id = kwargs.get('police_id')
        beneficiaire = get_object_or_404(Aliment, id=beneficiaire_id)
        police = get_object_or_404(Police, id=police_id)
        libelle = request.POST.get('libelle')
        type_document_field = request.POST.get('type_document')
        type_document = TypeDocument.objects.filter(libelle=type_document_field).first()
        fichier = request.FILES.get('fichier')
        confidentialite = request.POST.get('confidentialite')
        commentaire = request.POST.get('commentaire')
        document = Document(
            aliment=beneficiaire,
            police=police,
            nom=libelle,
            type_document=TypeDocument.objects.get(id=type_document.id),
            fichier=fichier,
            confidentialite=confidentialite,
            commentaire=commentaire
        )
        document.save()

        return redirect('grh.beneficiaire_overview', police_id=police_id, beneficiaire_id=beneficiaire_id)


class ImporterPhotoBeneficiaireView(TemplateView):
    template_name = "grh/importer_photo_beneficiaire.html"

    def dispatch(self, request, *args, **kwargs):
        police_id = kwargs.get('police_id')
        client = request.user.utilisateur_grh
        self.police = get_object_or_404(Police, id=police_id, client=client)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        police_id = kwargs.get('police_id')
        beneficiaire_id = kwargs.get('beneficiaire_id')
        police = get_object_or_404(Police, id=police_id, client=self.police.client)
        beneficiaire = get_object_or_404(Aliment, id=beneficiaire_id)

        context['police'] = police
        context['beneficiaire'] = beneficiaire

        return context

    def post(self, request, *args, **kwargs):
        beneficiaire_id = kwargs.get('beneficiaire_id')
        police_id = kwargs.get('police_id')
        beneficiaire = get_object_or_404(Aliment, id=beneficiaire_id)
        fichier = request.FILES.get('photo')

        if fichier:
            file_content = fichier.read()
            file_name = default_storage.get_available_name(f"photos/{beneficiaire_id}_{police_id}_{fichier.name}")
            file_path = default_storage.save(file_name, ContentFile(file_content))
            beneficiaire.photo = file_path
            beneficiaire.save()

        return redirect('grh.beneficiaire_overview', police_id=police_id, beneficiaire_id=beneficiaire_id)


class AjouterMembreFamilleBeneficiaire(TemplateView):
    template_name = "grh/formulaire_ajouter_beneficiaire_famille.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        police_id = kwargs.get('police_id')
        beneficiaire_id = kwargs.get('beneficiaire_id')
        police = get_object_or_404(Police, id=police_id)
        beneficiaire = get_object_or_404(Aliment, id=beneficiaire_id)

        adherents_principaux = getAdherentsPrincipaux(police_id)

        pays = Pays.objects.all()
        civilites = Civilite.objects.exclude(code='STE')  # CIVILITES

        has_conjoint = Aliment.objects.filter(adherent_principal=beneficiaire,
                                              qualite_beneficiaire__libelle='CONJOINT').exists()
        if has_conjoint:
            qualite_benef_types = ['ENFANT', 'ASCENDANT']
        else:
            qualite_benef_types = ['CONJOINT', 'ENFANT', 'ASCENDANT']

        masculin = Genre.MASCULIN
        feminin = Genre.FEMININ
        
        context['police'] = police
        context['beneficiaire'] = beneficiaire
        context['adherents_principaux'] = adherents_principaux
        context['pays'] = pays
        context['civilites'] = civilites
        context['qualites'] = qualite_benef_types
        context['M'] = masculin
        context['F'] = feminin
        
        return context

    def post(self, request, *args, **kwargs):

        beneficiaire_id = kwargs.get('beneficiaire_id')
        adherent = get_object_or_404(Aliment, id=beneficiaire_id)

        police_id = kwargs.get('police_id')
        police = get_object_or_404(Police, id=police_id)
        
        nom = request.POST.get('nom', None)
        prenoms = request.POST.get('prenoms', None)

        civilite_code = request.POST.get('civilite')
        civilite = Civilite.objects.get(code=civilite_code)
        
        date_naissance = request.POST.get('date_naissance', None)

        if date_naissance:
            date_naissance = datetime.strptime(date_naissance, '%Y-%m-%d')

        genre = request.POST.get('genre', None)
        email = request.POST.get('email', None)
        code_postal = request.POST.get('code_postal', None)
        photo = request.FILES.get('photo')
        adresse = request.POST.get('adresse', None)
        ville = request.POST.get('ville', None)

        formule = request.POST.get('formule', None)
        numero_securite_sociale = request.POST.get('numero_securite_sociale', None)

        bureau = adherent.bureau
        aliment_prospect_exists = Prospect.objects.filter(email=adherent.email).exists()
        
        if aliment_prospect_exists:
            aliment_prospect = Prospect.objects.filter(email=adherent.email).first()
        else:
            aliment_prospect = Prospect(
                    nom=adherent.nom,
                    prenoms=adherent.prenoms,
                    email=adherent.email,
                    bureau=adherent.bureau,
                    qualite_beneficiaire=adherent.qualite_beneficiaire,
                    police=police
                )
            aliment_prospect.save()
            aliment_prospect.adherent_principal = aliment_prospect
            aliment_prospect.save()

        new_member_data = {
            'nom': nom,
            'prenoms': prenoms,
            'adherent_principal': aliment_prospect,
            'qualite_beneficiaire': qualite_beneficiaire,
            'civilite': civilite,
            'date_naissance': date_naissance,
            'genre': genre,
            'email': email,
            'code_postal': code_postal,
            'photo': photo,
            'adresse': adresse,
            'ville': ville,
            'bureau': bureau,
            'police': police,
            'aliment_adherent_principal': adherent,
            'numero_securite_sociale': numero_securite_sociale,  # Include numero_securite_sociale

        }
        new_member_famille = Prospect.objects.create(**new_member_data)
        new_member_famille.statut_enrolement = StatutEnrolement.ENCOURS
        new_member_famille.save()

        return redirect('grh.beneficiaire_overview', police_id=police_id, beneficiaire_id=beneficiaire_id)


class AjouterBeneficiaire(TemplateView):
    template_name = "grh/formulaire_ajouter_beneficiaire_police.html"

    def dispatch(self, request, *args, **kwargs):
        # Extract police_id from kwargs
        police_id = kwargs.get('police_id')
        # Get the client associated with the currently logged-in user
        client = request.user.utilisateur_grh
        # Check if the police exists and belongs to the client's associated polices
        self.police = get_object_or_404(Police, id=police_id, client=client)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        police_id = kwargs.get('police_id')
        adherent_principal_id = kwargs.get('adherent_principal_id')

        # Fetch police object; the dispatch method ensures this police is valid
        police = get_object_or_404(Police, id=police_id)

        if adherent_principal_id:
            adherents_principaux = Aliment.objects.filter(id=adherent_principal_id)
        else:
            adherents_principaux = getAdherentsPrincipaux(police_id)

        pays = Pays.objects.all()
        civilites = Civilite.objects.exclude(code='STE')  # CIVILITES

        country_code = self.request.user.utilisateur_grh.bureau.pays.code        #has_conjoint = Aliment.objects.filter(adherent_principal=beneficiaire, ualite_beneficiaire__libelle='CONJOINT').exists()
        #if has_conjoint:
        #    qualite_benef_types = ['ENFANT', 'ASCENDANT']
        #else:
        #    qualite_benef_types = ['CONJOINT', 'ENFANT', 'ASCENDANT']
        qualite_benef_types = ['CONJOINT', 'ENFANT', 'ASCENDANT']
        masculin = Genre.MASCULIN
        feminin = Genre.FEMININ

        context['police'] = police
        context['adherents_principaux'] = adherents_principaux
        context['adherent_principal_id'] = adherent_principal_id
        context['pays'] = pays
        context['civilites'] = civilites
        context['qualites'] = qualite_benef_types
        context['qualites_beneficiaires'] = qualites_beneficiaires
        context['M'] = masculin
        context['F'] = feminin
        context['country_code'] = country_code

        return context

    def post(self, request, *args, **kwargs):

        #beneficiaire_id = kwargs.get('beneficiaire_id')
        police_id = kwargs.get('police_id')
        police = get_object_or_404(Police, id=police_id)

        nom = request.POST.get('nom', None)
        prenoms = request.POST.get('prenoms', None)

        civilite_code = request.POST.get('civilite')
        civilite = Civilite.objects.get(code=civilite_code)

        date_naissance = request.POST.get('date_naissance', None)
        date_affiliation = request.POST.get('date_affiliation', None)

        qualite_beneficiaire_id = request.POST.get('qualite_beneficiaire', None)


        adherent_principal_id = request.POST.get('adherent_principal')
        #adherent_principal = Aliment.objects.filter(id=aliment_adherent_principal_id).first()

        pays_naissance_id = request.POST.get('pays_naissance')
        #pays_naissance = Pays.objects.filter(id=pays_naissance_id).first()
        
        pays_naissance = get_object_or_404(Pays, id=pays_naissance_id) if pays_naissance_id else None
        numero_securite_sociale = request.POST.get('numero_securite_sociale', None)


        if date_naissance:
            date_naissance = datetime.strptime(date_naissance, '%Y-%m-%d')

        if date_affiliation:
            date_affiliation = datetime.strptime(date_affiliation, '%Y-%m-%d')

        genre = request.POST.get('genre', None)

        telephone_mobile = request.POST.get('telephone_mobile', None)
        if telephone_mobile:
            telephone_mobile = format_phone_number(request.POST.get('telephone_mobile'),request.POST.get('selected_country_dial_code_mobile'))

        numero_piece = request.POST.get('numero_piece', None)
        matricule_employe = request.POST.get('matricule_employe', None)
        email = request.POST.get('email', None)
        code_postal = request.POST.get('code_postal', None)
        photo = request.FILES.get('photo')
        adresse = request.POST.get('adresse', None)
        ville = request.POST.get('ville', None)
        pays_residence_id = request.POST.get('pays_residence', None)

        formule = request.POST.get('formule', None)

        bureau = request.user.bureau

        new_member_data = {
            'nom': nom,
            'prenoms': prenoms,
            'adherent_principal_id': adherent_principal_id,
            'qualite_beneficiaire': qualite_beneficiaire,
            'civilite': civilite,
            'date_naissance': date_naissance,
            'date_affiliation': date_affiliation,
            'genre': genre,
            'telephone_mobile': telephone_mobile,
            'numero_piece': numero_piece,
            'matricule_employe': matricule_employe,
            'email': email,
            'code_postal': code_postal,
            'photo': photo,
            'adresse': adresse,
            'ville': ville,
            'pays_naissance': pays_naissance,
            'pays_residence_id': pays_residence_id,
            'bureau': bureau,
            #'police': police,
            'statut_incorporation': StatutIncorporation.ENCOURS,
            'numero_securite_sociale':numero_securite_sociale
        }

        new_aliment_by_grh = Aliment.objects.create(**new_member_data)

        new_aliment_by_grh.save()

        # créer un mouvement d'incorporation en attente
        mouvement = Mouvement.objects.filter(code="DMD-INCORPO-GRH").first()

        #rester sur la même page et afficher le message de succès
        return redirect('grh.police_overview', police_id=police_id)


# ENRÔLEMENT
class Enrolement(TemplateView):
    template_name = "grh/enrolement/enrolement.html"

    def get(self, request, *args, **kwargs):

        campagne_id = kwargs.get('campagne_id')
        uiid = kwargs.get('uiid')

        campagne = get_object_or_404(Campagne, id=campagne_id)

        # NOT OPENED YET
        if campagne.date_debut > timezone.now():
            status = '403'
            campagne.statut = StatutValidite.BROUILLON
            campagne.save()
            error_url = reverse('grh.error_enrolement',
                                kwargs={'campagne_id': campagne_id, 'uiid': uiid, 'status': status})
            return redirect(error_url)

        # EXPIRED
        if campagne.date_fin < timezone.now().replace(hour=0, minute=0, second=0, microsecond=0):
            status = '404'
            campagne.statut = StatutValidite.CLOTURE
            campagne.save()
            error_url = reverse('grh.error_enrolement',
                                kwargs={'campagne_id': campagne_id, 'uiid': uiid, 'status': status})
            return redirect(error_url)

        return super().get(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        campagne_id = kwargs.get('campagne_id')
        uiid = kwargs.get('uiid')
        aliment_id = kwargs.get('aliment_id')

        campagne = get_object_or_404(Campagne, id=campagne_id)

        if aliment_id:
            aliment = get_object_or_404(Aliment, id=aliment_id)
            return redirect(reverse('grh.enrolement_by_aliment', args=[campagne.id, uiid, aliment.id]))
        else:
            return redirect(reverse('grh.enrolement', args=[campagne.id, uiid]))

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        campagne_id = kwargs.get('campagne_id')
        uiid = kwargs.get('uiid')
        aliment_id = kwargs.get('aliment_id')

        if aliment_id:
            aliment = get_object_or_404(Aliment, id=aliment_id)
            context['aliment'] = aliment

        campagne = get_object_or_404(Campagne, id=campagne_id)

        duration = campagne.date_fin - timezone.now()

        days, seconds = max(duration.days, 0), max(duration.seconds, 0)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        duree_expiration_lien = {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
        }

        context['campagne'] = campagne
        context['duree_expiration_lien'] = duree_expiration_lien

        return context


class FormulaireEnrolement(TemplateView):
    template_name = "grh/enrolement/formulaire_enrolement.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        campagne_id = kwargs.get('campagne_id')
        uiid = kwargs.get('uiid')
        prospect_id = kwargs.get('prospect_id')

        aliment_id = kwargs.get('aliment_id')
        if aliment_id:
            aliment = get_object_or_404(Aliment, id=aliment_id)
            context['aliment'] = aliment

        campagne = get_object_or_404(Campagne, id=campagne_id)

        country_code = campagne.created_by.utilisateur_grh.bureau.pays.code

        civilites_list = Civilite.objects.exclude(code='STE')  # CIVILITES
        masculin = Genre.MASCULIN
        feminin = Genre.FEMININ

        context['campagne'] = campagne

        context['country_code'] = country_code
        context['civilites_list'] = civilites_list
        context['M'] = masculin
        context['F'] = feminin

        return context

    def post(self, request, *args, **kwargs):

        campagne_id = kwargs.get('campagne_id')
        uiid = kwargs.get('uiid')
        aliment_id = kwargs.get('aliment_id')

        campagne = get_object_or_404(Campagne, id=campagne_id)

        if 'enregistrer' in request.POST:

            date_entree = request.POST.get('date_entree')
            if date_entree:
                date_entree = datetime.strptime(date_entree, '%Y-%m-%d')

            date_naissance = request.POST.get('date_naissance')
            if date_naissance:
                date_naissance = datetime.strptime(date_naissance, '%Y-%m-%d')

            nom = request.POST.get('nom')
            prenoms = request.POST.get('prenoms')
            civilite_code = request.POST.get('civilite')
            genre = request.POST.get('genre')

            photo = request.FILES.get('photo')
            
            #
            matricule_employe = request.POST.get('matricule_employe')

            qualite_beneficiaire_code = request.POST.get('qualite_beneficiaire')
            email = request.POST.get('email')
            ville = request.POST.get('ville')
            adresse = request.POST.get('adresse')
            code_postal = request.POST.get('code_postal')
            lieu_naissance = request.POST.get('lieu_naissance')

            telephone_mobile = request.POST.get('tel_mobile')
            telephone_fixe = request.POST.get('tel_fixe')

            if telephone_mobile:
                telephone_mobile = format_phone_number(request.POST.get('tel_mobile'),
                                                       request.POST.get('selected_country_dial_code_mobile'))

            if telephone_fixe:
                telephone_fixe = format_phone_number(request.POST.get('tel_fixe'), request.POST.get('selected_country_dial_code_fixe'))

            civilite = Civilite.objects.get(code=civilite_code)  # Fk
            numero_securite_sociale = request.POST.get('numero_securite_sociale')  # Retrieve numero_securite_sociale

            prospect_data = {
                'nom': nom,
                'prenoms': prenoms,
                'date_naissance': date_naissance,
                'lieu_naissance': lieu_naissance,
                'telephone_mobile': telephone_mobile,
                'telephone_fixe': telephone_fixe,
                'civilite': civilite,  # Fk
                'genre': genre,
                'photo': photo,
                'matricule_employe': matricule_employe,
                'email': email,
                'ville': ville,
                'adresse': adresse,
                'code_postal': code_postal,
                'numero_securite_sociale': numero_securite_sociale,  # Include numero_securite_sociale

            }

            if photo:
                file_name = os.path.join('prospects', photo.name)
                default_storage.save(file_name, ContentFile(photo.read()))
                prospect_data['photo'] = file_name

        if aliment_id:
            return redirect(reverse('grh.enrolement_by_aliment', args=[campagne.id, uiid, aliment.id]))
        else:
            return redirect(reverse('grh.enrolement', args=[campagne.id, uiid]))


class ErrorEnrolementView(TemplateView):
    template_name = 'grh/enrolement/error_enrolement.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        campagne_id = kwargs.get('campagne_id')
        #   uiid = kwargs.get('uiid')
        status = kwargs.get('status')

        campagne = get_object_or_404(Campagne, id=campagne_id)

        context['campagne'] = campagne
        context['status'] = status

        return context


# CHANGE BÉNÉFICIAIRE ID
class ChangeBeneficiaireIdView(View):

    def get(self, request, *args, **kwargs):

        selected_beneficiaire_id = request.GET.get('selected_beneficiaire_id')
        request.session['beneficiaire_id'] = selected_beneficiaire_id

        return JsonResponse({'status': 'success'})


# RESET PASSWROD 
class PasswordResetView(PasswordResetView):
    template_name = 'grh/auth/password_reset.html'
    hotp = pyotp.HOTP(settings.OTP_SECRET_KEY, digits=6)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        self.request.session['error'] = None
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        email = self.request.POST.get('email', None)
        try:
            user = User.objects.filter(email=email, utilisateur_grh__isnull=False).first()
            if user:

                code_verification = int(datetime.now().strftime("%Y%m%d%H%M%S"))
                # send otp mail
                send_otp_mail(user.email, self.hotp.at(code_verification))

                self.request.session['email'] = email
                self.request.session['user'] = user.id
                self.request.session['code_verification'] = code_verification
                self.request.session['username'] = user.username

                return redirect('grh.password_reset_otp')

            error_message = "Veuillez utiliser un compte utilisateur valide GRH !"
            context['error'] = error_message
            messages.error(self.request, error_message)
            return self.render_to_response(context)

        except User.DoesNotExist:
            error_message = "Une erreur s'est produite lors de l'envoi du code de verification !"
            context['error'] = error_message
            messages.error(self.request, error_message)
            return self.render_to_response(context)





class PasswordResetOtpView(PasswordResetView):
    template_name = 'grh/auth/verification_code.html'
    url = reverse_lazy('grh.password_reset')

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        self.request.session['error'] = None
        email = self.request.session.get('email', None)
        code_verification = self.request.session.get('code_verification', None)
        if not email or not code_verification:
            return redirect(self.url)

        context['email'] = email
        context['code_verification'] = code_verification
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        otp = self.request.POST.get('code', None)
        code_verification = request.POST.get('code_verification', None)
        # Verification des champs
        if not otp:
            context['error'] = "Ce champ est obligatoire."
            return self.render_to_response(context)

        if not code_verification:
            context['error'] = "Votre code de verification est invalide ou expiré."
            return self.render_to_response(context)

        # Verification du code OTP
        if self.hotp.verify(otp, int(code_verification)):
            return redirect(reverse_lazy('grh.password_reset_form'))
        else:
            context['error'] = "Votre code de verification est invalide ou expiré."
            return self.render_to_response(context)

class PasswordResetFormView(PasswordResetView):
    template_name = 'grh/auth/password_reset_form.html'
    url = reverse_lazy('grh.login')
    url2 = reverse_lazy('grh.password_reset_complete')

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        email = self.request.session.get('email', None)
        code_verification = self.request.session.get('code_verification', None)
        user = self.request.session.get('user', None)
        self.request.session['error'] = None
        if not email or not code_verification or not user:
            self.request.session['error'] = "Votre code de verification est invalide ou expiré."
            return redirect(self.url)

        context['email'] = email
        context['code_verification'] = code_verification
        context['user'] = user
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        password = self.request.POST.get('password', None)
        confirm_password = request.POST.get('confirm_password', None)
        user_id = self.request.session.get('user', None)
        user = User.objects.filter(id=user_id).first()
        # Verification des champs
        if password != confirm_password or not password or not confirm_password:
            context['error'] = "Les mots de passe ne correspondent pas."
            return self.render_to_response(context)

        if not user:
            context['error'] = "Votre code de verification est invalide ou expiré."
            return self.render_to_response(context)

        # Modification du mot de passe
        user.set_password(password)
        user.save()
        # Suppression des sessions
        del self.request.session['email']
        del self.request.session['code_verification']
        del self.request.session['user']
        del self.request.session['error']
        del self.request.session['username']

        return redirect(self.url2)




class PasswordResetDoneView(TemplateView):
    template_name = 'grh/auth/password_reset_done.html'


class PasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'grh/auth/password_reset_complete.html'


# DEMANDES INCORPORATIONS GRH 
class IncorporationsByGrhView(TemplateView):
    template_name = "grh/incorporations_by_grh.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        police_id = kwargs.get('police_id')
        police = get_object_or_404(Police, id=police_id)

        aliments = Aliment.objects.all()

        context['aliments'] = aliments
        context['police'] = police

        #
        etat_police = police.etat_police
        context['etat_police'] = etat_police


        return context





