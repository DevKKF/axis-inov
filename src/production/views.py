# Create your views here.
import datetime
from datetime import timedelta
import json
import os
import re
import uuid

import PyPDF2
import docx
import pdfkit
import pypandoc
from ast import literal_eval
from datetime import datetime as datetimes
from datetime import date
from datetime import datetime, timezone
from django.utils.dateparse import parse_date
from datetime import timedelta
from io import BytesIO
from pprint import pprint
from sqlite3 import Date
from datetime import date
from decimal import Decimal, InvalidOperation
from venv import create

from django.db.models import Max
import locale
from docx import Document
from docx.shared import Inches
from num2words import num2words
from django.templatetags.static import static
from django.views.decorators.http import require_GET
#import pdfkit
from PyPDF2 import PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.utils.safestring import mark_safe

import openpyxl
import pandas as pd
# import qrcode
# import qrcode.image.svg
# from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core import serializers
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.db.models import Sum, Q, ExpressionWrapper, F, DurationField, Max, Case, When, Value
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.cache import never_cache
## INOV API MOBILE
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from docx import Document as WordDocument
# from django_dump_die.middleware import dd
from fpdf import FPDF
from urllib3 import request
from xhtml2pdf import pisa
from datetime import datetime, timezone
from django.utils.timezone import now
from django.utils.html import strip_tags
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction

from configurations.models import Compagnie, MarqueVehicule, Pays, Civilite, Profession, \
    Produit, Formule, GarantieBranche, GarantieFormule, ConditionsAssurance, MoyensTransport, \
    Territorialite, ModeCalcul, Duree, TypeCarosserie, User, Fractionnement, ModeReglement, \
    Regularisation, Bureau, BusinessUnit, TypeCompagnie, Groupe, PosteDommage, TypeSinistre, TypeIntervenant, Responsabilite, Circonstance, \
    Devise, Taxe, BureauTaxe, Apporteur, BaseCalcul, TypeQuittance, NatureQuittance, TypeClient, TypePersonne, Langue, \
    Branche, ParamProduitCompagnie, CategorieVehicule, Banque, Carburant, Usage, Carosserie, GarantieCirconstance, \
    NatureOperation, TypeTarif, Rubrique, Periodicite, \
    AuthGroup, ActionLog, SousRubrique, TypePrefinancement, CompteTresorerie, \
    GroupeInter, TypeFichier

from inov import settings
from production.forms import ContactForm, FilialeForm, AcompteForm, DocumentForm, PoliceForm, PhotoUploadForm
from production.helper_production import create_alimet_helper
from production.models import FormuleRubriquePrefinance, ModePrefinancement, Motif, Mouvement, Client, Police, \
    Acompte, Document, Filiale, AutreRisque, PoliceGarantie, AlimentPolice, PoliceAssureur, Courrier, \
    Contact, Quittance, SecteurActivite, TypeDocument, Statut, FormuleGarantie, MouvementPolice, StatutQuittance, \
    Genre, StatutFamilial, PlacementEtGestion, ModeRenouvellement, CalculTM, ApporteurPolice, TaxePolice, \
    TaxeQuittance, Reglement, OptionYesNo, TypeMajorationContrat, Vehicule, VehiculePolice, Energie, \
    StatutPolice, Operation, PeriodeCouverture, \
    OperationReglement, HistoriquePolice, HistoriqueApporteurPolice, HistoriqueTaxePolice, Marchandise, HistoriqueAliment, \
    HistoriquePoliceGarantie
from production.templatetags.my_filters import money_field, convertir_date_multiformat, supprimer_espaces, convertir_date_jj_mm_aaaa, format_montant, money_format_mille, \
    arrondis_nombre, transformer_statut
from shared.enum import StatutIncorporation, StatutValidite, StatutSinistre, StatutEnrolement, StatutTraitement, \
    StatutReversementCompagnie, StatutValiditeQuittance, Confidentialite
from sinistre.models import Sinistre, DossierSinistre, MouvementSinistre, AlimentPoliceSinistre, Intervenant, SinistreIntervenant, GarantieSinistre, Provision, ReglementSinistre, \
    HistoriqueSinistre, HistoriqueSinistreIntervenant, HistoriqueGarantieSinistre, HistoriqueProvision, HistoriqueAlimentPoliceSinistre
from sinistre.forms import SinistreForm
from comptabilite.models import EncaissementCommission
from django.contrib.auth.models import Group
import traceback
from django.core.files.base import File
from xhtml2pdf import pisa



## INOV API MOBILE
from django.views.decorators.csrf import csrf_exempt


@method_decorator(login_required, name='dispatch')
class DetailsClientView(TemplateView):
    permission_required = "production.view_clients"
    template_name = 'client/index.html'
    model = Client

    def get(self, request, client_id, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)


        clients = Client.objects.filter(id=client_id, bureau=request.user.bureau)
        if clients:
            client = clients.first()

            pprint(client.pays.devise)
            polices = Police.objects.filter(client_id=client_id, statut=StatutPolice.ACTIF, statut_contrat='CONTRAT', statut_validite=StatutValidite.VALIDE).order_by('-id')

            derniere_police = polices.first()

            #les anciennes polices qui un mouvement_police de résiliation
            #anciennes_polices = polices.filter(id__in=select police_id from mouvemet_police where date_debut >=today).exclude(id=derniere_police.id)
            anciennes_polices = polices.filter(
                id__in=MouvementPolice.objects.filter(
                    mouvement__code="RESIL",
                    statut_validite=StatutValidite.VALIDE,
                    #date_effet__gte=datetime.datetime.now(tz=timezone.utc).date(),
                    police_id__in=polices.values_list('id', flat=True)
                ).values_list('police_id', flat=True)
            )

            statut_contrat = "CONTRAT"

            quittances = []
            for police in polices:
                quittances_of_police = Quittance.objects.filter(police_id=police.id)
                quittances.extend(quittances_of_police)

            acomptes = Acompte.objects.filter(client_id=client_id)

            filiales = Filiale.objects.filter(client_id=client_id)

            documents = Document.objects.filter(client_id=client_id)

            contacts = Contact.objects.filter(client_id=client_id)

            pays = Pays.objects.all().order_by('nom')

            types_documents = TypeDocument.objects.filter(is_production=1).order_by('libelle')

            types_prefinancements = TypePrefinancement.objects.filter(statut=Statut.ACTIF).order_by('libelle')

            # pour la creation de police
            branches = Branche.objects.filter(status=True).order_by('nom')
            produits = Produit.objects.all().order_by('nom')
            bureaux = Bureau.objects.all().order_by('nom')
            utilisateurs = None  # User.objects.all().order_by('last_name')
            apporteurs = Apporteur.objects.filter(status=True).order_by('nom')
            fractionnements = Fractionnement.objects.all().order_by('libelle')
            modes_reglements = ModeReglement.objects.all().order_by('libelle')
            regularisations = Regularisation.objects.all().order_by('libelle')
            compagnies = Compagnie.objects.filter(bureau=request.user.bureau, status=True).order_by('nom')
            durees = Duree.objects.all().order_by('libelle')
            devises = Devise.objects.filter(id=client.pays.devise_id).order_by('libelle')
            taxes = Taxe.objects.all().order_by('libelle')
            bureau_taxes = BureauTaxe.objects.filter(bureau_id=client.bureau_id)
            bases_calculs = BaseCalcul.objects.all().order_by('libelle')
            modes_calculs = ModeCalcul.objects.all().order_by('libelle')

            placement_gestion = PlacementEtGestion
            mode_renouvellement = ModeRenouvellement
            calcul_tm = CalculTM
            type_majoration_contrat = TypeMajorationContrat
            # statut_contrat = StatutContrat

            bureaux = Bureau.objects.filter(id=request.user.bureau.id)

            context_perso = {'client': client, 'contacts': contacts, 'polices': polices, 'quittances': quittances,
                             'acomptes': acomptes,
                             'filiales': filiales, 'documents': documents, 'types_documents': types_documents,
                             'branches': branches, 'produits': produits, 'pays': pays,
                             'compagnies': compagnies, 'durees': durees, 'placement_gestion': placement_gestion,
                             'mode_renouvellement': mode_renouvellement,
                             'calcul_tm': calcul_tm,
                             'fractionnements': fractionnements, 'modes_reglements': modes_reglements,
                             'regularisations': regularisations,
                             'devises': devises, 'utilisateurs': utilisateurs, 'bureaux': bureaux, 'taxes': taxes,
                             'bureau_taxes': bureau_taxes,
                             'apporteurs': apporteurs, 'bases_calculs': bases_calculs,
                             'type_majoration_contrat': type_majoration_contrat, 'modes_calculs': modes_calculs,
                             'statut_contrat': statut_contrat,
                             'types_prefinancements': types_prefinancements,
                             'anciennes_polices': anciennes_polices
                             }

            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        else:
            return redirect("clients")


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
def add_contact(request, client_id):
    if request.method == "POST":

        form = ContactForm(request.POST)

        if form.is_valid():

            client_id = request.POST.get('client_id')

            contact = form.save(commit=False)
            contact.client = Client.objects.get(id=client_id)
            contact.save()

            response = {
                'statut': 1,
                'message': _("Enregistrement effectué avec succès !"),
                'data': {
                    'id': contact.pk,
                    'nom': contact.nom,
                    'prenoms': contact.prenoms,
                    'fonction': contact.fonction,
                    'telephone': contact.telephone,
                    'email': contact.email,
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


# modification d'un contact
@login_required
def modifier_contact(request, contact_id):

    contact = Contact.objects.get(id=contact_id)

    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()

            response = {
                'statut': 1,
                'message': "Modification effectuée avec succès !",
                'data': {
                    'id': contact.pk,
                    'nom': contact.nom,
                    'prenoms': contact.prenoms,
                    'fonction': contact.fonction,
                    'telephone': contact.telephone,
                    'email': contact.email,
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

        form = ContactForm()

        context = {
            'contact': contact,
            'form': form,
        }

        return render(request, 'client/modification_contact.html', context)


@login_required
def supprimer_contact(request, contact_id):
    if request.method == "POST":

        contact_id = request.POST.get('contact_id')

        contact = Contact.objects.get(id=contact_id)
        if contact.pk is not None:
            contact.delete()

            response = {
                'statut': 1,
                'message': "Contact supprimé avec succès !",
            }

        else:

            response = {
                'statut': 0,
                'message': "Contact non trouvé !",
            }

        return JsonResponse(response)


@login_required
def add_filiale(request, client_id):
    if request.method == "POST":

        form = FilialeForm(request.POST)

        if form.is_valid():

            client_id = request.POST.get('client_id')

            filiale = form.save(commit=False)
            filiale.client = Client.objects.get(id=client_id)
            filiale.save()

            response = {
                'statut': 1,
                'message': "Enregistrement effectué avec succès !",
                'data': {
                    'id': filiale.pk,
                    'nom': filiale.nom,
                    'adresse': filiale.adresse,
                    'pays': filiale.pays.nom,
                    'ville': filiale.ville,
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


def modifier_filiale(request, filiale_id):
    filiale = Filiale.objects.get(id=filiale_id)

    if request.method == 'POST':
        form = FilialeForm(request.POST, instance=filiale)
        if form.is_valid():
            form.save()

            response = {
                'statut': 1,
                'message': "Modification effectuée avec succès !",
                'data': {
                    'id': filiale.pk,
                    'nom': filiale.nom,
                    'adresse': filiale.adresse,
                    'pays': filiale.pays.nom,
                    'ville': filiale.ville,
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

        filiale = Filiale.objects.get(id=filiale_id)
        pays = Pays.objects.all().order_by('nom')

        form = FilialeForm()

        return render(request, 'client/modification_filiale.html',
                      {'filiale': filiale, 'pays': pays, 'form': form})


def supprimer_filiale(request, filiale_id):
    if request.method == "POST":

        filiale_id = request.POST.get('filiale_id')

        filiale = Filiale.objects.get(id=filiale_id)
        if filiale.pk is not None:
            filiale.delete()

            response = {
                'statut': 1,
                'message': "Filiale supprimée avec succès !",
            }

        else:

            response = {
                'statut': 0,
                'message': "Filiale non trouvée !",
            }

        return JsonResponse(response)


@login_required
def add_document(request, client_id):
    if request.method == "POST":

        form = DocumentForm(request.POST, request.FILES)

        if form.is_valid():

            client = Client.objects.get(id=client_id)
            type_document_id = request.POST.get('type_document')

            document = form.save(commit=False)
            document.client = client
            document.type_document = TypeDocument.objects.get(id=type_document_id)
            document.save()

            pprint("document.fichier")
            pprint(document.fichier.path)

            response = {
                'statut': 1,
                'message': _("Enregistrement effectue avec succes !"),
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
                'message': _("Veuillez renseigner correctement le formulaire !"),
                'errors': form.errors,
            }

            return JsonResponse(response)


@login_required
def handle_uploaded_document(f, filename):
    path_ot_db = '/clients/documents/'
    dirname = settings.MEDIA_URL.replace('/', '') + path_ot_db
    path = os.path.join(dirname)

    if not os.path.exists(path):
        os.makedirs(path)

    with open(dirname + '/' + filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return path_ot_db + '/' + filename


@login_required
def modifier_document(request, document_id):
    document = Document.objects.get(id=document_id)

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)

        if form.is_valid():

            document_update = form.save(commit=False)
            document_update.save()

            response = {
                'statut': 1,
                'message': "Modification effectuée avec succès !",
                'data': {
                    'id': document_update.pk,
                    'nom': document_update.nom,
                    'fichier': '<a href="' + document_update.fichier.url + '"><i class="fa fa-file" title="Aperçu"></i> Afficher</a>',
                    'type_document': document_update.type_document.libelle,
                    'confidentialite': document_update.confidentialite,
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


    else:

        document = Document.objects.get(id=document_id)
        if document.sinistre:
            typedocuments = TypeDocument.objects.filter(is_sinistre=1).order_by('libelle')
        else:
            typedocuments = TypeDocument.objects.filter(is_production=1).order_by('libelle')
        confidentialite = Confidentialite

        form = DocumentForm()

        return render(request, 'client/modification_document.html',
                      {'document': document, 'typedocuments': typedocuments, 'form': form, 'confidentialite':confidentialite})


@login_required
def supprimer_document(request, document_id):
    if request.method == "POST":

        document_id = request.POST.get('document_id')

        document = Document.objects.get(id=document_id)
        if document.pk is not None:
            document.delete()

            response = {
                'statut': 1,
                'message': "Document supprimé avec succès !",
            }

        else:

            response = {
                'statut': 0,
                'message': "Document non trouvé !",
            }

        return JsonResponse(response)


@login_required
def add_acompte(request, client_id):

    if request.method == "POST":

        client_id = request.POST.get('client_id')

        acompte = Acompte(
            credit=request.POST.get('montant', '').replace(' ', ''),
            date_versement=convertir_date_multiformat(request.POST.get('date_versement')),
            periode_debut=convertir_date_multiformat(request.POST.get('periode_debut')),
            periode_fin=convertir_date_multiformat(request.POST.get('periode_fin')),
            solde=request.POST.get('montant', '').replace(' ', ''),
        )
        acompte.client = Client.objects.get(id=client_id)
        acompte.save()

        response = {
            'statut': 1,
            'message': "Enregistrement effectué avec succès !",
            'data': {
                'id': acompte.pk,
                'montant': acompte.credit,
                'date_versement': acompte.date_versement,
            }
        }

        return JsonResponse(response)


@login_required
def modifier_acompte(request, acompte_id):
    acompte = Acompte.objects.get(id=acompte_id)

    if request.method == 'POST':

        Acompte.objects.filter(id=acompte_id).update(
            credit=request.POST.get('montant', '').replace(' ', ''),
            date_versement=convertir_date_multiformat(request.POST.get('date_versement')),
            periode_debut=convertir_date_multiformat(request.POST.get('periode_debut')),
            periode_fin=convertir_date_multiformat(request.POST.get('periode_fin')),
            solde=request.POST.get('montant', '').replace(' ', ''),
        )

        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': acompte.pk,
                'nom': acompte.credit,
                'date_versement': acompte.date_versement,
            }
        }

        return JsonResponse(response)

    else:

        return render(request, 'client/modification_acompte.html',
                      {'acompte': acompte})


@login_required
def supprimer_acompte(request, acompte_id):
    if request.method == "POST":

        acompte_id = request.POST.get('acompte_id')
        print("acompte id : ", acompte_id)
        acompte = Acompte.objects.get(id=acompte_id)
        if acompte.pk is not None:

            acompte.delete()

            response = {
                'statut': 1,
                'message': "Acompte supprimé avec succès !",
            }

            return JsonResponse(response)

        else:

            response = {
                'statut': 0,
                'message': "Acompte non trouvé !",
            }

        return JsonResponse(response)


# ajout de police
@transaction.atomic  # open a transaction
@login_required
def add_police(request, client_id):
    taxes = request.COOKIES.get('taxes')
    aliments = request.session.get('aliments', [])
    client = Client.objects.get(id=client_id)

    if request.method == 'POST':

        form = PoliceForm(request.POST)

        if form.is_valid():

            produit = Produit.objects.get(id=request.POST.get('produit'))
            compagnie = Compagnie.objects.get(id=request.POST.get('compagnie'))
            typecompagnie_prin = TypeCompagnie.objects.get(id=1)
            typecompagnie = request.POST.get('typecompagnie')
            compagnie_id = request.POST.get('compagnie_id')
            formule_id = request.POST.get('formule')
            commercial_id = request.POST.get('commercial_id')
            gestionnaire_id = request.POST.get('gestionnaire_id')
            production_id = request.POST.get('production_id')
            numero = request.POST.get('numero')
            apporteur = request.POST.get('apporteur')
            garantie_reponse = request.POST.get('garantie')
            date_debut_effet = request.POST.get('date_debut_effet')
            date_fin_effet = request.POST.get('date_fin_effet')
            date_fin_police = request.POST.get('date_fin_police')
            preavis_de_resiliation = request.POST.get('preavis_de_resiliation')
            mode_renouvellement = request.POST.get('mode_renouvellement')
            fractionnement_id = request.POST.get('fractionnement')
            mode_reglement_id = request.POST.get('mode_reglement')
            regularisation_id = request.POST.get('regularisation')
            date_prochaine_facture = request.POST.get('date_prochaine_facture')
            participation = request.POST.get('participation')
            taux_participation = request.POST.get('taux_participation').replace(' ', '')
            if taux_participation == "": taux_participation = 0
            prime_ht = request.POST.get('prime_ht').replace(' ', '')
            if prime_ht == "": prime_ht = 0
            prime_ttc = request.POST.get('prime_ttc').replace(' ', '')
            if prime_ttc == "": prime_ttc = 0
            taxe = request.POST.get('taxe').replace(' ', '')
            if taxe == "": taxe = 0
            autres_taxes = request.POST.get('autres_taxes').replace(' ', '')
            if autres_taxes == "": autres_taxes = 0
            taux_com_courtage = request.POST.get('taux_com_courtage').replace(' ', '')
            if taux_com_courtage == "": taux_com_courtage = 0
            taux_com_courtage_terme = request.POST.get('taux_com_courtage_terme').replace(' ', '')
            if taux_com_courtage_terme == "": taux_com_courtage_terme = 0
            commission_courtage = request.POST.get('commission_courtage').replace(' ', '')
            if commission_courtage == "": commission_courtage = 0
            commission_intermediaires = request.POST.get('commission_intermediaire').replace(' ', '')
            if commission_intermediaires == "": commission_intermediaires = 0
            cout_police_compagnie = request.POST.get('cout_police_compagnie').replace(' ', '')
            if cout_police_compagnie == "": cout_police_compagnie = 0
            cout_police_courtier = request.POST.get('cout_police_courtier').replace(' ', '')
            if cout_police_courtier == "": cout_police_courtier = 0
            calcul_tm = request.POST.get('calcul_tm')
            devise_id = request.POST.get('devise')
            ar_libelle = request.POST.get('risque_name')
            ar_description = request.POST.get('risque_description')
            date_entree = request.POST.get('date_entree')
            date_sortie = request.POST.get('date_sortie')
            mis_en_circulation = request.POST.get('date_mise_circulation')

            num_certificat = request.POST.get('num_certificat')
            num_fact_fournisseur = request.POST.get('num_fact_fournisseur')
            ref_dai = request.POST.get('ref_dai')
            date_commande = request.POST.get('date_commande')
            nombre_colis = request.POST.get('nombre_colis')
            poids_brut = request.POST.get('poids_brut')
            plein_souscription = request.POST.get('plein_souscription')
            immatriculation_march = request.POST.get('immatriculation_march')
            pavillon_cie_prest = request.POST.get('pavillon_cie_prest')
            destination = request.POST.get('destination')
            lieu_transit_transbordement = request.POST.get('lieu_transit_transbordement')
            date_emmision_certificat = request.POST.get('date_emmision_certificat')
            date_sortie_march = request.POST.get('date_sortie_march')
            num_commande = request.POST.get('num_commande')
            marchandises_description = request.POST.get('marchandises_description')
            poids_net = request.POST.get('poids_net')
            valeur_assuree = supprimer_espaces(request.POST.get('valeur_assuree'))
            marque_modele_type = request.POST.get('marque_modele_type')
            debut_voyage = request.POST.get('debut_voyage')
            lieu_depart = request.POST.get('lieu_depart')
            nom_commissaire = request.POST.get('nom')
            telephone_commissaire = request.POST.get('telephone')
            code_commissaire = request.POST.get('code')
            adresse_commissaire = request.POST.get('adresse')
            courriel_commissaire = request.POST.get('email')
            taux_risque_ordinaire = request.POST.get('taux_risque_ordinaire')
            taux_risque_guerre = request.POST.get('taux_risque_guerre')
            taux_supprime = request.POST.get('taux_supprime')
            taux_reduction_commerciale = supprimer_espaces(request.POST.get('taux_reduction_commerciale'))
            taux_taxe = supprimer_espaces(request.POST.get('taux_taxe'))
            accessoires = supprimer_espaces(request.POST.get('accessoires'))
            autres_frais = supprimer_espaces(request.POST.get('autres_frais'))
            prime_risque_ordinaire = supprimer_espaces(request.POST.get('prime_risque_ordinaire'))
            prime_risque_guerre = supprimer_espaces(request.POST.get('prime_risque_guerre'))
            prime_supprime = supprimer_espaces(request.POST.get('prime_supprime'))
            prime_brut = supprimer_espaces(request.POST.get('prime_brut'))
            prime_reduction = supprimer_espaces(request.POST.get('prime_reduction'))
            total_taxe = supprimer_espaces(request.POST.get('total_taxe'))
            prime_ttc_mar = supprimer_espaces(request.POST.get('prime_ttc_mar'))
            moyens_transport_id = request.POST.get('moyens_transport_id')
            conditions_assurance_id = request.POST.get('conditions_assurance_id')

            statut_contrat = request.POST.get('statut_contrat')
            statut_contrat = "CONTRAT"

            police_created = Police(
                bureau_id=client.bureau_id,
                client_id=client_id,
                devise_id=devise_id,
                created_by=request.user,
                produit_id=produit.id,
                commercial_id=commercial_id,
                gestionnaire_id=gestionnaire_id,
                production_id=production_id,
                numero=numero,
                date_souscription=datetime.now(),
                date_debut_effet=date_debut_effet if date_debut_effet else None,
                date_fin_effet=date_fin_effet if date_fin_effet else None,
                date_fin_police=date_fin_police if date_fin_police else None,
                preavis_de_resiliation=preavis_de_resiliation,
                date_prochaine_facture=date_prochaine_facture if date_prochaine_facture else None,
                participation=participation,
                taux_participation=taux_participation,
                statut_contrat = statut_contrat,
                statut = Statut.ACTIF,
            )
            police_created.save()

            code_bureau = request.user.bureau.code
            police_created.numero_provisoire = str(code_bureau) + 'P' + str(Date.today().year)[-2:] + str(
                police_created.pk).zfill(6)
            if police_created.numero == "":
                police_created.numero = police_created.numero_provisoire

            police_created.save()

            police = Police.objects.get(id=police_created.pk)

            # enregistrer les intermédiaires si existants
            intermediaires = request.POST.getlist('intermediaires')
            base_calcul_taux_retrocession = request.POST.getlist('base_calcul_taux_retrocession')
            taux_com_affaire_nouvelle = request.POST.getlist('taux_com_affaire_nouvelle')
            taux_com_renouvelement = request.POST.getlist('taux_com_renouvelement')

            pprint('len(intermediaires) : ' + str(len(intermediaires)))
            if len(intermediaires) > 0:  # pourquoi j'ai mis 3: à vérifier, en attendant je met à 0
                i = 0
                for apporteur_id in intermediaires:
                    apporteur_id = int('0' + apporteur_id)
                    base_calcul = int('0' + base_calcul_taux_retrocession[i])
                    taux_com_an = float('0' + taux_com_affaire_nouvelle[i])
                    taux_com_renew = float('0' + taux_com_renouvelement[i])

                    pprint({'apporteur_id': apporteur_id, 'base_calcul': base_calcul, 'taux_com_an': taux_com_an,
                            'taux_com_renew': taux_com_renew})

                    # Insérer la ligne si renseignée
                    if apporteur_id > 0 and base_calcul > 0 and (taux_com_an > 0 or taux_com_renew > 0):
                        ApporteurPolice.objects.create(police_id=police.id, apporteur_id=apporteur_id,
                                                       base_calcul_id=base_calcul,
                                                       taux_com_affaire_nouvelle=taux_com_an,
                                                       taux_com_renouvellement=taux_com_renew, ).save()
                    i += 1

            # enregistrer les autres taxes
            taxes = request.COOKIES.get('taxes')
            print('Cookies : ', taxes)
            if taxes:
                taxes = json.loads(taxes)

                for taxe in taxes:
                    taxe = list(taxe.values())
                    taxe_id = taxe[0]
                    taxe_montant = taxe[1]

                    # Insérer la ligne
                    TaxePolice.objects.create(police_id=police.id, taxe_id=taxe_id, montant=taxe_montant).save()

            # créer une ligne dans période de couverture
            periode_couverture = PeriodeCouverture(
                police_id=police.id,
                date_debut_effet=date_debut_effet,
                date_fin_effet=date_fin_effet if date_fin_effet else None,
            )
            periode_couverture.save()

            historique_police_created = HistoriquePolice(
                police_id=police.id,
                bureau_id=client.bureau_id,
                client_id=client_id,
                produit_id=produit.id,
                commercial_id=commercial_id,
                gestionnaire_id=gestionnaire_id,
                numero=police.numero,
                apporteur=apporteur,
                garantie=garantie_reponse,
                date_souscription=datetime.now(),
                date_debut_effet=police.date_debut_effet,
                date_fin_effet=date_fin_effet if date_fin_effet else None,
                date_fin_police=date_fin_police if date_fin_police else None,
                preavis_de_resiliation=preavis_de_resiliation,
                mode_renouvellement=mode_renouvellement,
                fractionnement_id=fractionnement_id,
                mode_reglement_id=mode_reglement_id,
                regularisation_id=regularisation_id,
                date_prochaine_facture=date_prochaine_facture if date_prochaine_facture else None,
                participation=participation,
                taux_participation=taux_participation,
                taxe=taxe,
                prime_ht=prime_ht,
                prime_ttc=prime_ttc,
                autres_taxes=autres_taxes,
                taux_com_courtage=taux_com_courtage,
                taux_com_courtage_terme=taux_com_courtage_terme,
                commission_courtage=commission_courtage,
                commission_intermediaires=commission_intermediaires,
                cout_police_compagnie=cout_police_compagnie,
                cout_police_courtier=cout_police_courtier,
                calcul_tm=calcul_tm,
                devise_id=devise_id,
                statut_contrat=statut_contrat,
                statut=Statut.ACTIF,
                date_du_jour=datetime.now(),
                created_by=request.user
            )
            historique_police_created.save()

            dernier_historique = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()

            # Initialiser une liste pour les garanties
            garanties = []
            # Parcourir les données POST pour trouver les champs de garantie
            for key, value in request.POST.items():
                if key.startswith('garantie_'):
                    garantie_id = key.split('_')[1]
                    franchise = request.POST.get(f'franchise_{garantie_id}', '0')
                    capital = request.POST.get(f'capital_{garantie_id}', '0')

                    # Ajouter les données extraites à la liste
                    garanties.append({
                        'garantie_id': garantie_id,
                        'franchise': franchise,
                        'capital': capital,
                    })

            print("Garantie transmis", garanties)
            # Enregistrer chaque garantie de la police
            for garantie in garanties:
                franchise = garantie['franchise'].replace(' ', '')
                capital = garantie['capital'].replace(' ', '')

                print("id garantie : ", garantie['garantie_id'])
                print("franchise garantie : ", franchise)
                print("capital garantie : ", capital)

                police_garantie = PoliceGarantie(
                    client_id=client_id,
                    police_id=police.id,
                    created_by=request.user,
                    garantie_id=garantie['garantie_id'],
                    formule_id=formule_id,
                    franchise=franchise if franchise else None,
                    capital=capital if capital else None,
                )
                police_garantie.save()


            police_assureur = PoliceAssureur(
                client_id=client_id,
                historique_police_id=dernier_historique.id,
                type_compagnie_id=typecompagnie_prin.id,
                compagnie_id=compagnie.id,
                date_creation=datetime.now(),
                created_by=request.user
            )
            police_assureur.save()

            #Si type_compagnie est choisi avec une autre compagnie choisie
            if typecompagnie and compagnie_id:
                police_assureur_autre = PoliceAssureur(
                    client_id=client_id,
                    historique_police_id=dernier_historique.id,
                    type_compagnie_id=typecompagnie,
                    compagnie_id=compagnie_id,
                    date_creation=datetime.now(),
                    created_by=request.user
                )
                police_assureur_autre.save()

            # créer une ligne de mouvement_police avec le mouvement affaire nouvelle et le motif affaire nouvelle
            mp = MouvementPolice()
            mp.police = police
            mp.mouvement = Mouvement.objects.get(code='AN')
            mp.motif = Motif.objects.get(code='AN')
            mp.date_effet = dernier_historique.date_debut_effet
            mp.date_fin_periode_garantie = dernier_historique.date_fin_effet if dernier_historique.date_fin_effet else None
            mp.save()

            # TODO MISE EN PLACE DE LA PARTIE ALIMENT DE LA POLICE
            produit_code = Produit.objects.filter(id=request.POST.get('produit')).first()
            if produit_code.code == "10001":
                print("Création police avec mono-véhicule")
                vehicule_existant = Vehicule.objects.filter(numero_immatriculation=request.POST.get('immatriculation')).first()

                if vehicule_existant:
                    if date_entree:
                        date_entree_conversion = datetime.strptime(date_entree, '%Y-%m-%d').date()

                    if (vehicule_existant.date_sortie and date_entree_conversion) and date_entree_conversion > vehicule_existant.date_sortie:

                        aliment_police = AlimentPolice(
                            vehicule_id = vehicule_existant.id,
                            usage_id=request.POST.get('usage_id'),
                            historique_police_id=dernier_historique.id,
                            police_id=police.id,
                            created_by=request.user,
                            numero_parc=request.POST.get('num_parc'),
                            proprietaire=request.POST.get('proprietaire'),
                            conducteur=request.POST.get('conducteur'),
                            valeur_actuelle=supprimer_espaces(request.POST.get('valeur_actuelle', '')),
                            date_mis_en_circulation=mis_en_circulation if mis_en_circulation else None,
                            date_entree=date_entree if date_entree else None,
                            date_sortie=date_sortie if date_sortie else None,
                            date_liaison = datetime.now(),
                            commentaire = request.POST.get('commentaire'),
                            statut = Statut.ACTIF
                        )
                        aliment_police.save()

                    else:

                        response = {
                            'statut': 0,
                            'message': "Ce véhicule est déjà lié à une police et sa date de sortie n'est pas encore connue à ce jour.",
                            'data': {
                                'vehicule': vehicule_existant.numero_immatriculation,
                                'produit': police.produit.nom,
                            }
                        }
                        return JsonResponse(response)
                else:

                    vehicule_created = Vehicule(
                        categorie_vehicule_id=request.POST.get('categorie_id'),
                        carburant_id=request.POST.get('carburant_id'),
                        carosserie_id=request.POST.get('carosserie_id'),
                        numero_immatriculation=request.POST.get('immatriculation'),
                        numero_immat_provisoire=request.POST.get('immatriculation_provisioire'),
                        numero_serie=request.POST.get('num_serie'),
                        marque=request.POST.get('marque'),
                        modele=request.POST.get('modele'),
                        places_assises=request.POST.get('places_assises'),
                        valeur_neuve=supprimer_espaces(request.POST.get('valeur_neuve', '')),
                        puissance=request.POST.get('puissance_fiscale'),
                        poids_a_vide=request.POST.get('poids_a_vide'),
                        poids_a_charge=request.POST.get('poid_tac')
                    )
                    vehicule_created.save()

                    vehicule = Vehicule.objects.get(id=vehicule_created.pk)

                    aliment_police = AlimentPolice(
                        vehicule_id=vehicule.id,
                        usage_id=request.POST.get('usage_id'),
                        historique_police_id=dernier_historique.id,
                        police_id=police.id,
                        created_by=request.user,
                        numero_parc=request.POST.get('num_parc'),
                        proprietaire=request.POST.get('proprietaire'),
                        conducteur=request.POST.get('conducteur'),
                        valeur_actuelle=supprimer_espaces(request.POST.get('valeur_actuelle', '')),
                        date_mis_en_circulation=mis_en_circulation if mis_en_circulation else None,
                        date_entree=date_entree if date_entree else None,
                        date_sortie=date_sortie if date_sortie else None,
                        date_liaison=datetime.now(),
                        commentaire=request.POST.get('commentaire'),
                        statut=Statut.ACTIF
                    )
                    aliment_police.save()

            elif produit_code.code == "10002":
                print("Création police avec flotte-auto")
                # Récupérer les aliments de la session
                aliments_en_session = request.session.get('aliments', [])

                if aliments_en_session:
                    for aliment in aliments_en_session:
                        # Conversion des dates si nécessaire
                        date_entree = aliment.get('date_entree')
                        date_sortie = aliment.get('date_sortie')
                        mis_en_circulation = aliment.get('mis_en_circulation')

                        #Récupéaration de la catégorie
                        categorie = CategorieVehicule.objects.filter(libelle=aliment.get('T_categorie_id')).first()
                        energie = Carburant.objects.filter(code=aliment.get('energie')).first()

                        if date_entree:
                            date_entree = convertir_date_multiformat(date_entree)
                        if date_sortie:
                            date_sortie = convertir_date_multiformat(date_sortie)
                        if mis_en_circulation:
                            mis_en_circulation = convertir_date_multiformat(mis_en_circulation)

                        vehicule_existant = Vehicule.objects.filter(numero_immatriculation=aliment.get('immat')).first()

                        if vehicule_existant:
                            if vehicule_existant.date_sortie and date_entree > vehicule_existant.date_sortie:
                                aliment_police = AlimentPolice(
                                    vehicule_id=vehicule_existant.id,
                                    usage_id=request.POST.get('T_usage_id'),
                                    historique_police_id=dernier_historique.id,
                                    police_id=police.id,
                                    created_by=request.user,
                                    numero_parc=aliment.get('num_parc'),
                                    proprietaire=aliment.get('proprietaire'),
                                    conducteur=aliment.get('conducteur'),
                                    valeur_actuelle=supprimer_espaces(aliment.get('valeur_actuelle', '')),
                                    date_mis_en_circulation=mis_en_circulation if mis_en_circulation else None,
                                    date_entree=date_entree if date_entree else None,
                                    date_sortie=date_sortie if date_sortie else None,
                                    date_liaison=datetime.now(),
                                    commentaire=aliment.get('comment'),
                                    statut=Statut.ACTIF
                                )
                                aliment_police.save()

                        else:
                            vehicule_created = Vehicule(
                                categorie_vehicule_id=categorie.id if categorie else None,
                                carburant_id=energie.id if energie else None,
                                carosserie_id=aliment.get('T_carosserie_id'),
                                numero_immatriculation=aliment.get('immat'),
                                numero_immat_provisoire=aliment.get('immat_prov'),
                                numero_serie=aliment.get('num_serie'),
                                marque=aliment.get('marque'),
                                modele=aliment.get('modele'),
                                places_assises=aliment.get('places_assises'),
                                valeur_neuve=supprimer_espaces(aliment.get('valeur_neuve', '')),
                                puissance=aliment.get('puissance'),
                                poids_a_vide=aliment.get('poids_a_vide'),
                                poids_a_charge=aliment.get('poids_a_charge')
                            )
                            vehicule_created.save()

                            vehicule = Vehicule.objects.get(id=vehicule_created.pk)

                            aliment_police = AlimentPolice(
                                vehicule_id=vehicule.id,
                                usage_id=aliment.get('T_usage_id'),
                                historique_police_id=dernier_historique.id,
                                police_id=police.id,
                                created_by=request.user,
                                numero_parc=aliment.get('num_parc'),
                                proprietaire=aliment.get('proprietaire'),
                                conducteur=aliment.get('conducteur'),
                                valeur_actuelle=supprimer_espaces(aliment.get('valeur_actuelle', '')),
                                date_mis_en_circulation=mis_en_circulation if mis_en_circulation else None,
                                date_entree=date_entree if date_entree else None,
                                date_sortie=date_sortie if date_sortie else None,
                                date_liaison=datetime.now(),
                                commentaire=aliment.get('comment'),
                                statut=Statut.ACTIF
                            )
                            aliment_police.save()

                aliments = request.session.get('aliments', None)
                # Vider les aliements enregistrer en session
                if 'aliments' in request.session:
                    del request.session['aliments']

                print("Aliment transmis :", aliments)

            elif produit_code.code in ["50001", "50002"]:
                print("Création police avec marchandise")
                marchandise_created = Marchandise(
                    moyens_transport_id = moyens_transport_id,
                    conditions_assurance_id = conditions_assurance_id,
                    devise_id = devise_id,
                    num_certificat = num_certificat,
                    num_fact_fournisseur = num_fact_fournisseur,
                    ref_dai = ref_dai,
                    date_commande = date_commande if date_commande else None,
                    nombre_colis = nombre_colis,
                    poids_brut = poids_brut,
                    plein_souscription = plein_souscription,
                    immatriculation = immatriculation_march,
                    pavillon_cie_prest = pavillon_cie_prest,
                    destination = destination,
                    lieu_transit_transbordement = lieu_transit_transbordement,
                    date_emmision_certificat = date_emmision_certificat if date_emmision_certificat else None,
                    date_sortie = date_sortie_march if date_sortie_march else None,
                    num_commande = num_commande,
                    marchandises_description = marchandises_description,
                    poids_net = poids_net,
                    valeur_assuree = valeur_assuree if valeur_assuree else 0,
                    marque_modele_type = marque_modele_type,
                    debut_voyage = debut_voyage if debut_voyage else None,
                    lieu_depart = lieu_depart,
                    nom_commissaire = nom_commissaire,
                    telephone_commissaire = telephone_commissaire,
                    code_commissaire = code_commissaire,
                    adresse_commissaire = adresse_commissaire,
                    courriel_commissaire = courriel_commissaire,
                    taux_risque_ordinaire = taux_risque_ordinaire if taux_risque_ordinaire else 0,
                    taux_risque_guerre = taux_risque_guerre if taux_risque_guerre else 0,
                    taux_supprime = taux_supprime if taux_supprime else 0,
                    taux_taxe = taux_taxe if taux_taxe else 0,
                    taux_reduction_commerciale = taux_reduction_commerciale if taux_reduction_commerciale else 0,
                    accessoires = accessoires if accessoires else 0,
                    autres_frais = autres_frais if autres_frais else 0,
                    prime_risque_ordinaire = prime_risque_ordinaire if prime_risque_ordinaire else 0,
                    prime_risque_guerre = prime_risque_guerre if prime_risque_guerre else 0,
                    prime_supprime = prime_supprime if prime_supprime else 0,
                    prime_brut = prime_brut if prime_brut else 0,
                    prime_reduction=prime_reduction if prime_reduction else 0,
                    total_taxe = total_taxe if total_taxe else 0,
                    prime_ttc_mar = prime_ttc_mar if prime_ttc_mar else 0,
                    date_liaison=datetime.now(),
                    created_by=request.user,
                    statut=Statut.ACTIF
                )
                marchandise_created.save()

                marchandise = Marchandise.objects.get(id=marchandise_created.pk)

                aliment_police = AlimentPolice(
                    marchandise_id=marchandise.id,
                    historique_police_id=dernier_historique.id,
                    police_id=police.id,
                    created_by=request.user,
                    date_liaison=datetime.now(),
                    statut=Statut.ACTIF
                )
                aliment_police.save()

            else:
                print("Création police avec autres-risques")
                autre_risque_created = AutreRisque(
                    created_by = request.user,
                    libelle = ar_libelle,
                    description = ar_description,
                    date_liaison=datetime.now(),
                    date_du_jour=datetime.now(),
                    statut = Statut.ACTIF
                )
                autre_risque_created.save()

                autre_risque = AutreRisque.objects.get(id=autre_risque_created.pk)

                aliment_police = AlimentPolice(
                    autre_risque_id=autre_risque.id,
                    historique_police_id=dernier_historique.id,
                    police_id=police.id,
                    created_by=request.user,
                    date_liaison=datetime.now(),
                    statut=Statut.ACTIF
                )
                aliment_police.save()

            response = {
                'statut': 1,
                'message': "Police enregistrée avec succès !",
                'data': {
                    'id': police.pk,
                    'numero': police.numero,
                    'produit': police.produit.nom,
                    'prime_ht': dernier_historique.prime_ht,
                    'prime_ttc': dernier_historique.prime_ttc,
                    'commission_courtage': dernier_historique.commission_courtage,
                    'date_debut_effet': dernier_historique.date_debut_effet,
                    'date_fin_effet': dernier_historique.date_fin_effet,
                    'statut': police.statut,
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


# modification de police
@transaction.atomic  # open a transaction
@login_required
def modifier_police(request, police_id):

    if request.method == 'POST':
        # Récupérer la police à mettre à jour
        police_old = Police.objects.get(id=police_id)

        produit_id = request.POST.get('produit')
        police_produit_id = request.POST.get('police_produit_id')

        produit = ''
        if produit_id:
            produit = Produit.objects.filter(id=produit_id).first()
        if police_produit_id:
            produit = Produit.objects.filter(id=police_produit_id).first()

        compagnie = Compagnie.objects.get(id=request.POST.get('compagnie'))
        typecompagnie_prin = TypeCompagnie.objects.get(id=1)
        typecompagnie = request.POST.get('typecompagnie')
        compagnie_id = request.POST.get('compagnie_id')
        formule_id = request.POST.get('formule')
        numero = request.POST.get('numero')
        commercial_id = request.POST.get('commercial_id')
        gestionnaire_id = request.POST.get('gestionnaire_id')
        production_id = request.POST.get('production_id')
        apporteur = request.POST.get('apporteur')
        garantie_reponse = request.POST.get('garantie')
        date_debut_effet = request.POST.get('date_debut_effet')
        date_fin_effet = request.POST.get('date_fin_effet')
        date_fin_police = request.POST.get('date_fin_police')
        preavis_de_resiliation = request.POST.get('preavis_de_resiliation')
        mode_renouvellement = request.POST.get('mode_renouvellement')
        fractionnement_id = request.POST.get('fractionnement')
        mode_reglement_id = request.POST.get('mode_reglement')
        regularisation_id = request.POST.get('regularisation')
        date_prochaine_facture = request.POST.get('date_prochaine_facture')
        participation = request.POST.get('participation')
        taux_participation = request.POST.get('taux_participation').replace(' ', '')
        if taux_participation == "": taux_participation = 0
        prime_ht = request.POST.get('prime_ht').replace(' ', '')
        if prime_ht == "": prime_ht = 0
        prime_ttc = request.POST.get('prime_ttc').replace(' ', '')
        if prime_ttc == "": prime_ttc = 0
        taxe = request.POST.get('taxe').replace(' ', '')
        #if taxe == "": taxe = 0
        autres_taxes = request.POST.get('autres_taxes').replace(' ', '')
        #if autres_taxes == "": autres_taxes = 0
        taux_com_courtage = request.POST.get('taux_com_courtage').replace(' ', '')
        if taux_com_courtage == "": taux_com_courtage = 0
        taux_com_courtage_terme = request.POST.get('taux_com_courtage_terme').replace(' ', '')
        if taux_com_courtage_terme == "": taux_com_courtage_terme = 0
        commission_courtage = request.POST.get('commission_courtage').replace(' ', '')
        if commission_courtage == "": commission_courtage = 0
        commission_intermediaires = request.POST.get('commission_intermediaire').replace(' ', '')
        if commission_intermediaires == "": commission_intermediaires = 0
        cout_police_compagnie = request.POST.get('cout_police_compagnie').replace(' ', '')
        if cout_police_compagnie == "": cout_police_compagnie = 0
        cout_police_courtier = request.POST.get('cout_police_courtier').replace(' ', '')
        if cout_police_courtier == "": cout_police_courtier = 0
        calcul_tm = request.POST.get('calcul_tm')
        devise_id = request.POST.get('devise')

        ar_libelle = request.POST.get('risque_name')
        ar_description = request.POST.get('risque_description')
        date_entree = request.POST.get('date_entree')
        date_sortie = request.POST.get('date_sortie')
        mis_en_circulation = request.POST.get('date_mise_circulation')

        num_certificat = request.POST.get('num_certificat')
        num_fact_fournisseur = request.POST.get('num_fact_fournisseur')
        ref_dai = request.POST.get('ref_dai')
        date_commande = request.POST.get('date_commande')
        nombre_colis = request.POST.get('nombre_colis')
        poids_brut = request.POST.get('poids_brut')
        plein_souscription = request.POST.get('plein_souscription')
        immatriculation_march = request.POST.get('immatriculation_march')
        pavillon_cie_prest = request.POST.get('pavillon_cie_prest')
        destination = request.POST.get('destination')
        lieu_transit_transbordement = request.POST.get('lieu_transit_transbordement')
        date_emmision_certificat = request.POST.get('date_emmision_certificat')
        date_sortie_march = request.POST.get('date_sortie_march')
        num_commande = request.POST.get('num_commande')
        marchandises_description = request.POST.get('marchandises_description')
        poids_net = request.POST.get('poids_net')
        valeur_assuree = supprimer_espaces(request.POST.get('valeur_assuree', ''))
        marque_modele_type = request.POST.get('marque_modele_type')
        debut_voyage = request.POST.get('debut_voyage')
        lieu_depart = request.POST.get('lieu_depart')
        nom_commissaire = request.POST.get('nom')
        telephone_commissaire = request.POST.get('telephone')
        code_commissaire = request.POST.get('code')
        adresse_commissaire = request.POST.get('adresse')
        courriel_commissaire = request.POST.get('email')
        taux_risque_ordinaire = request.POST.get('taux_risque_ordinaire', '')
        taux_risque_guerre = request.POST.get('taux_risque_guerre', '')
        taux_supprime = request.POST.get('taux_supprime', '')
        taux_reduction_commerciale = supprimer_espaces(request.POST.get('taux_reduction_commerciale', ''))
        taux_taxe = supprimer_espaces(request.POST.get('taux_taxe', ''))
        accessoires = supprimer_espaces(request.POST.get('accessoires', ''))
        autres_frais = supprimer_espaces(request.POST.get('autres_frais', ''))
        prime_risque_ordinaire = supprimer_espaces(request.POST.get('prime_risque_ordinaire', ''))
        prime_risque_guerre = supprimer_espaces(request.POST.get('prime_risque_guerre', ''))
        prime_supprime = supprimer_espaces(request.POST.get('prime_supprime', ''))
        prime_brut = supprimer_espaces(request.POST.get('prime_brut', ''))
        prime_reduction = supprimer_espaces(request.POST.get('prime_reduction', ''))
        total_taxe = supprimer_espaces(request.POST.get('total_taxe', ''))
        prime_ttc_mar = supprimer_espaces(request.POST.get('prime_ttc_mar', ''))
        moyens_transport_id = request.POST.get('moyens_transport_id')
        conditions_assurance_id = request.POST.get('conditions_assurance_id')

        statut_contrat = request.POST.get('statut_contrat')
        statut_contrat = "CONTRAT"

        dernier_historique = HistoriquePolice.objects.filter(police_id=police_old.id).order_by('-date_du_jour').first()

        # Historique apporteur police
        apporteurs_old = ApporteurPolice.objects.filter(police_id=police_id)
        for apporteur_old in apporteurs_old:
            HistoriqueApporteurPolice.objects.create(
                taux_com_affaire_nouvelle=apporteur_old.taux_com_affaire_nouvelle,
                taux_com_renouvellement=apporteur_old.taux_com_renouvellement,
                base_calcul=apporteur_old.base_calcul,
                apporteur=apporteur_old.apporteur,
                historique_police_id=dernier_historique.id,
                date_effet=apporteur_old.date_effet,
                statut_validite=apporteur_old.statut_validite,
                created_at=apporteur_old.created_at,
                updated_at=apporteur_old.updated_at,
                deleted_at=apporteur_old.deleted_at,
                added_by_id=apporteur_old.added_by_id,
            )

        # Suppression des apporteurs polices
        if apporteur == "NON":
            ApporteurPolice.objects.filter(police_id=police_id).delete()

        # Enregistrer les intermédiaires si existants
        intermediaires = request.POST.getlist('intermediaires')

        base_calcul_taux_retrocession = request.POST.getlist('base_calcul_taux_retrocession')
        taux_com_affaire_nouvelle = request.POST.getlist('taux_com_affaire_nouvelle')
        taux_com_renouvelement = request.POST.getlist('taux_com_renouvelement')

        # Bien revoir la procédure pour ne pas ajouter et supprimer
        if len(intermediaires) > 0:
            i = 0
            for apporteur_id in intermediaires:

                apporteur_id = int('0' + apporteur_id)

                taux_retro_str = base_calcul_taux_retrocession[i].strip()

                if taux_retro_str:
                    base_calcul = float(taux_retro_str.replace(' ', '').replace(',', '.'))
                else:
                    base_calcul = 0.0

                if i < len(taux_com_affaire_nouvelle):
                    taux_com_str = taux_com_affaire_nouvelle[i].strip()
                else:
                    taux_com_str = 0.0

                if taux_com_str:
                    taux_com_an = float(taux_com_str.replace(' ', '').replace(',', '.'))
                else:
                    taux_com_an = 0.0

                if i < len(taux_com_renouvelement):
                    taux_renouvellement_str = taux_com_renouvelement[i].strip()
                else:
                    taux_renouvellement_str = 0.0

                if taux_renouvellement_str:
                    taux_com_renew = float(taux_renouvellement_str.replace(' ', '').replace(',', '.'))
                else:
                    taux_com_renew = 0.0

                # Insérer la ligne si renseignée
                if apporteur_id > 0 and base_calcul > 0 and (taux_com_an > 0 or taux_com_renew > 0):
                    apporteur_existant = ApporteurPolice.objects.filter(police_id=police_old.id, apporteur_id=apporteur_id,
                                                                        base_calcul_id=base_calcul,
                                                                        taux_com_affaire_nouvelle=taux_com_an,
                                                                        taux_com_renouvellement=taux_com_renew).first()
                    if not apporteur_existant:
                        # Vider la table intermédiaire pour ajouter les nouveaux
                        ApporteurPolice.objects.filter(police_id=police_id).update(
                            statut_validite=StatutValidite.SUPPRIME, updated_at=datetime.now(tz=timezone.utc))

                        ApporteurPolice.objects.create(police_id=police_old.id, apporteur_id=apporteur_id,
                                                       base_calcul_id=base_calcul,
                                                       taux_com_affaire_nouvelle=taux_com_an,
                                                       taux_com_renouvellement=taux_com_renew, ).save()
                i += 1

        # Historique taxe police
        taxes_old = TaxePolice.objects.filter(police_id=police_id)

        # enregistrer les autres taxes
        taxes = request.POST.get('liste_autres_taxes_modification')

        if len(taxes) > 0:
            taxes = json.loads(taxes)

            for taxe in taxes:
                taxe = list(taxe.values())
                taxe_id = taxe[0]
                taxe_montant = taxe[1]

                # Insérer la ligne
                TaxePolice.objects.create(police_id=police_old.id, taxe_id=taxe_id, montant=taxe_montant).save()

        # Suppression des garanties polices
        if garantie_reponse == "NON":
            PoliceGarantie.objects.filter(police_id=police_id).delete()

        # Initialiser une liste pour les garanties
        garanties = []
        # Parcourir les données POST pour trouver les champs de garantie
        for key, value in request.POST.items():
            if key.startswith('garantie_'):
                garantie_id = key.split('_')[1]  # Extraire l'ID de la garantie
                franchise = request.POST.get(f'franchise_{garantie_id}', '0')  # Obtenir la franchise
                capital = request.POST.get(f'capital_{garantie_id}', '0')  # Obtenir le capital

                # Ajouter les données extraites à la liste
                garanties.append({
                    'garantie_id': garantie_id,
                    'franchise': franchise,
                    'capital': capital,
                })
        print("Garantie transmis", garanties)

        # Récupérer les garanties existantes associées à la police
        garanties_existantes = PoliceGarantie.objects.filter(police_id=police_old.id)

        # Identifie les garanties à conserver (celles qui sont dans le formulaire)
        garanties_selectionnees_ids = {garantie['garantie_id'] for garantie in garanties}

        # Supprimer les garanties qui ne sont plus sélectionnées
        for police_garantie in garanties_existantes:
            if str(police_garantie.garantie_id) not in garanties_selectionnees_ids:
                police_garantie.statut = Statut.INACTIF
                police_garantie.updated_by = request.user
                police_garantie.save()

        # Enregistrer les nouvelles garanties ou mettre à jour celles existantes
        for garantie in garanties:
            garantie_id = garantie['garantie_id'].strip()
            franchise = supprimer_espaces(garantie['franchise'].strip())
            capital = supprimer_espaces(garantie['capital'].strip())

            # Vérifier si la garantie existe déjà pour la police
            police_garantie = PoliceGarantie.objects.filter(garantie_id=garantie_id, police_id=police_old.id).first()

            if police_garantie:
                # Historisation des anciennes valeurs avant modification
                HistoriquePoliceGarantie.objects.create(
                    police_garantie_id=police_garantie.id,
                    police_id=police_old.id,
                    garantie_id=garantie_id,
                    formule_id=formule_id,
                    franchise=franchise if franchise else None,
                    capital=capital if capital else None,
                    created_by=request.user,
                )

                # Mise à jour de la garantie
                police_garantie.formule_id = formule_id
                police_garantie.franchise = franchise if franchise else None
                police_garantie.capital = capital if capital else None
                police_garantie.updated_by = request.user
                police_garantie.statut = Statut.ACTIF
                police_garantie.save()

            else:
                # Création d'une nouvelle garantie
                PoliceGarantie.objects.create(
                    client_id=police_old.client_id,
                    police_id=police_old.id,
                    created_by=request.user,
                    garantie_id=garantie_id,
                    formule_id=formule_id,
                    franchise=franchise if franchise else None,
                    capital=capital if capital else None,
                    statut=Statut.ACTIF,
                )

        # Relier l'historique police au mouvement police
        # Obtenir l'avant-dernier mouvement de police
        mouvement_police = MouvementPolice.objects.filter(police_id=police_id, historique_police_id__isnull=True).order_by('-id').first()
        if mouvement_police:
            mouvement_police.historique_police_id = dernier_historique.id
            mouvement_police.save()

        # Création du monvement police
        movement_data_save = request.session.get('add_avenant')
        print('movement_data_save : ', movement_data_save)
        if movement_data_save:
            date_fin_periode_garantie = movement_data_save.get('date_fin_periode_garantie')
            mouvement_police = MouvementPolice.objects.create(police_id=police_id,
                                                              mouvement_id=movement_data_save.get('mouvement'),
                                                              motif_id=movement_data_save.get('motif'),
                                                              date_effet=movement_data_save.get('date_effet') if movement_data_save.get('date_effet') else None,
                                                              date_fin_periode_garantie=date_fin_periode_garantie if date_fin_periode_garantie else None,
                                                              created_by=request.user
                                                              )
            mouvement_police.save()
            mouvement = Mouvement.objects.get(id=mouvement_police.mouvement_id)

            # Si c'est un renouvellement, créer une période de couverture
            if mouvement.code == "AVENANT":
                # Créer une ligne dans période de couverture
                periode_couverture = PeriodeCouverture.objects.create(
                    police_id=police_old.id,
                    date_debut_effet=mouvement_police.date_effet if mouvement_police.date_effet else None,
                    date_fin_effet=mouvement_police.date_fin_periode_garantie if mouvement_police.date_fin_periode_garantie else None,
                ).save()

                # Mouvement de retrait d'un aliment
                motif = movement_data_save.get('motif')

                if motif == "12":
                    print('Avenant de retrait')
                    selected_aliments = []
                    today = now().date()  # Récupérer la date du jour

                    # Parcourir les données du formulaire
                    for key, value in request.POST.items():
                        if key.startswith("aliment_"):  # Vérifie si c'est une case cochée
                            aliment_id = key.split("_")[1]  # Récupérer l'ID du véhicule
                            date_sortie_key = f"date_sortie_{aliment_id}"

                            if date_sortie_key in request.POST and request.POST[
                                date_sortie_key].strip():  # Vérifier si la date est remplie
                                selected_aliments.append({
                                    'id': aliment_id,
                                    'date_sortie': request.POST[date_sortie_key]
                                })

                    if not selected_aliments:
                        pass
                    else:
                        print('selected_aliments ', selected_aliments)
                        for selected_aliment in selected_aliments:
                            aliment_id = selected_aliment['id'].strip()
                            date_sortie = parse_date(selected_aliment['date_sortie'].strip())

                            if date_sortie:
                                aliment = AlimentPolice.objects.filter(police_id=police_old.id, id=aliment_id).first()

                                if aliment:
                                    # Déterminer le statut en fonction de la date de sortie
                                    statut = "INACTIF" if date_sortie < today else "ACTIF"

                                    print('aliment sélectionné ', aliment)
                                    print('aliment_id ', aliment_id)
                                    print('today ', today)
                                    print('date_sortie ', date_sortie)
                                    print('statut ', statut)

                                    aliment.date_sortie = date_sortie
                                    aliment.statut = statut
                                    aliment.save()

                                    # Créer une nouvelle ligne d'historique
                                    historique_vehicule = HistoriqueAliment.objects.create(
                                        vehicule_id=aliment.vehicule_id,
                                        numero_immatriculation=aliment.vehicule.numero_immatriculation,
                                        numero_immat_provisoire=aliment.vehicule.numero_immat_provisoire,
                                        numero_serie=aliment.vehicule.numero_serie,
                                        numero_parc=aliment.numero_parc,
                                        proprietaire=aliment.proprietaire,
                                        conducteur=aliment.conducteur,
                                        marque=aliment.vehicule.marque,
                                        modele=aliment.vehicule.modele,
                                        places_assises=aliment.vehicule.places_assises,
                                        valeur_neuve=aliment.vehicule.valeur_neuve,
                                        valeur_actuelle=aliment.valeur_actuelle,
                                        puissance=aliment.vehicule.puissance,
                                        date_entree=aliment.date_entree if aliment.date_entree else None,
                                        date_sortie=aliment.date_sortie if aliment.date_sortie else None,
                                        date_mis_en_circulation=aliment.date_mis_en_circulation if aliment.date_mis_en_circulation else None,
                                        poids_a_vide=aliment.vehicule.poids_a_vide,
                                        poids_a_charge=aliment.vehicule.poids_a_charge,
                                        categorie_vehicule_id=aliment.vehicule.categorie_vehicule_id,
                                        carburant_id=aliment.vehicule.carburant_id,
                                        carosserie_id=aliment.vehicule.carosserie_id,
                                        usage_id=aliment.usage_id,
                                        commentaire=aliment.commentaire,
                                        statut=aliment.statut,
                                        updated_by_id=request.user.id,
                                    ).save()

        print('autres_taxes ', autres_taxes)

        # Créer l'historique avant la mise à jour
        histtorique_police = HistoriquePolice.objects.create(
            police=police_old,
            client_id=police_old.client_id,
            bureau_id=police_old.client.bureau_id,
            commercial_id=commercial_id,
            gestionnaire_id=gestionnaire_id,
            production_id=production_id,
            produit=police_old.produit,
            bureau=police_old.bureau,
            devise=police_old.devise,
            numero=numero,
            apporteur=apporteur if apporteur else dernier_historique.apporteur,
            garantie=garantie_reponse if garantie_reponse else dernier_historique.garantie,
            date_souscription=date_debut_effet if date_debut_effet else None,
            date_debut_effet=date_debut_effet if date_debut_effet else None,
            date_fin_effet=date_fin_effet if date_fin_effet else None,
            date_fin_police=date_fin_police if date_fin_police else None,
            preavis_de_resiliation=preavis_de_resiliation,
            mode_renouvellement=mode_renouvellement,
            fractionnement_id=fractionnement_id,
            mode_reglement_id=mode_reglement_id,
            regularisation_id=regularisation_id,
            date_prochaine_facture=date_prochaine_facture if date_prochaine_facture else None,
            participation=participation,
            taux_participation=taux_participation,
            prime_ht=prime_ht,
            prime_ttc=prime_ttc,
            taxe=taxe,
            autres_taxes=autres_taxes,
            taux_com_courtage=taux_com_courtage,
            taux_com_courtage_terme=taux_com_courtage_terme,
            commission_courtage=commission_courtage,
            commission_intermediaires=commission_intermediaires,
            cout_police_compagnie=cout_police_compagnie,
            cout_police_courtier=cout_police_courtier,
            calcul_tm=calcul_tm,
            statut_contrat=statut_contrat,
            statut=Statut.ACTIF,
            date_du_jour=datetime.now(),
            created_by=request.user,
        )

        # Mise à jour de la police
        police = Police.objects.filter(id=police_id).update(
            produit_id=produit.id,
            devise_id=devise_id,
            commercial_id=commercial_id,
            gestionnaire_id=gestionnaire_id,
            production_id=production_id,
            created_by=request.user,
            numero=numero,
            date_souscription=datetime.now(),
            preavis_de_resiliation=preavis_de_resiliation,
            date_debut_effet=date_debut_effet if date_debut_effet else None,
            date_fin_effet=date_fin_effet if date_fin_effet else None,
            date_fin_police=date_fin_police if date_fin_police else None,
            date_prochaine_facture=date_prochaine_facture if date_prochaine_facture else None,
            participation=participation,
            taux_participation=taux_participation,
            statut_contrat=statut_contrat,
            statut=Statut.ACTIF,
            updated_by=request.user
        )
        police = Police.objects.get(id=police_id)

        # Créer un nouveau assureur principal
        if typecompagnie_prin:
            police_assureur = PoliceAssureur(
                client_id=police.client_id,
                historique_police=histtorique_police,
                type_compagnie_id=typecompagnie_prin.id,
                compagnie_id=compagnie.id,
                date_creation=datetime.now(),
                created_by=request.user
            )
            police_assureur.save()

            # Si type_compagnie est choisi avec une autre compagnie choisie
            if typecompagnie and compagnie_id:
                police_assureur_autre = PoliceAssureur(
                    client_id=police.client_id,
                    historique_police=histtorique_police,
                    type_compagnie_id=typecompagnie,
                    compagnie_id=compagnie_id,
                    date_creation=datetime.now(),
                    created_by=request.user
                )
                police_assureur_autre.save()

        # TODO MISE EN PLACE DE LA PARTIE ALIMENT DE LA POLICE

        if produit.code == "10001":
            vehicule_id = request.POST.get('vehicule_id')

            if vehicule_id:
                vehicule = Vehicule.objects.get(id=vehicule_id)
                alimentpolice = AlimentPolice.objects.get(id=request.POST.get('mono_vehicule_aliment_id'))

                print('aliment police id : ', alimentpolice.id)

                # Créer une nouvelle ligne d'historique
                historique_vehicule = HistoriqueAliment(
                    vehicule_id=vehicule.id,
                    numero_immatriculation=vehicule.numero_immatriculation,
                    numero_immat_provisoire=vehicule.numero_immat_provisoire,
                    numero_serie=vehicule.numero_serie,
                    numero_parc=alimentpolice.numero_parc,
                    proprietaire=alimentpolice.proprietaire,
                    conducteur=alimentpolice.conducteur,
                    marque=vehicule.marque,
                    modele=vehicule.modele,
                    places_assises=vehicule.places_assises,
                    valeur_neuve=vehicule.valeur_neuve,
                    valeur_actuelle=alimentpolice.valeur_actuelle,
                    puissance=vehicule.puissance,
                    date_entree=alimentpolice.date_entree if alimentpolice.date_entree else None,
                    date_mis_en_circulation=alimentpolice.date_mis_en_circulation if alimentpolice.date_mis_en_circulation else None,
                    poids_a_vide=vehicule.poids_a_vide,
                    poids_a_charge=vehicule.poids_a_charge,
                    categorie_vehicule_id=vehicule.categorie_vehicule_id,
                    carburant_id=vehicule.carburant_id,
                    carosserie_id=vehicule.carosserie_id,
                    usage_id=alimentpolice.usage_id,
                    commentaire=alimentpolice.commentaire,
                    statut=alimentpolice.statut,
                    updated_by_id=request.user.id,
                )
                historique_vehicule.save()

                # Mise à jour de la table véhicule
                vehicule.numero_immatriculation = request.POST.get('immatriculation')
                vehicule.numero_immat_provisoire = request.POST.get('immatriculation_provisioire')
                vehicule.numero_serie = request.POST.get('num_serie')
                vehicule.marque = request.POST.get('marque')
                vehicule.modele = request.POST.get('modele')
                vehicule.places_assises = request.POST.get('places_assises')
                vehicule.valeur_neuve = supprimer_espaces(request.POST.get('valeur_neuve', ''))
                vehicule.puissance = request.POST.get('puissance_fiscale')
                vehicule.date_entree = date_entree if date_entree else None
                vehicule.date_mis_en_circulation = mis_en_circulation if mis_en_circulation else None
                vehicule.poids_a_vide = request.POST.get('poids_a_vide')
                vehicule.poids_a_charge = request.POST.get('poid_tac')
                vehicule.categorie_vehicule_id = request.POST.get('categorie_id')
                vehicule.carburant_id = request.POST.get('carburant_id')
                vehicule.carosserie_id = request.POST.get('carosserie_id')
                vehicule.updated_by_id = request.user.id
                vehicule.save()

                # Mise à jour de police-aliment-vehicule
                if alimentpolice:
                    AlimentPolice.objects.filter(vehicule_id=vehicule.id).update(
                        police_id=police.id,
                        vehicule_id=vehicule.id,
                        updated_by_id=request.user.id,
                        usage_id=request.POST.get('usage_id'),
                        proprietaire=request.POST.get('proprietaire'),
                        conducteur=request.POST.get('conducteur'),
                        numero_parc=request.POST.get('num_parc'),
                        valeur_actuelle=supprimer_espaces(request.POST.get('valeur_actuelle', '')),
                        commentaire=request.POST.get('commentaire'),
                    )
            else:
                vehicule_created = Vehicule(
                    categorie_vehicule_id=request.POST.get('categorie_id'),
                    carburant_id=request.POST.get('carburant_id'),
                    carosserie_id=request.POST.get('carosserie_id'),
                    numero_immatriculation=request.POST.get('immatriculation'),
                    numero_immat_provisoire=request.POST.get('immatriculation_provisioire'),
                    numero_serie=request.POST.get('num_serie'),
                    marque=request.POST.get('marque'),
                    modele=request.POST.get('modele'),
                    places_assises=request.POST.get('places_assises'),
                    valeur_neuve=supprimer_espaces(request.POST.get('valeur_neuve', '')),
                    puissance=request.POST.get('puissance_fiscale'),
                    poids_a_vide=request.POST.get('poids_a_vide'),
                    poids_a_charge=request.POST.get('poid_tac')
                )
                vehicule_created.save()

                vehicule = Vehicule.objects.get(id=vehicule_created.pk)

                aliment_police = AlimentPolice(
                    vehicule_id=vehicule.id,
                    usage_id=request.POST.get('usage_id'),
                    historique_police=histtorique_police,
                    police_id=police.id,
                    created_by=request.user,
                    numero_parc=request.POST.get('num_parc'),
                    proprietaire=request.POST.get('proprietaire'),
                    conducteur=request.POST.get('conducteur'),
                    valeur_actuelle=supprimer_espaces(request.POST.get('valeur_actuelle', '')),
                    date_mis_en_circulation=mis_en_circulation if mis_en_circulation else None,
                    date_entree=date_entree if date_entree else None,
                    date_liaison=datetime.now(),
                    commentaire=request.POST.get('commentaire'),
                    statut=Statut.ACTIF
                )
                aliment_police.save()

        elif produit.code == "10002":

            # Récupérer les aliments de la session
            aliments = request.session.get('aliments', [])

            if aliments:
                for aliment in aliments:
                    # Conversion des dates si nécessaire
                    date_entree = convertir_date_multiformat(aliment.get('date_entree')) if aliment.get('date_entree') else None
                    date_sortie = convertir_date_multiformat('date_sortie') if aliment.get('date_sortie') else None
                    mis_en_circulation = convertir_date_multiformat('mis_en_circulation') if aliment.get('mis_en_circulation') else None

                    # Récupéaration de la catégorie
                    categorie = CategorieVehicule.objects.filter(libelle=aliment.get('T_categorie_id')).first()
                    energie = Carburant.objects.filter(code=aliment.get('energie')).first()

                    vehicule = Vehicule.objects.filter(numero_immatriculation=aliment.get('immat')).first()

                    if vehicule:
                        # Mettre à jour le véhicule existant
                        vehicule.categorie_vehicule_id = categorie.id if categorie else None
                        vehicule.carburant_id = energie.id if energie else None
                        vehicule.carosserie_id = aliment.get('T_carosserie_id')
                        vehicule.numero_immatriculation = aliment.get('immat')
                        vehicule.numero_immat_provisoire = aliment.get('immat_prov')
                        vehicule.numero_serie = aliment.get('num_serie')
                        vehicule.marque = aliment.get('marque')
                        vehicule.modele = aliment.get('modele')
                        vehicule.places_assises = aliment.get('places_assises')
                        vehicule.date_entree = date_entree
                        vehicule.date_mis_en_circulation = mis_en_circulation
                        vehicule.valeur_neuve = supprimer_espaces(aliment.get('valeur_neuve', ''))
                        vehicule.puissance = aliment.get('puissance')
                        vehicule.poids_a_vide = aliment.get('poids_a_vide')
                        vehicule.poids_a_charge = aliment.get('poids_a_charge')
                        vehicule.updated_by = request.user
                        vehicule.save()

                        # Mise à jour de la relation police-aliment
                        AlimentPolice.objects.filter(vehicule_id=vehicule.id).update(
                            police_id=police_id,
                            vehicule_id=vehicule.id,
                            updated_by=request.user,
                            usage_id=aliment.get('T_usage_id'),
                            proprietaire=aliment.get('proprietaire'),
                            conducteur=aliment.get('conducteur'),
                            numero_parc=aliment.get('num_parc'),
                            valeur_actuelle=supprimer_espaces(aliment.get('valeur_actuelle', '')),
                            commentaire=aliment.get('comment'),
                        )

                    else:
                        vehicule_created = Vehicule(
                            categorie_vehicule_id=categorie.id if categorie else None,
                            carburant_id=energie.id if energie else None,
                            carosserie_id=aliment.get('T_carosserie_id'),
                            numero_immatriculation=aliment.get('immat'),
                            numero_immat_provisoire=aliment.get('immat_prov'),
                            numero_serie=aliment.get('num_serie'),
                            marque=aliment.get('marque'),
                            modele=aliment.get('modele'),
                            places_assises=aliment.get('places_assises'),
                            valeur_neuve=supprimer_espaces(aliment.get('valeur_neuve', '')),
                            puissance=aliment.get('puissance'),
                            poids_a_vide=aliment.get('poids_a_vide'),
                            poids_a_charge=aliment.get('poids_a_charge')
                        )
                        vehicule_created.save()

                        vehicule = Vehicule.objects.get(id=vehicule_created.pk)

                        aliment_police = AlimentPolice(
                            vehicule_id=vehicule.id,
                            usage_id=aliment.get('T_usage_id'),
                            historique_police=histtorique_police,
                            police_id=police.id,
                            created_by=request.user,
                            numero_parc=aliment.get('num_parc'),
                            proprietaire=aliment.get('proprietaire'),
                            conducteur=aliment.get('conducteur'),
                            valeur_actuelle=supprimer_espaces(aliment.get('valeur_actuelle', '')),
                            date_mis_en_circulation=mis_en_circulation if mis_en_circulation else None,
                            date_entree=date_entree if date_entree else None,
                            date_sortie=date_sortie if date_sortie else None,
                            date_liaison=datetime.now(),
                            commentaire=aliment.get('comment'),
                            statut=Statut.ACTIF
                        )
                        aliment_police.save()

            aliments = request.session.get('aliments', None)
            # Vider les aliements enregistrer en session
            if 'aliments' in request.session:
                del request.session['aliments']

        elif produit.code in ["50001", "50002"]:
            marchandise_id = request.POST.get('marchandise_id')

            if marchandise_id:
                marchandise = Marchandise.objects.get(id=marchandise_id)
                alimentpolice = AlimentPolice.objects.get(id=request.POST.get('marchandise_aliment_id'))

                print('aliment police id : ', alimentpolice.id)

                # Créer une nouvelle ligne d'historique
                marchandise_historique_created = HistoriqueAliment(
                    marchandise_id=marchandise.id,
                    moyens_transport_id=moyens_transport_id,
                    conditions_assurance_id=conditions_assurance_id,
                    devise_id=devise_id,
                    num_certificat=num_certificat,
                    num_fact_fournisseur=num_fact_fournisseur,
                    ref_dai=ref_dai,
                    date_commande=date_commande if date_commande else None,
                    nombre_colis=nombre_colis,
                    poids_brut=poids_brut,
                    plein_souscription=plein_souscription,
                    immatriculation=immatriculation_march,
                    pavillon_cie_prest=pavillon_cie_prest,
                    destination=destination,
                    lieu_transit_transbordement=lieu_transit_transbordement,
                    date_emmision_certificat=date_emmision_certificat if date_emmision_certificat else None,
                    date_sortie=date_sortie_march if date_sortie_march else None,
                    num_commande=num_commande,
                    marchandises_description=marchandises_description,
                    poids_net=poids_net,
                    valeur_assuree=valeur_assuree,
                    marque_modele_type=marque_modele_type,
                    debut_voyage=debut_voyage if debut_voyage else None,
                    lieu_depart=lieu_depart,
                    nom_commissaire=nom_commissaire,
                    telephone_commissaire=telephone_commissaire,
                    code_commissaire=code_commissaire,
                    adresse_commissaire=adresse_commissaire,
                    courriel_commissaire=courriel_commissaire,
                    taux_risque_ordinaire=taux_risque_ordinaire if taux_risque_ordinaire else None,
                    taux_risque_guerre=taux_risque_guerre if taux_risque_guerre else None,
                    taux_supprime=taux_supprime if taux_supprime else None,
                    taux_taxe=taux_taxe if taux_taxe else None,
                    taux_reduction_commerciale=taux_reduction_commerciale if taux_reduction_commerciale else None,
                    accessoires=accessoires if accessoires else None,
                    autres_frais=autres_frais if autres_frais else None,
                    prime_risque_ordinaire=prime_risque_ordinaire if prime_risque_ordinaire else None,
                    prime_risque_guerre=prime_risque_guerre if prime_risque_guerre else None,
                    prime_supprime=prime_supprime if prime_supprime else None,
                    prime_brut=prime_brut if prime_brut else None,
                    prime_reduction=prime_reduction if prime_reduction else None,
                    total_taxe=total_taxe if total_taxe else None,
                    prime_ttc_mar=prime_ttc_mar if prime_ttc_mar else None,
                    date_liaison=datetime.now(),
                    created_by=marchandise.created_by,
                    updated_by=marchandise.updated_by,
                    statut=marchandise.statut
                )
                marchandise_historique_created.save()

                # Mise à jour de la marchandise
                marchandise.moyens_transport_id = moyens_transport_id
                marchandise.conditions_assurance_id = conditions_assurance_id
                marchandise.devise_id = devise_id
                marchandise.num_certificat = num_certificat
                marchandise.num_fact_fournisseur = num_fact_fournisseur
                marchandise.ref_dai = ref_dai
                marchandise.date_commande = date_commande if date_commande else None
                marchandise.nombre_colis = nombre_colis
                marchandise.poids_brut = poids_brut
                marchandise.plein_souscription = plein_souscription
                marchandise.immatriculation = immatriculation_march
                marchandise.pavillon_cie_prest = pavillon_cie_prest
                marchandise.destination = destination
                marchandise.lieu_transit_transbordement = lieu_transit_transbordement
                marchandise.date_emmision_certificat = date_emmision_certificat if date_emmision_certificat else None
                marchandise.date_sortie = date_sortie_march if date_sortie_march else None
                marchandise.num_commande = num_commande
                marchandise.marchandises_description = marchandises_description
                marchandise.poids_net = poids_net
                marchandise.valeur_assuree = valeur_assuree
                marchandise.marque_modele_type = marque_modele_type
                marchandise.debut_voyage = debut_voyage if debut_voyage else None
                marchandise.lieu_depart = lieu_depart
                marchandise.nom_commissaire = nom_commissaire
                marchandise.telephone_commissaire = telephone_commissaire
                marchandise.code_commissaire = code_commissaire
                marchandise.adresse_commissaire = adresse_commissaire
                marchandise.courriel_commissaire = courriel_commissaire
                marchandise.taux_risque_ordinaire = taux_risque_ordinaire if taux_risque_ordinaire else None
                marchandise.taux_risque_guerre = taux_risque_guerre if taux_risque_guerre else None
                marchandise.taux_supprime = taux_supprime if taux_supprime else None
                marchandise.taux_reduction_commerciale = taux_reduction_commerciale if taux_reduction_commerciale else None
                marchandise.taux_taxe = taux_taxe if taux_taxe else None
                marchandise.accessoires = accessoires if accessoires else None
                marchandise.autres_frais = autres_frais if autres_frais else None
                marchandise.prime_risque_ordinaire = prime_risque_ordinaire if prime_risque_ordinaire else None
                marchandise.prime_risque_guerre = prime_risque_guerre if prime_risque_guerre else None
                marchandise.prime_supprime = prime_supprime if prime_supprime else None
                marchandise.prime_brut = prime_brut if prime_brut else None
                marchandise.total_taxe = total_taxe if total_taxe else None
                marchandise.prime_reduction = prime_reduction if prime_reduction else None
                marchandise.prime_ttc_mar = prime_ttc_mar if prime_ttc_mar else None
                marchandise.updated_at = datetime.now()
                marchandise.updated_by = request.user
                marchandise.save()

            else:
                marchandise_created = Marchandise(
                    moyens_transport_id=moyens_transport_id,
                    conditions_assurance_id=conditions_assurance_id,
                    devise_id=devise_id,
                    num_certificat=num_certificat,
                    num_fact_fournisseur=num_fact_fournisseur,
                    ref_dai=ref_dai,
                    date_commande=date_commande if date_commande else None,
                    nombre_colis=nombre_colis,
                    poids_brut=poids_brut,
                    plein_souscription=plein_souscription,
                    immatriculation=immatriculation_march,
                    pavillon_cie_prest=pavillon_cie_prest,
                    destination=destination,
                    lieu_transit_transbordement=lieu_transit_transbordement,
                    date_emmision_certificat=date_emmision_certificat if date_emmision_certificat else None,
                    date_sortie=date_sortie_march if date_sortie_march else None,
                    num_commande=num_commande,
                    marchandises_description=marchandises_description,
                    poids_net=poids_net,
                    valeur_assuree=valeur_assuree,
                    marque_modele_type=marque_modele_type,
                    debut_voyage=debut_voyage if debut_voyage else None,
                    lieu_depart=lieu_depart,
                    nom_commissaire=nom_commissaire,
                    telephone_commissaire=telephone_commissaire,
                    code_commissaire=code_commissaire,
                    adresse_commissaire=adresse_commissaire,
                    courriel_commissaire=courriel_commissaire,
                    taux_risque_ordinaire=taux_risque_ordinaire if taux_risque_ordinaire else None,
                    taux_risque_guerre=taux_risque_guerre if taux_risque_guerre else None,
                    taux_supprime=taux_supprime if taux_supprime else None,
                    taux_taxe=taux_taxe if taux_taxe else None,
                    taux_reduction_commerciale=taux_reduction_commerciale if taux_reduction_commerciale else None,
                    accessoires=accessoires if accessoires else None,
                    autres_frais=autres_frais if autres_frais else None,
                    prime_risque_ordinaire=prime_risque_ordinaire if prime_risque_ordinaire else None,
                    prime_risque_guerre=prime_risque_guerre if prime_risque_guerre else None,
                    prime_supprime=prime_supprime if prime_supprime else None,
                    prime_brut=prime_brut if prime_brut else None,
                    prime_reduction=prime_reduction if prime_reduction else None,
                    total_taxe=total_taxe if total_taxe else None,
                    prime_ttc_mar=prime_ttc_mar if prime_ttc_mar else None,
                    date_liaison=datetime.now(),
                    created_by=request.user,
                    statut=Statut.ACTIF
                )
                marchandise_created.save()

                marchandise = Marchandise.objects.get(id=marchandise_created.pk)

                aliment_police = AlimentPolice(
                    marchandise_id=marchandise.id,
                    historique_police=histtorique_police,
                    police_id=police.id,
                    created_by=request.user,
                    date_liaison=datetime.now(),
                    statut=Statut.ACTIF
                )
                aliment_police.save()

        else:
            autre_risque_id = request.POST.get('autre_risque_id')

            print("autre_risque_id ", autre_risque_id)
            if autre_risque_id:
                autrerisque = AutreRisque.objects.get(id=autre_risque_id)

                # Créer sa ligne d'historique
                autrerisque_historique_created = HistoriqueAliment(
                    autre_risque_id=autrerisque.id,
                    libelle=autrerisque.libelle,
                    description=autrerisque.description,
                    date_liaison=datetime.now(),
                    created_by=autrerisque.created_by,
                    updated_by=autrerisque.updated_by,
                    statut=autrerisque.statut
                )
                autrerisque_historique_created.save()

                # Mise à jour de l'autre risque
                autrerisque.libelle = ar_libelle
                autrerisque.description = ar_description
                autrerisque.updated_at = datetime.now()
                autrerisque.updated_by = request.user
                autrerisque.save()

            else:
                autre_risque_created = AutreRisque(
                    created_by=request.user,
                    libelle=ar_libelle,
                    description=ar_description,
                    date_liaison=datetime.now(),
                    date_du_jour=datetime.now(),
                    statut=Statut.ACTIF
                )
                autre_risque_created.save()

                autre_risque = AutreRisque.objects.get(id=autre_risque_created.pk)

                aliment_police = AlimentPolice(
                    autre_risque_id=autre_risque.id,
                    historique_police_id=dernier_historique.id,
                    police_id=police.id,
                    created_by=request.user,
                    date_liaison=datetime.now(),
                    statut=Statut.ACTIF
                )
                aliment_police.save()

        response = {
            'statut': 1,
            'message': "Police modifiée avec succès !",
            'data': {
                'id': police.pk,
                'numero': police.numero,
                'prime_ht': dernier_historique.prime_ht,
                'prime_ttc': dernier_historique.prime_ttc,
                'commission_courtage': dernier_historique.commission_courtage,
                'statut': police.statut,
            }
        }

        return JsonResponse(response)

    else:

        police = Police.objects.get(id=police_id)

        periode_couverture = PeriodeCouverture.objects.filter(police_id=police_id).order_by('-id').first()

        apporteurs_police = ApporteurPolice.objects.filter(police_id=police_id, statut_validite=StatutValidite.VALIDE).all()

        # pour la creation de police
        produits = Produit.objects.all().order_by('nom')
        apporteurs = Apporteur.objects.filter(Q(bureau=request.user.bureau) | Q(bureau__isnull=True)).filter(status=True).order_by('nom')
        fractionnements = Fractionnement.objects.all().order_by('libelle')
        modes_reglements = ModeReglement.objects.all().order_by('libelle')
        regularisations = Regularisation.objects.all().order_by('libelle')
        compagnies = Compagnie.objects.filter(bureau=request.user.bureau, status=True).order_by('nom')
        durees = Duree.objects.all().order_by('libelle')
        devises = Devise.objects.all().order_by('libelle')
        taxes = Taxe.objects.all().order_by('libelle')
        bureau_taxes = BureauTaxe.objects.filter(bureau_id=police.bureau_id)
        bases_calculs = BaseCalcul.objects.all().order_by('libelle')
        modes_calculs = ModeCalcul.objects.all().order_by('libelle')
        branches = Branche.objects.filter(status=True).order_by('nom')
        types_prefinancements = TypePrefinancement.objects.filter(statut=Statut.ACTIF).order_by('libelle')

        catgories = CategorieVehicule.objects.all().order_by('libelle')
        carburants = Carburant.objects.all().order_by('libelle')
        usages = Usage.objects.all().order_by('libelle')
        carosseries = Carosserie.objects.all().order_by('libelle')
        conditions_assurances = ConditionsAssurance.objects.filter(status=True).order_by('libelle')
        moyens_transports = MoyensTransport.objects.filter(status=True).order_by('libelle')
        today = datetime.now(tz=timezone.utc)

        mono_vehicule = AlimentPolice.objects.filter(police_id=police.id, vehicule_id__isnull=False).first()
        marchandise_first = AlimentPolice.objects.filter(police_id=police.id, marchandise_id__isnull=False).first()
        autresrisque = AlimentPolice.objects.filter(police_id=police.id, autre_risque_id__isnull=False).first()

        placement_gestion = PlacementEtGestion
        mode_renouvellement = ModeRenouvellement
        calcul_tm = CalculTM
        type_majoration_contrat = TypeMajorationContrat
        optionYesNo = OptionYesNo

        # Injecter les valeurs pour autres taxes dejà renseignées
        for bt in bureau_taxes:
            taxe_police = TaxePolice.objects.filter(police_id=police_id).filter(taxe_id=bt.taxe_id).first()

            if taxe_police is not None:
                bt.montant_existant = taxe_police.montant
            else:
                bt.montant_existant = 0

        dernier_historique = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()

        assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id, type_compagnie_id=1).first() if dernier_historique else []
        autre_assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id).exclude(type_compagnie_id=1).first()
        compagnie_autre = Compagnie.objects.exclude(id=assureur_police.compagnie_id).order_by('nom')

        typecompagnie = TypeCompagnie.objects.exclude(code="ASSPR").order_by('libelle')
        formules = Formule.objects.order_by('libelle')

        commercials = []
        utilisateur = User.objects.all().order_by('-first_name').exclude(is_admin_group=1)
        for user in utilisateur:
            if user.is_commercial:
                commercials.append(user)

        gestionnaires = []
        utilisateur = User.objects.all().order_by('-first_name').exclude(is_admin_group=1)
        for user in utilisateur:
            if user.is_sinistre:
                gestionnaires.append(user)

        productions = []
        utilisateur = User.objects.all().order_by('-first_name').exclude(is_admin_group=1)
        for user in utilisateur:
            if user.is_production:
                productions.append(user)

        # Récupérer les véhicules associés à la police
        vehicules = AlimentPolice.objects.filter(police_id=police_id, vehicule_id__isnull=False, statut=Statut.ACTIF)

        return render(request, 'police/modal_police_modification.html',
                      {'police': police, 'periode_couverture':periode_couverture,
                       'branches': branches, 'produits': produits,
                       'dernier_historique': dernier_historique, 'assureur_police': assureur_police,
                       'autre_assureur_police': autre_assureur_police,
                       'compagnies': compagnies, 'durees': durees, 'placement_gestion': placement_gestion,
                       'mode_renouvellement': mode_renouvellement,
                       'calcul_tm': calcul_tm, 'optionYesNo': optionYesNo, 'formules': formules,
                       'fractionnements': fractionnements, 'modes_reglements': modes_reglements,
                       'regularisations': regularisations, 'typecompagnie': typecompagnie,
                       'devises': devises, 'taxes': taxes, 'types_prefinancements': types_prefinancements,
                       'bureau_taxes': bureau_taxes, 'compagnie_autre': compagnie_autre,
                       'apporteurs': apporteurs, 'bases_calculs': bases_calculs, 'modes_calculs': modes_calculs,
                       'apporteurs_police': apporteurs_police, 'type_majoration_contrat': type_majoration_contrat,
                       'catgories': catgories, 'carburants': carburants, 'usages': usages,
                       'carosseries': carosseries, 'conditions_assurances': conditions_assurances,
                       'moyens_transports': moyens_transports, 'today':today, 'vehicules':vehicules,
                       'mono_vehicule': mono_vehicule, 'marchandise_first': marchandise_first,
                       'autresrisque': autresrisque, 'commercials': commercials,
                       'gestionnaires': gestionnaires, 'productions': productions,
                       })


def get_aliments_session(request):
    police_id = request.GET.get('police_id')

    # Récupérer les véhicules associés à la police
    vehicules = AlimentPolice.objects.filter(police_id=police_id, vehicule_id__isnull=False, statut=Statut.ACTIF)

    # Charger les aliments existants depuis la session
    aliments = request.session.get('aliments', [])
    if vehicules.exists():
        immatriculations_en_session = {alim['immat'] for alim in aliments}

        nouveaux_aliments = []
        for veh in vehicules:
            immat = veh.vehicule.numero_immatriculation if veh.vehicule.numero_immatriculation else None

            if immat and immat not in immatriculations_en_session:
                aliment = {
                    'immat': immat,
                    'proprietaire': veh.proprietaire,
                    'marque': veh.vehicule.marque,
                    'mis_en_circulation': str(veh.date_mis_en_circulation),
                    'modele': veh.vehicule.modele,
                    'conducteur': veh.conducteur,
                    'energie': veh.vehicule.carburant.code,
                    'date_entree': str(veh.date_entree) if veh.date_entree else None,
                    'valeur_actuelle': veh.valeur_actuelle,
                    'poids_a_vide': veh.vehicule.poids_a_vide,
                    'poids_a_charge': veh.vehicule.poids_a_charge,
                    'puissance': veh.vehicule.puissance,
                    'immat_prov': veh.vehicule.numero_immat_provisoire,
                    'num_parc': veh.numero_parc,
                    'num_serie': veh.vehicule.numero_serie,
                    'places_assises': veh.vehicule.places_assises,
                    'valeur_neuve': veh.vehicule.valeur_neuve,
                    'T_categorie_id': veh.vehicule.categorie_vehicule.libelle,
                    'T_carosserie_id': veh.vehicule.carosserie_id,
                    'T_usage_id': veh.usage_id,
                    'comment': veh.commentaire,
                }
                nouveaux_aliments.append(aliment)
                immatriculations_en_session.add(immat)

        # Ajouter les nouveaux aliments aux existants
        aliments.extend(nouveaux_aliments)
        request.session['aliments'] = aliments


    aliments = request.session.get('aliments', [])

    print('aliments chargés : ',aliments)
    print('vehicules chargés : ',vehicules)

    return JsonResponse({'success': True, 'data': aliments})


def get_garanties_by_police(request):
    """Récupère les garanties d'une police pour affichage au chargement du modal."""
    police_id = request.GET.get('police_id')
    police_garanties = PoliceGarantie.objects.filter(police_id=police_id, statut=Statut.ACTIF).values('garantie_id', 'franchise', 'capital', 'garantie__nom')

    garanties = [
        {
            'id': g['garantie_id'],
            'nom': g['garantie__nom'],
            'active': True,
            'franchise': money_field(g['franchise']),
            'capital': money_field(g['capital'])
        } for g in police_garanties
    ]
    return JsonResponse({'garanties': garanties})


# Charger les garanties en fonction de la formule
def get_garanties_by_formule_modification(request):
    police_id = request.GET.get('police_id')
    formule_id = request.GET.get('formule_id')

    # Garanties de la police existante
    police_garanties = PoliceGarantie.objects.filter(police_id=police_id, statut=Statut.ACTIF).values('garantie_id', 'franchise', 'capital')

    # Garanties liées à la formule sélectionnée
    garanties_formule = GarantieFormule.objects.filter(formule_id=formule_id).values('garantie__id', 'garantie__nom')

    # Préparer une liste des garanties avec leurs états
    garanties = []
    for g_formule in garanties_formule:
        garantie_id = g_formule['garantie__id']
        garantie_nom = g_formule['garantie__nom']

        # Vérifie si la garantie fait partie de celles de la police
        police_garantie = next((pg for pg in police_garanties if pg['garantie_id'] == garantie_id), None)

        if police_garantie:
            # Garantie activée avec valeurs existantes
            garanties.append({
                'id': garantie_id,
                'nom': garantie_nom,
                'active': True,
                'franchise': money_field(police_garantie['franchise']),
                'capital': money_field(police_garantie['capital'])
            })
        else:
            # Garantie non activée, valeurs par défaut
            garanties.append({
                'id': garantie_id,
                'nom': garantie_nom,
                'active': False,
                'franchise': '',
                'capital': ''
            })
    print('garanties ', garanties)
    return JsonResponse({'garanties': garanties})


#Vérification des immats
def is_immatriculation_exists(request, immat):

    aliments_existant = request.session.get('aliments', [])
    immatriculations_existes = {alim['immat'] for alim in aliments_existant}
    return immat in immatriculations_existes


@csrf_exempt
def import_excel_aliments(request):
    if request.method == "POST":
        fichier = request.FILES.get("fichier_aliment")

        if not fichier:
            return JsonResponse({'success': False, 'message': "Aucun fichier joint."}, status=400)

        # Lire le fichier Excel
        try:
            data = pd.read_excel(fichier)
            data = data.iloc[1:]  # Ignorer la première ligne si elle est un en-tête supplémentaire
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Erreur de lecture du fichier Excel : {str(e)}"},
                                status=400)

        # Colonnes obligatoires
        colonnes_obligatoires = [
            'immat', 'proprietaire', 'marque', 'energie', 'puissance', 'mis_en_circulation', 'T_categorie_id', 'T_usage_id'
        ]
        colonnes_manquantes = [col for col in colonnes_obligatoires if col not in data.columns]
        if colonnes_manquantes:
            return JsonResponse({
                'success': False,
                'message': f"Colonnes obligatoires manquantes : {', '.join(colonnes_manquantes)}",
            }, status=400)

        # Charger les catégories depuis la base de données
        categories = {cat.id: cat.libelle for cat in CategorieVehicule.objects.all()}
        data['T_categorie_id'] = data['T_categorie_id'].map(categories)

        if data['T_categorie_id'].isnull().any():
            return JsonResponse({
                'success': False,
                'message': 'Certaines catégories dans le fichier ne correspondent pas à la base de données.',
            }, status=400)

        # Charger les aliments existants dans la session
        aliments_existant = request.session.get('aliments', [])

        nouveaux_aliments = []

        for _, row in data.iterrows():
            immat = row['immat']

            if not is_immatriculation_exists(request, immat):  # Vérifie si l'immatriculation existe déjà
                aliment = {
                    'immat': immat,
                    'proprietaire': row['proprietaire'],
                    'marque': row['marque'],
                    'energie': row['energie'],
                    'puissance': row['puissance'],
                    'mis_en_circulation': str(row['mis_en_circulation']),
                    # Ajout des champs facultatifs
                    'modele': row.get('modele', None),
                    'conducteur': row.get('chauffeur', None),
                    'date_entree': str(row.get('date_entree', None)),
                    'immat_prov': row.get('immat_prov', None),
                    'num_parc': row.get('num_parc', None),
                    'num_serie': row.get('num_serie', None),
                    'places_assises': row.get('place', None),
                    'valeur_neuve': row.get('valeur_neuve', None),
                    'valeur_actuelle': row.get('valeur_actuelle', None),
                    'poids_a_vide': row.get('poids_a_vide', None),
                    'poids_a_charge': row.get('poids_a_charge', None),
                    'T_categorie_id': row['T_categorie_id'],
                    'T_carosserie_id': row.get('T_carosserie_id', None),
                    'T_usage_id': row.get('T_usage_id', None),
                    'comment': row.get('comment', None),
                }
                nouveaux_aliments.append(aliment)
            else:
                print(f"⚠️ Immatriculation déjà existante : {immat}")
        
        # Mettre à jour la session uniquement avec les nouveaux aliments
        if nouveaux_aliments:
            aliments_existant = request.session.get('aliments', [])
            aliments_existant.extend(nouveaux_aliments)
            request.session['aliments'] = aliments_existant

        print('Aliment ajouté en session : ', request.session.get('aliments', []))

        # Vérifier si les nouveaux aliments sont bien ajoutés
        if not nouveaux_aliments:
            return JsonResponse({
                'success': True,
                'message': 'Aucune nouvelle immatriculation à ajouter.',
                'data': []
            }, status=200)

        return JsonResponse({
            'success': True,
            'message': 'Importation réussie !',
            'data': request.session.get('aliments', [])  # Renvoyer tous les aliments de la session
        }, status=200)

    return JsonResponse({'success': False, 'message': "Requête invalide."}, status=400)


@csrf_exempt
def import_formulaire_aliments(request):
    if request.method == 'POST':
        try:
            # Récupération de l'immatriculation
            immat = request.POST.get('immatriculation')
            if not immat:
                return JsonResponse({'success': False, 'message': 'Immatriculation manquante.'}, status=400)

            # Vérifier si l'immatriculation existe déjà
            if is_immatriculation_exists(request, immat):  # Vérifier les doublons
                return JsonResponse({
                    'success': False,
                    'message': f"L'immatriculation {immat} existe déjà en session.",
                    'data': request.session.get('aliments', [])
                }, status=400)

            # Vérification de la catégorie
            categorie_id = request.POST.get('categorie_id')
            categorie = CategorieVehicule.objects.filter(id=categorie_id).first()

            if not categorie:
                return JsonResponse({'success': False, 'message': 'Catégorie non trouvée.'}, status=400)

            # Vérification de l'énergie
            carburant_id = request.POST.get('carburant_id')
            carburant = Carburant.objects.filter(id=carburant_id).first()

            if not carburant:
                return JsonResponse({'success': False, 'message': 'Carburant non trouvé.'}, status=400)

            # Création du nouvel aliment
            nouvel_aliment = {
                'immat': immat,
                'proprietaire': request.POST.get('proprietaire'),
                'marque': request.POST.get('marque'),
                'energie': carburant.code,
                'puissance': request.POST.get('puissance_fiscale'),
                'mis_en_circulation': request.POST.get('date_mise_circulation'),
                'modele': request.POST.get('modele'),
                'conducteur': request.POST.get('conducteur'),
                'date_entree': request.POST.get('date_entree'),
                'immat_prov': request.POST.get('immatriculation_provisioire'),
                'num_parc': request.POST.get('num_parc'),
                'num_serie': request.POST.get('num_serie'),
                'places_assises': request.POST.get('places_assises'),
                'valeur_neuve': request.POST.get('valeur_a_neuf'),
                'valeur_actuelle': request.POST.get('valeur_actuelle'),
                'poids_a_vide': request.POST.get('poid_vide'),
                'poids_a_charge': request.POST.get('poid_tac'),
                'T_categorie_id': categorie.libelle,
                'T_carosserie_id': request.POST.get('carosserie_id'),
                'T_usage_id': request.POST.get('usage_id'),
                'comment': request.POST.get('commentaire')
            }

            # Mettre à jour la session
            aliments_existant = request.session.get('aliments', [])
            aliments_existant.append(nouvel_aliment)
            request.session['aliments'] = aliments_existant

            print('Aliment ajouté en session : ', nouvel_aliment)

            return JsonResponse({
                'success': True,
                'message': "Ajout de l'aliment effectué avec succès !",
                'data': [nouvel_aliment]
            }, status=200)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f"Erreur lors de l'enregistrement : {str(e)}"
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': 'Requête invalide ou données manquantes.'
    }, status=400)


@csrf_exempt
def supprimer_aliment(request, index):
    print('Suppression aliment en cours...')
    if request.method == 'POST':
        try:
            # Supposons que vous stockez les aliments en session
            aliments = request.session.get('aliments', [])
            if 0 <= index < len(aliments):
                aliments.pop(index)  # Supprimer l'aliment de la session
                request.session['aliments'] = aliments  # Mettre à jour la session
                return JsonResponse({'success': True, 'message': 'Aliment supprimé.'})
            return JsonResponse({'success': False, 'error': 'Index invalide.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'}, status=405)


@csrf_exempt
def supprimer_aliment_modification(request):
    if request.method == 'POST':
        immat = request.POST.get('immat')

        if not immat:
            return JsonResponse({'success': False, 'message': 'Immatriculation manquante.'}, status=400)

        vehicule = Vehicule.objects.filter(numero_immatriculation=immat).first()
        print('vehicule trouvé : ', vehicule)
        if vehicule:
            HistoriqueAliment.objects.filter(vehicule_id=vehicule.id).delete()
            AlimentPolice.objects.filter(vehicule_id=vehicule.id).delete()
            vehicule.delete()

        # Charger les aliments existants dans la session
        aliments_existant = request.session.get('aliments', [])

        # Supprimer l'aliment avec l'immatriculation correspondante
        aliments_existant = [alim for alim in aliments_existant if alim['immat'] != immat]

        # Mettre à jour la session
        request.session['aliments'] = aliments_existant

        return JsonResponse({'success': True, 'message': 'Immatriculation supprimée avec succès.'})

    return JsonResponse({'success': False, 'message': 'Requête invalide.'}, status=400)


# Supprimer les données en session à la fermeture du modal
def clear_session(request):
    if request.method == 'POST':
        aliments = request.session.get('aliments', None)

        if 'aliments' in request.session:
            del request.session['aliments']

        return JsonResponse({'success': True, 'data': aliments}, status=200)

    return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'}, status=405)


#Chargement des garanties de la branche liée au produit
def get_garanties_by_produit(request):
    branche_id = request.GET.get('produit_id')
    garanties = GarantieBranche.objects.filter(branche_id=branche_id).values('garantie__id', 'garantie__nom')
    garanties = [{'id': g['garantie__id'], 'nom': g['garantie__nom']} for g in garanties]
    return JsonResponse({'garanties': list(garanties)})


#Chargement des garanties de la formule
def get_garanties_by_formule(request):
    formule_id = request.GET.get('formule_id')
    garanties = GarantieFormule.objects.filter(formule_id=formule_id).values('garantie__id', 'garantie__nom')
    garanties = [{'id': g['garantie__id'], 'nom': g['garantie__nom']} for g in garanties]
    return JsonResponse({'garanties': list(garanties)})



@login_required
# edition des cartes des adhérents
def editer_cartes(request, police_id):
    return render(request, 'admin/form_edition_cartes.html')


# IMPRESSION DE LA CARTE
class CARTE_SANTE(FPDF):
    # marron (167, 79, 51)
    # jaune (234, 173, 82)
    start_x = 0
    start_y = 0

    def set_origin(self, x, y):
        self.start_x = x
        self.start_y = y

    def set_cadre(self):
        self.set_draw_color(234, 173, 82)
        self.set_fill_color(167, 79, 51)
        self.set_text_color(0, 0, 0)
        self.set_line_width(.1)

        self.rect(self.start_x + 4, self.start_y + 4, 102, 55)  # cadre de la carte
        self.rect(self.start_x + 5, self.start_y + 4, 4, 55, 'F')  # bande verticale

        self.rect(self.start_x + 5, self.start_y + 4, 4, 55, 'F')

    def set_logo(self, logo_src):
        # LE LOGO
        self.image(logo_src, self.start_x + 10, self.start_y + 5, 0, 10)

    def set_photo(self, photo_src):
        self.set_draw_color(128, 128, 128)  # gray
        self.rect(self.start_x + 90, self.start_y + 5, 15, 17)
        self.image(photo_src, self.start_x + 90, self.start_y + 5, 15, 17)

    def set_numero_carte(self, numero):
        # Arial bold 15
        self.set_font('Arial', '', 12)
        self.set_draw_color(0, 80, 180)
        self.set_fill_color(255, 255, 255)
        self.set_text_color(0, 0, 0)
        self.set_line_width(.1)

        self.set_font('Arial', '', 10)
        self.set_xy(self.start_x + 40, self.start_y + 5)
        self.cell(20, 5, "N° CARTE:", 0, 0, 'L', 1)

        self.set_x(self.start_x + 60)
        self.set_font('Arial', 'B', 12)
        # Title
        self.cell(30, 5, numero, 0, 0, 'L', 1)
        # Line break
        self.ln(10)

        # si inactive, imprimé le statut dessus

    def set_statut(self, statut):
        if statut == Statut.INACTIF:
            self.set_font('Arial', 'B', 10)
            self.set_xy(self.start_x + 50, self.start_y + 10)
            self.set_text_color(255, 0, 0)
            self.cell(55, 5, "I N A C T I V E", 0, 0, 'L', 0)
            self.set_text_color(0, 0, 0)

    def set_nom_beneficiaire(self, nom, date_naissance, numero_cmu):
        if nom is None: nom = ''
        if date_naissance is None: date_naissance = ''
        if numero_cmu is None: numero_cmu = ''

        self.set_y(self.start_y + 22)

        self.set_fill_color(167, 79, 51)
        self.rect(self.start_x + 11, self.start_y + 22, 1, 4, 'F')
        self.set_xy(self.start_x + 12, self.start_y + 22)
        self.set_font('Arial', '', 8)
        self.cell(95, 4, "BÉNÉFICIAIRE", 0, 1, 'L', 0)

        self.ln(1)
        self.set_x(self.start_x + 10)
        self.set_font('Arial', 'B', 10)
        self.cell(95, 4, nom, 0, 1, 'L', 0)

        self.set_font('Arial', '', 8)
        self.ln(1)
        self.set_x(self.start_x + 10)
        self.cell(17, 4, "Né(e) le:", 0, 0, 'L', 0)
        self.set_font('Arial', 'B', 10)
        self.set_x(self.start_x + 27)
        self.cell(30, 4, str(date_naissance), 0, 1, 'L', 0)

        self.set_font('Arial', '', 8)
        self.ln(1)
        self.set_x(self.start_x + 10)
        self.cell(17, 4, "N° CMU:", 0, 0, 'L', 0)
        self.set_font('Arial', 'B', 10)
        self.set_x(self.start_x + 27)
        self.cell(30, 4, str(numero_cmu), 0, 0, 'L', 0)

    def set_nom_adherent_principal(self, adherent_principal, numero_police):
        if adherent_principal:
            nom = adherent_principal.nom + " " + adherent_principal.prenoms
            self.set_y(self.start_y + 43)
            self.set_fill_color(167, 79, 51)
            self.rect(self.start_x + 11, self.start_y + 45, 1, 4, 'F')
            self.set_xy(self.start_x + 12, self.start_y + 45)

            self.set_font('Arial', '', 8)
            self.cell(60, 4, "ADHÉRENT PRINCIPAL", 0, 1, 'L', 0)
            self.ln(1)
            self.set_x(self.start_x + 10)
            self.set_font('Arial', 'B', 10)
            self.cell(60, 4, nom, 0, 1, 'L', 0)

            self.set_font('Arial', '', 8)
            self.ln(1)
            self.set_x(self.start_x + 10)
            self.cell(17, 4, "N° POLICE:", 0, 0, 'L', 0)
            self.set_font('Arial', 'B', 10)
            self.set_x(self.start_x + 27)
            self.cell(43, 4, str(numero_police), 0, 0, 'L', 0)

    def set_qrcode(self, photo_src):
        self.set_draw_color(128, 128, 128)
        self.rect(self.start_x + 62, self.start_y + 40, 15, 15)
        self.image(photo_src, self.start_x + 62, self.start_y + 40, 15, 15)

    def set_signature_filialle(self, photo_src):
        # self.rect(self.start_x + 89, self.start_y + 40, 15, 15)
        self.image(photo_src, self.start_x + 89, self.start_y + 40, 15, 15)

    def set_origin_verso(self, x, y):
        self.start_x = x
        self.start_y = y

    def set_cadre_verso(self):
        self.set_draw_color(234, 173, 82)
        self.set_fill_color(167, 79, 51)
        self.set_text_color(0, 0, 0)
        self.set_line_width(.1)

        self.rect(self.start_x + 4, self.start_y + 4, 102, 55)  # cadre de la carte

    def set_informations_verso(self, informations, nom_bureau, whatsapp, telephone, email, adresse):
        if nom_bureau is None: nom_bureau = ''
        if whatsapp is None: whatsapp = ''
        if telephone is None: telephone = ''
        if email is None: email = ''
        if adresse is None: adresse = ''

        self.set_xy(self.start_x + 8, self.start_y + 8)

        self.set_draw_color(167, 79, 51)
        self.set_fill_color(234, 173, 82)
        self.set_text_color(255, 255, 255)
        self.set_draw_color(255, 255, 255)
        self.set_fill_color(255, 255, 255)
        self.set_text_color(0, 0, 0)

        self.set_font('Arial', '', 9)
        self.multi_cell(94, 4, informations, 1, 'L', 1)
        self.ln(4)
        self.set_x(self.start_x + 8)
        self.set_font('Arial', 'B', 14)
        self.multi_cell(94, 5, nom_bureau, 1, 'C', 1)
        self.ln(5)

        self.set_x(self.start_x + 8)
        self.set_font('Arial', '', 10)
        self.cell(24, 4, "WhatsApp: ", 1, 0, 'L', 1)
        self.set_font('Arial', '', 10)
        self.set_x(self.start_x + 32)
        self.cell(70, 4, str(whatsapp), 1, 1, 'L', 1)

        self.set_x(self.start_x + 8)
        self.set_font('Arial', '', 10)
        self.cell(24, 4, "Fixe: ", 1, 0, 'L', 1)
        self.set_font('Arial', '', 10)
        self.set_x(self.start_x + 32)
        self.cell(70, 4, str(telephone), 1, 1, 'L', 1)

        self.set_x(self.start_x + 8)
        self.set_font('Arial', '', 10)
        self.cell(24, 4, "E-mail: ", 1, 0, 'L', 1)
        self.set_font('Arial', '', 10)
        self.set_x(self.start_x + 32)
        self.cell(70, 4, str(email), 1, 1, 'L', 1)

        self.ln(4)
        self.set_x(self.start_x + 8)
        self.set_font('Arial', '', 9)
        self.multi_cell(94, 5, str(adresse), 1, 'L', 1)


# defining the function to convert an HTML file to a PDF file
def html_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None



def download(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, "cartes/" + filename)
    # file_path = os.path.join(filename)

    response = FileResponse(open(file_path, 'rb'))
    return response


def dateFromDB(date_naissance):
    formated_date = None

    if date_naissance:
        date = datetime.datetime.strptime(str(date_naissance), "%Y-%m-%d")

        if date.day > 1:
            jour = str(date.day)
        else:
            jour = "0" + str(date.day)

        if date.month > 1:
            mois = str(date.month)
        else:
            mois = "0" + str(date.month)

        annee = str(date.year)

        formated_date = jour + "/" + mois + "/" + annee

    return formated_date


@login_required
def ajax_apporteurs(request):
    apporteurs = Apporteur.objects.filter(status=True)
    apporteurs_serialize = serializers.serialize('json', apporteurs)

    return HttpResponse(apporteurs_serialize, content_type='application/json')


@login_required
def ajax_produits(request, branche_id):
    produits = Produit.objects.filter(branche_id=branche_id)
    produits_serialize = serializers.serialize('json', produits)

    return HttpResponse(produits_serialize, content_type='application/json')


def modification_ajax_produits(request, branche_id):
    """
    Vue pour renvoyer les produits associés à une branche spécifique au format JSON.
    :param request: La requête HTTP.
    :param branche_id: L'ID de la branche pour laquelle charger les produits.
    :return: Une réponse JSON contenant les produits de la branche.
    """
    try:
        # Récupérer la branche ou renvoyer une 404 si elle n'existe pas
        branche = get_object_or_404(Branche, id=branche_id)

        # Récupérer tous les produits associés à cette branche
        produits = Produit.objects.filter(branche=branche)

        # Préparer les données à renvoyer au format JSON
        produits_data = [
            {
                "pk": produit.id,  # ID du produit
                "fields": {
                    "nom": produit.nom,  # Nom du produit
                    # Ajouter d'autres champs si nécessaire (ex: code, description, etc.)
                }
            }
            for produit in produits
        ]

        # Renvoyer les données au format JSON
        return JsonResponse(produits_data, safe=False)

    except Exception as e:
        # En cas d'erreur, renvoyer une réponse d'erreur au format JSON
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def sous_rubriques_by_rubrique(request, rubrique_id):
    actes = SousRubrique.objects.filter(rubrique_id=rubrique_id, status=1).order_by('libelle')
    actes_serialize = serializers.serialize('json', actes)

    return HttpResponse(actes_serialize, content_type='application/json')


@login_required
def regroupements_actes_by_rubrique(request, rubrique_id):
    actes = RegroupementActe.objects.filter(rubrique_id=rubrique_id, status=1).order_by('libelle')
    actes_serialize = serializers.serialize('json', actes)

    return HttpResponse(actes_serialize, content_type='application/json')


@login_required
def sous_regroupements_actes_by_rubrique(request, rubrique_id):
    data = SousRegroupementActe.objects.filter(rubrique_id=rubrique_id, status=1).order_by('libelle')
    data_serialize = serializers.serialize('json', data)

    return HttpResponse(data_serialize, content_type='application/json')


@login_required
def actes_by_rubrique(request, rubrique_id):
    rubrique = Rubrique.objects.get(id=rubrique_id)

    if rubrique.code != 'PHARMACIE':
        actes = Acte.objects.filter(rubrique_id=rubrique_id, status=1).order_by('libelle')
    else:
        actes = []

    actes_serialize = serializers.serialize('json', actes)
    return HttpResponse(actes_serialize, content_type='application/json')


@login_required
def actes_by_regroupement_acte(request, regroupement_acte_id):
    regroupement_acte = RegroupementActe.objects.get(id=regroupement_acte_id)
    if regroupement_acte and regroupement_acte.rubrique.code != 'PHARMACIE':
        actes = Acte.objects.filter(regroupement_acte_id=regroupement_acte_id, status=1).order_by('libelle')
    else:
        actes = []

    actes_serialize = serializers.serialize('json', actes)

    return HttpResponse(actes_serialize, content_type='application/json')


@login_required
def formules_by_police(request, police_id):
    formules = FormuleGarantie.objects.filter(police_id=police_id, statut=Statut.ACTIF)
    formules_serialize = serializers.serialize('json', formules)

    return HttpResponse(formules_serialize, content_type='application/json')


@login_required
def polices_restantes(request, police_id):
    police = Police.objects.get(id=police_id)
    polices_restantes = Police.objects.filter(client_id=police.client_id, statut_validite=StatutValidite.VALIDE).exclude(id=police_id)
    polices_restantes = [x for x in polices_restantes if x.etat_police=="En cours" ]

    polices_restantes_serialize = serializers.serialize('json', polices_restantes)

    return HttpResponse(polices_restantes_serialize, content_type='application/json')


@login_required
# récupère le taux paramétré sur le produit en fonction de la compagnie
def ajax_infos_compagnie(request, compagnie_id, produit_id):
    param_produit_compagnie = ParamProduitCompagnie.objects.filter(compagnie_id=compagnie_id,
                                                                   produit_id=produit_id).first()
    print(param_produit_compagnie)
    if (param_produit_compagnie is not None):
        response = {
            'id': param_produit_compagnie.compagnie.id,
            'code': param_produit_compagnie.compagnie.code,
            'nom': param_produit_compagnie.compagnie.nom,
            'taux_com_courtage': param_produit_compagnie.taux_com_courtage,
            'taux_com_courtage_terme': param_produit_compagnie.taux_com_courtage_terme,
        }

    else:
        response = {
            'taux_com_courtage': '',
            'taux_com_courtage_terme': '',
            'taux_com_gestion': '',
        }

    return JsonResponse(response)


def motifs_by_mouvement(request, mouvement_id):
    motifs = Motif.objects.filter(mouvement_id=mouvement_id)
    motifs_serialize = serializers.serialize('json', motifs)
    return HttpResponse(motifs_serialize, content_type='application/json')


# détails d'une police, du bureau de l'utisateur
@method_decorator(login_required, name='dispatch')
class DetailsPoliceView(TemplateView):
    template_name = 'police/index.html'
    model = Police

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        police_id = kwargs['police_id']
        polices = Police.objects.filter(id=police_id, bureau=request.user.bureau, statut_validite=StatutValidite.VALIDE)
        if polices:
            police = polices.first()

            dernier_historique = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()

            duree = 0
            if dernier_historique.date_debut_effet:

                #nouveau
                duree_police_data = (
                    HistoriquePolice.objects.filter(police_id=police.id)
                    .order_by('-date_du_jour')
                    .annotate(
                        duree_police_en_mois=ExpressionWrapper(
                            Case(
                                When(date_fin_effet__isnull=False, then=F('date_fin_effet') - F('date_debut_effet')),
                                When(date_fin_police__isnull=False, then=F('date_fin_police') - F('date_debut_effet')),
                            ),
                            output_field=DurationField()  # ✅ Assure que la sortie est bien une durée
                        )
                    )
                    .values('id', 'duree_police_en_mois')
                    .first()
                )

                # Vérifier si une durée a été trouvée
                duree_police_en_mois = duree_police_data['duree_police_en_mois'] if duree_police_data else None

                # Calcul de la durée en mois uniquement si une durée est définie
                if duree_police_en_mois:
                    nombre_total_mois = duree_police_en_mois.days // 30
                    duree = f"{nombre_total_mois} mois"
                else:
                    duree = "Indéfini"

                print('Durée de la police :', duree)

            mouvement_police = MouvementPolice.objects.filter(police_id=police_id, statut_validite=StatutValidite.VALIDE).order_by('-id').first()

            apporteurs_police = ApporteurPolice.objects.filter(police_id=police_id, statut_validite=StatutValidite.VALIDE)

            assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id, type_compagnie_id=1).first()
            autre_assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id).exclude(type_compagnie_id=1).first()

            context_perso = {'police': police, 'duree_police': duree,
                             'mouvement_police': mouvement_police, 'dernier_historique': dernier_historique, 'assureur_police': assureur_police, 'autre_assureur_police': autre_assureur_police,
                             'apporteurs_police': apporteurs_police}

            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        else:
            #liste_clients_url = reverse('clients')
            return redirect("clients")

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@method_decorator(login_required, name='dispatch')
class DetailsHistoriquePoliceView(TemplateView):
    template_name = 'police/historique_police_detail.html'
    model = HistoriquePolice

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        police_id = kwargs['police_id']
        hist_police_id = kwargs['historique_police_id']
        hist_polices = HistoriquePolice.objects.filter(id=hist_police_id)
        detail_police = Police.objects.filter(id=police_id)

        if hist_polices:
            hist_police = hist_polices.first()
            police = detail_police.first()

            duree = 0
            if hist_police.date_debut_effet:

                # Calculer la différence en mois
                '''duree_police_en_mois = (police.date_fin_effet.year - police.date_debut_effet.year) * 12 + (
                        police.date_fin_effet.month - police.date_debut_effet.month)

                duree = str(duree_police_en_mois) + ' mois'

                if duree_police_en_mois == 0:
                    duree = str((police.date_fin_effet - police.date_debut_effet).days) + ' jours'
                '''

                #nouveau
                duree_police_data = (
                    HistoriquePolice.objects.filter(id=hist_police_id)
                    .annotate(
                        duree_police_en_mois=ExpressionWrapper(
                            Case(
                                When(date_fin_effet__isnull=False, then=F('date_fin_effet') - F('date_debut_effet')),
                                When(date_fin_police__isnull=False, then=F('date_fin_police') - F('date_debut_effet')),
                            ),
                            output_field=DurationField()  # ✅ Assure que la sortie est bien une durée
                        )
                    )
                    .values('id', 'duree_police_en_mois')
                    .first()
                )

                # Vérifier si une durée a été trouvée
                duree_police_en_mois = duree_police_data['duree_police_en_mois'] if duree_police_data else None

                # Calcul de la durée en mois uniquement si une durée est définie
                if duree_police_en_mois:
                    nombre_total_mois = duree_police_en_mois.days // 30
                    duree = f"{nombre_total_mois} mois"
                else:
                    duree = "Indéfini"  # Gérer le cas où il n'y a pas de durée valide

                print('Durée de la police :', duree)


            etat_police = ""
            hist_mouvement_police = MouvementPolice.objects.filter(historique_police_id=hist_police_id, statut_validite=StatutValidite.VALIDE).order_by('-id').first()

            hist_apporteurs_police = HistoriqueApporteurPolice.objects.filter(historique_police_id=hist_police_id)

            assureur_police = PoliceAssureur.objects.filter(historique_police_id=hist_police_id, type_compagnie_id=1).first()
            autre_assureur_police = PoliceAssureur.objects.filter(historique_police_id=hist_police_id).exclude(type_compagnie_id=1).first()

            context_perso = {'police': police, 'historiquepolice': hist_police, 'etat_police': etat_police, 'duree_police': duree,
                             'mouvement_police': hist_mouvement_police, 'assureur_police': assureur_police, 'autre_assureur_police': autre_assureur_police,
                             'apporteurs_police': hist_apporteurs_police,}
            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        else:
            #liste_clients_url = reverse('clients')
            return redirect("clients")

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


# get all police quittances
@method_decorator(login_required, name='dispatch')
class PoliceQuittancesView(TemplateView):
    template_name = 'police/quittances.html'
    model = Quittance

    def get(self, request, police_id, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        police = Police.objects.get(id=police_id)

        # Récupération du client
        client = Client.objects.filter(id=police.client_id).first()

        quittances = Quittance.objects.filter(police_id=police_id, statut_validite=StatutValidite.VALIDE, import_stats=False).order_by('-id')
        types_quittances = TypeQuittance.objects.all()

        '''
        for avenant in mouvements_police:
            quittances_of_avenant = Quittance.objects.filter(mouvement_police_id = avenant.id)
            quittances.extend(quittances_of_avenant)
        '''

        # filtrer les quittances impayés
        quittances_payees = filter(lambda quittance: quittance.statut == StatutQuittance.PAYE, quittances)
        quittances_impayees = filter(lambda quittance: quittance.statut == StatutQuittance.IMPAYE, quittances)
        quittances_honoraires = filter(lambda quittance: quittance.type_quittance.code == "HONORAIRE", quittances)
        quittances_emissions = filter(lambda quittance: quittance.type_quittance.code == "EMISSION", quittances)
        quittances_ristournes = filter(lambda quittance: quittance.nature_quittance.code == "Ristourne", quittances)
        quittances_annulees = Quittance.objects.filter(police_id=police_id, statut_validite=StatutValiditeQuittance.ANNULEE, import_stats=False).order_by('-numero')

        # etat police = dernier motif
        etat_police = police.etat_police

        documents = Document.objects.filter(quittance__in=quittances)

        # Récupérer le dernier historique
        dernier_historique = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()

        # Récupérer les assureurs associés à l'historique
        assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id, type_compagnie_id=1).first()
        autre_assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id).exclude(type_compagnie_id=1).first()

        print("Police assureur : ", assureur_police)

        context_perso = {'police': police, 'client':client, 'types_quittances': types_quittances, 'quittances': quittances, 'documents': documents,
                         'quittances_payees': quittances_payees, 'quittances_impayees': quittances_impayees, 'quittances_honoraires': quittances_honoraires, 'quittances_emissions':quittances_emissions, 'dernier_historique': dernier_historique, 'assureur_police': assureur_police, 'autre_assureur_police': autre_assureur_police,
                         'quittances_ristournes': quittances_ristournes, 'quittances_annulees': quittances_annulees, 'etat_police': etat_police}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


# new code
@login_required
def add_document_to_quittance(request, quittance_id, police_id):
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            police = get_object_or_404(Police, id=police_id)
            quittance = get_object_or_404(Quittance, id=quittance_id)

            type_document_id = request.POST.get('type_document')

            document = form.save(commit=False)
            document.police = police
            document.quittance = quittance
            document.type_document = get_object_or_404(TypeDocument, id=type_document_id)
            document.save()

            response = {
                'statut': 1,
                'message': "Enregistrement effectué avec succès !",
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


@login_required
def details_quittance(request, quittance_id):
    quittance = Quittance.objects.get(id=quittance_id)
    police = quittance.police

    natures_quittances = NatureQuittance.objects.all().order_by('libelle')
    types_quittances = TypeQuittance.objects.all().order_by('libelle')
    types_documents = TypeDocument.objects.filter(is_production=1).order_by('libelle')

    taxes_quittances = TaxeQuittance.objects.filter(quittance_id=quittance_id)

    reglements = Reglement.objects.filter(quittance_id=quittance_id)
    documents = Document.objects.filter(quittance_id=quittance)

    # reglements = Quittance.objects.all()

    return render(request, 'police/modal_details_quittance.html',
                  {'police': police, 'types_quittances': types_quittances, 'natures_quittances': natures_quittances,'types_documents':types_documents,
                   'taxes_quittances': taxes_quittances, 'quittance': quittance, 'reglements': reglements,'documents':documents })


@login_required
def add_quittance(request, police_id):
    police = Police.objects.get(id=police_id)

    error = False
    error_message = ""

    if request.method == 'POST':
        commission_intermediaires = supprimer_espaces(request.POST.get('commission_intermediaire'))
        nature_quittance_id = request.POST.get('nature_quittance')
        type_quittance_id = request.POST.get('type_quittance')
        prime_ht = supprimer_espaces(request.POST.get('prime_ht'))
        cout_police_courtier_req = request.POST.get('cout_police_courtier')
        cout_police_courtier = supprimer_espaces(cout_police_courtier_req) if cout_police_courtier_req else 0
        cout_police_compagnie_req = request.POST.get('cout_police_compagnie')
        cout_police_compagnie = supprimer_espaces(cout_police_compagnie_req) if cout_police_compagnie_req else 0
        taxe = supprimer_espaces(request.POST.get('taxe'))
        autres_taxes = supprimer_espaces(request.POST.get('autres_taxes'))
        prime_ttc = supprimer_espaces(request.POST.get('prime_ttc'))
        taux_com_courtage = supprimer_espaces(request.POST.get('taux_com_courtage'))
        if taux_com_courtage == "": taux_com_courtage = 0
        commission_courtage = supprimer_espaces(request.POST.get('commission_courtage'))
        if commission_courtage == "": commission_courtage = 0
        date_emission = request.POST.get('date_emission')
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')

        # Convert numeric values to appropriate types or set default to 0
        prime_ht = int(prime_ht) if prime_ht else 0
        if cout_police_courtier :
            cout_police_courtier = int(cout_police_courtier) if cout_police_courtier else 0
        if cout_police_compagnie:
            cout_police_compagnie = int(cout_police_compagnie) if cout_police_compagnie else 0
        taxe = int(taxe) if taxe else 0
        autres_taxes = int(autres_taxes) if autres_taxes else 0
        prime_ttc = int(prime_ttc) if prime_ttc else 0
        solde = prime_ttc  # set solde directly

        taux_com_courtage_formatted = str(taux_com_courtage).replace(',', '.')

        commission_courtage = int(commission_courtage) if commission_courtage else 0
        commission_intermediaires = int(commission_intermediaires) if commission_intermediaires else 0

        devise = police.bureau.pays.devise

        # Récupérer le dernier historique
        dernier_historique = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()

        # Récupérer les assureurs associés à l'historique
        assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id,type_compagnie_id=1).first()
        autre_assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id).exclude(type_compagnie_id=1).first()

        print("Police assureur : ", assureur_police)

        # print(nature_quittance_id == '3')
        # dd(nature_quittance_id)

        # Create Quittance object
        quittance = Quittance.objects.create(police_id=police_id,
                                            compagnie=assureur_police.compagnie,
                                            devise=devise,
                                            nature_quittance_id=nature_quittance_id,
                                            type_quittance_id=type_quittance_id,
                                            prime_ht=prime_ht,
                                            cout_police_courtier=cout_police_courtier,
                                            cout_police_compagnie=cout_police_compagnie,
                                            taxe=taxe,
                                            autres_taxes=autres_taxes,
                                            prime_ttc=prime_ttc,
                                            montant_cout_police_courtier_regle=0,
                                            montant_regle=0,
                                            solde=solde,
                                            taux_com_courtage=taux_com_courtage,
                                            commission_courtage=commission_courtage,
                                            commission_intermediaires=commission_intermediaires,
                                            date_emission=date_emission,
                                            date_debut=date_debut,
                                            date_fin=date_fin,
                                            statut=StatutQuittance.IMPAYE,
                                            created_by=request.user,
                                            bureau=request.user.bureau
                                        )

        # Mettre a jour le numero
        code_bureau = request.user.bureau.code
        numero = str(code_bureau) + str(Date.today().year)[-2:] + '-' + str(quittance.pk).zfill(7) + '-Q'
        quittance.numero = numero
        quittance.save()

        # enregistrer les autres taxes si existants
        taxes = request.COOKIES.get('taxes_quittance')

        print(taxes)

        if taxes:
            taxes = json.loads(taxes)

            for taxe in taxes:
                taxe = list(taxe.values())
                taxe_id = taxe[0]
                taxe_montant = taxe[1]

                # Insérer la ligne
                TaxeQuittance.objects.create(quittance_id=quittance.id, taxe_id=taxe_id, montant=taxe_montant).save()

        # il s'agit d'une quittance ristourne alors reglons la automatiquement
        if nature_quittance_id == '3':
            # Caclculer le pourcentage des coms qui se trouvent sur la quittance pour déterminer les montants des coms sur les règlements

            date_paiement = datetime.now(tz=timezone.utc)

            montant_compagnie = prime_ttc - commission_courtage

            pprint('tx_com_courtage' + str(taux_com_courtage) + 'montant_com_courtage' + str(commission_courtage))

            reglement = Reglement.objects.create(quittance_id=quittance.id,
                                                    montant=prime_ttc,
                                                    montant_compagnie=montant_compagnie,
                                                    compagnie=quittance.compagnie,
                                                    devise_id=devise.pk,
                                                    banque_id=None,
                                                    compte_tresorerie_id=None,
                                                    numero_piece=None,
                                                    montant_com_courtage=commission_courtage,
                                                    montant_com_intermediaire=commission_intermediaires,
                                                    mode_reglement_id=None,
                                                    date_paiement=date_paiement,
                                                    statut_reversement_compagnie=StatutReversementCompagnie.REVERSE,
                                                    created_by=request.user,
                                                    bureau=request.user.bureau)
            reglement.save()
            # mettre à jour son numéro
            reglement.numero = 'R' + str(Date.today().year) + str(reglement.pk).zfill(6)
            reglement.save()

            # mise à jour du solde de la quittance
            quittance.montant_regle = prime_ttc
            quittance.solde = 0
            quittance.statut = StatutQuittance.PAYE
            quittance.updated_at = date_paiement
            quittance.save()

            operation = Operation.objects.create(nature_operation=None,
                                                 numero_piece=None,
                                                 montant_total=prime_ttc,
                                                 compte_tresorerie_id=None,
                                                 devise_id=devise.pk,
                                                 mode_reglement_id=None,
                                                 date_operation=date_paiement,
                                                 created_by=request.user,
                                                 uuid=uuid.uuid4())
            operation.save()

            nombre_quittances = 1

            # Lier l'opération au règlement
            operation_reglement = OperationReglement.objects.create(operation=operation, reglement=reglement, created_by=request.user)
            operation_reglement.save()


            # mettre à jour le total dans operation
            operation.montant_total = prime_ttc
            operation.nombre_quittances = nombre_quittances
            operation.numero = 'OP' + str(Date.today().year) + str(operation.pk).zfill(6)
            operation.save()


        response = {
            'statut': 1,
            'message': "Quittance enregistrée avec succès !",
            'data': {
                'id': quittance.pk,
                'numero': quittance.numero,
                'montant': quittance.prime_ttc,
            }
        }

        return JsonResponse(response)

    else:

        # Récupérer le dernier historique
        dernier_historique = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()

        # Récupérer les assureurs associés à l'historique
        assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id,type_compagnie_id=1).first()
        autre_assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id).exclude(type_compagnie_id=1).first()

        print("Police assureur : ", assureur_police)

        natures_quittances = NatureQuittance.objects.filter(status=True).order_by('libelle')
        types_quittances = TypeQuittance.objects.filter(status=True).order_by('libelle')

        bureau_taxes = BureauTaxe.objects.filter(bureau_id=police.bureau_id)
        for bureau_taxe in bureau_taxes:
            print(bureau_taxe)

        #staxes_police = TaxePolice.objects.filter(police=police)
        taxes_police = BureauTaxe.objects.filter(bureau=police.bureau) #pour être plus flexible, pas obligé que la taxe ait été ajouté sur la police avant qu'elle apparaisse à la création de la quittance

        param_produit = ParamProduitCompagnie.objects.filter(produit=police.produit, compagnie=assureur_police.compagnie)[:1].get()

        police_dernier_mouvement = MouvementPolice.objects.filter(police=police, statut_validite=StatutValidite.VALIDE, motif__code__in=["AN", "RENOUV"]).last()

        #get apporteur : un seul apporteur par police
        apporteurs_polices = ApporteurPolice.objects.filter(police=police)

        today = datetime.now(tz=timezone.utc)

        return render(request, 'police/modal_add_quittance.html',
                      {'police': police, 'police_dernier_mouvement': police_dernier_mouvement, 'taxes_police': taxes_police, 'param_produit': param_produit, 'today': today,
                       'types_quittances': types_quittances, 'natures_quittances': natures_quittances, 'dernier_historique': dernier_historique, 'assureur_police': assureur_police, 'autre_assureur_police': autre_assureur_police,
                       'bureau_taxes': bureau_taxes, 'apporteurs_polices': apporteurs_polices})


@login_required
def add_reglement(request, police_id):
    if request.method == 'POST':
        uuid_reglement = request.POST.get('uuid_reglement')
        devise_id = request.POST.get('devise')
        # banque_id = request.POST.get('banque')
        banque_emettrice = request.POST.get('banque')
        compte_tresorerie_id = request.POST.get('compte_tresorerie')
        numero_piece = request.POST.get('numero_piece')
        nature_operation = request.POST.get('nature_operation')
        mode_reglement = request.POST.get('mode_reglement')
        date_paiement = request.POST.get('date_paiement')
        quittances_regles = request.POST.getlist('quittance_regle')
        montants_regles = request.POST.getlist('montant_regle')

        nature_operation_code = "REGCLT"
        nature_operation = NatureOperation.objects.filter(code=nature_operation_code).first()

        #Vérifier si l'uuid n'existe pas déjà dans opération pour s'assurer que l'utilisateur n'as pas cliqué 2 fois
        uuid_reglement_existant = Operation.objects.filter(uuid=uuid_reglement)
        if not uuid_reglement_existant:

            # enregistrer les infos dans operation
            nombre_quittances = 0
            montant_total_regle = 0
            operation = Operation.objects.create(nature_operation=nature_operation,
                                                 numero_piece=numero_piece,
                                                 montant_total=montant_total_regle,
                                                 compte_tresorerie_id=compte_tresorerie_id,
                                                 devise_id=devise_id,
                                                 mode_reglement_id=mode_reglement,
                                                 date_operation=date_paiement,
                                                 created_by=request.user,
                                                 uuid=uuid_reglement)
            operation.save()


            # enregistrer le details dans reglements (liste les quittances reglées avec chaque montant)
            i = 0
            for montant_regle in montants_regles:
                quittance_regle_id = quittances_regles[i]
                i = i + 1

                if montant_regle is not None and quittance_regle_id is not None:
                    montant_regle = float(montant_regle.replace(' ', ''))
                    quittance = Quittance.objects.get(id=quittance_regle_id)

                    if montant_regle > 0 and quittance is not None:

                        cout_police_courtier = quittance.cout_police_courtier
                        # Calcul du montant courtier à payer sur le règlement
                        montant_police_courtier = arrondis_nombre((cout_police_courtier * montant_regle) / quittance.solde)

                        print('Coût courtier restant : ',cout_police_courtier)

                        # Caclculer le pourcentage des coms qui se trouvent sur la quittance pour déterminer les montants des coms sur les règlements

                        tx_com_courtage = (67500 * 100) / quittance.prime_ttc
                        tx_com_intermediaire = (quittance.commission_intermediaires * 100) / quittance.prime_ttc

                        montant_com_courtage = arrondis_nombre((tx_com_courtage / 100) * montant_regle)
                        montant_com_intermediaire = arrondis_nombre((tx_com_intermediaire / 100) * montant_regle)
                        montant_compagnie = arrondis_nombre(montant_regle - (montant_com_courtage + montant_police_courtier))

                        print('tx_com_courtage : ', tx_com_courtage)
                        print('tx_com_intermediaire : ', tx_com_intermediaire)
                        print('montant_com_courtage : ', montant_com_courtage)
                        print('montant_com_intermediaire : ', montant_com_intermediaire)
                        print('montant_compagnie : ', montant_compagnie)
                        print('montant_police_courtier : ', montant_police_courtier)

                        reglement = Reglement.objects.create(quittance_id=quittance_regle_id,
                                                             montant=montant_regle,
                                                             montant_compagnie=montant_compagnie,
                                                             compagnie=quittance.compagnie,
                                                             devise_id=devise_id,
                                                             #banque_id=banque_id,
                                                             banque_emettrice=banque_emettrice,
                                                             compte_tresorerie_id=compte_tresorerie_id,
                                                             numero_piece=numero_piece,
                                                             montant_com_courtage=montant_com_courtage,
                                                             montant_com_intermediaire=montant_com_intermediaire,
                                                             montant_police_courtier=montant_police_courtier,
                                                             mode_reglement_id=mode_reglement,
                                                             date_paiement=date_paiement,
                                                             created_by=request.user,
                                                             bureau=request.user.bureau)
                        reglement.save()
                        # mettre à jour son numéro
                        reglement.numero = 'R' + str(Date.today().year) + str(reglement.pk).zfill(6)
                        reglement.save()

                        # mise à jour du solde de la quittance
                        quittance.montant_cout_police_courtier_regle = quittance.montant_cout_police_courtier_regle + montant_police_courtier
                        quittance.cout_police_courtier = quittance.cout_police_courtier - montant_police_courtier
                        quittance.montant_regle = quittance.montant_regle + montant_regle
                        quittance.solde = quittance.solde - montant_regle
                        if quittance.solde == 0: quittance.statut = StatutQuittance.PAYE
                        quittance.updated_at = datetime.now(tz=timezone.utc)
                        quittance.save()

                        montant_total_regle += montant_regle
                        nombre_quittances = nombre_quittances + 1

                        # Lier l'opération au règlement
                        operation_reglement = OperationReglement.objects.create(operation=operation, reglement=reglement, created_by=request.user)
                        operation_reglement.save()


            # mettre à jour le total dans operation
            operation.montant_total = montant_total_regle
            operation.nombre_quittances = nombre_quittances
            operation.numero = 'OP' + str(Date.today().year) + str(operation.pk).zfill(6)
            operation.save()

            response = {
                'statut': 1,
                'message': "Règlement effectué avec succès !",
                'data': {}
            }

        else:
            response = {
                'statut': 0,
                'message': "Règlement déjà effectué, veuillez vérifier !",
                'data': {}
            }

        return JsonResponse(response)


    else:
        police = Police.objects.get(id=police_id)
        natures_operations = NatureOperation.objects.all()
        devises = Devise.objects.all()
        modes_reglements = ModeReglement.objects.all()
        comptes_tresoreries = CompteTresorerie.objects.filter(status=True)
        banques = Banque.objects.filter(bureau=request.user.bureau, status=True)
        quittances_impayees = Quittance.objects.filter(police_id=police_id, statut=StatutQuittance.IMPAYE, statut_validite=StatutValidite.VALIDE, import_stats=False)

        uuid_reglement = uuid.uuid4()
        today = datetime.now(tz=timezone.utc)
        return render(request, 'police/modal_add_reglement.html',
                      {'police': police, 'today': today, 'quittances_impayees': quittances_impayees, 'devises': devises,
                       'natures_operations': natures_operations, 'modes_reglements': modes_reglements,
                       'banques': banques, 'comptes_tresoreries': comptes_tresoreries, 'uuid_reglement': uuid_reglement})


@login_required
def imprimer_recu_reglement(request, quittance_id, reglement_id):
    quittance = Quittance.objects.get(id=quittance_id)
    reglement = Reglement.objects.get(id=reglement_id)
    police = quittance.police

    # Récupérer le dernier historique de la police
    dernier_historique = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()

    # Récupérer l'assureur associé à l'historique
    assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id, type_compagnie_id=1).first()

    # Chemin du document Word
    doc_path = os.path.join(settings.BASE_DIR, 'production', 'templates', 'police', 'courriers', "3-Recu paiement.docx")

    doc_path = r"{}".format(doc_path)  # Pour s'assurer que c'est bien une chaîne Unicode

    # Charger le document Word
    document = WordDocument(doc_path)

    user = request.user

    # Définir les remplacements de base
    base_replacements = {
        'DESTINATAIRE_TITRE': reglement.quittance.police.client.civilite if reglement.quittance.police.client.civilite else '',
        'DESTINATAIRE_NOM': reglement.quittance.police.client.nom if reglement.quittance.police.client.nom else '',
        'DESTINATAIRE_PRÉNOM': reglement.quittance.police.client.prenoms if reglement.quittance.police.client.prenoms else '',
        'DESTINATAIRE_ADRESSELIGNE1': reglement.quittance.police.client.adresse if reglement.quittance.police.client.adresse else '',
        'DESTINATAIRE_ADRESSELIGNE2': '',
        'DESTINATAIRE_CODEPOSTAL': reglement.quittance.police.client.adresse_postale if reglement.quittance.police.client.adresse_postale else '',
        'DESTINATAIRE_VILLE': reglement.quittance.police.client.ville if reglement.quittance.police.client.ville else '',
        'CABINET_VILLECAB': reglement.quittance.police.bureau.ville,
        'QUITTANCE_NUMÉROPOLICE': reglement.quittance.police.numero,
        'QUITTANCE_NUMÉRO': reglement.quittance.numero,
        'PAIEMENT_ID_OPER': reglement.numero,
        'QUITTANCE_DATEDÉBUT': reglement.quittance.date_debut.strftime('%d-%m-%Y'),
        'QUITTANCE_DATEFIN': reglement.quittance.date_fin.strftime('%d-%m-%Y'),
        'COMPAGNIE_NOM': assureur_police.compagnie.nom if assureur_police.compagnie.nom else '',
        'POLICE_BRANCHE': reglement.quittance.police.produit.branche.nom if reglement.quittance.police.produit.branche.nom else '',
        'ASSURÉ_NOM': reglement.quittance.police.client.nom,
        'ASSURÉ_PRÉNOM': reglement.quittance.police.client.prenoms,
        'SIGNATAIRE_NOM': request.user.first_name,
        'SIGNATAIRE_PRENOM': request.user.last_name,
        '$QUITTANCE_PRIMETOTALE': f"{num2words(reglement.montant, lang='fr').capitalize()} {reglement.quittance.police.client.pays.devise.code}",
        'QUITTANCE_PRIMETOTALE$$': f"{format_montant(reglement.montant)} {reglement.quittance.police.client.pays.devise.code}",
        'PAIEMENT_LIBELLE_MODEREG': reglement.mode_reglement.libelle if reglement.mode_reglement else '',
        'PAIEMENT_BANQUE_CLIENT': reglement.banque_emettrice if reglement.banque_emettrice else '',
        'PAIEMENT_NUMERO_CHEQUE': reglement.compte_tresorerie.code if reglement.compte_tresorerie else '',
        'POLICE_NUMÉRO': reglement.quittance.police.numero,
        'POLICE_NOMPRODUIT': reglement.quittance.police.produit.nom,
        'CABINET_MENTIONS': reglement.quittance.police.bureau.mention_legale,
        'LIBRE_TODAY': datetimes.today().strftime('%d/%m/%Y'),
    }

    replacements = {}
    for key, value in base_replacements.items():
        formats = [
            f'«{key}»', f'"{key}"', key
        ]
        for fmt in formats:
            replacements[fmt] = str(value) if value else ""

    # Fonction pour remplacer le logo séparément
    def replace_logo_in_document(document, logo_path):
        if not logo_path:
            return

        for paragraph in document.paragraphs:
            if 'LOGO_SOC' in paragraph.text:
                for run in paragraph.runs:
                    if 'LOGO_SOC' in run.text:
                        run.clear()
                        run.add_picture(logo_path, width=Inches(1.0))
                        break

        # Remplacer dans les en-têtes et les pieds de page également
        for section in document.sections:
            # En-têtes
            for paragraph in section.header.paragraphs:
                if 'LOGO_SOC' in paragraph.text:
                    for run in paragraph.runs:
                        if 'LOGO_SOC' in run.text:
                            run.clear()
                            run.add_picture(logo_path, width=Inches(1.0))
                            break

            # Pieds de page
            for paragraph in section.footer.paragraphs:
                if 'LOGO_SOC' in paragraph.text:
                    for run in paragraph.runs:
                        if 'LOGO_SOC' in run.text:
                            run.clear()
                            run.add_picture(logo_path, width=Inches(1.0))
                            break

    # Fonction pour remplacer les autres placeholders
    def replace_placeholders_in_paragraph(paragraph):
        original_text = paragraph.text
        new_text = original_text

        for placeholder, value in replacements.items():
            if placeholder in new_text:
                new_text = new_text.replace(placeholder, value)

        if new_text != original_text:
            first_run = paragraph.runs[0] if paragraph.runs else paragraph.add_run()
            first_run.text = new_text
            for run in paragraph.runs[1:]:
                run.clear()

    def replace_placeholders_in_document(document):
        for paragraph in document.paragraphs:
            replace_placeholders_in_paragraph(paragraph)

        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        replace_placeholders_in_paragraph(paragraph)

        for section in document.sections:
            for paragraph in section.header.paragraphs + section.footer.paragraphs:
                replace_placeholders_in_paragraph(paragraph)
            for table in section.header.tables + section.footer.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            replace_placeholders_in_paragraph(paragraph)

    def generate_document_response(document):
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename="RECU PAIEMENT.docx"'
        document.save(response)
        return response

    # Remplacement du logo
    if user.bureau.logo and hasattr(user.bureau.logo, 'path') and os.path.isfile(
            user.bureau.logo.path):
        logo_path = user.bureau.logo.path
        replace_logo_in_document(document, logo_path)
    else:
        # Fonction pour remplacer le texte tout en conservant le format
        def remplacer_texte_avec_format(paragraphs, ancien_texte, nouveau_texte):
            for para in paragraphs:
                for run in para.runs:
                    if ancien_texte in run.text:
                        run.text = run.text.replace(ancien_texte, nouveau_texte)

        # Remplacer dans le corps du document
        remplacer_texte_avec_format(document.paragraphs, '«LOGO_SOC»', '')

        # Remplacer également dans les en-têtes (headers)
        for section in document.sections:
            remplacer_texte_avec_format(section.header.paragraphs, '«LOGO_SOC»', '')

        # Remplacer également dans les pieds de page (footers)
        for section in document.sections:
            remplacer_texte_avec_format(section.footer.paragraphs, '«LOGO_SOC»', '')

    # Remplacement des autres placeholders
    replace_placeholders_in_document(document)

    return generate_document_response(document)


@login_required
def add_lettrage(request, police_id):

    police = Police.objects.get(id=police_id)
    acomptes = Acompte.objects.filter(client_id=police.client_id, solde__gt=0)
    quittances_impayees = Quittance.objects.filter(police_id=police_id, statut=StatutQuittance.IMPAYE, statut_validite=StatutValidite.VALIDE, import_stats=False)
    uuid_reglement = uuid.uuid4()
    today = datetime.now(tz=timezone.utc)

    if request.method == 'POST':
        uuid_reglement = request.POST.get('uuid_reglement')
        date_paiement = datetime.now(tz=timezone.utc)

        # Initialiser une liste pour les acomptes cochés
        acompte_lettrage = []
        # Parcourir les données POST pour trouver les champs d'acompte cochés
        for key, value in request.POST.items():
            if key.startswith('montant_acompte_'):
                montant_acompte_id = key.split('_')[2]
                # Vérifier si la checkbox correspondante est présente dans les données POST
                if f"checkbox_acompte_a_utiliser_{montant_acompte_id}" in request.POST:
                    solde_acompte = request.POST.get(f'solde_acompte_{montant_acompte_id}', '0').replace(' ', '')

                    try:
                        solde_acompte = float(solde_acompte)
                    except ValueError:
                        print(f"Erreur de conversion pour l'acompte {montant_acompte_id}.")
                        continue

                    # Ajouter les données extraites à la liste
                    acompte_lettrage.append({
                        'acompte_id': montant_acompte_id,
                        'solde_acompte': solde_acompte,
                    })

        quittances_lettrage = []
        # Parcourir les données POST pour trouver les quittances cochées
        for key, value in request.POST.items():
            if key.startswith('quittance_a_solde_'):
                quittance_a_solde_id = key.split('_')[-1]
                # Vérifier si la checkbox correspondante est présente dans les données POST
                if f"checkbox_quittance_a_regler_{quittance_a_solde_id}" in request.POST:
                    # Récupérer les valeurs nécessaires avec des valeurs par défaut
                    solde_quittance = request.POST.get(f'solde_quittance_{quittance_a_solde_id}', '0').replace(' ', '')
                    solde_apres_transmit = request.POST.get(f'solde_apres_transmit_{quittance_a_solde_id}','0').replace(' ', '')
                    montant_a_regler_transmit = request.POST.get(f'montant_a_regler_transmit_{quittance_a_solde_id}','0').replace(' ', '')

                    # Convertir les valeurs en nombres
                    try:
                        solde_quittance = float(solde_quittance)
                        solde_apres_transmit = float(solde_apres_transmit)
                        montant_a_regler_transmit = float(montant_a_regler_transmit)
                    except ValueError:
                        print(f"Erreur de conversion pour la quittance {quittance_a_solde_id}.")
                        continue

                    # Ajouter les données extraites à la liste
                    quittances_lettrage.append({
                        'quittance_id': quittance_a_solde_id,
                        'solde_quittance': solde_quittance,
                        'solde_apres_transmit': solde_apres_transmit,
                        'montant_a_regler_transmit': montant_a_regler_transmit,
                    })

        uuid_reglement_existant = Operation.objects.filter(uuid=uuid_reglement)
        if not uuid_reglement_existant:
            # enregistrer les infos dans operation
            nombre_quittances = 0
            montant_total_regle = 0
            operation = Operation.objects.create(montant_total=montant_total_regle,
                                                 date_operation=date_paiement,
                                                 created_by=request.user,
                                                 uuid=uuid_reglement)
            operation.save()

            # TODO CREATION DES REGLEMENTS ET MISE A JOUR DES QUITTANCES COCHEES
            # Si des quittances sont chargées
            if len(quittances_lettrage) > 0:
                culmul_montant_a_regler_quittance = 0
                for quittance in quittances_lettrage:
                    montant_a_regler_transmit = quittance['montant_a_regler_transmit']
                    solde_apres_transmit = quittance['solde_apres_transmit']

                    quittance_existe = Quittance.objects.filter(id=quittance['quittance_id']).first()

                    if quittance_existe:
                        if solde_apres_transmit == 0.0:
                            # Alors quittance totalement reglée par l'acompte
                            quittance_existe.montant_regle = quittance_existe.montant_regle + quittance_existe.solde
                            quittance_existe.solde = Decimal(0)
                            quittance_existe.statut = StatutQuittance.PAYE
                            quittance_existe.updated_at = datetime.now(tz=timezone.utc)
                        else:
                            # Alors quittance reglée par l'acompte partiellement
                            quittance_existe.montant_regle = quittance_existe.montant_regle + montant_a_regler_transmit
                            quittance_existe.solde = solde_apres_transmit
                            quittance_existe.updated_at = datetime.now(tz=timezone.utc)

                        quittance_existe.save()

                        montant_total_regle += quittance_existe.montant_regle
                        nombre_quittances = nombre_quittances + 1
                        culmul_montant_a_regler_quittance += montant_a_regler_transmit

                        # Calcul des parts
                        tx_com_courtage = (quittance_existe.commission_courtage * 100) / quittance_existe.prime_ttc
                        tx_com_intermediaire = (quittance_existe.commission_intermediaires * 100) / quittance_existe.prime_ttc
                        montant_com_courtage = (tx_com_courtage / 100) * quittance_existe.montant_regle
                        montant_com_intermediaire = (tx_com_intermediaire / 100) * quittance_existe.montant_regle
                        montant_compagnie = quittance_existe.montant_regle - (montant_com_courtage + quittance_existe.cout_police_courtier)

                        # Création de la ligne de règlement
                        reglement = Reglement.objects.create(quittance_id=quittance_existe.id,
                                                             montant=quittance_existe.montant_regle,
                                                             montant_compagnie=montant_compagnie,
                                                             compagnie=quittance_existe.compagnie,
                                                             montant_com_courtage=montant_com_courtage,
                                                             montant_com_intermediaire=montant_com_intermediaire,
                                                             date_paiement=date_paiement,
                                                             created_by=request.user,
                                                             bureau=request.user.bureau)
                        #reglement.save()
                        # mettre à jour son numéro
                        reglement.numero = 'R' + str(Date.today().year) + str(reglement.pk).zfill(6)
                        reglement.save()

                        # Lier l'opération au règlement
                        operation_reglement = OperationReglement.objects.create(operation=operation,
                                                                                reglement=reglement,
                                                                                created_by=request.user)
                        operation_reglement.save()

                # mettre à jour le total dans operation
                operation.montant_total = montant_total_regle
                operation.nombre_quittances = nombre_quittances
                operation.numero = 'OP' + str(Date.today().year) + str(operation.pk).zfill(6)
                operation.save()

            # TODO MISE A JOUR DES ACOMPTES COCHES
            # Si les acomptes sont chargés
            if len(acompte_lettrage) > 0:
                # Calcul du culmul des montants des acomptes utilisés
                cumul_montant_total_acomptes = Decimal(0)
                for acomptes in acompte_lettrage:
                    acompte = Acompte.objects.filter(id=acomptes['acompte_id']).first()
                    if acompte:
                        cumul_montant_total_acomptes += Decimal(acompte.solde)

                # Conversion de culmul_montant_a_regler_quittance en Decimal si nécessaire
                culmul_montant_a_regler_quittance = Decimal(culmul_montant_a_regler_quittance)

                if cumul_montant_total_acomptes > culmul_montant_a_regler_quittance:
                    # Calcul de l'excédent
                    excedent = Decimal(cumul_montant_total_acomptes - culmul_montant_a_regler_quittance)

                    # Récupérer uniquement la dernière ligne d'acompte coché
                    dernier_acompte = None
                    if acompte_lettrage:
                        dernier_acompte_data = acompte_lettrage[-1]  # Dernier élément dans la liste
                        try:
                            dernier_acompte_id = dernier_acompte_data['acompte_id']
                            dernier_acompte = Acompte.objects.get(id=dernier_acompte_id)
                        except Acompte.DoesNotExist:
                            print(f"L'acompte avec l'ID {dernier_acompte_id} n'existe pas.")
                    else:
                        print("Aucun acompte coché trouvé.")

                    # Appliquer l'excédent uniquement au dernier acompte
                    if dernier_acompte.solde <= excedent:
                        excedent -= dernier_acompte.solde
                        dernier_acompte.solde = 0
                    else:
                        dernier_acompte.solde = excedent
                        excedent = 0
                    dernier_acompte.save()

                    # Remettre à jour tous les autres acomptes à zéro (hors mis le dernier acompte)
                    for acomptes in acompte_lettrage[:-1]:
                        acompte = Acompte.objects.get(id=acomptes['acompte_id'])
                        acompte.solde = 0
                        acompte.save()

                else:
                    # Remettre à jour tous les autres acomptes
                    for acomptes in acompte_lettrage:
                        acompte = Acompte.objects.get(id=acomptes['acompte_id'])
                        acompte.solde = 0
                        acompte.save()

            response = {
                'statut': 1,
                'message': "Lettrage de compte effectué, veuillez vérifier !",
                'data': {}
            }
            return JsonResponse(response)

        else:
            response = {
                'statut': 0,
                'message': "Lettrage de compte déjà effectué, veuillez vérifier !",
                'data': {}
            }
            return JsonResponse(response)

    else:

        return render(request, 'police/modal_add_lettrage.html',
                      {'police': police, 'today': today, 'quittances_impayees': quittances_impayees, 'acomptes': acomptes, 'uuid_reglement': uuid_reglement})


# all police avenants
@method_decorator(login_required, name='dispatch')
class PoliceAvenantsView(TemplateView):
    template_name = 'police/avenants.html'
    model = Police

    def get(self, request, police_id, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        police = Police.objects.filter(id=police_id, bureau=request.user.bureau, statut_validite=StatutValidite.VALIDE).first()
        if police:
            mouvements = Mouvement.objects.filter(type="POLICE").exclude(code="AN").order_by('libelle')
            mouvements_police = MouvementPolice.objects.filter(police_id=police_id, statut_validite=StatutValidite.VALIDE).order_by('-id') #, statut_validite=StatutValidite.VALIDE

            # etat police = dernier motif
            etat_police = police.etat_police

            if etat_police != "Suspendu":
                # Retirer mise en vigueur (REMVIG) sauf cas de suspention
                mouvements = mouvements.exclude(code="REMVIG").order_by('libelle')


            context_perso = {'police': police, 'mouvements_police': mouvements_police, 'mouvements': mouvements,
                             'etat_police': etat_police}

            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        else:
            return redirect("clients")


    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


# all police garanties
@method_decorator(login_required, name='dispatch')
class PoliceGedView(TemplateView):
    template_name = 'police/ged.html'
    model = Police

    def get(self, request, police_id, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        police = Police.objects.filter(id=police_id, bureau=request.user.bureau, statut_validite=StatutValidite.VALIDE).first()
        if police:
            types_documents = TypeDocument.objects.filter(is_production=1).order_by('libelle')
            documents = Document.objects.filter(police_id=police_id)

            # etat police = dernier motif
            etat_police = police.etat_police

            context_perso = {'police': police, 'documents': documents, 'types_documents': types_documents,
                             'etat_police': etat_police, }

            context = {**context_original, **context_perso}

            return self.render_to_response(context)
        else:
            return redirect("clients")

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


def police_add_document(request, police_id):
    if request.method == "POST":

        form = DocumentForm(request.POST, request.FILES)

        if form.is_valid():

            police = Police.objects.get(id=police_id)
            type_document_id = request.POST.get('type_document')

            document = form.save(commit=False)
            document.client = police.client
            document.police = police
            document.type_document = TypeDocument.objects.get(id=type_document_id)
            document.save()

            pprint("document.fichier")
            pprint(document.fichier.path)



            response = {
                'statut': 1,
                'message': "Enregistrement effectué avec succès !",
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


# get all sinistres for police
@method_decorator(login_required, name='dispatch')
class PoliceSinistresView(TemplateView):
    template_name = 'police/sinistres.html'
    model = DossierSinistre

    def get(self, request, police_id, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        police = Police.objects.filter(id=police_id, bureau=request.user.bureau, statut_validite=StatutValidite.VALIDE).first()
        if police:

            #TODO VIDER LES INTERVENANTS ET DES GARANTIES DU SINISTRE
            if 'intervenants' in request.session:
                del request.session['intervenants']

            if 'garanties_sinistre' in request.session:
                del request.session['garanties_sinistre']

            # Récupération de client
            client = Client.objects.filter(id=police.client_id).first()

            # Récupérer le dernier historique
            dernier_historique = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()

            # Récupérer les assureurs associés à l'historique
            assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id, type_compagnie_id=1).first() if dernier_historique else []
            today = datetime.now(tz=timezone.utc)

            mouvements = Mouvement.objects.filter(type_mouvement_id=2).order_by('libelle')
            typesinistres = TypeSinistre.objects.filter(statut=1).order_by('libelle')
            typeintervenants = TypeIntervenant.objects.filter(statut=1).order_by('libelle')
            typedocuments = TypeDocument.objects.filter(is_sinistre=1).order_by('libelle')
            responsabilites = Responsabilite.objects.filter(statut=1)
            circonstances = Circonstance.objects.filter(statut=1, branche_id=police.produit.branche_id).order_by('libelle')

            garanties = PoliceGarantie.objects.filter(police_id=police.id)
            pays = Pays.objects.all().order_by('nom')
 
            aliments = 0
            aliment = 0
            if police.produit.code == '10001' or police.produit.code == '10002' or police.produit.code == '50001' or police.produit.code == '50002':
                pass
            else:
                aliment = AlimentPolice.objects.filter(police_id=police.id).first()

            date_jour = datetime.now(tz=timezone.utc).strftime('%Y-%m-%d')
            date_fin_effet = police.date_fin_effet.strftime('%Y-%m-%d') if police.date_fin_effet else None

            border_date_color = ""
            if police.date_fin_effet and date_fin_effet > date_jour:
                border_date_color = "green"
            else:
                border_date_color = "red"

            context_perso = {
                'police': police,
                'client': client,
                'dossiers_sinistres': None,
                'sinistres': None,
                'border_date_color': border_date_color,
                'dernier_historique': dernier_historique,
                'assureur_police': assureur_police,
                'today': today,
                'mouvements': mouvements,
                'typesinistres': typesinistres,
                'typeintervenants': typeintervenants,
                'typedocuments': typedocuments,
                'responsabilites': responsabilites,
                'circonstances': circonstances,
                'garanties': garanties,
                'pays': pays,
                'aliment': aliment
            }

            context = {**context_original, **context_perso}

            return self.render_to_response(context)
        else:
            return redirect("clients")

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


def police_sinistres_datatable(request, police_id):
    items_per_page = 10
    page_number = request.GET.get('page')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', items_per_page))
    sort_column_index = int(request.GET.get('order[0][column]'))
    sort_direction = request.GET.get('order[0][dir]')

    search_numero_sinistre = request.GET.get('num_sinistre', '')
    search_type_sinistre = request.GET.get('type_sinistre_id', '')
    search_date_declaration = request.GET.get('date_declaration', '')
    search_date_ouverture = request.GET.get('date_ouverture', '')
    search_value = request.GET.get('search[value]')

    queryset = Sinistre.objects.filter(police_id=police_id).order_by('id')

    if search_numero_sinistre:
        queryset = queryset.filter(numero__contains=search_numero_sinistre)

    if search_type_sinistre:
        queryset = queryset.filter(type_sinistre_id=search_type_sinistre)

    if search_date_declaration:
        queryset = queryset.filter(date_declaration__contains=search_date_declaration)

    if search_date_ouverture:
        queryset = queryset.filter(date_ouverture__contains=search_date_ouverture)

    # Map column index to corresponding model field for sorting
    sort_columns = {
        0: '-numero',
        1: '-date_ouverture',
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
    for s in page_obj:
        detail_url = reverse('sinistre.details', args=[s.id])
        actions_html = f'<a href="{detail_url}"><span class="badge btn-sm btn-details rounded-pill"><i class="fa fa-eye"></i> {_("Détails")}</span></a>&nbsp;&nbsp;'

        # etat sinistre = dernier motif
        etat_sinistre = s.etat_sinistre
        statut_html = f'<span class="badge badge-{transformer_statut(etat_sinistre)}">{etat_sinistre}</span>'

        data_iten = {
            "id": s.id,
            "numero": s.numero if s.numero else "",
            "type_sinistre": s.type_sinistre.libelle if s.type_sinistre else '',
            "date_declaration": s.date_declaration.strftime("%d/%m/%Y"),
            "date_ouverture": s.date_ouverture.strftime("%d/%m/%Y"),
            "statut": statut_html,
            "actions": actions_html,
        }

        data.append(data_iten)

    return JsonResponse({
        "data": data,
        "recordsTotal": queryset.count(),
        "recordsFiltered": paginator.count,
        "draw": int(request.GET.get('draw', 1)),
    })


@method_decorator(login_required, name='dispatch')
class DetailsSinistreView(TemplateView):
    template_name = 'sinistre/index.html'
    model = Sinistre

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        sinistre_id = kwargs['sinistre_id']
        sinistres = Sinistre.objects.filter(id=sinistre_id, bureau=request.user.bureau)
        if sinistres:
            sinistre = sinistres.first()

            #Totaux
            total_franchises = sinistre.total_franchises
            total_capitaux = sinistre.total_capitaux
            total_prime_nette = sinistre.total_prime_nette
            total_prime_ttc = sinistre.total_prime_ttc

            intervenants = SinistreIntervenant.objects.filter(sinistre_id=sinistre_id)
            garantie_sinistres = GarantieSinistre.objects.filter(sinistre_id=sinistre_id)
            mouvement_sinistre = MouvementSinistre.objects.filter(sinistre_id=sinistre_id, statut_validite=StatutValidite.VALIDE).order_by('-id').first()
            aliment_police_sinistre = AlimentPoliceSinistre.objects.filter(sinistre_id=sinistre_id).order_by('-id').first()

            context_perso = {
                'sinistre': sinistre,
                'intervenants': intervenants,
                'garantie_sinistres': garantie_sinistres,
                'mouvement_sinistre': mouvement_sinistre,
                'total_franchises': total_franchises,
                'total_capitaux': total_capitaux,
                'total_prime_nette': total_prime_nette,
                'total_prime_ttc': total_prime_ttc,
                'aliment_police_sinistre': aliment_police_sinistre,
            }
            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        else:
            #liste_clients_url = reverse('clients')
            return redirect("clients")

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


@method_decorator(login_required, name='dispatch')
class SinistreGedView(TemplateView):
    template_name = 'sinistre/ged.html'
    model = Sinistre

    def get(self, request, sinistre_id, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        sinistre = Sinistre.objects.filter(id=sinistre_id, bureau=request.user.bureau).first()
        if sinistre:
            police = Police.objects.filter(id=sinistre.police_id, bureau=request.user.bureau).first()
            types_documents = TypeDocument.objects.filter(is_sinistre=1).order_by('libelle')
            documents = Document.objects.filter(sinistre_id=sinistre_id)

            context_perso = {
                'sinistre': sinistre,
                'police': police,
                'documents': documents,
                'types_documents': types_documents,
            }

            context = {**context_original, **context_perso}

            return self.render_to_response(context)
        else:
            return redirect("clients")

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


# all sinistre avenants
@method_decorator(login_required, name='dispatch')
class SinistreAvenantsView(TemplateView):
    template_name = 'sinistre/avenants.html'
    model = Sinistre

    def get(self, request, sinistre_id, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        sinistre = Sinistre.objects.filter(id=sinistre_id, bureau=request.user.bureau).first()
        if sinistre:
            police = Police.objects.filter(id=sinistre.police_id, bureau=request.user.bureau).first()
            mouvements = Mouvement.objects.filter(type_mouvement_id=2).exclude(code="OS").order_by('libelle')
            mouvements_sinistre = MouvementSinistre.objects.filter(sinistre_id=sinistre_id, statut_validite=StatutValidite.VALIDE).order_by('-id')

            # etat sinistre = dernier motif
            etat_sinistre = sinistre.etat_sinistre

            if etat_sinistre != "Suspendu":
                # Retirer mise en vigueur (REMVIG) sauf cas de suspention
                mouvements = mouvements.exclude(code="REMVIG").order_by('libelle')


            context_perso = {'sinistre': sinistre, 'police': police, 'mouvements_sinistre': mouvements_sinistre, 'mouvements': mouvements,
                             'etat_sinistre': etat_sinistre}

            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        else:
            return redirect("clients")


    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


# ajout d'avenant
def add_sinistre_avenant(request, sinistre_id):
    sinistre = Sinistre.objects.get(id=sinistre_id)

    if request.method == 'POST':

        if request.POST.get('mouvement') in ["19", "20"]:
            request.session['add_sinistre_avenant'] = request.POST
            response = {
                'statut': 1,
                'message': "Enregistrement effectuée avec succès !",
                'data': {}
            }

        else:
            date_cloture_sinistre = request.POST.get('date_cloture_sinistre')

            mouvement_sinistre = MouvementSinistre.objects.create(
                sinistre=sinistre,
                police_id=sinistre.police_id,
                mouvement_id=request.POST.get('mouvement'),
                motif_id=request.POST.get('motif'),
                date_effet=request.POST.get('date_effet'),
                date_cloture_sinistre=date_cloture_sinistre if date_cloture_sinistre else None,
                created_by=request.user
            )
            mouvement_sinistre.save()

            mouvement = Mouvement.objects.get(id=mouvement_sinistre.mouvement_id)

            motif = Motif.objects.get(id=mouvement_sinistre.motif_id)

            response = {
                'statut': 1,
                'message': "Enregistrement effectuée avec succès !",
                'data': {
                    'id': mouvement_sinistre.pk,
                    'mouvement': mouvement.libelle,
                    'motif': motif.libelle,
                    'date_effet': mouvement_sinistre.date_effet,
                    'date_cloture_sinistre': mouvement_sinistre.date_cloture_sinistre,
                }
            }

        return JsonResponse(response)


def sinistre_add_document(request, sinistre_id):
    if request.method == "POST":

        form = DocumentForm(request.POST, request.FILES)

        if form.is_valid():

            sinistre = Sinistre.objects.get(id=sinistre_id)
            type_document_id = request.POST.get('type_document')

            document = form.save(commit=False)
            document.client = sinistre.client
            document.sinistre = sinistre
            document.type_document = TypeDocument.objects.get(id=type_document_id)
            document.save()

            pprint("document.fichier")
            pprint(document.fichier.path)

            response = {
                'statut': 1,
                'message': "Enregistrement effectué avec succès !",
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


def police_save_sinistre(request, police_id):
    police = Police.objects.get(id=police_id)
    client = Client.objects.get(id=police.client_id)

    if request.method == 'POST':

        form = SinistreForm(request.POST)

        if form.is_valid():
            vehicule_id = request.POST.get('vehicule_id')
            marchandise_id = request.POST.get('marchandise_id')
            autre_risque_id = request.POST.get('autre_risque_id')
            compagnie_id = request.POST.get('compagnie_id')
            date_survenance = request.POST.get('date_survenance')
            date_ouverture = request.POST.get('date_ouverture')
            date_cloture = request.POST.get('date_cloture')
            risque = request.POST.get('risque')
            date_declaration = request.POST.get('date_declaration')
            date_reouverture = request.POST.get('date_reouverture')
            sinistre_recours = request.POST.get('sinistre_recours')
            circonstance_id = request.POST.get('circonstance_id')
            lieu_survenance = request.POST.get('lieu_survenance')
            tva_recuperee = request.POST.get('tva_recuperee')
            type_sinistre_id = request.POST.get('type_sinistre_id')
            franchise = request.POST.get('franchise').replace(' ', '')
            responsabilite_id = request.POST.get('responsabilite_id')
            fait_generateur = request.POST.get('fait_generateur')
            point_de_choc = request.POST.get('point_de_choc')
            commentaire = request.POST.get('commentaire')
            numero = request.POST.get('numero')

            sinistre_created = Sinistre(
                bureau_id=client.bureau_id,
                client_id=client.id,
                police_id=police.id,
                compagnie_id=compagnie_id,
                type_sinistre_id=type_sinistre_id,
                responsabilite_id=responsabilite_id,
                circonstance_id=circonstance_id,
                created_by=request.user,
                numero=numero,
                created_at=datetime.now(),
                date_survenance=date_survenance if date_survenance else None,
                date_declaration=date_declaration if date_declaration else None,
                date_ouverture=date_ouverture if date_ouverture else None,
                date_cloture=date_cloture if date_cloture else None,
                date_reouverture=date_reouverture if date_reouverture else None,
                sinistre_recours=sinistre_recours,
                lieu_survenance=lieu_survenance,
                tva_recuperee=tva_recuperee,
                fait_generateur=fait_generateur,
                point_de_choc=point_de_choc,
                commentaire=commentaire,
                franchise=supprimer_espaces(franchise) if franchise else 0,
            )
            sinistre_created.save()

            code_bureau = request.user.bureau.code
            sinistre_created.numero_provisoire = str(code_bureau) + 'P' + str(Date.today().year)[-2:] + str(
                sinistre_created.pk).zfill(6)
            if sinistre_created.numero == "":
                sinistre_created.numero = sinistre_created.numero_provisoire

            sinistre_created.save()

            sinistre = Sinistre.objects.get(id=sinistre_created.pk)

            # Créer une ligne de mouvement_sinistre avec le mouvement ouverture sinistre et le motif ouverture sinistre
            ms = MouvementSinistre()
            ms.sinistre = sinistre
            ms.police = police
            ms.mouvement = Mouvement.objects.get(code='OS')
            ms.motif = Motif.objects.get(code='OS')
            ms.date_effet = sinistre.date_ouverture
            ms.created_by = request.user
            ms.save()

            # Créer la ligne de l'aliment lié au sinistre
            aliment_police = None

            if vehicule_id:
                try:
                    aliment_police = AlimentPolice.objects.get(vehicule_id=vehicule_id)
                except AlimentPolice.DoesNotExist:
                    pass  # Gérer l'absence de l'objet si nécessaire

            if marchandise_id:
                try:
                    aliment_police = AlimentPolice.objects.get(marchandise_id=marchandise_id)
                except AlimentPolice.DoesNotExist:
                    pass  # Gérer l'absence de l'objet si nécessaire

            if not aliment_police and autre_risque_id:
                try:
                    aliment_police = AlimentPolice.objects.get(autre_risque_id=autre_risque_id)
                except AlimentPolice.DoesNotExist:
                    pass  # Gérer l'absence de l'objet si nécessaire

            if aliment_police:
                aliment_sinitre_created = AlimentPoliceSinistre(
                    police=police,
                    sinistre=sinistre,
                    aliment_police=aliment_police,
                    risque=risque,
                )
                aliment_sinitre_created.save()
            else:
                # Ajouter une gestion si l'aliment_police n'existe pas.
                print(f"Aucun AlimentPolice trouvé pour vehicule_id={vehicule_id} ou marchandise_id={marchandise_id} ou autre_risque_id={autre_risque_id}")

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


def police_save_sinistre(request, police_id):
    police = Police.objects.get(id=police_id)
    client = Client.objects.get(id=police.client_id)

    if request.method == 'POST':

        form = SinistreForm(request.POST)

        if form.is_valid():
            vehicule_id = request.POST.get('vehicule_id')
            marchandise_id = request.POST.get('marchandise_id')
            autre_risque_id = request.POST.get('autre_risque_id')
            compagnie_id = request.POST.get('compagnie_id')
            date_survenance = request.POST.get('date_survenance')
            date_ouverture = request.POST.get('date_ouverture')
            date_cloture = request.POST.get('date_cloture')
            risque = request.POST.get('risque')
            date_declaration = request.POST.get('date_declaration')
            date_reouverture = request.POST.get('date_reouverture')
            sinistre_recours = request.POST.get('sinistre_recours')
            circonstance_id = request.POST.get('circonstance_id')
            lieu_survenance = request.POST.get('lieu_survenance')
            tva_recuperee = request.POST.get('tva_recuperee')
            type_sinistre_id = request.POST.get('type_sinistre_id')
            franchise = request.POST.get('franchise').replace(' ', '')
            responsabilite_id = request.POST.get('responsabilite_id')
            fait_generateur = request.POST.get('fait_generateur')
            point_de_choc = request.POST.get('point_de_choc')
            commentaire = request.POST.get('commentaire')
            numero = request.POST.get('numero')

            sinistre_created = Sinistre(
                bureau_id=client.bureau_id,
                client_id=client.id,
                police_id=police.id,
                compagnie_id=compagnie_id,
                type_sinistre_id=type_sinistre_id,
                responsabilite_id=responsabilite_id,
                circonstance_id=circonstance_id,
                created_by=request.user,
                numero=numero,
                created_at=datetime.now(),
                date_survenance=date_survenance if date_survenance else None,
                date_declaration=date_declaration if date_declaration else None,
                date_ouverture=date_ouverture if date_ouverture else None,
                date_cloture=date_cloture if date_cloture else None,
                date_reouverture=date_reouverture if date_reouverture else None,
                sinistre_recours=sinistre_recours,
                lieu_survenance=lieu_survenance,
                tva_recuperee=tva_recuperee,
                fait_generateur=fait_generateur,
                point_de_choc=point_de_choc,
                commentaire=commentaire,
                franchise=supprimer_espaces(franchise) if franchise else 0,
            )
            sinistre_created.save()

            code_bureau = request.user.bureau.code
            sinistre_created.numero_provisoire = str(code_bureau) + 'P' + str(Date.today().year)[-2:] + str(
                sinistre_created.pk).zfill(6)
            if sinistre_created.numero == "":
                sinistre_created.numero = sinistre_created.numero_provisoire

            sinistre_created.save()

            sinistre = Sinistre.objects.get(id=sinistre_created.pk)

            # Créer une ligne de mouvement_sinistre avec le mouvement ouverture sinistre et le motif ouverture sinistre
            ms = MouvementSinistre()
            ms.sinistre = sinistre
            ms.police = police
            ms.mouvement = Mouvement.objects.get(code='OS')
            ms.motif = Motif.objects.get(code='OS')
            ms.date_effet = sinistre.date_ouverture
            ms.created_by = request.user
            ms.save()

            # Créer la ligne de l'aliment lié au sinistre
            aliment_police = None

            if vehicule_id:
                try:
                    aliment_police = AlimentPolice.objects.get(vehicule_id=vehicule_id)
                except AlimentPolice.DoesNotExist:
                    pass  # Gérer l'absence de l'objet si nécessaire

            if marchandise_id:
                try:
                    aliment_police = AlimentPolice.objects.get(marchandise_id=marchandise_id)
                except AlimentPolice.DoesNotExist:
                    pass  # Gérer l'absence de l'objet si nécessaire

            if not aliment_police and autre_risque_id:
                try:
                    aliment_police = AlimentPolice.objects.get(autre_risque_id=autre_risque_id)
                except AlimentPolice.DoesNotExist:
                    pass  # Gérer l'absence de l'objet si nécessaire

            if aliment_police:
                aliment_sinitre_created = AlimentPoliceSinistre(
                    police=police,
                    sinistre=sinistre,
                    aliment_police=aliment_police,
                    risque=risque,
                )
                aliment_sinitre_created.save()
            else:
                # Ajouter une gestion si l'aliment_police n'existe pas.
                print(f"Aucun AlimentPolice trouvé pour vehicule_id={vehicule_id} ou marchandise_id={marchandise_id} ou autre_risque_id={autre_risque_id}")

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
                )
                intervenant_created.save()
                intervenant = Intervenant.objects.get(id=intervenant_created.pk)

                # Créer la ligne intervenant du sinistre
                aliment_sinitre_created = SinistreIntervenant(
                    intervenant_id=intervenant.id,
                    sinistre=sinistre
                )
                aliment_sinitre_created.save()

            # Récupérer les garanties de la session
            garanties_sinistre = request.session.get("garanties_sinistre", [])
            for garantie_sinistre in garanties_sinistre:
                garantie_sinistre_created = GarantieSinistre(
                    sinistre=sinistre,
                    circonstance_id=circonstance_id,
                    garantie_id=garantie_sinistre.get('id'),
                    franchise=supprimer_espaces(garantie_sinistre.get('franchise', 0)) if garantie_sinistre.get('franchise', 0) else None,
                    capital=supprimer_espaces(garantie_sinistre.get('capital', 0)) if garantie_sinistre.get('capital', 0) else None,
                    prime_nette=supprimer_espaces(garantie_sinistre.get('prime_net', 0)) if garantie_sinistre.get('prime_net', 0) else None,
                    prime_ttc=supprimer_espaces(garantie_sinistre.get('prime_ttc', 0)) if garantie_sinistre.get('prime_ttc', 0) else None,
                )
                garantie_sinistre_created.save()

            # Récupérer les données des provisions
            provisions_data = json.loads(request.POST.get('provisions', '{}'))
            print('provisions_data : ', provisions_data)
            # Enregistrer les provisions
            for postedommage_id, garanties in provisions_data.items():

                for garantie_id, montants in garanties.items():
                    Provision.objects.create(
                        sinistre=sinistre,
                        garantie_id=garantie_id,
                        poste_dommage=PosteDommage.objects.get(libelle=postedommage_id),
                        estimation=supprimer_espaces(montants.get("estimation")) if montants.get("estimation") else None,
                        deja_regle=supprimer_espaces(montants.get("deja_regle")) if montants.get("deja_regle") else None,
                        provision=supprimer_espaces(montants.get("provision")) if montants.get("provision") else None,
                    )

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


# modification de sinistre
@transaction.atomic  # open a transaction
@login_required
def modifier_sinistre(request, sinistre_id):

    if request.method == 'POST':
        sinistre_old = Sinistre.objects.get(id=sinistre_id)
        alimentpolicesinistre = AlimentPoliceSinistre.objects.filter(sinistre_id=sinistre_old.id).first()

        vehicule_id = request.POST.get('vehicule_id')
        marchandise_id = request.POST.get('marchandise_id')
        autre_risque_id = request.POST.get('autre_risque_id')
        date_survenance = request.POST.get('date_survenance')
        date_ouverture = request.POST.get('date_ouverture')
        date_cloture = request.POST.get('date_cloture')
        risque = request.POST.get('risque')
        date_declaration = request.POST.get('date_declaration')
        date_reouverture = request.POST.get('date_reouverture')
        sinistre_recours = request.POST.get('sinistre_recours')
        circonstance_id = request.POST.get('circonstance_id')
        lieu_survenance = request.POST.get('lieu_survenance')
        tva_recuperee = request.POST.get('tva_recuperee')
        type_sinistre_id = request.POST.get('type_sinistre_id')
        franchise = request.POST.get('franchise').replace(' ', '')
        responsabilite_id = request.POST.get('responsabilite_id')
        fait_generateur = request.POST.get('fait_generateur')
        point_de_choc = request.POST.get('point_de_choc')
        commentaire = request.POST.get('commentaire')

        historiq_sinistre_created = HistoriqueSinistre(
            sinistre_id=sinistre_old.id,
            bureau_id=sinistre_old.bureau_id,
            client_id=sinistre_old.client_id,
            police_id=sinistre_old.police_id,
            compagnie_id=sinistre_old.compagnie_id,
            type_sinistre_id=sinistre_old.type_sinistre_id,
            responsabilite_id=sinistre_old.responsabilite_id,
            circonstance_id=sinistre_old.circonstance_id,
            created_by=sinistre_old.created_by,
            numero=sinistre_old.numero,
            numero_provisoire=sinistre_old.numero_provisoire,
            created_at=sinistre_old.created_at,
            date_survenance=sinistre_old.date_survenance,
            date_declaration=sinistre_old.date_declaration,
            date_ouverture=sinistre_old.date_ouverture,
            date_cloture=sinistre_old.date_cloture,
            date_reouverture=sinistre_old.date_reouverture,
            sinistre_recours=sinistre_old.sinistre_recours,
            lieu_survenance=sinistre_old.lieu_survenance,
            tva_recuperee=sinistre_old.tva_recuperee,
            fait_generateur=sinistre_old.fait_generateur,
            point_de_choc=sinistre_old.point_de_choc,
            commentaire=sinistre_old.commentaire,
            franchise=sinistre_old.franchise,
        )
        historiq_sinistre_created.save()
        historiq_sinistre = HistoriqueSinistre.objects.get(id=historiq_sinistre_created.pk)

        # Mise à jour du sinistre
        sinistre = Sinistre.objects.filter(id=sinistre_id).update(
            type_sinistre_id=type_sinistre_id,
            responsabilite_id=responsabilite_id,
            circonstance_id=circonstance_id,
            updated_at=datetime.now(),
            date_survenance=date_survenance if date_survenance else None,
            date_declaration=date_declaration if date_declaration else None,
            date_ouverture=date_ouverture if date_ouverture else None,
            date_cloture=date_cloture if date_cloture else None,
            date_reouverture=date_reouverture if date_reouverture else None,
            sinistre_recours=sinistre_recours,
            lieu_survenance=lieu_survenance,
            tva_recuperee=tva_recuperee,
            fait_generateur=fait_generateur,
            point_de_choc=point_de_choc,
            commentaire=commentaire,
            franchise=supprimer_espaces(franchise) if franchise else 0,
            updated_by=request.user
        )
        sinistre = Sinistre.objects.get(id=sinistre_id)

        # Provisions sinistre
        with transaction.atomic():
            provisions_existantes = {
                (p.poste_dommage.libelle, str(p.garantie_id)): p
                for p in Provision.objects.filter(sinistre=sinistre)
            }
            provisions_data = json.loads(request.POST.get('provisions', '{}'))

            historiques = []
            provisions_a_supprimer = []
            provisions_a_creer = []

            for poste_dommage_libelle, garanties in provisions_data.items():
                # Ignorer les provisions avec le libellé "Totaux"
                if poste_dommage_libelle == "Totaux":
                    continue
                print('poste_dommage_libelle : ', poste_dommage_libelle)
                poste_dommage_obj = PosteDommage.objects.get(libelle=poste_dommage_libelle)

                for garantie_id, montants in garanties.items():
                    estimation = supprimer_espaces(montants.get("estimation")) if montants.get("estimation") else None
                    deja_regle = supprimer_espaces(montants.get("deja_regle")) if montants.get("deja_regle") else None
                    provision_val = supprimer_espaces(montants.get("provision")) if montants.get("provision") else None

                    key = (poste_dommage_libelle, garantie_id)
                    if key in provisions_existantes:
                        provision_obj = provisions_existantes[key]

                        # Enregistrer l'historique avant la mise à jour
                        historiques.append(HistoriqueProvision(
                            sinistre=provision_obj.sinistre,
                            historique_sinistre_id=historiq_sinistre.id,
                            garantie=provision_obj.garantie,
                            poste_dommage=provision_obj.poste_dommage,
                            estimation=provision_obj.estimation,
                            deja_regle=provision_obj.deja_regle,
                            provision=provision_obj.provision,
                        ))

                        # Mettre à jour la provision existante
                        provision_obj.estimation = estimation
                        provision_obj.deja_regle = deja_regle
                        provision_obj.provision = provision_val
                        provision_obj.save()

                        del provisions_existantes[key]  # Supprimer de la liste des provisions existantes
                    else:
                        # Créer une nouvelle provision
                        provisions_a_creer.append(Provision(
                            sinistre=sinistre,
                            garantie_id=garantie_id,
                            poste_dommage=poste_dommage_obj,
                            estimation=estimation,
                            deja_regle=deja_regle,
                            provision=provision_val,
                        ))

            # Supprimer les provisions restantes (celles qui n'étaient pas dans les données reçues)
            for provision_obj in provisions_existantes.values():
                historiques.append(HistoriqueProvision(
                    sinistre=provision_obj.sinistre,
                    historique_sinistre_id=historiq_sinistre.id,
                    garantie=provision_obj.garantie,
                    poste_dommage=provision_obj.poste_dommage,
                    estimation=provision_obj.estimation,
                    deja_regle=provision_obj.deja_regle,
                    provision=provision_obj.provision,
                ))
                provisions_a_supprimer.append(provision_obj)

            HistoriqueProvision.objects.bulk_create(historiques)
            Provision.objects.bulk_create(provisions_a_creer)
            Provision.objects.filter(id__in=[p.id for p in provisions_a_supprimer]).delete()

        #Garanties sinistre
        with transaction.atomic():
            # 1️⃣ Récupérer les anciennes garanties du sinistre
            garanties_existantes = GarantieSinistre.objects.filter(sinistre=sinistre)

            # 2️⃣ Enregistrer dans HistoriqueGarantieSinistre avant modification
            historiques = []
            for garantie in garanties_existantes:
                historiques.append(HistoriqueGarantieSinistre(
                    historique_sinistre_id=historiq_sinistre.id,
                    circonstance=garantie.circonstance,
                    garantie=garantie.garantie,
                    franchise=garantie.franchise,
                    capital=garantie.capital,
                    prime_nette=garantie.prime_nette,
                    prime_ttc=garantie.prime_ttc,
                ))
            HistoriqueGarantieSinistre.objects.bulk_create(historiques)

            # 3️⃣ Parcourir les garanties récupérées depuis la session
            garanties_sinistre = request.session.get("garanties_sinistre", [])

            for garantie_sinistre in garanties_sinistre:
                garantie_id = garantie_sinistre.get('id')

                # Vérifie si la garantie existe déjà pour ce sinistre + circonstance
                garantie_obj, created = GarantieSinistre.objects.update_or_create(
                    sinistre=sinistre,
                    circonstance_id=circonstance_id,
                    garantie_id=garantie_id,
                    defaults={
                        'franchise': supprimer_espaces(garantie_sinistre.get('franchise', 0)) if garantie_sinistre.get(
                            'franchise', 0) else None,
                        'capital': supprimer_espaces(garantie_sinistre.get('capital', 0)) if garantie_sinistre.get(
                            'capital', 0) else None,
                        'prime_nette': supprimer_espaces(
                            garantie_sinistre.get('prime_net', 0)) if garantie_sinistre.get('prime_net', 0) else None,
                        'prime_ttc': supprimer_espaces(garantie_sinistre.get('prime_ttc', 0)) if garantie_sinistre.get(
                            'prime_ttc', 0) else None,
                    }
                )

        #Intervenants sinistre
        with transaction.atomic():
            # 1️⃣ Récupérer les anciens intervenants liés au sinistre
            anciens_intervenants = SinistreIntervenant.objects.filter(sinistre=sinistre)

            # 2️⃣ Enregistrer dans HistoriqueSinistreIntervenant
            historiques = []
            for si in anciens_intervenants:
                historique = HistoriqueSinistreIntervenant(
                    historique_sinistre_id=historiq_sinistre.id,
                    intervenant=si.intervenant
                )
                historiques.append(historique)
            HistoriqueSinistreIntervenant.objects.bulk_create(historiques)

            # 3️⃣ Parcourir les intervenants récupérés depuis la session
            intervenants = request.session.get('intervenants', [])

            for intervenant_data in intervenants:
                portable = intervenant_data.get('portable')
                email = intervenant_data.get('email')

                # Chercher si intervenant existe déjà (portable + email pour garantir unicité)
                intervenant_qs = Intervenant.objects.filter(portable=portable, email=email)

                if intervenant_qs.exists():
                    intervenant_obj = intervenant_qs.first()
                    # Mise à jour des informations
                    Intervenant.objects.filter(id=intervenant_obj.id).update(
                        type_intervenant_id=intervenant_data.get('type_intervenant_id'),
                        pays_id=intervenant_data.get('pays_id'),
                        nom=intervenant_data.get('nom'),
                        prenoms=intervenant_data.get('prenoms'),
                        telephone=intervenant_data.get('telephone'),
                        fax=intervenant_data.get('fax'),
                        code_postal=intervenant_data.get('code_postal'),
                        boite_postale=intervenant_data.get('boite_postale'),
                        ville=intervenant_data.get('ville'),
                    )
                else:
                    # Créer un nouvel intervenant
                    intervenant_obj = Intervenant.objects.create(
                        type_intervenant_id=intervenant_data.get('type_intervenant_id'),
                        pays_id=intervenant_data.get('pays_id'),
                        nom=intervenant_data.get('nom'),
                        prenoms=intervenant_data.get('prenoms'),
                        telephone=intervenant_data.get('telephone'),
                        portable=portable,
                        fax=intervenant_data.get('fax'),
                        email=email,
                        code_postal=intervenant_data.get('code_postal'),
                        boite_postale=intervenant_data.get('boite_postale'),
                        ville=intervenant_data.get('ville'),
                    )

                # Liaison SinistreIntervenant
                SinistreIntervenant.objects.update_or_create(
                    sinistre=sinistre,
                    intervenant=intervenant_obj
                )

        # Gérer la ligne de l'aliment lié au sinistre
        aliment_police = None

        if vehicule_id:
            try:
                aliment_police = AlimentPolice.objects.get(vehicule_id=vehicule_id)
            except AlimentPolice.DoesNotExist:
                pass  # Gérer l'absence de l'objet si nécessaire

        elif marchandise_id:
            try:
                aliment_police = AlimentPolice.objects.get(marchandise_id=marchandise_id)
            except AlimentPolice.DoesNotExist:
                pass  # Gérer l'absence de l'objet si nécessaire

        if not aliment_police and autre_risque_id:
            try:
                aliment_police = AlimentPolice.objects.get(autre_risque_id=autre_risque_id)
            except AlimentPolice.DoesNotExist:
                pass  # Gérer l'absence de l'objet si nécessaire

        if aliment_police:
            if alimentpolicesinistre:
                histo_aliment_sinitre = HistoriqueAlimentPoliceSinistre(
                    historique_sinistre_id=historiq_sinistre.id,
                    police_id=sinistre.police_id,
                    sinistre=sinistre,
                    aliment_police=aliment_police,
                    risque=risque,
                )
                histo_aliment_sinitre.save()

                # Mise à jour
                aliment_sinitre = AlimentPoliceSinistre.objects.filter(id=alimentpolicesinistre.id).update(
                    aliment_police=aliment_police,
                    risque=risque,
                )
            else:
                aliment_sinitre_created = AlimentPoliceSinistre(
                    police_id=sinistre.police_id,
                    sinistre=sinistre,
                    aliment_police=aliment_police,
                    risque=risque,
                )
                aliment_sinitre_created.save()
        else:
            # Ajouter une gestion si l'aliment_police n'existe pas.
            print(f"Aucun AlimentPolice trouvé pour vehicule_id={vehicule_id} ou marchandise_id={marchandise_id} ou autre_risque_id={autre_risque_id}")

        # Relier l'historique sinistre au mouvement sinistre
        # Obtenir l'avant-dernier mouvement de sinistre
        mouvement_sinistre = MouvementSinistre.objects.filter(sinistre_id=sinistre_id, historique_sinistre_id__isnull=True).order_by('-id').first()
        if mouvement_sinistre:
            mouvement_sinistre.historique_sinistre_id = historiq_sinistre.id
            mouvement_sinistre.save()

        # Création du monvement sinistre
        movement_data_save = request.session.get('add_sinistre_avenant')
        print('movement_data_save : ', movement_data_save)
        if movement_data_save:
            mouvement_sinistre = MouvementSinistre.objects.create(sinistre_id=sinistre.id,
                                                                  mouvement_id=movement_data_save.get('mouvement'),
                                                                  motif_id=movement_data_save.get('motif'),
                                                                  date_effet=movement_data_save.get(
                                                                      'date_effet') if movement_data_save.get(
                                                                      'date_effet') else None,
                                                                  created_by=request.user
                                                                  )
            mouvement_sinistre.save()

        response = {
            'statut': 1,
            'message': "Sinistre modifié avec succès !",
            'data': {
            }
        }

        return JsonResponse(response)

    else:

        sinistre = Sinistre.objects.get(id=sinistre_id)
        police = Police.objects.filter(id=sinistre.police_id, bureau=request.user.bureau, statut_validite=StatutValidite.VALIDE).first()
        client = Client.objects.filter(id=police.client_id).first()

        # Récupérer le dernier historique
        dernier_historique = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()

        # Récupérer les assureurs associés à l'historique
        assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id,
                                                        type_compagnie_id=1).first() if dernier_historique else []
        today = datetime.now(tz=timezone.utc)

        mouvements = Mouvement.objects.filter(type_mouvement_id=2).order_by('libelle')
        typesinistres = TypeSinistre.objects.filter(statut=1).order_by('libelle')
        typeintervenants = TypeIntervenant.objects.filter(statut=1).order_by('libelle')
        typedocuments = TypeDocument.objects.filter(is_sinistre=1).order_by('libelle')
        responsabilites = Responsabilite.objects.filter(statut=1)
        #circonstances = Circonstance.objects.filter(statut=1, branche_id=police.produit.branche_id).order_by('libelle')
        circonstances = Circonstance.objects.filter(statut=1).order_by('libelle')
        pays = Pays.objects.all().order_by('nom')

        aliments = 0
        aliment = 0
        if police.produit.code == '10001' or police.produit.code == '10002' or police.produit.code == '50001' or police.produit.code == '50002':
            aliments = AlimentPolice.objects.filter(police_id=police.id)
        else:
            aliment = AlimentPolice.objects.filter(police_id=police.id).first()

        alimentpolicesinistre = AlimentPoliceSinistre.objects.filter(sinistre_id=sinistre.id).first()

        return render(request, 'sinistre/modal_sinistre_modification.html',{
          'sinistre': sinistre,
          'police': police,
          'client': client,
          'dernier_historique': dernier_historique,
          'assureur_police': assureur_police,
          'today': today,
          'mouvements': mouvements,
          'typesinistres': typesinistres,
          'typeintervenants': typeintervenants,
          'typedocuments': typedocuments,
          'responsabilites': responsabilites,
          'circonstances': circonstances,
          'pays': pays,
          'aliments': aliments,
          'aliment': aliment,
          'alimentpolicesinistre': alimentpolicesinistre,
        })


def information_vehicule(request, vehicule_id):
    vehicule = Vehicule.objects.filter(id=vehicule_id).first()
    if not vehicule:
        return JsonResponse({'error': 'Véhicule non trouvé'}, status=404)

    # Récupérer les informations de aliment_police associées
    aliment = AlimentPolice.objects.filter(vehicule=vehicule).first()

    data = {
        'id': vehicule.id,
        'numero_immatriculation': vehicule.numero_immatriculation,
        'marque': vehicule.marque,
        'risque_info': vehicule.marque+'-'+vehicule.numero_immatriculation,
        'date_entree': aliment.date_entree if aliment else None,
        'date_sortie': aliment.date_sortie if aliment else None,
    }

    return JsonResponse(data)


@require_GET
def search_vehicules(request, police_id):
    immatriculation = request.GET.get('immatriculation', '').strip()
    if len(immatriculation) < 2:
        return JsonResponse([], safe=False)

    vehicules = Vehicule.objects.filter(
        numero_immatriculation__icontains=immatriculation,
        alimentpolice__police_id=police_id,
        alimentpolice__statut='ACTIF'
    ).distinct().values('id', 'numero_immatriculation', 'marque', 'modele')

    return JsonResponse(list(vehicules), safe=False)


@require_GET
def vehicule_detail(request, vehicule_id):
    vehicule = get_object_or_404(Vehicule, id=vehicule_id)

    alimentinfo = AlimentPolice.objects.filter(vehicule_id=vehicule.id).first()

    data = {
        'id': vehicule.id,
        'num_serie': vehicule.numero_serie,
        'marque': vehicule.marque,
        'modele': vehicule.modele,
        'numero_immatriculation': vehicule.numero_immatriculation,
        'usage': alimentinfo.usage.libelle if alimentinfo and alimentinfo.usage.libelle else '',
        'date_entree': alimentinfo.date_entree.strftime('%Y-%m-%d') if alimentinfo and alimentinfo.date_entree else '',
        'date_sortie': alimentinfo.date_sortie.strftime('%Y-%m-%d') if alimentinfo and alimentinfo.date_sortie else '',
    }

    return JsonResponse(data)


def information_marchandise(request, marchandise_id):
    marchandise = Marchandise.objects.filter(id=marchandise_id).first()
    if not marchandise:
        return JsonResponse({'error': 'Marchandise non trouvée'}, status=404)

    # Récupérer les informations de aliment_police associées
    aliment = AlimentPolice.objects.filter(marchandise=marchandise).first()

    data = {
        'id': marchandise.id,
        'numero_certificat': marchandise.num_certificat,
        'description': marchandise.marchandises_description,
        'risque_info': marchandise.num_certificat+'-'+marchandise.marchandises_description,
    }

    return JsonResponse(data)


@csrf_exempt
def get_intervenants_session(request):
    try:
        police_id = request.GET.get('police_id')
        police = Police.objects.filter(
            id=police_id,
            bureau=request.user.bureau,
            statut_validite=StatutValidite.VALIDE
        ).first()

        if not police:
            return JsonResponse({'success': False, 'message': "Police non trouvée."}, status=404)

        client = Client.objects.filter(id=police.client_id).first()
        intervenants = request.session.setdefault('intervenants', [])

        if client:
            client_intervenant = {
                'id': str(uuid.uuid4()),  # ID unique pour le client
                'police_id': police.id,
                'type_intervenant_id': 1,
                'typeintervenant': 'Tiers Personne',
                'nom': client.nom.strip().upper(),
                'prenoms': client.prenoms.strip().upper(),
                'portable': client.telephone_fixe.strip() if client.telephone_fixe else '',
                'telephone': client.telephone_mobile.strip() if client.telephone_mobile else '',
                'email': client.email.strip().lower() if client.email else '',
                'code_postal': client.adresse,
                'boite_postale': client.adresse_postale,
                'ville': client.ville,
                'pays_id': client.pays_id
            }

            # Vérification simplifiée de l'existence de l'intervenant
            existe_deja = any(
                intervenant['nom'] == client_intervenant['nom'] and
                intervenant['prenoms'] == client_intervenant['prenoms'] and
                intervenant['typeintervenant'] == client_intervenant['typeintervenant']
                for intervenant in intervenants
            )

            if not existe_deja:
                intervenants.insert(0, client_intervenant)
                request.session['intervenants'] = intervenants

        return JsonResponse({'success': True, 'data': intervenants}, status=200)

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
def get_intervenants_session_sinistre(request):
    sinistre_id = request.GET.get('sinistre_id')
    sinistre = Sinistre.objects.filter(id=sinistre_id).first()

    if not sinistre:
        return JsonResponse({'success': False, 'message': "Sinistre non trouvé."}, status=404)

    intervenants_sinistre = SinistreIntervenant.objects.filter(sinistre_id=sinistre.id).order_by('-id')
    intervenants_session = request.session.setdefault('intervenants', [])

    for intervenant_sinistre in intervenants_sinistre:
        sinistre_intervenant = {
            'id': str(uuid.uuid4()),
            'sinistre_id': sinistre_id,
            'police_id': sinistre.police_id,
            'type_intervenant_id': intervenant_sinistre.intervenant.type_intervenant_id,
            'typeintervenant': intervenant_sinistre.intervenant.type_intervenant.libelle,
            'nom': intervenant_sinistre.intervenant.nom,
            'prenoms': intervenant_sinistre.intervenant.prenoms,
            'portable': intervenant_sinistre.intervenant.portable,
            'telephone': intervenant_sinistre.intervenant.telephone,
            'fax': intervenant_sinistre.intervenant.fax,
            'email': intervenant_sinistre.intervenant.email,
            'code_postal': intervenant_sinistre.intervenant.code_postal,
            'boite_postale': intervenant_sinistre.intervenant.boite_postale,
            'ville': intervenant_sinistre.intervenant.ville,
            'pays_id': intervenant_sinistre.intervenant.pays_id
        }

        # Vérification simplifiée de l'existence de l'intervenant dans la session
        existe_deja = any(
            intervenant['nom'] == sinistre_intervenant['nom'] and
            intervenant['prenoms'] == sinistre_intervenant['prenoms'] and
            intervenant['typeintervenant'] == sinistre_intervenant['typeintervenant']
            for intervenant in intervenants_session
        )

        if not existe_deja:
            intervenants_session.insert(0, sinistre_intervenant)
            request.session['intervenants'] = intervenants_session

    return JsonResponse({"intervenants": request.session['intervenants']})


@csrf_exempt
def add_intervenant_session(request):
    if request.method == 'POST':
        try:
            typeintervenant_id = request.POST.get('typeintervenant_id')
            police_id = request.POST.get('police_id')
            typeintervenant = TypeIntervenant.objects.filter(id=typeintervenant_id).first()

            if not typeintervenant:
                return JsonResponse({'success': False, 'message': 'Type intervenant non trouvé.'}, status=400)

            # Récupération des données du formulaire
            nom = request.POST.get('nom', '')
            prenoms = request.POST.get('prenoms', '')
            portable = request.POST.get('portable', '')
            email = request.POST.get('email', '')
            telephone = request.POST.get('telephone', '')
            fax = request.POST.get('fax', '')
            code_postal = request.POST.get('code_postal', '')
            boite_postale = request.POST.get('boite_postale', '')
            ville = request.POST.get('ville', '')
            pays_id = request.POST.get('pays_id', '')

            intervenants_existant = request.session.setdefault('intervenants', [])

            # Vérification simplifiée de l'existence de l'intervenant
            existe_deja = any(
                intervenant['nom'] == nom and
                intervenant['prenoms'] == prenoms and
                intervenant['typeintervenant'] == typeintervenant.libelle
                for intervenant in intervenants_existant
            )

            if existe_deja:
                return JsonResponse({'success': False, 'message': "Cet intervenant existe déjà en session."}, status=400)

            # Création du nouvel intervenant
            nouvel_intervenant = {
                'id': str(uuid.uuid4()),  # ID unique
                'police_id': police_id,
                'type_intervenant_id': typeintervenant_id,
                'typeintervenant': typeintervenant.libelle,
                'nom': nom,
                'prenoms': prenoms,
                'portable': portable,
                'telephone': telephone,
                'fax': fax,
                'email': email,
                'code_postal': code_postal,
                'boite_postale': boite_postale,
                'ville': ville,
                'pays_id': pays_id
            }

            intervenants_existant.append(nouvel_intervenant)
            request.session['intervenants'] = intervenants_existant

            return JsonResponse({
                'success': True,
                'message': "Ajout d'intervenant effectué avec succès !",
                'data': intervenants_existant
            }, status=200)

        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Erreur lors de l'enregistrement : {str(e)}"}, status=500)

    return JsonResponse({'success': False, 'message': 'Requête invalide.'}, status=400)


@csrf_exempt
def add_intervenant_session_sinistre(request):
    try:
        sinistre_id = request.POST.get('sinistre_id')
        typeintervenant_id = request.POST.get('typeintervenant_id')
        nom = request.POST.get('nom')
        prenoms = request.POST.get('prenoms')
        portable = request.POST.get('portable')
        telephone = request.POST.get('telephone')
        email = request.POST.get('email')
        code_postal = request.POST.get('code_postal')
        boite_postale = request.POST.get('boite_postale')
        ville = request.POST.get('ville')
        pays_id = request.POST.get('pays_id')

        sinistre = Sinistre.objects.filter(id=sinistre_id).first()
        typeintervenant = TypeIntervenant.objects.filter(id=typeintervenant_id).first()

        if not sinistre:
            return JsonResponse({'success': False, 'message': "Sinistre non trouvé."}, status=404)

        if not typeintervenant:
            return JsonResponse({'success': False, 'message': "Type d'intervenant non trouvé."}, status=404)

        # Ajouter l'intervenant à la session
        intervenants_session = request.session.setdefault('intervenants', [])
        intervenant_dict = {
            'id': str(uuid.uuid4()),
            'sinistre_id': sinistre.id,
            'type_intervenant_id': typeintervenant.id,
            'typeintervenant': typeintervenant.libelle,
            'nom': nom.strip().upper(),
            'prenoms': prenoms.strip().upper(),
            'portable': portable.strip() if portable else '',
            'telephone': telephone.strip() if telephone else '',
            'email': email.strip().lower() if email else '',
            'code_postal': code_postal,
            'boite_postale': boite_postale,
            'ville': ville,
            'pays_id': pays_id
        }

        intervenants_session.append(intervenant_dict)
        request.session['intervenants'] = intervenants_session

        return JsonResponse({'success': True, 'message': "Intervenant ajouté avec succès."}, status=200)

    except Exception as e:
        print(f"Erreur lors de l'ajout de l'intervenant : {e}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
def delete_intervenant_session(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            intervenant_id = str(data.get("intervenant_id"))
            police_id = str(data.get("police_id"))

            if "intervenants" in request.session:
                intervenants = request.session["intervenants"]
                intervenants = [inter for inter in intervenants if str(inter["id"]) != intervenant_id]
                request.session["intervenants"] = intervenants

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Requête invalide"})


@csrf_exempt
def delete_intervenant_session_sinistre(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            intervenant_id = str(data.get("intervenant_id"))
            sinistre_id = str(data.get("sinistre_id"))

            if "intervenants" in request.session:
                intervenants = request.session["intervenants"]
                print('intervenants avant suppression : ', intervenants)
                intervenants = [inter for inter in intervenants if str(inter["id"]) != intervenant_id]
                request.session["intervenants"] = intervenants

                print('intervenants après suppression : ', request.session["intervenants"])

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Requête invalide"})


def charger_garanties_circonstance_session_sinistre(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        circonstance_id = data.get('circonstance_id')
        sinistre_id = data.get('sinistre_id')

        # Vérification des paramètres
        if not circonstance_id or not sinistre_id:
            return JsonResponse({'success': False, 'message': 'Paramètres manquants'})

        # Récupérer les garanties existantes en session
        garanties_session = request.session.get('garanties_sinistre', [])
        session_ids = {str(g['id']) for g in garanties_session}

        # Récupérer les garanties liées à cette circonstance
        garanties = GarantieSinistre.objects.filter(circonstance_id=circonstance_id, sinistre_id=sinistre_id)

        # Ajouter uniquement celles qui ne sont pas déjà en session
        for garan in garanties:
            garantie_id = str(garan.garantie_id)
            if garantie_id not in session_ids:
                garanties_session.append({
                    'id': garantie_id,
                    'sinistre_id': sinistre_id,
                    'nom': garan.garantie.nom,
                    'mouvement': "Ouverture de sinistre",
                    'date': garan.created_at.strftime('%d/%m/%Y') if garan.created_at else '',
                })
                session_ids.add(garantie_id)  # Marquer comme ajouté

        # Sauvegarder dans session
        request.session['garanties_sinistre'] = garanties_session
        request.session.modified = True

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})


def recuperer_garantie_circonstance_sinistre(request):
    data = json.loads(request.body)
    circonstance_id = str(data.get("circonstance_id"))
    sinistre_id = str(data.get("sinistre_id"))

    garantiecirconstances = GarantieCirconstance.objects.filter(circonstance_id=circonstance_id)

    # Sérialiser postedommages
    garantiecirconstances_list = [{
        "id": garantiecirconstance.garantie_id,
        "nom": garantiecirconstance.garantie.nom if garantiecirconstance.garantie else '',
        "sinistre_id": sinistre_id,
        # Ajoutez d'autres champs si nécessaire
    } for garantiecirconstance in garantiecirconstances]

    if garantiecirconstances_list:
        context = {
            'garanties': garantiecirconstances_list,
        }
        return render(request, 'sinistre/sinistre_garantie_table.html', context)
    else:
        return JsonResponse({'message': "Aucune garantie trouvée.", 'status': 'no_garanties'})


def recuperer_garantie_circonstance(request):
    data = json.loads(request.body)
    circonstance_id = str(data.get("circonstance_id"))

    garantiecirconstances = GarantieCirconstance.objects.filter(circonstance_id=circonstance_id)

    # Sérialiser postedommages
    garantiecirconstances_list = [{
        "id": garantiecirconstance.garantie_id,
        "nom": garantiecirconstance.garantie.nom if garantiecirconstance.garantie else '',
        # Ajoutez d'autres champs si nécessaire
    } for garantiecirconstance in garantiecirconstances]

    if garantiecirconstances_list:
        context = {
            'garanties': garantiecirconstances_list,
        }
        return render(request, 'police/sinistre_garantie_table.html', context)
    else:
        return JsonResponse({'message': "Aucune garantie trouvée.", 'status': 'no_garanties'})


@csrf_exempt
def vider_garanties_sinistre(request):
    """Vide les garanties en session."""
    if 'garanties_sinistre' in request.session:
        del request.session['garanties_sinistre']
    return JsonResponse({'success': True})


def enregistrer_garanties_sinistre(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            nouvelles_garanties = data.get("garanties", [])

            # Récupérer les garanties existantes en session (ou initialiser une liste vide)
            garanties_session = request.session.get("garanties_sinistre", [])

            # Convertir en dictionnaire pour faciliter les mises à jour
            garanties_dict = {g["id"]: g for g in garanties_session}

            for garantie in nouvelles_garanties:
                garantie_id = garantie.get("id")
                if garantie_id:
                    garanties_dict[garantie_id] = garantie  # Mise à jour ou ajout

            # Sauvegarder les garanties mises à jour dans la session
            request.session["garanties_sinistre"] = list(garanties_dict.values())
            request.session.modified = True

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Méthode non autorisée"})


def enregistrer_garanties_circonstance_sinistre(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            nouvelles_garanties = data.get("garanties", [])

            # Récupérer les garanties existantes en session (ou initialiser une liste vide)
            garanties_session = request.session.get("garanties_sinistre", [])

            # Convertir en dictionnaire pour faciliter les mises à jour
            garanties_dict = {g["id"]: g for g in garanties_session}

            for garantie in nouvelles_garanties:
                garantie_id = garantie.get("id")
                if garantie_id:
                    garanties_dict[garantie_id] = garantie  # Mise à jour ou ajout

            # Sauvegarder les garanties mises à jour dans la session
            request.session["garanties_sinistre"] = list(garanties_dict.values())
            request.session.modified = True

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Méthode non autorisée"})


def recuperer_garanties_sinistre(request):
    garanties = request.session.get("garanties_sinistre", [])

    for garantie in garanties:
        garantie["mouvement"] = "Ouverture Sinistre"
        garantie["date"] = now().strftime("%Y-%m-%d")

    return JsonResponse({"garanties": garanties})


def afficher_provision_sinistre(request):
    postedommages = PosteDommage.objects.filter(statut=1)
    garanties_sinistre = request.session.get("garanties_sinistre", [])

    # Sérialiser postedommages
    postedommages_list = [{
        "id": poste.id,
        "libelle": poste.libelle,
        # Ajoutez d'autres champs si nécessaire
    } for poste in postedommages]

    context = {
        'postedommages': postedommages_list,
        'garanties_sinistre': garanties_sinistre,
    }

    return render(request, 'police/sinistre_provision_table.html', context)


def recuperer_garanties_circonstance_sinistre(request):
    garanties = request.session.get("garanties_sinistre", [])

    for garantie in garanties:
        garantie["mouvement"] = "Ouverture Sinistre"
        garantie["date"] = now().strftime("%Y-%m-%d")

    return JsonResponse({"garanties": garanties})


def afficher_provision_circonstance_sinistre(request):
    sinistre_id = request.GET.get('sinistre_id')

    garanties_sinistre = request.session.get("garanties_sinistre", [])
    garanties_ids = [garantie['id'] for garantie in garanties_sinistre]

    postedommages = PosteDommage.objects.filter(statut=1)

    # Récupération des provisions liées
    provisions = Provision.objects.filter(
        garantie_id__in=garanties_ids,
        sinistre_id=sinistre_id
    )

    # Organiser provisions
    provisions_dict = {}
    for provision in provisions:
        key = f"{provision.poste_dommage_id}_{provision.garantie_id}"
        provisions_dict[key] = {
            "estimation": provision.estimation,
            "deja_regle": provision.deja_regle,
            "provision": provision.provision,
        }

    # Sérialisation poste dommage
    postedommages_list = [{
        "id": poste.id,
        "libelle": poste.libelle,
    } for poste in postedommages]

    context = {
        'postedommages': postedommages_list,
        'garanties_sinistre': garanties_sinistre,
        'provisions_dict': provisions_dict,
    }

    return render(request, 'sinistre/sinistre_provision_table.html', context)


@csrf_exempt
def enregistrer_montant_garantie_sinistre(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            postedommage_id = data.get("postedommageId")
            garantie_id = data.get("garantieId")
            type_montant = data.get("type")
            valeur = int(data.get("valeur", 0))

            # Vérifier si le poste dommage correspond à "Franchise"
            if "Franchise" in postedommage_id.lower():
                valeur *= -1  # Appliquer le signe négatif

            # Récupération des montants en session
            session_key = "montants_garantie_sinistre"
            montants = request.session.get(session_key, {})

            # Initialiser la structure si besoin
            if garantie_id not in montants:
                montants[garantie_id] = {"estimation": 0, "deja_regle": 0, "provision": 0}

            # Mise à jour des valeurs
            montants[garantie_id][type_montant] += valeur
            request.session[session_key] = montants
            request.session.modified = True
            print('montants : ', montants)
            return JsonResponse({"success": True, "totaux": montants})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Méthode non autorisée"}, status=400)


@csrf_exempt
def enregistrer_montant_garantie_circonstance_sinistre(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            sinistre_id = data.get("sinistreId")
            postedommage_id = data.get("postedommageId")
            garantie_id = data.get("garantieId")
            type_montant = data.get("type")
            valeur = int(data.get("valeur", 0))

            # Vérifier si le poste dommage correspond à "Franchise"
            if "Franchise" in postedommage_id.lower():
                valeur *= -1  # Appliquer le signe négatif

            # Récupération des montants en session
            session_key = "montants_garantie_sinistre"
            montants = request.session.get(session_key, {})

            # Initialiser la structure si besoin
            if garantie_id not in montants:
                montants[garantie_id] = {"estimation": 0, "deja_regle": 0, "provision": 0}

            # Mise à jour des valeurs
            montants[garantie_id][type_montant] += valeur
            request.session[session_key] = montants
            request.session.modified = True

            return JsonResponse({"success": True, "totaux": montants})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Méthode non autorisée"}, status=400)


def vider_intervenants_garanties_session(request):
    try:
        if 'intervenants' in request.session:
            del request.session['intervenants']

        if 'garanties_sinistre' in request.session:
            del request.session['garanties_sinistre']

        return JsonResponse({'success': True})

    except KeyError as e:
        print(f"Clé de session introuvable : {e}")
        return JsonResponse({'success': False, 'error': f"Clé de session introuvable : {e}"})

    except Exception as e:
        print(f"Erreur lors de la suppression des données de session : {e}")
        return JsonResponse({'success': False, 'error': f"Erreur lors de la suppression des données de session : {e}"})


@csrf_exempt
def delete_garantie_session(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            garantie_id = str(data.get("garantie_id"))

            if "garanties_sinistre" in request.session:
                garanties_sinistre = request.session["garanties_sinistre"]

                garanties_sinistre = [g for g in garanties_sinistre if str(g["id"]) != garantie_id]
                request.session["garanties_sinistre"] = garanties_sinistre

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Requête invalide"})


def get_formules(request, police_id):
    # Récupérez les formules associées à la police_id (ajustez selon votre modèle)
    formules = FormuleGarantie.objects.filter(police_id=police_id).values('code', 'libelle')

    # Convertissez les résultats en un format JSON approprié
    formules_list = [{'code': formule['code'], 'libelle': formule['libelle']} for formule in formules]

    return JsonResponse({'formules': formules_list})


def getAliments(police_id):
    aliments = []

    police = Police.objects.filter(pk=police_id, statut_validite=StatutValidite.VALIDE)
    for formule in police.formules:

        aliment_formule = AlimentFormule.objects.filter(formule_id=formule.id, statut=Statut.ACTIF).order_by('-id')

        for af in aliment_formule:
            if af.aliment not in aliments:
                aliments.append(af.aliment)

    return aliments


def getAdherentsPrincipaux(police_id):
    aliments = []

    police = Police.objects.get(id=police_id)

    for formule in police.formules:

        aliment_formule = AlimentFormule.objects.filter(formule_id=formule.id, statut=Statut.ACTIF, statut_validite=StatutValidite.VALIDE).order_by('-id')

        for af in aliment_formule:
            if af.aliment.statut == Statut.ACTIF and af.aliment.qualite_beneficiaire and af.aliment.qualite_beneficiaire.code == "AD":
                if af.aliment not in aliments:
                    aliments.append(af.aliment)

    return aliments


def check_pandas_value(value):
    return value if pd.notna(value) else None


def check_pandas_date_value(value):
    return pd.to_datetime(value) if pd.notna(value) else None


#TODO CHANGEMENT DE COMPAGNIE
@transaction.atomic
def changement_compagnie(request, client_id):
    #dd("Désactivé pour l'instant")

    rstatut = 0
    rmessage = ""
    rerrors = {}

    try:
        if request.method == 'POST':

            ancienne_police_id = request.POST.get('ancienne_police')
            nouvelle_police_id = request.POST.get('nouvelle_police')

            ancienne_police = Police.objects.filter(id=ancienne_police_id, statut_validite=StatutValidite.VALIDE).first()
            nouvelle_police = Police.objects.filter(id=nouvelle_police_id, statut_validite=StatutValidite.VALIDE).first()

            if ancienne_police and nouvelle_police:
                anciennes_formules = FormuleGarantie.objects.filter(police=ancienne_police)

                #Pour chaque formule
                pprint("Pour chaque formule")
                for old_formule in anciennes_formules:

                    # vérifier qu'il y a des bénéficiaires actif sur la formule
                    pprint("TRAITEMENT DES FORMULES DE GARANTIE ET SPECIFICITES")
                    pprint("vérifier qu'il y a des bénéficiaires actif sur la formule")

                    #Créer la nouvelle formule
                    pprint("Créer la nouvelle formule")
                    new_formule = FormuleGarantie.objects.create(police=nouvelle_police,
                                                                 created_by=request.user,
                                                                 territorialite=old_formule.territorialite,
                                                                 type_tarif=old_formule.type_tarif,
                                                                 libelle=old_formule.libelle,
                                                                 taux_couverture=old_formule.taux_couverture,
                                                                 plafond_conso_famille=old_formule.plafond_conso_famille,
                                                                 plafond_conso_individuelle=old_formule.plafond_conso_individuelle,
                                                                 taux_tm=old_formule.taux_tm,
                                                                 garantis_pharmacie=old_formule.garantis_pharmacie,
                                                                 date_debut=nouvelle_police.date_debut_effet,
                                                                 )
                    code_bureau = request.user.bureau.code
                    code_formule = str(code_bureau) + str(Date.today().year)[-2:] + '-' + str(new_formule.pk).zfill(7)

                    new_formule.code = 'F' + str(Date.today().year)[-2:] + '' + str(new_formule.pk).zfill(7)
                    new_formule.save()


                    #Réccupérer les barèmes de l'ancienne formule
                    pprint("Réccupérer les barèmes de l'ancienne formule")
                    anciens_baremes = Bareme.objects.filter(formulegarantie=old_formule)

                    #Copier les barèmes sur la nouvelle formule
                    pprint("Copier les barèmes sur la nouvelle formule")
                    for old_bareme in anciens_baremes:
                        new_bareme = Bareme.objects.create(formulegarantie=new_formule,
                                                           created_by=request.user,
                                                           rubrique_id=old_bareme.rubrique_id,
                                                           sous_rubrique_id=old_bareme.sous_rubrique_id,
                                                           regroupement_acte_id=old_bareme.regroupement_acte_id,
                                                           acte_id=old_bareme.acte_id,
                                                           is_garanti=old_bareme.is_garanti,
                                                           qualite_beneficiaire_id=old_bareme.qualite_beneficiaire_id,
                                                           taux_couverture=old_bareme.taux_couverture,
                                                           taux_tm=old_bareme.taux_tm,
                                                           plafond_individuel=old_bareme.plafond_individuel,
                                                           plafond_famille=old_bareme.plafond_famille,
                                                           plafond_rubrique=old_bareme.plafond_rubrique,
                                                           plafond_sous_rubrique=old_bareme.plafond_sous_rubrique,
                                                           plafond_regroupement_acte=old_bareme.plafond_regroupement_acte,
                                                           plafond_acte=old_bareme.plafond_acte,
                                                           nombre_acte=old_bareme.nombre_acte,
                                                           periodicite_id=old_bareme.periodicite_id,
                                                           # unite_frequence = unite_frequence,
                                                           # frequence = frequence,
                                                           age_minimum=old_bareme.age_minimum,
                                                           age_maximum=old_bareme.age_maximum,
                                                           date_debut=nouvelle_police.date_debut_effet,
                                                           )
                        new_bareme.save()
                        pprint("new_bareme crée")
                        pprint(new_bareme)


                #save log
                ActionLog.objects.create(done_by=request.user, action="changement_assureur",
                                         description="Changement d'assureur: copie des formules et bénéficiaires de la police " + str(ancienne_police.numero) + " vers la police " + str(nouvelle_police.numero), table="",
                                         row=None, data_before=None,
                                         data_after=None)

                rstatut = 1
                rmessage = "Opération effectuée avec succès."
                rerrors = {}

            else:
                rstatut = 0
                message = "Polices non trouvées"


    except Exception as e:
        error_message = str(e)

        rmessage = "Erreur lors du traitement: " + error_message
        rerrors = {'Erreur': error_message}

    response = {
        'statut': rstatut,
        'message': rmessage,
        'errors': rerrors,
    }

    return JsonResponse(response)


def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)

    return obj


#Liste des véhicules de la police
@never_cache
def police_vehicules(request, police_id):
    police = Police.objects.get(id=police_id)

    vehicules = AlimentPolice.objects.filter(police_id=police.id)

    catgories = CategorieVehicule.objects.all().order_by('libelle')
    carburants = Carburant.objects.all().order_by('libelle')
    usages = Usage.objects.all().order_by('libelle')
    carosseries = Carosserie.objects.all().order_by('libelle')
    formules = Formule.objects.filter(status=True).order_by('libelle')

    pprint(vehicules)

    return render(request, 'police/vehicules.html',
                  {'police': police, 'vehicules': vehicules, 'catgories': catgories,
                   'carosseries': carosseries, 'carburants': carburants, 'usages': usages, 'formules': formules})


# ajout de véhicule
def add_vehicule(request, police_id):
    police = Police.objects.get(id=police_id)

    if request.method == 'POST':

        immatriculation = request.POST.get('immatriculation')
        date_entree = request.POST.get('date_entree')
        date_sortie = request.POST.get('date_sortie')
        mis_en_circulation = convertir_date_multiformat(request.POST.get('date_mise_circulation'))

        immatriculation_existante = Vehicule.objects.filter(numero_immatriculation=immatriculation).first()

        if date_entree:
            date_entree_conversion = convertir_date_multiformat(date_entree)
        else:
            date_entree_conversion = None
        if date_sortie:
            date_sortie_conversion = convertir_date_multiformat(date_sortie)
        else:
            date_sortie_conversion = None

        if date_sortie_conversion:
            if date_entree_conversion > date_sortie_conversion:

                response = {
                    'statut': 2,
                    'message': "La date de sortie ne doit pas être inférieure à la date d'entrée",
                }
                return JsonResponse(response)

            else:
                if immatriculation_existante:
                    response = {
                        'statut': 2,
                        'message': f"Ce véhicule d'immatriculation : {immatriculation_existante.numero_immatriculation} existe déjà dans le système",
                    }
                    return JsonResponse(response)
                else:
                    # Créer une ligne véhicule
                    vehicule_created = Vehicule.objects.create(
                        numero_immatriculation=request.POST.get('immatriculation'),
                        numero_immat_provisoire=request.POST.get('immatriculation_provisioire'),
                        numero_serie=request.POST.get('num_serie'),
                        marque=request.POST.get('marque'),
                        modele=request.POST.get('modele'),
                        places_assises=request.POST.get('places_assises'),
                        valeur_neuve=supprimer_espaces(request.POST.get('valeur_neuve', '')),
                        puissance=request.POST.get('puissance_fiscale'),
                        poids_a_vide=request.POST.get('poids_a_vide'),
                        poids_a_charge=request.POST.get('poid_tac'),
                        categorie_vehicule_id=request.POST.get('categorie_id'),
                        carburant_id=request.POST.get('carburant_id'),
                        carosserie_id=request.POST.get('carosserie_id'),
                    )
                    vehicule_created.save()
                    vehicule = Vehicule.objects.get(id=vehicule_created.pk)

                    # Créer la relation police-aliment-vehicule
                    AlimentPolice.objects.create(
                        police_id=police.id,
                        vehicule_id=vehicule.id,
                        created_by=request.user,
                        date_entree=police.date_debut_effet,
                        date_mis_en_circulation=mis_en_circulation if mis_en_circulation else None,
                        usage_id=request.POST.get('usage_id'),
                        proprietaire=request.POST.get('proprietaire'),
                        conducteur=request.POST.get('conducteur'),
                        numero_parc=request.POST.get('num_parc'),
                        valeur_actuelle=supprimer_espaces(request.POST.get('valeur_actuelle', '')),
                        commentaire=request.POST.get('commentaire'),
                        date_liaison=datetime.now(),
                    )

                    response = {
                        'statut': 1,
                        'message': "Véhicule ajouté avec succès !",
                        'data': {
                            'id': vehicule.pk,
                        }
                    }

                    return JsonResponse(response)
        else:
            if immatriculation_existante:
                response = {
                    'statut': 2,
                    'message': f"Ce véhicule d'immatriculation : {immatriculation_existante.numero_immatriculation} existe déjà dans le système",
                }
                return JsonResponse(response)
            else:
                # Créer une ligne véhicule
                vehicule_created = Vehicule.objects.create(
                    numero_immatriculation=request.POST.get('immatriculation'),
                    numero_immat_provisoire=request.POST.get('immatriculation_provisioire'),
                    numero_serie=request.POST.get('num_serie'),
                    marque=request.POST.get('marque'),
                    modele=request.POST.get('modele'),
                    places_assises=request.POST.get('places_assises'),
                    valeur_neuve=supprimer_espaces(request.POST.get('valeur_neuve', '')),
                    puissance=request.POST.get('puissance_fiscale'),
                    poids_a_vide=request.POST.get('poids_a_vide'),
                    poids_a_charge=request.POST.get('poid_tac'),
                    categorie_vehicule_id=request.POST.get('categorie_id'),
                    carburant_id=request.POST.get('carburant_id'),
                    carosserie_id=request.POST.get('carosserie_id'),
                )
                vehicule_created.save()
                vehicule = Vehicule.objects.get(id=vehicule_created.pk)

                # Créer la relation police-aliment-vehicule
                AlimentPolice.objects.create(
                    police_id=police.id,
                    vehicule_id=vehicule.id,
                    created_by=request.user,
                    date_entree=police.date_debut_effet,
                    date_mis_en_circulation=mis_en_circulation if mis_en_circulation else None,
                    usage_id=request.POST.get('usage_id'),
                    proprietaire=request.POST.get('proprietaire'),
                    conducteur=request.POST.get('conducteur'),
                    numero_parc=request.POST.get('num_parc'),
                    valeur_actuelle=supprimer_espaces(request.POST.get('valeur_actuelle', '')),
                    commentaire=request.POST.get('commentaire'),
                    date_liaison=datetime.now(),
                )

                response = {
                    'statut': 1,
                    'message': "Véhicule ajouté avec succès !",
                    'data': {
                        'id': vehicule.pk,
                    }
                }
                return JsonResponse(response)

    else:
        response = {
            'statut': 2,
            'message': "Cette methode n'est pas reconnue !",
        }
        return JsonResponse(response)


#Modifier le véhicule
def update_vehicule(request, police_id, aliment_police_id):
    police = Police.objects.get(id=police_id)
    alimentpolice = AlimentPolice.objects.get(id=aliment_police_id)
    vehicule = Vehicule.objects.filter(id=alimentpolice.vehicule_id).first()

    catgories = CategorieVehicule.objects.all().order_by('libelle')
    carburants = Carburant.objects.all().order_by('libelle')
    usages = Usage.objects.all().order_by('libelle')
    carosseries = Carosserie.objects.all().order_by('libelle')
    formules = Formule.objects.filter(status=True).order_by('libelle')

    if request.method == 'POST':

        date_entree = convertir_date_multiformat(request.POST.get('date_entree'))
        date_sortie = request.POST.get('date_sortie')
        mis_en_circulation = convertir_date_multiformat(request.POST.get('date_mise_circulation'))

        if date_sortie:
            date_sortie_conversion = convertir_date_multiformat(date_sortie)
        else:
            date_sortie_conversion = None

        if date_sortie_conversion:
            if date_entree > date_sortie_conversion:
                response = {
                    'statut': 2,
                    'message': "La date de sortie ne doit pas être inférieure à la date d'entrée",
                    'data': {
                        'vehicule': vehicule.numero_immatriculation,
                        'produit': police.produit.nom,
                    }
                }
                return JsonResponse(response)
            else:

                # Créer une nouvelle ligne d'historique
                historique_vehicule = HistoriqueAliment(
                    vehicule_id=vehicule.id,
                    numero_immatriculation=vehicule.numero_immatriculation,
                    numero_immat_provisoire=vehicule.numero_immat_provisoire,
                    numero_serie=vehicule.numero_serie,
                    numero_parc=alimentpolice.numero_parc,
                    proprietaire=alimentpolice.proprietaire,
                    conducteur=alimentpolice.conducteur,
                    marque=vehicule.marque,
                    modele=vehicule.modele,
                    places_assises=vehicule.places_assises,
                    valeur_neuve=vehicule.valeur_neuve,
                    valeur_actuelle=alimentpolice.valeur_actuelle,
                    puissance=vehicule.puissance,
                    date_entree=alimentpolice.date_entree,
                    date_sortie=alimentpolice.date_sortie,
                    date_mis_en_circulation=alimentpolice.date_mis_en_circulation,
                    poids_a_vide=vehicule.poids_a_vide,
                    poids_a_charge=vehicule.poids_a_charge,
                    categorie_vehicule_id=vehicule.categorie_vehicule_id,
                    carburant_id=vehicule.carburant_id,
                    carosserie_id=vehicule.carosserie_id,
                    usage_id=alimentpolice.usage_id,
                    commentaire=alimentpolice.commentaire,
                    statut=alimentpolice.statut,
                    updated_by_id=request.user.id,
                )
                historique_vehicule.save()

                # Mise à jour de la table véhicule
                vehicule.numero_immatriculation = request.POST.get('immatriculation')
                vehicule.numero_immat_provisoire = request.POST.get('immatriculation_provisioire')
                vehicule.numero_serie = request.POST.get('num_serie')
                vehicule.marque = request.POST.get('marque')
                vehicule.modele = request.POST.get('modele')
                vehicule.places_assises = request.POST.get('places_assises')
                vehicule.valeur_neuve = supprimer_espaces(request.POST.get('valeur_neuve', ''))
                vehicule.puissance = request.POST.get('puissance_fiscale')
                vehicule.date_entree = date_entree if date_entree else None
                vehicule.date_mis_en_circulation = mis_en_circulation if mis_en_circulation else None
                vehicule.poids_a_vide = request.POST.get('poids_a_vide')
                vehicule.poids_a_charge = request.POST.get('poid_tac')
                vehicule.categorie_vehicule_id = request.POST.get('categorie_id')
                vehicule.carburant_id = request.POST.get('carburant_id')
                vehicule.carosserie_id = request.POST.get('carosserie_id')
                vehicule.updated_by_id = request.user.id
                vehicule.save()

                # Mise à jour de police-aliment-vehicule
                if alimentpolice and date_sortie:
                    AlimentPolice.objects.filter(vehicule_id=vehicule.id).update(
                        police_id=police.id,
                        vehicule_id=vehicule.id,
                        updated_by_id=request.user.id,
                        usage_id=request.POST.get('usage_id'),
                        proprietaire=request.POST.get('proprietaire'),
                        conducteur=request.POST.get('conducteur'),
                        numero_parc=request.POST.get('num_parc'),
                        valeur_actuelle=supprimer_espaces(request.POST.get('valeur_actuelle', '')),
                        commentaire=request.POST.get('commentaire'),
                        date_sortie=date_sortie or None,
                    )

                response = {
                    'statut': 1,
                    'message': "Modification effectuée avec succès !",
                    'data': {
                        'id': vehicule.pk,
                    }
                }

                return JsonResponse(response)

        else:

            # Créer une nouvelle ligne d'historique
            historique_vehicule = HistoriqueAliment(
                vehicule_id=vehicule.id,
                numero_immatriculation=vehicule.numero_immatriculation,
                numero_immat_provisoire=vehicule.numero_immat_provisoire,
                numero_serie=vehicule.numero_serie,
                numero_parc=alimentpolice.numero_parc,
                proprietaire=alimentpolice.proprietaire,
                conducteur=alimentpolice.conducteur,
                marque=vehicule.marque,
                modele=vehicule.modele,
                places_assises=vehicule.places_assises,
                valeur_neuve=vehicule.valeur_neuve,
                valeur_actuelle=alimentpolice.valeur_actuelle,
                puissance=vehicule.puissance,
                date_entree=alimentpolice.date_entree,
                date_sortie=alimentpolice.date_sortie,
                date_mis_en_circulation=alimentpolice.date_mis_en_circulation,
                poids_a_vide=vehicule.poids_a_vide,
                poids_a_charge=vehicule.poids_a_charge,
                categorie_vehicule_id=vehicule.categorie_vehicule_id,
                carburant_id=vehicule.carburant_id,
                carosserie_id=vehicule.carosserie_id,
                usage_id=alimentpolice.usage_id,
                commentaire=alimentpolice.commentaire,
                statut=alimentpolice.statut,
                updated_by_id=request.user.id,
            )
            historique_vehicule.save()

            # Mise à jour de la table véhicule
            vehicule.numero_immatriculation = request.POST.get('immatriculation')
            vehicule.numero_immat_provisoire = request.POST.get('immatriculation_provisioire')
            vehicule.numero_serie = request.POST.get('num_serie')
            vehicule.marque = request.POST.get('marque')
            vehicule.modele = request.POST.get('modele')
            vehicule.places_assises = request.POST.get('places_assises')
            vehicule.valeur_neuve = supprimer_espaces(request.POST.get('valeur_neuve', ''))
            vehicule.puissance = request.POST.get('puissance_fiscale')
            vehicule.date_entree = date_entree if date_entree else None
            vehicule.date_mis_en_circulation = mis_en_circulation if mis_en_circulation else None
            vehicule.poids_a_vide = request.POST.get('poids_a_vide')
            vehicule.poids_a_charge = request.POST.get('poid_tac')
            vehicule.categorie_vehicule_id = request.POST.get('categorie_id')
            vehicule.carburant_id = request.POST.get('carburant_id')
            vehicule.carosserie_id = request.POST.get('carosserie_id')
            vehicule.updated_by_id = request.user.id
            vehicule.save()

            # Mise à jour de police-aliment-vehicule
            if alimentpolice:
                AlimentPolice.objects.filter(vehicule_id=vehicule.id).update(
                    police_id=police.id,
                    vehicule_id=vehicule.id,
                    updated_by_id=request.user.id,
                    usage_id=request.POST.get('usage_id'),
                    proprietaire=request.POST.get('proprietaire'),
                    conducteur=request.POST.get('conducteur'),
                    numero_parc=request.POST.get('num_parc'),
                    valeur_actuelle=supprimer_espaces(request.POST.get('valeur_actuelle', '')),
                    commentaire=request.POST.get('commentaire'),
                    date_sortie=date_sortie or None,
                )

            response = {
                'statut': 1,
                'message': "Modification effectuée avec succès !",
                'data': {
                    'id': vehicule.pk,
                }
            }

            return JsonResponse(response)

    else:

        context ={
            'alimentpolice': alimentpolice,
            'police': police,
            'catgories': catgories,
            'carosseries': carosseries,
            'carburants': carburants,
            'usages': usages,
            'formules': formules
        }

        return render(request, 'police/modal_vehicule_modification.html', context)


# Afficher les details d'un vehicule
def details_vehicule(request, police_id, aliment_police_id):
    police = Police.objects.get(id=police_id)
    vehicule_aliment = AlimentPolice.objects.get(id=aliment_police_id)
    energies = Carburant.objects.all().order_by('libelle')

    sinistres = []

    tarifs = []

    historiques = HistoriqueAliment.objects.filter(vehicule_id=vehicule_aliment.vehicule_id).order_by('-id')
    print(historiques)

    return render(
        request,
        'police/modal_details_vehicule.html',
        {
            'police': police,
            'vehicule_aliment': vehicule_aliment,
            'tarifs': tarifs,
            'sinistres': sinistres,
            'energies': energies,
            'historiques': historiques,
        }
    )


# Afficher l'historique du véhicule
def details_historique_vehicule(request, vehicule_id, historique_id):
    vehicule = Vehicule.objects.get(id=vehicule_id)
    historique = HistoriqueAliment.objects.get(id=historique_id)

    return render(
        request,
        'police/modal_historique_vehicule.html',
        {
            'vehicule': vehicule,
            'historique': historique,
        }
    )


# Supprimer un vehicule mais c'est resté en cours
def supprimer_vehicule(request, vehicule_id):

    if request.method == "POST":

        vehicule_id = request.POST.get('vehicule_id')

        vehicule = Vehicule.objects.get(id=vehicule_id)
        if vehicule.pk is not None:
            alimentpolice = AlimentPolice.objects.filter(vehicule_id=vehicule.id).first()

            alimentpolice.delete()
            vehicule.delete()

            response = {
                'statut': 1,
                'message': "Vehicule supprimé avec succès !",
            }

        else:

            response = {
                'statut': 0,
                'message': "Vehicule non trouvé !",
            }

        return JsonResponse(response)


# Importation des vehicules
def import_vehicules(request, police_id):
    police = Police.objects.get(id=police_id)
    if request.method == "POST":
        fichier = request.FILES.get("fichier")

        if not fichier:
            response = {
                'statut': 0,
                'message': "Aucun fichier joint."
            }
            return JsonResponse(response)

        # Lire le fichier Excel
        try:
            data = pd.read_excel(fichier)
            data = data.iloc[1:]  # Ignorer la première ligne si elle est un en-tête supplémentaire
        except Exception as e:
            response = {
                'statut': 0,
                'message': f"Erreur de lecture du fichier Excel : {str(e)}"
            }
            return JsonResponse(response)

        # Colonnes obligatoires
        colonnes_obligatoires = [
            'immat', 'proprietaire', 'marque', 'energie',
            'date_entree', 'puissance', 'mis_en_circulation', 'T_categorie_id'
        ]
        colonnes_manquantes = [col for col in colonnes_obligatoires if col not in data.columns]
        if colonnes_manquantes:
            response = {
                'statut': 0,
                'message': f"Colonnes obligatoires manquantes : {', '.join(colonnes_manquantes)}"
            }
            return JsonResponse(response)

        # Vérifier si des champs obligatoires sont vides
        lignes_incompletes = []
        for index, row in data.iterrows():
            for col in colonnes_obligatoires:
                if pd.isna(row[col]):
                    lignes_incompletes.append(index + 2)  # +2 pour compenser l'index et l'en-tête
                    break

        if lignes_incompletes:
            response = {
                'statut': 0,
                'message': f"Certaines lignes contiennent des champs obligatoires non renseignés : Lignes {', '.join(map(str, lignes_incompletes))}"
            }
            return JsonResponse(response)

        # Charger les véhicules existants dans la table
        vehicule_existant = Vehicule.objects.values('numero_immatriculation')
        immatriculations_existes = {vehicule['numero_immatriculation'] for vehicule in vehicule_existant}

        # Ajouter uniquement les nouvelles immatriculations
        nouveaux_vehicules = []
        for _, row in data.iterrows():
            immat = row['immat']  # Correspondance avec la colonne Excel
            date_sortie_req = row['date_sortie']
            print("date sortie :", date_sortie_req)
            if date_sortie_req:
                date_sortie = convertir_date_multiformat(date_sortie_req)
            mis_en_circulation = convertir_date_multiformat(row['mis_en_circulation'])
            energie = Carburant.objects.filter(code=row['energie']).first()

            if immat not in immatriculations_existes:
                try:
                    # Créer une ligne véhicule
                    nouveaux_vehicule = Vehicule(
                        numero_immatriculation=immat,
                        numero_immat_provisoire=row['immat_prov'],
                        numero_serie=row['num_serie'],
                        marque=row['marque'],
                        modele=row['modele'],
                        places_assises=row['place'],
                        valeur_neuve=supprimer_espaces(row['valeur_neuve', '']),
                        puissance=row['puissance'],
                        poids_a_vide=row['poids_a_vide'],
                        poids_a_charge=row['poids_a_charge'],
                        categorie_vehicule_id=row['T_categorie_id'],
                        carburant_id=energie.id if energie else None,
                        carosserie_id=row['T_carosserie_id'],
                    )
                    nouveaux_vehicule.save()
                    vehicule = Vehicule.objects.get(id=nouveaux_vehicule.pk)

                    # Créer la relation police-aliment-vehicule
                    AlimentPolice.objects.create(
                        police_id=police.id,
                        vehicule_id=vehicule.id,
                        created_by=request.user,
                        date_entree=police.date_debut_effet,
                        date_mis_en_circulation=mis_en_circulation if mis_en_circulation else None,
                        usage_id=row['T_usage_id'],
                        proprietaire=row['proprietaire'],
                        conducteur=row['chauffeur'],
                        numero_parc=row['num_parc'],
                        valeur_actuelle=supprimer_espaces(row['valeur_actuelle', '']),
                        commentaire=row['comment'],
                        date_sortie=date_sortie if date_sortie else None,
                        date_liaison=datetime.now(),
                    )
                except KeyError as e:
                    response = {
                        'statut': 0,
                        'message': f"Champ manquant dans une ligne : {str(e)}"
                    }
                    return JsonResponse(response)

        response = {
            'statut': 1,
            'message': "Importation des véhicules effectuée avec succès"
        }
        return JsonResponse(response)

    response = {
        'statut': 0,
        'message': "Requête invalide"
    }
    return JsonResponse(response)


#Liste des marchandises de la police
@never_cache
def police_marchandises(request, police_id):
    police = Police.objects.get(id=police_id)

    marchandises = AlimentPolice.objects.filter(police_id=police.id)
    print("marchandises", marchandises)

    conditions_assurances = ConditionsAssurance.objects.filter(status=True).order_by('libelle')
    moyens_transports = MoyensTransport.objects.filter(status=True).order_by('libelle')
    today = datetime.now(tz=timezone.utc)

    return render(request, 'police/marchandises.html',
                  {'police': police, 'marchandises': marchandises, 'conditions_assurances': conditions_assurances,
                   'moyens_transports': moyens_transports, 'today': today})


# ajout une marchandise
def add_marchandise(request, police_id):
    police = Police.objects.get(id=police_id)

    dernier_historique = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()

    if request.method == 'POST':

        devise_id = request.POST.get('devise')
        num_certificat = request.POST.get('num_certificat')
        num_fact_fournisseur = request.POST.get('num_fact_fournisseur')
        ref_dai = request.POST.get('ref_dai')
        date_commande = convertir_date_multiformat(request.POST.get('date_commande'))
        nombre_colis = request.POST.get('nombre_colis')
        poids_brut = request.POST.get('poids_brut')
        plein_souscription = request.POST.get('plein_souscription')
        immatriculation_march = request.POST.get('immatriculation_march')
        pavillon_cie_prest = request.POST.get('pavillon_cie_prest')
        destination = request.POST.get('destination')
        lieu_transit_transbordement = request.POST.get('lieu_transit_transbordement')
        date_emmision_certificat = convertir_date_multiformat(request.POST.get('date_emmision_certificat'))
        date_sortie_march = convertir_date_multiformat(request.POST.get('date_sortie_march'))
        num_commande = request.POST.get('num_commande')
        marchandises_description = request.POST.get('marchandises_description')
        poids_net = request.POST.get('poids_net')
        valeur_assuree = supprimer_espaces(request.POST.get('valeur_assuree'))
        marque_modele_type = request.POST.get('marque_modele_type')
        debut_voyage = convertir_date_multiformat(request.POST.get('debut_voyage'))
        lieu_depart = request.POST.get('lieu_depart')
        nom_commissaire = request.POST.get('nom')
        telephone_commissaire = request.POST.get('telephone')
        code_commissaire = request.POST.get('code')
        adresse_commissaire = request.POST.get('adresse')
        courriel_commissaire = request.POST.get('email')
        taux_risque_ordinaire = request.POST.get('taux_risque_ordinaire')
        taux_risque_guerre = request.POST.get('taux_risque_guerre')
        taux_supprime = request.POST.get('taux_supprime')
        taux_reduction_commerciale = supprimer_espaces(request.POST.get('taux_reduction_commerciale'))
        taux_taxe = supprimer_espaces(request.POST.get('taux_taxe'))
        accessoires = supprimer_espaces(request.POST.get('accessoires'))
        autres_frais = supprimer_espaces(request.POST.get('autres_frais'))
        prime_risque_ordinaire = supprimer_espaces(request.POST.get('prime_risque_ordinaire'))
        prime_risque_guerre = supprimer_espaces(request.POST.get('prime_risque_guerre'))
        prime_supprime = supprimer_espaces(request.POST.get('prime_supprime'))
        prime_brut = supprimer_espaces(request.POST.get('prime_brut'))
        prime_reduction = supprimer_espaces(request.POST.get('prime_reduction'))
        total_taxe = supprimer_espaces(request.POST.get('total_taxe'))
        prime_ttc_mar = supprimer_espaces(request.POST.get('prime_ttc_mar'))
        moyens_transport_id = request.POST.get('moyens_transport_id')
        conditions_assurance_id = request.POST.get('conditions_assurance_id')

        marchandise_created = Marchandise(
            moyens_transport_id=moyens_transport_id,
            conditions_assurance_id=conditions_assurance_id,
            devise_id=devise_id,
            num_certificat=num_certificat,
            num_fact_fournisseur=num_fact_fournisseur,
            ref_dai=ref_dai,
            date_commande=date_commande,
            nombre_colis=nombre_colis,
            poids_brut=poids_brut,
            plein_souscription=plein_souscription,
            immatriculation=immatriculation_march,
            pavillon_cie_prest=pavillon_cie_prest,
            destination=destination,
            lieu_transit_transbordement=lieu_transit_transbordement,
            date_emmision_certificat=date_emmision_certificat,
            date_sortie=date_sortie_march,
            num_commande=num_commande,
            marchandises_description=marchandises_description,
            poids_net=poids_net,
            valeur_assuree=valeur_assuree,
            marque_modele_type=marque_modele_type,
            debut_voyage=debut_voyage,
            lieu_depart=lieu_depart,
            nom_commissaire=nom_commissaire,
            telephone_commissaire=telephone_commissaire,
            code_commissaire=code_commissaire,
            adresse_commissaire=adresse_commissaire,
            courriel_commissaire=courriel_commissaire,
            taux_risque_ordinaire=taux_risque_ordinaire,
            taux_risque_guerre=taux_risque_guerre,
            taux_supprime=taux_supprime,
            taux_taxe=taux_taxe,
            taux_reduction_commerciale=taux_reduction_commerciale,
            accessoires=accessoires,
            autres_frais=autres_frais,
            prime_risque_ordinaire=prime_risque_ordinaire,
            prime_risque_guerre=prime_risque_guerre,
            prime_supprime=prime_supprime,
            prime_brut=prime_brut,
            prime_reduction=prime_reduction,
            total_taxe=total_taxe,
            prime_ttc_mar=prime_ttc_mar,
            date_liaison=datetime.now(),
            created_by=request.user,
            statut=Statut.ACTIF
        )
        marchandise_created.save()

        marchandise = Marchandise.objects.get(id=marchandise_created.pk)

        aliment_police = AlimentPolice(
            marchandise_id=marchandise.id,
            historique_police_id=dernier_historique.id,
            police_id=police.id,
            created_by=request.user,
            date_liaison=datetime.now(),
            statut=Statut.ACTIF
        )
        aliment_police.save()

        response = {
            'statut': 1,
            'message': "Marchandise ajoutée avec succès !",
            'data': {
                'id': marchandise.id,
                'marchandises_description': marchandise.marchandises_description,
            }
        }
        return JsonResponse(response)

    else:
        response = {
            'statut': 2,
            'message': "Cette methode n'est pas reconnue !",
        }
        return JsonResponse(response)


# Afficher les details d'une marchandise
def details_marchandise(request, police_id, marchandise_id):
    police = Police.objects.get(id=police_id)
    marchandise = Marchandise.objects.get(id=marchandise_id)
    conditions_assurances = ConditionsAssurance.objects.filter(status=True).order_by('libelle')
    moyens_transports = MoyensTransport.objects.filter(status=True).order_by('libelle')

    sinistres = []

    tarifs = []

    historiques = HistoriqueAliment.objects.filter(marchandise_id=marchandise_id).order_by('-id')

    return render(
        request,
        'police/modal_details_marchandise.html',
        {
            'police': police,
            'marchandise': marchandise,
            'tarifs': tarifs,
            'sinistres': sinistres,
            'conditions_assurances': conditions_assurances,
            'moyens_transports': moyens_transports,
            'historiques': historiques,
        }
    )


#Modifier le marchandise
def update_marchandise(request, police_id, marchandise_id):
    police = Police.objects.get(id=police_id)
    marchandise = Marchandise.objects.get(id=marchandise_id)
    alimentpolice = AlimentPolice.objects.filter(marchandise_id=marchandise.id)

    conditions_assurances = ConditionsAssurance.objects.filter(status=True).order_by('libelle')
    moyens_transports = MoyensTransport.objects.filter(status=True).order_by('libelle')
    today = datetime.now(tz=timezone.utc)

    if request.method == 'POST':

        devise_id = request.POST.get('devise')
        num_certificat = request.POST.get('num_certificat')
        num_fact_fournisseur = request.POST.get('num_fact_fournisseur')
        ref_dai = request.POST.get('ref_dai')
        date_commande = request.POST.get('date_commande')
        nombre_colis = request.POST.get('nombre_colis')
        poids_brut = request.POST.get('poids_brut')
        plein_souscription = request.POST.get('plein_souscription')
        immatriculation_march = request.POST.get('immatriculation_march')
        pavillon_cie_prest = request.POST.get('pavillon_cie_prest')
        destination = request.POST.get('destination')
        lieu_transit_transbordement = request.POST.get('lieu_transit_transbordement')
        date_emmision_certificat = request.POST.get('date_emmision_certificat')
        date_sortie_march = request.POST.get('date_sortie_march')
        num_commande = request.POST.get('num_commande')
        marchandises_description = request.POST.get('marchandises_description')
        poids_net = request.POST.get('poids_net')
        valeur_assuree = supprimer_espaces(request.POST.get('valeur_assuree'))
        marque_modele_type = request.POST.get('marque_modele_type')
        debut_voyage = request.POST.get('debut_voyage')
        lieu_depart = request.POST.get('lieu_depart')
        nom_commissaire = request.POST.get('nom')
        telephone_commissaire = request.POST.get('telephone')
        code_commissaire = request.POST.get('code')
        adresse_commissaire = request.POST.get('adresse')
        courriel_commissaire = request.POST.get('email')
        taux_risque_ordinaire = request.POST.get('taux_risque_ordinaire')
        taux_risque_guerre = request.POST.get('taux_risque_guerre')
        taux_supprime = request.POST.get('taux_supprime')
        taux_reduction_commerciale = supprimer_espaces(request.POST.get('taux_reduction_commerciale'))
        taux_taxe = supprimer_espaces(request.POST.get('taux_taxe'))
        accessoires = supprimer_espaces(request.POST.get('accessoires'))
        autres_frais = supprimer_espaces(request.POST.get('autres_frais'))
        prime_risque_ordinaire = supprimer_espaces(request.POST.get('prime_risque_ordinaire'))
        prime_risque_guerre = supprimer_espaces(request.POST.get('prime_risque_guerre'))
        prime_supprime = supprimer_espaces(request.POST.get('prime_supprime'))
        prime_brut = supprimer_espaces(request.POST.get('prime_brut'))
        prime_reduction = supprimer_espaces(request.POST.get('prime_reduction'))
        total_taxe = supprimer_espaces(request.POST.get('total_taxe'))
        prime_ttc_mar = supprimer_espaces(request.POST.get('prime_ttc_mar'))
        moyens_transport_id = request.POST.get('moyens_transport_id')
        conditions_assurance_id = request.POST.get('conditions_assurance_id')

        #Créer sa ligne d'historique
        marchandise_historique_created = HistoriqueAliment(
            marchandise_id=marchandise.id,
            moyens_transport_id=moyens_transport_id,
            conditions_assurance_id=conditions_assurance_id,
            devise_id=devise_id,
            num_certificat=num_certificat,
            num_fact_fournisseur=num_fact_fournisseur,
            ref_dai=ref_dai,
            date_commande=date_commande if date_commande else None,
            nombre_colis=nombre_colis,
            poids_brut=poids_brut,
            plein_souscription=plein_souscription,
            immatriculation=immatriculation_march,
            pavillon_cie_prest=pavillon_cie_prest,
            destination=destination,
            lieu_transit_transbordement=lieu_transit_transbordement,
            date_emmision_certificat=date_emmision_certificat if date_emmision_certificat else None,
            date_sortie=date_sortie_march if date_sortie_march else None,
            num_commande=num_commande,
            marchandises_description=marchandises_description,
            poids_net=poids_net,
            valeur_assuree=valeur_assuree,
            marque_modele_type=marque_modele_type,
            debut_voyage=debut_voyage if debut_voyage else None,
            lieu_depart=lieu_depart,
            nom_commissaire=nom_commissaire,
            telephone_commissaire=telephone_commissaire,
            code_commissaire=code_commissaire,
            adresse_commissaire=adresse_commissaire,
            courriel_commissaire=courriel_commissaire,
            taux_risque_ordinaire=taux_risque_ordinaire if taux_risque_ordinaire else None,
            taux_risque_guerre=taux_risque_guerre if taux_risque_guerre else None,
            taux_supprime=taux_supprime if taux_supprime else None,
            taux_taxe=taux_taxe if taux_taxe else None,
            taux_reduction_commerciale=taux_reduction_commerciale if taux_reduction_commerciale else None,
            accessoires=accessoires if accessoires else None,
            autres_frais=autres_frais if autres_frais else None,
            prime_risque_ordinaire=prime_risque_ordinaire if prime_risque_ordinaire else None,
            prime_risque_guerre=prime_risque_guerre if prime_risque_guerre else None,
            prime_supprime=prime_supprime if prime_supprime else None,
            prime_brut=prime_brut if prime_brut else None,
            prime_reduction=prime_reduction if prime_reduction else None,
            total_taxe=total_taxe if total_taxe else None,
            prime_ttc_mar=prime_ttc_mar if prime_ttc_mar else None,
            date_liaison=datetime.now(),
            created_by=marchandise.created_by,
            updated_by=marchandise.updated_by,
            statut=marchandise.statut
        )
        marchandise_historique_created.save()

        # Mise à jour de la marchandise
        marchandise.moyens_transport_id=moyens_transport_id
        marchandise.conditions_assurance_id=conditions_assurance_id
        marchandise.devise_id=devise_id
        marchandise.num_certificat=num_certificat
        marchandise.num_fact_fournisseur=num_fact_fournisseur
        marchandise.ref_dai=ref_dai
        marchandise.date_commande=date_commande if date_commande else None
        marchandise.nombre_colis=nombre_colis
        marchandise.poids_brut=poids_brut
        marchandise.plein_souscription=plein_souscription
        marchandise.immatriculation=immatriculation_march
        marchandise.pavillon_cie_prest=pavillon_cie_prest
        marchandise.destination=destination
        marchandise.lieu_transit_transbordement=lieu_transit_transbordement
        marchandise.date_emmision_certificat=date_emmision_certificat if date_emmision_certificat else None
        marchandise.date_sortie=date_sortie_march if date_sortie_march else None
        marchandise.num_commande=num_commande
        marchandise.marchandises_description=marchandises_description
        marchandise.poids_net=poids_net
        marchandise.valeur_assuree=valeur_assuree
        marchandise.marque_modele_type=marque_modele_type
        marchandise.debut_voyage=debut_voyage if debut_voyage else None
        marchandise.lieu_depart=lieu_depart
        marchandise.nom_commissaire=nom_commissaire
        marchandise.telephone_commissaire=telephone_commissaire
        marchandise.code_commissaire=code_commissaire
        marchandise.adresse_commissaire=adresse_commissaire
        marchandise.courriel_commissaire=courriel_commissaire
        marchandise.taux_risque_ordinaire=taux_risque_ordinaire if taux_risque_ordinaire else None
        marchandise.taux_risque_guerre=taux_risque_guerre if taux_risque_guerre else None
        marchandise.taux_supprime=taux_supprime if taux_supprime else None
        marchandise.taux_reduction_commerciale=taux_reduction_commerciale if taux_reduction_commerciale else None
        marchandise.taux_taxe=taux_taxe if taux_taxe else None
        marchandise.accessoires=accessoires if accessoires else None
        marchandise.autres_frais=autres_frais if autres_frais else None
        marchandise.prime_risque_ordinaire=prime_risque_ordinaire if prime_risque_ordinaire else None
        marchandise.prime_risque_guerre=prime_risque_guerre if prime_risque_guerre else None
        marchandise.prime_supprime=prime_supprime if prime_supprime else None
        marchandise.prime_brut=prime_brut if prime_brut else None
        marchandise.total_taxe=total_taxe if total_taxe else None
        marchandise.prime_reduction=prime_reduction if prime_reduction else None
        marchandise.prime_ttc_mar=prime_ttc_mar if prime_ttc_mar else None
        marchandise.updated_at=datetime.now()
        marchandise.updated_by=request.user
        marchandise.save()

        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': marchandise.id,
                'num_certificat': marchandise.num_certificat,
            }
        }

        return JsonResponse(response)

    else:

        context ={
            'police': police,
            'marchandise': marchandise,
            'alimentpolice': alimentpolice,
            'conditions_assurances': conditions_assurances,
            'moyens_transports': moyens_transports,
            'today': today
        }

        return render(request, 'police/modal_marchandise_modification.html', context)


# Supprimer une marchandise mais c'est resté en cours
def supprimer_marchandise(request, police_id, marchandise_id):
    police = Police.objects.get(id=police_id)

    if request.method == "POST":

        marchandise_id = request.POST.get('marchandise_id')

        marchandise = Marchandise.objects.get(id=marchandise_id)
        if marchandise.pk is not None:
            alimentpolice = AlimentPolice.objects.filter(marchandise_id=marchandise.id).first()

            alimentpolice.delete()
            marchandise.delete()

            response = {
                'statut': 1,
                'message': "Marchandise supprimée avec succès !",
            }

        else:

            response = {
                'statut': 0,
                'message': "Marchandise non trouvée !",
            }

        return JsonResponse(response)


@never_cache
def police_autres_risques(request, police_id):
    police = Police.objects.get(id=police_id)

    autresrisques = AlimentPolice.objects.filter(police_id=police.id)
    print("autresrisques", autresrisques)

    today = datetime.now(tz=timezone.utc)

    return render(request, 'police/autresrisques.html',
                  {'police': police, 'autresrisques': autresrisques, 'today': today})


# ajout un autre risque
def add_autrerisque(request, police_id):
    police = Police.objects.get(id=police_id)

    dernier_historique = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()

    if request.method == 'POST':

        devise_id = request.POST.get('devise')
        libelle = request.POST.get('libelle')
        description = request.POST.get('description')

        autrerisque_created = AutreRisque(
            libelle=libelle,
            description=description,
            date_liaison=datetime.now(),
            created_by=request.user,
            statut=Statut.ACTIF
        )
        autrerisque_created.save()

        autrerisque = AutreRisque.objects.get(id=autrerisque_created.pk)

        aliment_police = AlimentPolice(
            autre_risque_id=autrerisque.id,
            historique_police_id=dernier_historique.id,
            police_id=police.id,
            created_by=request.user,
            date_liaison=datetime.now(),
            statut=Statut.ACTIF
        )
        aliment_police.save()

        response = {
            'statut': 1,
            'message': "Autre risque ajouté avec succès !",
            'data': {
                'id': autrerisque.id,
                'autrerisque_libelle': autrerisque.libelle,
            }
        }
        return JsonResponse(response)

    else:
        response = {
            'statut': 2,
            'message': "Cette methode n'est pas reconnue !",
        }
        return JsonResponse(response)


# Afficher les details d'un autre risque
def details_autrerisque(request, police_id, autre_risque_id):
    police = Police.objects.get(id=police_id)
    autre_risque = AutreRisque.objects.get(id=autre_risque_id)

    sinistres = []

    tarifs = []

    historiques = HistoriqueAliment.objects.filter(autre_risque_id=autre_risque_id).order_by('-id')

    return render(
        request,
        'police/modal_details_autrerisque.html',
        {
            'police': police,
            'autre_risque': autre_risque,
            'tarifs': tarifs,
            'sinistres': sinistres,
            'historiques': historiques,
        }
    )


#Modifier l'autre risque
def update_autrerisque(request, police_id, autre_risque_id):
    police = Police.objects.get(id=police_id)
    autrerisque = AutreRisque.objects.get(id=autre_risque_id)
    alimentpolice = AlimentPolice.objects.filter(autre_risque_id=autrerisque.id)

    if request.method == 'POST':

        devise_id = request.POST.get('devise')
        libelle = request.POST.get('libelle')
        description = request.POST.get('description')

        #Créer sa ligne d'historique
        autrerisque_historique_created = HistoriqueAliment(
            autre_risque_id=autrerisque.id,
            libelle=libelle,
            description=description,
            date_liaison=datetime.now(),
            created_by=autrerisque.created_by,
            updated_by=autrerisque.updated_by,
            statut=autrerisque.statut
        )
        autrerisque_historique_created.save()

        # Mise à jour de la autrerisque
        autrerisque.libelle=libelle
        autrerisque.description=description
        autrerisque.updated_at=datetime.now()
        autrerisque.updated_by=request.user
        autrerisque.save()

        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': autrerisque.id,
                'libelle': autrerisque.libelle,
            }
        }

        return JsonResponse(response)

    else:

        context ={
            'police': police,
            'autrerisque': autrerisque,
            'alimentpolice': alimentpolice
        }

        return render(request, 'police/modal_autrerisque_modification.html', context)


# Supprimer un autre risque
def supprimer_autresrisque(request, police_id, autresrisque_id):
    police = Police.objects.get(id=police_id)

    if request.method == "POST":

        autresrisque_id = request.POST.get('autresrisque_id')

        autresrisque = AutreRisque.objects.get(id=autresrisque_id)
        if autresrisque.pk is not None:
            alimentpolice = AlimentPolice.objects.filter(autre_risque_id=autresrisque.id).first()

            alimentpolice.delete()
            autresrisque.delete()

            response = {
                'statut': 1,
                'message': "Autre risque supprimé avec succès !",
            }

        else:

            response = {
                'statut': 0,
                'message': "Autre risque non trouvé !",
            }

        return JsonResponse(response)


# ajout d'avenant
def add_avenant(request, police_id):
    police = Police.objects.get(id=police_id)

    if request.method == 'POST':

        if request.POST.get('mouvement') in ["5", "16"]:
            request.session['add_avenant'] = request.POST
            response = {
                'statut': 1,
                'message': "Enregistrement effectuée avec succès !",
                'data': {}
            }

        else:
            date_fin_periode_garantie = request.POST.get('date_fin_periode_garantie')

            mouvement_police = MouvementPolice.objects.create(
                police_id=police_id,
                mouvement_id=request.POST.get('mouvement'),
                motif_id=request.POST.get('motif'),
                date_effet=request.POST.get('date_effet'),
                date_fin_periode_garantie=date_fin_periode_garantie if date_fin_periode_garantie else None,
                created_by=request.user
            )
            mouvement_police.save()

            mouvement = Mouvement.objects.get(id=mouvement_police.mouvement_id)

            motif = Motif.objects.get(id=mouvement_police.motif_id)

            #si c'est une résiliation ou annulation changer le statut de la police
            if mouvement.code == "ANNUL" or mouvement.code == "RESIL":
                Police.objects.filter(id=police.id).update(
                    statut="ANNULE",
                    updated_at=datetime.now(),
                )

            # si c'est une suspension changer le statut de la police
            if mouvement.code == "SUSP":
                Police.objects.filter(id=police.id).update(
                    statut="INACTIF",
                    updated_at=datetime.now(),
                )

            #si c'est un renouvellement, créer une période de couverture
            if mouvement.code == "AVENANT":

                # créer une ligne dans période de couverture
                periode_couverture = PeriodeCouverture.objects.create(
                    police_id=police.id,
                    date_debut_effet=mouvement_police.date_effet,
                    date_fin_effet=mouvement_police.date_fin_periode_garantie,
                ).save()

                #Mettre à jour la date début_effet et fin_effet de la police
                # police.date_debut_effet = mouvement_police.date_effet
                # police.date_fin_effet = mouvement_police.date_fin_periode_garantie
                # police.save()

                #Pour une avenant de renouvelement changer le statut de la police
                if motif.code == "RENOUV":
                    Police.objects.filter(id=police.id).update(
                        statut="ACTIF",
                        updated_at=datetime.now(),
                    )

            response = {
                'statut': 1,
                'message': "Enregistrement effectuée avec succès !",
                'data': {
                    'id': mouvement_police.pk,
                    'mouvement': mouvement.libelle,
                    'motif': motif.libelle,
                    'date_effet': mouvement_police.date_effet,
                    'date_fin_periode_garantie': mouvement_police.date_fin_periode_garantie,
                }
            }

        return JsonResponse(response)


def motifs_by_mouvement(request, mouvement_id):
    motifs = Motif.objects.filter(mouvement_id=mouvement_id)
    motifs_serialize = serializers.serialize('json', motifs)
    return HttpResponse(motifs_serialize, content_type='application/json')


# upload du fichier
def handle_uploaded_photo(f, filename, police_id):
    path_ot_db = '/aliments/police_' + str(police_id)
    dirname = settings.MEDIA_URL.replace('/', '') + path_ot_db
    path = os.path.join(dirname)

    if not os.path.exists(path):
        os.makedirs(path)

    with open(dirname + '/' + filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return path_ot_db + '/' + filename


# upload fichier tarification
def handle_uploaded_fichier(f, filename):
    path_ot_db = '/tarifs/'
    dirname = settings.MEDIA_URL.replace('/', '') + path_ot_db
    path = os.path.join(dirname)

    if not os.path.exists(path):
        os.makedirs(path)

    with open(dirname + '/' + filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return path_ot_db + '/' + filename


# Générer le code pour le client
def generate_client_code():
    current_year = str(date.today().year)[-2:]

    # Trouver le dernier code créé dans la base de données
    last_code = Client.objects.aggregate(Max('code'))['code__max']

    # Extraire le numéro incrémental du dernier code
    if last_code:
        last_number = int(last_code.split('-')[0])  # Ex: "0001-CL24" -> 0001
        new_number = last_number + 1
    else:
        new_number = 1  # Si aucun code n'existe encore

    # Formatage du nouveau numéro pour garder 4 chiffres
    new_code = f"{str(new_number).zfill(4)}-CL{current_year}"

    return new_code


@method_decorator(login_required, name='dispatch')
class ClientsView(TemplateView):
    permission_required = "production.view_clients"
    template_name = 'client/clients.html'
    model = Client

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        types_clients = TypeClient.objects.all().order_by('libelle')
        types_personnes = TypePersonne.objects.all().order_by('libelle')
        civilites = Civilite.objects.all().order_by('name')
        bureaux = Bureau.objects.all().order_by('nom')
        pays = Pays.objects.all().order_by('nom')
        business_units = BusinessUnit.objects.all().order_by('libelle')
        utilisateurs = User.objects.filter(bureau=request.user.bureau, type_utilisateur__code="INTERNE", is_active=True).order_by('last_name')
        secteurs_activite = SecteurActivite.objects.filter(status=True).order_by('libelle')
        groupes = Groupe.objects.filter(statut=True)

        commercials = []

        utilisateur = User.objects.all().order_by('-first_name').exclude(is_admin_group=1)
        for user in utilisateur:
            if user.is_commercial:
                commercials.append(user)

        context_perso = {'types_clients': types_clients, 'types_personnes': types_personnes, 'secteurs_activite': secteurs_activite,
                         'civilites': civilites, 'bureaux': bureaux, 'pays': pays, 'business_units': business_units, 'commercials':commercials,
                         'utilisateurs': utilisateurs, 'groupes': groupes}

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


def clients_datatable(request):
    items_per_page = 10
    page_number = request.GET.get('page')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', items_per_page))
    sort_column_index = int(request.GET.get('order[0][column]'))
    sort_direction = request.GET.get('order[0][dir]')
    search_nom = request.GET.get('search_nom', '').strip()
    search_numero_police = request.GET.get('search_numero_police', '').strip()
    search_type_personne = request.GET.get('search_type_personne', '').strip()
    search_commercial = request.GET.get('search_commercial', '').strip()

    user = request.user

    queryset = Client.objects.filter(statut=Statut.ACTIF, bureau_id=user.bureau_id)

    """
    if user.is_commercial:
        queryset = Client.objects.filter(statut=Statut.ACTIF, bureau_id=user.bureau_id, commercial_id=user.id)
    elif user.is_production:
        queryset = Client.objects.filter(statut=Statut.ACTIF, bureau_id=user.bureau_id)
    else:
        queryset = Client.objects.none()
    """

    if search_nom:
        queryset = queryset.filter(
            Q(nom__icontains=search_nom) | Q(prenoms__icontains=search_nom)
        )

    #un client a plusieurs polices
    if search_numero_police:
        queryset = queryset.filter(
            Q(polices__numero__icontains=search_numero_police)
        ).distinct()

        pprint(search_numero_police)


    if search_type_personne:
        queryset = queryset.filter(
            Q(type_personne_id=search_type_personne)
        )

    if search_commercial:
        queryset = queryset.filter(
            Q(commercial_id=search_commercial)
        )


    # Apply sorting
    queryset = queryset.order_by('-code')

    paginator = Paginator(queryset, length)
    page_obj = paginator.get_page(page_number)

    # Prepare the data in the expected format
    data = []
    for c in page_obj:

        detail_url = reverse('client_details', args=[c.id])  # URL to the detail view
        modifier_client_url = reverse('modifier_client', args=[c.id])  # URL to the detail view

        # Bouton "Détails"
        actions_html = f'<a href="{detail_url}" class="text-center"><span class="badge btn-sm btn-details rounded-pill"><i class="fa fa-eye"></i> {_("Détails")}</span></a>&nbsp;&nbsp;'

        # Ajout conditionnel du bouton "Modifier"
        if request.user.is_production:
            actions_html += f'<span style="cursor:pointer;" class="btn_modifier_client badge btn-sm btn-modifier rounded-pill text-center" data-client_id="{c.id}" data-model_name="client" data-modal_title="MODIFICATION D\'UN CLIENT" data-href="{modifier_client_url}"><i class="fas fa-edit"></i> {_("Modifier")}</span>&nbsp;&nbsp;'

        liste_numeros_polices = ''
        for p in c.polices.filter(statut_validite=StatutValidite.VALIDE):
            detail_police_url = reverse('police.details', args=[p.id])  #
            liste_numeros_polices += f'<a target="_blank" href="{detail_police_url}"><span class="bold">{p.numero}</span></a>, '

        if not c.nom: c.nom = ''
        if not c.prenoms: c.prenoms = ''

        data.append({
            "id": c.id,
            "nom": c.nom + ' ' + c.prenoms,
            "numero_police": liste_numeros_polices[:-2],
            "code": c.code,
            "type_personne": c.type_personne.libelle if c.type_personne else "",
            "type_client": c.type_client.libelle if c.type_client else "",
            "business_unit": c.business_unit.libelle if c.business_unit else "",
            "telephone_mobile": c.telephone_mobile,
            "statut": c.statut,
            "actions": actions_html,
        })

    return JsonResponse({
        "data": data,
        "recordsTotal": queryset.count(),
        "recordsFiltered": paginator.count,
        "draw": int(request.GET.get('draw', 1)),
    })


# ajout d'un client
@login_required
def add_client(request):

    if request.method == 'POST':

        date_naissance = request.POST.get('date_naissance', None)
        if date_naissance:
            date_naissance = datetime.strptime(date_naissance, '%Y-%m-%d').date()
        else:
            date_creation = request.POST.get('date_creation')
            if date_creation:
                date_naissance = datetime.strptime(date_creation, '%Y-%m-%d').date()
            else:
                date_naissance = None

        client_created = Client.objects.create(bureau_id=67,
                                       nom=request.POST.get('nom'),
                                       prenoms=request.POST.get('prenoms'),
                                       secteur_activite_id=request.POST.get('secteur_activite_id'),
                                       type_client_id=request.POST.get('type_client_id'),
                                       business_unit_id=request.POST.get('business_unit_id'),
                                       commercial_id=request.POST.get('commercial'),
                                       groupe_id=request.POST.get('groupe_id'),
                                       date_naissance=date_naissance,
                                       telephone_mobile=request.POST.get('telephone_mobile'),
                                       telephone_fixe=request.POST.get('telephone_fixe'),
                                       email=request.POST.get('email'),
                                       ville=request.POST.get('ville'),
                                       adresse_postale=request.POST.get('adresse_postale'),
                                       adresse=request.POST.get('adresse'),
                                       site_web=request.POST.get('site_web'),
                                       twitter=request.POST.get('twitter'),
                                       instagram=request.POST.get('instagram'),
                                       facebook=request.POST.get('facebook'),
                                       civilite_id=request.POST.get('civilite_id'),
                                       sexe=request.POST.get('sexe'),
                                       created_by_id=request.user.id,
                                       created_at=datetime.now(),
                                       pays_id=request.POST.get('pays_id'),
                                       type_personne_id=request.POST.get('type_personne_id'),
                                       )

        #TODO : nomenclature du code client a trouver
        code_bureau = request.user.bureau.code
        client_created.code_provisoire = str(code_bureau) + str(Date.today().year)[-2:] + '-' + str(client_created.pk).zfill(7) + '-CL'
        client_created.code = generate_client_code()
        client_created.save()

        # Handle logo_client upload
        logo_client_file = request.FILES.get('logo_client')
        if logo_client_file:
            client_created.logo.save(logo_client_file.name, logo_client_file)
            client_created.save()

        try:
            pass
        except:
            pass


        response = {
            'statut': 1,
            'message': "Enregistrement effectuée avec succès !",
            'data': {
                'id': client_created.pk,
                'nom': client_created.nom,
                'prenoms': client_created.prenoms,
                'date_naissance': client_created.date_naissance,
                #'type_client': client_created.type_client.libelle if client_created.type_client else "",
                'type_personne': client_created.type_personne.libelle if client_created.type_personne else "",
                'ville': client_created.ville,
                'created_at': client_created.created_at,
                'statut': client_created.statut,
            }
        }

        return JsonResponse(response)


# modification d'un bénéficiaire
@login_required
def modifier_client(request, client_id):

    client = Client.objects.get(id=client_id)
    file_upload_path = ''

    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)

        date_naissance = request.POST.get('date_naissance')
        if date_naissance:
            date_naissance = datetime.strptime(date_naissance, '%Y-%m-%d').date()
        else:
            date_creation = request.POST.get('date_creation')
            if date_creation:
                date_naissance = datetime.strptime(date_creation, '%Y-%m-%d').date()
            else:
                date_naissance = None

        Client.objects.filter(id=client_id).update(nom=request.POST.get('nom'),
                                                   prenoms=request.POST.get('prenoms'),
                                                   secteur_activite_id=request.POST.get('secteur_activite_id'),
                                                   type_client_id=request.POST.get('type_client_id'),
                                                   business_unit_id=request.POST.get('business_unit_id'),
                                                   commercial_id=request.POST.get('commercial_id'),
                                                   groupe_id=request.POST.get('groupe_id'),
                                                   date_naissance=date_naissance,
                                                   telephone_mobile=request.POST.get('telephone_mobile'),
                                                   telephone_fixe=request.POST.get('telephone_fixe'),
                                                   email=request.POST.get('email'),
                                                   ville=request.POST.get('ville'),
                                                   adresse_postale=request.POST.get('adresse_postale'),
                                                   adresse=request.POST.get('adresse'),
                                                   site_web=request.POST.get('site_web'),
                                                   twitter=request.POST.get('twitter'),
                                                   instagram=request.POST.get('instagram'),
                                                   facebook=request.POST.get('facebook'),
                                                   ancienne_ref=request.POST.get('ancienne_ref'),
                                                   civilite_id=request.POST.get('civilite_id'),
                                                   sexe=request.POST.get('sexe'),
                                                   updated_at=datetime.now(),
                                                   pays_id=request.POST.get('pays_id'),
                                                   type_personne_id=request.POST.get('type_personne_id'),
                                                   )
        print(request.POST)
        # Handle logo_client upload
        logo_client_file = request.FILES.get('logo')
        if logo_client_file:
            client.logo.save(logo_client_file.name, logo_client_file)
            client.save()
            pprint("PHOTO SAUVEGARDÉ")


        response = {
            'statut': 1,
            'message': "Modification effectuée avec succès !",
            'data': {
                'id': client.pk,
                'nom': client.nom,
                'prenoms': client.prenoms,
                'date_naissance': client.date_naissance,
                'type_client': client.type_client.libelle if client.type_client else "",
                'type_personne': client.type_personne.libelle if client.type_personne else "",
                'ville': client.ville,
                'created_at': client.created_at,
                'statut': client.statut,
            }
        }

        return JsonResponse(response)

    else:
        client = Client.objects.get(id=client_id)
        types_clients = TypeClient.objects.all().order_by('libelle')
        types_personnes = TypePersonne.objects.all().order_by('libelle')
        civilites = Civilite.objects.all().order_by('name')
        business_units = BusinessUnit.objects.all().order_by('libelle')
        bureaux = Bureau.objects.all().order_by('nom')
        pays = Pays.objects.all().order_by('nom')
        utilisateurs = User.objects.all().order_by('last_name')
        genre = Genre
        secteurs_activite = SecteurActivite.objects.filter(status=True).order_by('libelle')
        groupes = Groupe.objects.filter(statut=True)

        commercials = []

        utilisateur = User.objects.all().order_by('-first_name').exclude(is_admin_group=1)
        for user in utilisateur:
            if user.is_commercial:
                commercials.append(user)

        return render(request, 'client/modal_client_modification.html',
                      {'client': client, 'types_clients': types_clients, 'types_personnes': types_personnes, 'secteurs_activite': secteurs_activite,
                       'civilites': civilites, 'business_units': business_units, 'bureaux': bureaux, 'pays': pays,
                       'utilisateurs': utilisateurs, 'genre': genre, 'commercials': commercials, 'groupes': groupes})


@login_required
def supprimer_client(request):
    if request.method == "POST":

        client_id = request.POST.get('client_id')

        client = Client.objects.get(id=client_id)
        if client.pk is not None:
            # client.delete()

            Client.objects.filter(id=client_id).update(statut=Statut.INACTIF)

            response = {
                'statut': 1,
                'message': "Client supprimé avec succès !",
            }

        else:

            response = {
                'statut': 0,
                'message': "Client non trouvé !",
            }

        return JsonResponse(response)


#Liste des polices du client
@method_decorator(login_required, name='dispatch')
class PoliceClientView(TemplateView):
    permission_required = "production.view_clients"
    template_name = 'client/client_polices.html'
    model = Client

    def get(self, request, client_id, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)


        clients = Client.objects.filter(id=client_id, bureau=request.user.bureau)
        if clients:
            client = clients.first()

            pprint(client.pays.devise)
            polices = Police.objects.filter(client_id=client_id, statut=StatutPolice.ACTIF, statut_contrat='CONTRAT', statut_validite=StatutValidite.VALIDE).order_by('-id')

            #les anciennes polices qui un mouvement_police de résiliation
            anciennes_polices = polices.filter(
                id__in=MouvementPolice.objects.filter(
                    mouvement__code="RESIL",
                    statut_validite=StatutValidite.VALIDE,
                    #date_effet__gte=datetime.datetime.now(tz=timezone.utc).date(),
                    police_id__in=polices.values_list('id', flat=True)
                ).values_list('police_id', flat=True)
            )

            statut_contrat = "CONTRAT"

            quittances = []
            for police in polices:
                quittances_of_police = Quittance.objects.filter(police_id=police.id)
                quittances.extend(quittances_of_police)

            acomptes = Acompte.objects.filter(client_id=client_id)

            filiales = Filiale.objects.filter(client_id=client_id)

            documents = Document.objects.filter(client_id=client_id)

            contacts = Contact.objects.filter(client_id=client_id)

            pays = Pays.objects.all().order_by('nom')

            types_documents = TypeDocument.objects.filter(is_production=1).order_by('libelle')

            types_prefinancements = TypePrefinancement.objects.filter(statut=Statut.ACTIF).order_by('libelle')

            # pour la creation de police
            branches = Branche.objects.filter(status=True).order_by('nom')
            produits = Produit.objects.all().order_by('nom')
            bureaux = Bureau.objects.all().order_by('nom')
            utilisateurs = None  # User.objects.all().order_by('last_name')
            apporteurs = Apporteur.objects.filter(status=True).order_by('nom')
            fractionnements = Fractionnement.objects.all().order_by('libelle')
            modes_reglements = ModeReglement.objects.all().order_by('libelle')
            regularisations = Regularisation.objects.all().order_by('libelle')
            compagnies = Compagnie.objects.filter(bureau=request.user.bureau, status=True).order_by('nom')
            durees = Duree.objects.all().order_by('libelle')
            devises = Devise.objects.filter(id=client.pays.devise_id).order_by('libelle')
            taxes = Taxe.objects.all().order_by('libelle')
            bureau_taxes = BureauTaxe.objects.filter(bureau_id=client.bureau_id)
            bases_calculs = BaseCalcul.objects.all().order_by('libelle')
            catgories = CategorieVehicule.objects.all().order_by('libelle')
            carburants = Carburant.objects.all().order_by('libelle')
            usages = Usage.objects.all().order_by('libelle')
            carosseries = Carosserie.objects.all().order_by('libelle')
            formules = Formule.objects.filter(status=True).order_by('libelle')
            typecompagnie = TypeCompagnie.objects.exclude(code="ASSPR").order_by('libelle')
            conditions_assurances = ConditionsAssurance.objects.filter(status=True).order_by('libelle')
            moyens_transports = MoyensTransport.objects.filter(status=True).order_by('libelle')
            today = datetime.now(tz=timezone.utc)

            placement_gestion = PlacementEtGestion
            mode_renouvellement = ModeRenouvellement
            calcul_tm = CalculTM
            type_majoration_contrat = TypeMajorationContrat

            bureaux = Bureau.objects.filter(id=request.user.bureau.id)

            aliments = request.session.get('aliments', None)
            #Vider les aliements enregistrer en session
            if 'aliments' in request.session:
                del request.session['aliments']

            print("Aliment transmis :", aliments)

            polices_data = []
            for contrat in polices:
                # Récupérer le dernier historique
                dernier_historique = HistoriquePolice.objects.filter(police_id=contrat.id).order_by('-date_du_jour').first()

                # Récupérer les assureurs associés à l'historique
                assureur_police = PoliceAssureur.objects.filter(historique_police_id=dernier_historique.id, type_compagnie_id=1) .first() if dernier_historique else []
                print("Police assureur : ", assureur_police)
                polices_data.append({
                    'police': contrat,
                    'dernier_historique': dernier_historique,
                    'assureur_police': assureur_police,
                })

            commercials = []
            utilisateur = User.objects.all().order_by('-first_name').exclude(is_admin_group=1)
            for user in utilisateur:
                if user.is_commercial:
                    commercials.append(user)

            gestionnaires = []
            utilisateur = User.objects.all().order_by('-first_name').exclude(is_admin_group=1)
            for user in utilisateur:
                if user.is_sinistre:
                    gestionnaires.append(user)

            productions = []
            utilisateur = User.objects.all().order_by('-first_name').exclude(is_admin_group=1)
            for user in utilisateur:
                if user.is_production:
                    productions.append(user)
            print('commercial id ', client.commercial_id)
            context_perso = {'client': client, 'contacts': contacts, 'polices': polices, 'quittances': quittances,
                             'acomptes': acomptes, 'typecompagnie': typecompagnie,
                             'filiales': filiales, 'documents': documents, 'types_documents': types_documents,
                             'branches': branches, 'produits': produits, 'pays': pays,
                             'compagnies': compagnies, 'durees': durees, 'placement_gestion': placement_gestion,
                             'mode_renouvellement': mode_renouvellement,
                             'calcul_tm': calcul_tm, 'conditions_assurances': conditions_assurances, 'moyens_transports': moyens_transports,
                             'fractionnements': fractionnements, 'modes_reglements': modes_reglements,
                             'regularisations': regularisations,
                             'devises': devises, 'utilisateurs': utilisateurs, 'bureaux': bureaux, 'taxes': taxes,
                             'bureau_taxes': bureau_taxes, 'today': today,
                             'apporteurs': apporteurs, 'bases_calculs': bases_calculs,
                             'type_majoration_contrat': type_majoration_contrat,
                             'statut_contrat': statut_contrat,
                             'types_prefinancements': types_prefinancements,
                             'anciennes_polices': anciennes_polices,
                             'catgories': catgories,
                             'carburants': carburants,
                             'usages': usages,
                             'carosseries':carosseries,
                             'formules':formules,
                             'polices_data':polices_data,
                             'commercials':commercials,
                             'gestionnaires':gestionnaires,
                             'productions':productions,
                             }

            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        else:
            return redirect("clients")


    def post(self):
        pass

    def get_context_data(self, **kwargs):

        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


# Récupérer les compagnies pour "Réassurance" ou "Coassurance"
def get_compagnies(request):
    # Récupérer les paramètres de la requête
    type_id = request.GET.get('type_id')
    exclude_compagnie_id = request.GET.get('compagnie_id')
    print("Compagnie choisie : ", exclude_compagnie_id)
    print("Type de compagnie : ", type_id)
    # Vérifiez que le type_id est fourni
    if not type_id:
        return JsonResponse({'error': 'Type ID is required.'}, status=400)

    try:
        # Filtrez les compagnies par type_id, en excluant celle spécifiée
        compagnies = Compagnie.objects.exclude(id=exclude_compagnie_id)

        # Créez la réponse JSON
        compagnies_data = [
            {'id': compagnie.id, 'nom': compagnie.nom}
            for compagnie in compagnies
        ]
        return JsonResponse({'compagnies': compagnies_data}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def produits_by_branche(request, branche_id):
    produits = Produit.objects.filter(branche_id=branche_id)
    produits_serialize = serializers.serialize('json', produits)
    return HttpResponse(produits_serialize, content_type='application/json')


def produit_sous_menu(request, produit_id):
    produit = Produit.objects.filter(id=produit_id)
    produit_serialize = serializers.serialize('json', produit)
    return HttpResponse(produit_serialize, content_type='application/json')


#Liste des contacts du client
@method_decorator(login_required, name='dispatch')
class ContactClientView(TemplateView):
    permission_required = "production.view_clients"
    template_name = 'client/client_contacts.html'
    model = Client

    def get(self, request, client_id, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)


        clients = Client.objects.filter(id=client_id, bureau=request.user.bureau)
        if clients:
            client = clients.first()

            statut_contrat = "CONTRAT"

            contacts = Contact.objects.filter(client_id=client_id).order_by('-id')

            context_perso = {'client': client, 'contacts': contacts,'statut_contrat': statut_contrat}

            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        else:
            return redirect("clients")


    def post(self):
        pass

    def get_context_data(self, **kwargs):

        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


#Liste des filiales du client
@method_decorator(login_required, name='dispatch')
class FilialeClientView(TemplateView):
    permission_required = "production.view_clients"
    template_name = 'client/client_filiales.html'
    model = Client

    def get(self, request, client_id, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)


        clients = Client.objects.filter(id=client_id, bureau=request.user.bureau)
        if clients:
            client = clients.first()

            statut_contrat = "CONTRAT"

            filiales = Filiale.objects.filter(client_id=client_id).order_by('-id')

            pays = Pays.objects.all().order_by('nom')

            context_perso = {'client': client,
                             'filiales': filiales, 'pays': pays, 'statut_contrat': statut_contrat
                             }

            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        else:
            return redirect("clients")


    def post(self):
        pass

    def get_context_data(self, **kwargs):

        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


#Liste des acomptes du client
@method_decorator(login_required, name='dispatch')
class AcompteClientView(TemplateView):
    permission_required = "production.view_clients"
    template_name = 'client/client_acomptes.html'
    model = Client

    def get(self, request, client_id, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)


        clients = Client.objects.filter(id=client_id, bureau=request.user.bureau)
        if clients:
            client = clients.first()

            acomptes = Acompte.objects.filter(client_id=client_id, solde__gt=0).order_by('date_versement')

            pays = Pays.objects.all().order_by('nom')

            bureaux = Bureau.objects.filter(id=request.user.bureau.id)

            quittances = Quittance.objects.filter(police__client_id=client_id, statut=StatutQuittance.IMPAYE, statut_validite=StatutValidite.VALIDE)

            solde_acomptes = sum(acompte.solde for acompte in acomptes)
            solde_quittances = sum(quittance.solde for quittance in quittances)
            difference_acomptes_quittances = solde_acomptes - solde_quittances

            context_perso = {
                'client': client,
                'acomptes': acomptes,
                'pays': pays,
                'bureaux': bureaux,
                'quittances': quittances,
                'solde_acomptes': solde_acomptes,
                'solde_quittances': solde_quittances,
                'difference_acomptes_quittances': difference_acomptes_quittances
            }

            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        else:
            return redirect("clients")


    def post(self):
        pass

    def get_context_data(self, **kwargs):

        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


#Liste des quittance du client
@method_decorator(login_required, name='dispatch')
class QuittancesClientView(TemplateView):
    permission_required = "production.view_clients"
    template_name = 'client/client_quittances.html'
    model = Client

    def get(self, request, client_id, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)


        clients = Client.objects.filter(id=client_id, bureau=request.user.bureau)
        if clients:
            client = clients.first()

            quittances = Quittance.objects.filter(police__client_id=client_id)

            # filtrer les quittances avec des statuts
            quittances_payees = Quittance.objects.filter(police__client_id=client_id, statut=StatutQuittance.PAYE, import_stats=False)
            quittances_impayees = Quittance.objects.filter(police__client_id=client_id, statut=StatutQuittance.IMPAYE, import_stats=False)
            quittances_honoraires = Quittance.objects.filter(police__client_id=client_id, type_quittance__code="HONORAIRE", import_stats=False)
            quittances_emissions = Quittance.objects.filter(police__client_id=client_id, type_quittance__code="EMISSION", import_stats=False)
            quittances_ristournes = Quittance.objects.filter(police__client_id=client_id, nature_quittance__code="Ristourne", import_stats=False)
            quittances_annulees = Quittance.objects.filter(police__client_id=client_id, statut_validite=StatutValiditeQuittance.ANNULEE, import_stats=False)

            context_perso = {
                'client': client,
                'quittances': quittances,
                'quittances_payees': quittances_payees,
                'quittances_impayees': quittances_impayees,
                'quittances_honoraires': quittances_honoraires,
                'quittances_emissions': quittances_emissions,
                'quittances_ristournes': quittances_ristournes,
                'quittances_annulees': quittances_annulees,
            }

            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        else:
            return redirect("clients")


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
def exporter_quittance(request, client_id, police_id):
    client = Client.objects.filter(id=client_id).first()
    police = Police.objects.filter(id=police_id).first()
    if request.method == 'POST':
        type_fichier_id = request.POST.get('type_fichier_id')
        date_exportation = request.POST.get('date_exportation')
        periode_debut = request.POST.get('periode_debut')
        periode_fin = request.POST.get('periode_fin')

        if int(type_fichier_id) in [1, 2, 3, 4]:

            typefichier = TypeFichier.objects.filter(id=type_fichier_id).first()
            pdf_url = reverse('generer_exportation_quittance', args=[typefichier.pk])
            pdf_url += (f""f"?de={date_exportation}"f"&pd={periode_debut}"f"&pf={periode_fin}"f"&cl={client.id}"f"&po={police.id}")

            response = {
                'statut': 1,
                'message': "Fichier généré avec succès !",
                'data': {
                    'typefichier_id': typefichier.id,
                    'date_exportation': date_exportation,
                    'periode_debut': periode_debut,
                    'periode_fin': periode_fin,
                    'pdf_url': pdf_url,
                },
            }
            return JsonResponse(response)

        else:
            response = {
                'statut': 0,
                'message': "Aucun type de fichier ne correspond au type de fichier soumis !",
                'data': []
            }
            return JsonResponse(response)

    else:

        typefichiers = TypeFichier.objects.all().order_by('-libelle').exclude(statut=0)
        today = datetime.now(tz=timezone.utc)

        return render(request, 'police/modal_exporter_quittance.html',
                      {'client': client, 'police':police, 'typefichiers': typefichiers, 'today':today})


#Générer le fichier d'exportation
def generer_exportation_quittance(request, typefichier_id):
    typefichier = TypeFichier.objects.filter(id=typefichier_id).first()

    # Récupérer les paramètres GET
    client = Client.objects.filter(id=request.GET.get('cl')).first()
    police = Police.objects.filter(id=request.GET.get('po')).first()
    date_exportation = request.GET.get('de')
    periode_debut = request.GET.get('pd')
    periode_fin = request.GET.get('pf')

    quittances = Quittance.objects.filter(police_id=police.id, police__client=client, statut_validite=StatutValidite.VALIDE).order_by('numero')
    
    if periode_debut and periode_fin:
        periode_debut = convertir_date_multiformat(periode_debut)
        periode_fin = convertir_date_multiformat(periode_fin)

        quittances = quittances.filter(
            Q(date_debut__gte=periode_debut, date_fin__lte=periode_fin) |
            (Q(statut=StatutQuittance.IMPAYE))
        ).order_by('numero')

    site_logo_url = request.build_absolute_uri(static(settings.JAZZMIN_SETTINGS['site_logo']))

    heure_actuelle = datetime.now().strftime('%H:%M:%S')
    
    quittance_impayees = Quittance.objects.filter(police_id=police.id, police__client=client, statut_validite=StatutValidite.VALIDE, statut=StatutQuittance.IMPAYE).order_by('numero')
    acomptes = Acompte.objects.filter(client_id=client.id, solde__gt=0)

    solde_acomptes = sum(acompte.solde for acompte in acomptes)
    solde_quittances = sum(quittance_impayee.solde for quittance_impayee in quittance_impayees)

    if solde_quittances > solde_acomptes:
        difference_acomptes_quittances = solde_quittances - solde_acomptes
    else:
        difference_acomptes_quittances = 0

    print('quittances : ', quittances)
    print("date_exportation : ", date_exportation)
    print("periode_debut : ", periode_debut)
    print("periode_fin : ", periode_fin)
    print("heure_actuelle : ", heure_actuelle)
    print("solde_acomptes : ", solde_acomptes)
    print("solde_quittances : ", solde_quittances)
    print("difference_acomptes_quittances : ", difference_acomptes_quittances)
    print("Logo : ", site_logo_url)

    contexte = {
        'client': client,
        'police': police,
        'quittances': quittances,
        'date_exportation': date_exportation,
        'periode_debut': periode_debut,
        'periode_fin': periode_fin,
        'heure_actuelle': heure_actuelle,
        'solde_acomptes': solde_acomptes,
        'solde_quittances': solde_quittances,
        'difference_acomptes_quittances': difference_acomptes_quittances,
        'site_logo_url': site_logo_url,
    }

    print('date_exportation : ', date_exportation)
    print('periode_debut : ', periode_debut)
    print('periode_fin : ', periode_fin)

    if typefichier:
        if typefichier.id == 1:
            pass
        elif typefichier.id == 2:

            pdf = render_pdf('police/courriers/quittances.html', contexte)

            pdf_file = PyPDF2.PdfReader(pdf)
            nombre_pages = len(pdf_file.pages)

            # Ajout du nombre de page obtenu au contexte pour le rendu final
            contexte['nombre_pages'] = nombre_pages
            pdf = render_pdf('police/courriers/quittances.html', contexte)

            # AFFICHER DIRECTEMENT
            return HttpResponse(File(pdf), content_type='application/pdf')

        elif typefichier.id == 3:

            # Chemin du document Word
            doc_path = os.path.join(settings.BASE_DIR, 'production', 'templates', 'police', 'courriers', "4-quittances.docx")

            doc_path = r"{}".format(doc_path)  # Pour s'assurer que c'est bien une chaîne Unicode

            # Charger le document Word
            document = WordDocument(doc_path)

            # Définir les remplacements de base
            base_replacements = {
                'BUREAU_NOM': client.bureau.nom if client.bureau.nom else '',
                'BUREAU_ADRESSE': client.bureau.addresse if client.bureau.addresse else '',
                'BUREAU_SITUATION_GEOGRAPHIQUE': client.bureau.situation_geographique if client.bureau.situation_geographique else '',
                'BUREAU_TELEPHONE': client.bureau.telephone if client.bureau.telephone else '',
                'BUREAU_FAX': client.bureau.fax if client.bureau.fax else '',
                'BUREAU_EMAIL': client.bureau.email if client.bureau.email else '',
                'POLICE_NUMERO': police.numero if police.numero else '',
                'CLIENT_NOM': client.nom if client.nom else '',
                'CLIENT_PRENOMS': client.prenoms if client.prenoms else '',
                'PERIODE': '', #"PERIODE ",periode_debut," - ",periode_fin,
                'DEVICE': 'XOF',
                'TOTAL_QUITTANCES_IMPAYEES': format_montant(solde_quittances) if solde_quittances else '0',
                'TOTAL_COMPTE_CLIENT': format_montant(solde_acomptes) if solde_acomptes else '0',
                'RESTANT_A_PAYER': format_montant( difference_acomptes_quittances) if difference_acomptes_quittances else '0',
                'LIBRE_TODAY': datetimes.today().strftime('%d/%m/%Y'),
                'LIBRE_TIMEDAY': heure_actuelle,
            }

            replacements = {}
            for key, value in base_replacements.items():
                formats = [
                    f'«{key}»', f'"{key}"', key
                ]
                for fmt in formats:
                    replacements[fmt] = str(value) if value else ""

            # Fonction pour remplacer le logo séparément
            def replace_logo_in_document(document, logo_path):
                if not logo_path:
                    return

                for paragraph in document.paragraphs:
                    if 'LOGO_SOC' in paragraph.text:
                        for run in paragraph.runs:
                            if 'LOGO_SOC' in run.text:
                                run.clear()
                                run.add_picture(logo_path, width=Inches(1.0))
                                break

                # Remplacer dans les en-têtes et les pieds de page également
                for section in document.sections:
                    # En-têtes
                    for paragraph in section.header.paragraphs:
                        if 'LOGO_SOC' in paragraph.text:
                            for run in paragraph.runs:
                                if 'LOGO_SOC' in run.text:
                                    run.clear()
                                    run.add_picture(logo_path, width=Inches(1.0))
                                    break

                    # Pieds de page
                    for paragraph in section.footer.paragraphs:
                        if 'LOGO_SOC' in paragraph.text:
                            for run in paragraph.runs:
                                if 'LOGO_SOC' in run.text:
                                    run.clear()
                                    run.add_picture(logo_path, width=Inches(1.0))
                                    break

            # Fonction pour remplacer les autres placeholders
            def replace_placeholders_in_paragraph(paragraph):
                original_text = paragraph.text
                new_text = original_text

                for placeholder, value in replacements.items():
                    if placeholder in new_text:
                        new_text = new_text.replace(placeholder, value)

                if new_text != original_text:
                    first_run = paragraph.runs[0] if paragraph.runs else paragraph.add_run()
                    first_run.text = new_text
                    for run in paragraph.runs[1:]:
                        run.clear()

            def replace_placeholders_in_document(document):
                for paragraph in document.paragraphs:
                    replace_placeholders_in_paragraph(paragraph)

                for table in document.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for paragraph in cell.paragraphs:
                                replace_placeholders_in_paragraph(paragraph)

                for section in document.sections:
                    for paragraph in section.header.paragraphs + section.footer.paragraphs:
                        replace_placeholders_in_paragraph(paragraph)
                    for table in section.header.tables + section.footer.tables:
                        for row in table.rows:
                            for cell in row.cells:
                                for paragraph in cell.paragraphs:
                                    replace_placeholders_in_paragraph(paragraph)

            def generate_document_response(document):
                response = HttpResponse(
                    content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
                response['Content-Disposition'] = 'attachment; filename="LISTE DES QUITTANCES.docx"'
                document.save(response)
                return response

            # Remplacement du logo

            if client.logo and hasattr(client.logo,
                                       'path') and os.path.isfile(
                client.logo.path):
                logo_path = client.logo.path
                replace_logo_in_document(document, logo_path)
            else:
                # Fonction pour remplacer le texte tout en conservant le format
                def remplacer_texte_avec_format(paragraphs, ancien_texte, nouveau_texte):
                    for para in paragraphs:
                        for run in para.runs:
                            if ancien_texte in run.text:
                                run.text = run.text.replace(ancien_texte, nouveau_texte)

                # Remplacer dans le corps du document
                remplacer_texte_avec_format(document.paragraphs, '«LOGO_SOC»', '')

                # Remplacer également dans les en-têtes (headers)
                for section in document.sections:
                    remplacer_texte_avec_format(section.header.paragraphs, '«LOGO_SOC»', '')

                # Remplacer également dans les pieds de page (footers)
                for section in document.sections:
                    remplacer_texte_avec_format(section.footer.paragraphs, '«LOGO_SOC»', '')

            # Remplacement des autres placeholders
            replace_placeholders_in_document(document)

            return generate_document_response(document)

        else:
            pass


#Liste des documents électronique du client
@method_decorator(login_required, name='dispatch')
class GEDClientView(TemplateView):
    permission_required = "production.view_clients"
    template_name = 'client/client_documents.html'
    model = Client

    def get(self, request, client_id, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        clients = Client.objects.filter(id=client_id, bureau=request.user.bureau)
        if clients:
            client = clients.first()

            pprint(client.pays.devise)

            statut_contrat = "CONTRAT"

            typedocuments = TypeDocument.objects.filter(is_sinistre=0, is_production=1)

            documents = Document.objects.filter(client_id=client_id)

            context_perso = {'client': client, 'documents': documents, 'typedocuments': typedocuments, 'statut_contrat': statut_contrat
                             }

            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        else:
            return redirect("clients")

    def post(self):
        pass

    def get_context_data(self, **kwargs):

        pprint(kwargs)
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


# Test excel file exploid
class ExcelFileView(View):
    def get(self, request, *args, **kwargs):
        formule = FormuleGarantie.objects.get(id=1)
        print(formule.tarfile.path)

        excel_data_df = pd.read_excel(formule.tarfile.path, sheet_name='actes')
        print(excel_data_df.head())
        print(excel_data_df)

        acte_row = excel_data_df.loc[excel_data_df['Code acte'] == 'CH0106']

        print(acte_row)
        print(acte_row.empty)
        print(acte_row.to_dict())
        print(acte_row.to_dict()['Code acte'])
        # print(acte_row.col)
        value = [i for i in acte_row.to_dict()['Code acte'] if acte_row.to_dict()['Code acte'][i] == "CH0106"]
        print("key by value:", value)
        print("key by value:", value[0])
        print(acte_row.to_dict()['Code acte'][value[0]])
        print(acte_row.to_dict().keys())
        acts = acte_row.to_dict()
        acts_kay = acte_row.to_dict().keys()

        dic = {}
        for i in list(acts_kay):
            print(i)
            print(type(i))
            dic[i] = acts[i][value[0]]

        print(dic)

        return HttpResponse("Get method is not allowed")


# liste des formules universelles pour assurance universelle
@method_decorator(login_required, name='dispatch')
class FormulesUniversellesView(TemplateView):
    # permission_required = "production.view_formules"
    template_name = 'police/formules_universelles.html'
    model = FormuleGarantie

    # @never_cache
    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        # police_id = kwargs['police_id']

        # police = Police.objects.get(id=police_id)
        bureau = request.user.bureau
        formules = FormuleGarantie.objects.filter(police__isnull=True, bureau=request.user.bureau, statut=Statut.ACTIF)
        territorialites = Territorialite.objects.all().order_by('libelle')
        types_tarifs = TypeTarif.objects.all().order_by('libelle')
        reseaux_soins = ""
        rubriques = Rubrique.objects.filter(status=True).order_by('libelle')
        mode_prefinancements = ModePrefinancement.objects.all().order_by('libelle')

        today = datetime.datetime.now(tz=timezone.utc)

        context_perso = {'bureau': bureau, 'formules': formules, 'types_tarifs': types_tarifs,
                         'territorialites': territorialites, 'reseaux_soins': reseaux_soins, 'rubriques': rubriques, 'mode_prefinancements':mode_prefinancements, 'today': today}

        context = {**context_original, **context_perso}

        return self.render_to_response(context)

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


# ajout de formule universelle pour assurance universelle
@login_required()
def add_formule_universelle(request):
    # police = Police.objects.get(id=police_id)

    # if police and request.method == 'POST':
    if request.method == 'POST':
        territorialite_id = request.POST.get('territorialite')
        type_tarif_id = request.POST.get('type_tarif')
        reseau_soin_id = request.POST.get('reseau_soin')
        taux_couverture = request.POST.get('taux_couverture')
        libelle = request.POST.get('libelle')
        plafond_conso_famille = request.POST.get('plafond_conso_famille').replace(' ', '')
        plafond_conso_individuelle = request.POST.get('plafond_conso_individuelle').replace(' ', '')
        garantis_pharmacie = request.POST.get('garantis_pharmacie')
        date_debut = request.POST.get('date_debut')

        #date_debut = police.date_debut_effet

        # Ajout des 5/6 champs complementaires
        infos_carte_consultation = request.POST.get('infos_carte_consultation')
        infos_carte_hospitalisation = request.POST.get('infos_carte_hospitalisation')
        infos_carte_ambulatoire = request.POST.get('infos_carte_ambulatoire')
        infos_carte_vitamine = request.POST.get('infos_carte_vitamine')
        infos_carte_vaccination = request.POST.get('infos_carte_vaccination')

        infos_carte_numero_police = request.POST.get('infos_carte_numero_police')
        infos_carte_show_numero_police = request.POST.get('infos_carte_show_numero_police',0)

        option_mode_prefinancement = request.POST.get('option_mode_prefinancement')
        selected_rubriques = request.POST.getlist('selected_rubriques') if option_mode_prefinancement == "TPP" else []

        if plafond_conso_famille == "": plafond_conso_famille = 0
        if plafond_conso_individuelle == "": plafond_conso_individuelle = 0

        taux_couverture = int(taux_couverture)
        taux_tm = 100 - taux_couverture

        territorialite = Territorialite.objects.get(id=territorialite_id)
        type_tarif = TypeTarif.objects.get(id=type_tarif_id)
        reseau_soin = ""

        mode_prefinancement = ModePrefinancement.objects.filter(code=option_mode_prefinancement).first()

        formule = FormuleGarantie.objects.create(
            created_by=request.user,
            # police_id=police_id,
            territorialite_id=territorialite.pk,
            type_tarif_id=type_tarif.pk,
            libelle=libelle,
            taux_couverture=taux_couverture,
            plafond_conso_famille=plafond_conso_famille,
            plafond_conso_individuelle=plafond_conso_individuelle,
            taux_tm=taux_tm,
            garantis_pharmacie=garantis_pharmacie,
            date_debut=date_debut,
            infos_carte_consultation=infos_carte_consultation,
            infos_carte_hospitalisation=infos_carte_hospitalisation,
            infos_carte_ambulatoire=infos_carte_ambulatoire,
            infos_carte_vitamine=infos_carte_vitamine,
            infos_carte_vaccination=infos_carte_vaccination,
            infos_carte_numero_police=infos_carte_numero_police,
            infos_carte_show_numero_police=infos_carte_show_numero_police,
            mode_prefinancement = mode_prefinancement,
            bureau = request.user.bureau
        )

        formule.save()

        code_bureau = request.user.bureau.code
        formule.code = 'F' + str(Date.today().year)[-2:] + '' + str(formule.pk).zfill(7) + str(code_bureau)
        formule.save()

        # associons des rubriques en cas de tiers payant partiel
        if option_mode_prefinancement == "TPP":
            for selected_rubrique in selected_rubriques:
                old_formule_rubrique = FormuleRubriquePrefinance.objects.filter(formulegarantie=formule, rubrique__id=int(selected_rubrique), statut_validite=StatutValidite.VALIDE).first()
                if old_formule_rubrique is None:
                    rubrique = Rubrique.objects.filter(id=int(selected_rubrique), status=True).first()
                    new_formule_rubrique = FormuleRubriquePrefinance.objects.create(
                        formulegarantie = formule,
                        rubrique = rubrique,
                        created_by=request.user
                    )
                    new_formule_rubrique.save()

        # suppressions des rubriques en dehors des selectionnées en cas de tiers payant partiel ou de l'ensemble dans le cas de tiers payant generalisé
        obsolete_formule_rubriques = FormuleRubriquePrefinance.objects.filter(formulegarantie=formule, statut_validite=StatutValidite.VALIDE).exclude(rubrique__id__in=selected_rubriques)
        for obsolete_formule_rubrique in obsolete_formule_rubriques:
            obsolete_formule_rubrique.statut_validite = StatutValidite.SUPPRIME
            obsolete_formule_rubrique.save()

        response = {
            'statut': 1,
            'message': "Enregistrement effectuée avec succès !",
            'data': {
                'id': formule.pk,
                'libelle': formule.libelle,
                'territorialite': formule.territorialite.libelle,
                'taux_couverture': formule.taux_couverture,
                'type_tarif': formule.type_tarif.libelle,
                'date_debut': formule.date_debut,
                'date_fin': formule.date_fin,
                'statut': formule.statut,
            }
        }

        return JsonResponse(response)


@method_decorator(login_required, name='dispatch')
class CourrierView(TemplateView):
    template_name = 'police/courrier.html'
    model = Courrier

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        police_id = kwargs.get('police_id')

            # Vérification de la police
        police = Police.objects.filter(id=police_id,bureau=request.user.bureau,statut_validite=StatutValidite.VALIDE).first()

        if police:
            courriers = Courrier.objects.all() # Récupère tous les courriers
            produits = Produit.objects.all()
            #today = timezone.now().date()
            today = datetime.now(tz=timezone.utc)

            context = {
                'police': police,  # Passe l'objet Police au template
                'courriers': courriers,  # Passe les courriers au template
                'produits': produits,
                'today': today,
            }

            return self.render_to_response(context)

        else:
            return redirect("clients")

    def get_context_data(self, **kwargs):
        # Ajout du contexte original enrichi avec admin.site.each_context
        context = super().get_context_data(**kwargs)
        context.update(admin.site.each_context(self.request))  # Contexte admin
        context['opts'] = self.model._meta  # Options du modèle Courrier
        return context


@method_decorator(login_required, name='dispatch')
class FormulesView(TemplateView):
    # permission_required = "production.view_formules"
    template_name = 'police/formules.html'
    model = FormuleGarantie

    # @never_cache
    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        police_id = kwargs['police_id']

        police = Police.objects.filter(id=police_id, bureau=request.user.bureau, statut_validite=StatutValidite.VALIDE).first()
        if police:
            formules = FormuleGarantie.objects.filter(police_id=police_id, statut=Statut.ACTIF)
            territorialites = Territorialite.objects.all().order_by('libelle')
            types_tarifs = TypeTarif.objects.all().order_by('libelle')
            reseaux_soins = ReseauSoin.objects.filter(bureau=police.bureau)
            rubriques = Rubrique.objects.filter(status=True).order_by('libelle')
            mode_prefinancements = ModePrefinancement.objects.all().order_by('libelle')

            today = datetime.now(tz=timezone.utc)

            context_perso = {'police': police, 'formules': formules, 'types_tarifs': types_tarifs,
                             'territorialites': territorialites, 'reseaux_soins': reseaux_soins, 'rubriques': rubriques, 'mode_prefinancements':mode_prefinancements, 'today': today}

            context = {**context_original, **context_perso}

            return self.render_to_response(context)

        else:
            return redirect("clients")

    def post(self):
        pass

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


# ajout de bareme
@login_required()
def add_formule(request, police_id):
    police = Police.objects.get(id=police_id)

    if police and request.method == 'POST':
        territorialite_id = request.POST.get('territorialite')
        type_tarif_id = request.POST.get('type_tarif')
        reseau_soin_id = request.POST.get('reseau_soin')
        taux_couverture = request.POST.get('taux_couverture')
        libelle = request.POST.get('libelle')
        plafond_conso_famille = request.POST.get('plafond_conso_famille').replace(' ', '')
        plafond_conso_individuelle = request.POST.get('plafond_conso_individuelle').replace(' ', '')
        garantis_pharmacie = request.POST.get('garantis_pharmacie')
        #date_debut = request.POST.get('date_debut')
        date_debut = police.date_debut_effet

        # Ajout des 5/6 champs complementaires
        infos_carte_consultation = request.POST.get('infos_carte_consultation')
        infos_carte_hospitalisation = request.POST.get('infos_carte_hospitalisation')
        infos_carte_ambulatoire = request.POST.get('infos_carte_ambulatoire')
        infos_carte_vitamine = request.POST.get('infos_carte_vitamine')
        infos_carte_vaccination = request.POST.get('infos_carte_vaccination')

        infos_carte_numero_police = request.POST.get('infos_carte_numero_police')
        infos_carte_show_numero_police = request.POST.get('infos_carte_show_numero_police')

        option_mode_prefinancement = request.POST.get('option_mode_prefinancement')
        selected_rubriques = request.POST.getlist('selected_rubriques') if option_mode_prefinancement == "TPP" else []


        exclusion = request.POST.get('exclusion')
        # print(option_type_prefinancement)
        # print(selected_rubriques)

        # obsolete_formule_rubriques = FormuleRubriquePrefinance.objects.filter(statut_validite=StatutValidite.VALIDE).exclude(rubrique__id__in=selected_rubriques)            

        # print(obsolete_formule_rubriques)

        if plafond_conso_famille == "": plafond_conso_famille = 0
        if plafond_conso_individuelle == "": plafond_conso_individuelle = 0

        taux_couverture = int(taux_couverture)
        taux_tm = 100 - taux_couverture

        territorialite = Territorialite.objects.get(id=territorialite_id)
        type_tarif = TypeTarif.objects.get(id=type_tarif_id)
        reseau_soin = ReseauSoin.objects.get(id=reseau_soin_id) if reseau_soin_id else None

        mode_prefinancement = ModePrefinancement.objects.filter(code=option_mode_prefinancement).first()

        formule = FormuleGarantie.objects.create(
            created_by=request.user,
            police_id=police_id,
            territorialite_id=territorialite.pk,
            type_tarif_id=type_tarif.pk,
            reseau_soin=reseau_soin,
            libelle=libelle,
            taux_couverture=taux_couverture,
            plafond_conso_famille=plafond_conso_famille,
            plafond_conso_individuelle=plafond_conso_individuelle,
            taux_tm=taux_tm,
            garantis_pharmacie=garantis_pharmacie,
            date_debut=date_debut,
            infos_carte_consultation=infos_carte_consultation,
            infos_carte_hospitalisation=infos_carte_hospitalisation,
            infos_carte_ambulatoire=infos_carte_ambulatoire,
            infos_carte_vitamine=infos_carte_vitamine,
            infos_carte_vaccination=infos_carte_vaccination,
            infos_carte_numero_police=infos_carte_numero_police,
            infos_carte_show_numero_police=infos_carte_show_numero_police,
            mode_prefinancement=mode_prefinancement,
            bureau=police.bureau,
            exclusion=exclusion
        )

        formule.save()

        code_bureau = request.user.bureau.code
        formule.code = 'F' + str(Date.today().year)[-2:] + '' + str(formule.pk).zfill(7) + str(code_bureau)
        formule.save()

        # associons des rubriques en cas de tiers payant partiel
        if option_mode_prefinancement == "TPP":
            for selected_rubrique in selected_rubriques:
                old_formule_rubrique = FormuleRubriquePrefinance.objects.filter(formulegarantie=formule, rubrique__id=int(selected_rubrique), statut_validite=StatutValidite.VALIDE).first()
                if old_formule_rubrique is None:
                    rubrique = Rubrique.objects.filter(id=int(selected_rubrique), status=True).first()
                    new_formule_rubrique = FormuleRubriquePrefinance.objects.create(
                        formulegarantie = formule,
                        rubrique = rubrique,
                        created_by=request.user
                    )
                    new_formule_rubrique.save()

        # suppressions des rubriques en dehors des selectionnées en cas de tiers payant partiel ou de l'ensemble dans le cas de tiers payant generalisé
        obsolete_formule_rubriques = FormuleRubriquePrefinance.objects.filter(formulegarantie=formule, statut_validite=StatutValidite.VALIDE).exclude(rubrique__id__in=selected_rubriques)
        for obsolete_formule_rubrique in obsolete_formule_rubriques:
            obsolete_formule_rubrique.statut_validite = StatutValidite.SUPPRIME
            obsolete_formule_rubrique.save()

        response = {
            'statut': 1,
            'message': "Enregistrement effectuée avec succès !",
            'data': {
                'id': formule.pk,
                'libelle': formule.libelle,
                'territorialite': formule.territorialite.libelle,
                'taux_couverture': formule.taux_couverture,
                'type_tarif': formule.type_tarif.libelle,
                'date_debut': formule.date_debut,
                'date_fin': formule.date_fin,
                'statut': formule.statut,
            }
        }

        return JsonResponse(response)


# dialog modifier formule et update réel
@login_required()
@never_cache
def modifier_formule(request, formule_id):
    formule = FormuleGarantie.objects.get(id=formule_id)
    police = formule.police if formule else None

    if request.method == 'POST':

        formule_before = formule
        pprint(formule_before)

        libelle = request.POST.get('libelle')
        taux_couverture = int(request.POST.get('taux_couverture').replace(" ", ""))
        type_tarif_id = request.POST.get('type_tarif')
        reseau_soin_id = request.POST.get('reseau_soin')
        territorialite_id = request.POST.get('territorialite')
        plafond_conso_individuelle = request.POST.get('plafond_conso_individuelle').replace(" ", "")
        plafond_conso_famille = request.POST.get('plafond_conso_famille').replace(" ", "")
        garantis_pharmacie = request.POST.get('garantis_pharmacie')
        date_debut = request.POST.get('date_debut') if formule_before.police is None else formule.date_debut
        exclusion = request.POST.get('exclusion')

        # Infos complementaires
        infos_carte_consultation = request.POST.get('infos_carte_consultation', '')
        infos_carte_hospitalisation = request.POST.get('infos_carte_hospitalisation', '')
        infos_carte_ambulatoire = request.POST.get('infos_carte_ambulatoire', '')
        infos_carte_vitamine = request.POST.get('infos_carte_vitamine', '')
        infos_carte_vaccination = request.POST.get('infos_carte_vaccination', '')
        infos_carte_show_numero_police = request.POST.get('infos_carte_show_numero_police', 0)

        option_mode_prefinancement = request.POST.get('option_mode_prefinancement')
        selected_rubriques = request.POST.getlist('selected_rubriques') if option_mode_prefinancement == "TPP" else []

        mode_prefinancement = ModePrefinancement.objects.filter(code=option_mode_prefinancement).first()

        if plafond_conso_famille == "": plafond_conso_famille = 0
        if plafond_conso_individuelle == "": plafond_conso_individuelle = 0

        if taux_couverture >= 0 and taux_couverture <= 100:
            formule.libelle = libelle
            formule.taux_couverture = taux_couverture
            formule.taux_tm = 100 - taux_couverture
            formule.type_tarif_id = type_tarif_id
            formule.territorialite_id = territorialite_id
            if reseau_soin_id: formule.reseau_soin_id = reseau_soin_id
            formule.plafond_conso_individuelle = plafond_conso_individuelle
            formule.plafond_conso_famille = plafond_conso_famille
            formule.garantis_pharmacie = garantis_pharmacie
            #formule.date_debut = date_debut
            formule.updated_at = datetime.datetime.now(tz=timezone.utc)
            formule.updated_by = request.user
            formule.exclusion=exclusion

            formule.infos_carte_consultation = infos_carte_consultation
            formule.infos_carte_hospitalisation = infos_carte_hospitalisation
            formule.infos_carte_ambulatoire = infos_carte_ambulatoire
            formule.infos_carte_vitamine = infos_carte_vitamine
            formule.infos_carte_vaccination = infos_carte_vaccination
            formule.infos_carte_show_numero_police = infos_carte_show_numero_police
            formule.mode_prefinancement = mode_prefinancement
            formule.date_debut = date_debut


            ActionLog.objects.create(done_by=request.user, action="update",
                                     description="Modification d'une formule de garantie", table="formulegarantie",
                                     row=formule.pk,
                                     #data_before=json.dumps(custom_model_to_dict(formule_before)),
                                     #data_after=json.dumps(custom_model_to_dict(formule))
                                     )

            formule.save()

            # associons des rubriques en cas de tiers payant partiel
            if option_mode_prefinancement == "TPP":
                for selected_rubrique in selected_rubriques:
                    old_formule_rubrique = FormuleRubriquePrefinance.objects.filter(formulegarantie=formule, rubrique__id=int(selected_rubrique), statut_validite=StatutValidite.VALIDE).first()
                    if old_formule_rubrique is None:
                        rubrique = Rubrique.objects.filter(id=int(selected_rubrique), status=True).first()
                        new_formule_rubrique = FormuleRubriquePrefinance.objects.create(
                            formulegarantie = formule,
                            rubrique = rubrique,
                            created_by=request.user
                        )
                        new_formule_rubrique.save()

            # suppressions des rubriques en dehors des selectionnées en cas de tiers payant partiel ou de l'ensemble dans le cas de tiers payant generalisé
            obsolete_formule_rubriques = FormuleRubriquePrefinance.objects.filter(formulegarantie=formule, statut_validite=StatutValidite.VALIDE).exclude(rubrique__id__in=selected_rubriques)
            for obsolete_formule_rubrique in obsolete_formule_rubriques:
                obsolete_formule_rubrique.statut_validite = StatutValidite.SUPPRIME
                obsolete_formule_rubrique.save()

            response = {
                'statut': 1,
                'message': "Modification effectuée avec succès !",
                'data': {
                    'id': formule.pk,
                    'libelle': formule.libelle,
                    'statut': formule.statut,
                }
            }

        else:
            response = {
                'statut': 0,
                'message': "Le taux de couverture doit être compris entre 0 et 100",
                'data': {
                }
            }

        return JsonResponse(response)


    else:

        formule = FormuleGarantie.objects.get(id=formule_id)
        formules = FormuleGarantie.objects.all()
        territorialites = Territorialite.objects.all().order_by('libelle')
        types_tarifs = TypeTarif.objects.all().order_by('libelle')
        reseaux_soins = ReseauSoin.objects.filter(bureau=request.user.bureau).order_by('nom')

        today =datetime.datetime.now(tz=timezone.utc)

        rubriques = Rubrique.objects.filter(status=True).order_by('libelle')
        mode_prefinancements = ModePrefinancement.objects.all().order_by('libelle')
        formule_rubriques = FormuleRubriquePrefinance.objects.filter(formulegarantie=formule, statut_validite=StatutValidite.VALIDE).order_by('rubrique__libelle')

        # formule.plafond_conso_famille = float(formule.plafond_conso_famille)
        # formule.plafond_conso_individuelle = float(formule.plafond_conso_individuelle)

        template = 'police/modal_formule_update.html' if police else 'police/modal_formule_update_universelle.html'

        return render(request, template, {'formule': formule, 'types_tarifs': types_tarifs,
                                                                    'territorialites': territorialites, 'reseaux_soins': reseaux_soins, 'rubriques': rubriques, 'mode_prefinancements':mode_prefinancements, 'formule_rubriques':formule_rubriques, 'today': today, 'police': police})


@login_required()
def export_sinistres_police(request, police_id):
    police = Police.objects.get(id=police_id)
    #today = datetime.datetime.now(tz=timezone.utc)

    if police:

        queryset = Sinistre.objects.filter(police=police, statut_validite=StatutValidite.VALIDE).order_by('-id')

        print("queryset")
        print(queryset)
        print(queryset.count())

        # Exportation excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="LISTE_SINISTRES_POLICE_'+str(police.numero)+'__{:%d:%m:%Y}.xlsx"'.format(timezone.now())

        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = 'SINISTRES - {}'.format(police.numero)

        # Write header row
        header = [
            'NUMERO_SINISTRE',
            'NUMERO_FEUILLE_SOIN',
            'BENEFICIAIRE',
            'NUMERO_CARTE',
            'QUALITE',
            'ADHERENT_PRINCIPAL',
            'ACTE',
            'PRESTATAIRE',
            'FRAIS_REEL',
            'PART_ASSUREUR',
            'PART_BENEFICIAIRE',
            'DATE_PRESTATION',
            'DATE_SAISIE',
            'REFERENCE_FACTURE',
            'DATE_RECEPTION_FACTURE',
            'ETAT',
        ]
        for col_num, column_title in enumerate(header, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.value = column_title

        # Write data rows
        data = []

        for sinistre in queryset:

            adherent_principal = ""
            numero_carte = ""
            beneficiaire = ""
            qualite = ""

            data_item = [
                sinistre.numero if sinistre.numero else "",
                sinistre.dossier_sinistre.numero if sinistre.dossier_sinistre and sinistre.dossier_sinistre.numero else "",
                beneficiaire,
                numero_carte if numero_carte else "",
                qualite,
                adherent_principal,
                sinistre.acte.libelle if sinistre.acte and sinistre.acte.libelle else "",
                sinistre.prestataire.name if sinistre.prestataire and sinistre.prestataire.name else "",
                sinistre.total_frais_reel,
                sinistre.total_part_compagnie if sinistre.part_compagnie else "",
                sinistre.total_part_assure if sinistre.part_assure else "",
                sinistre.date_survenance.strftime("%d/%m/%Y %H:%m") if sinistre.date_survenance else "",
                sinistre.created_at.strftime("%d/%m/%Y %H:%m") if sinistre.created_at else "",
                sinistre.reference_facture if sinistre.reference_facture else "",
                sinistre.date_reception_facture.strftime("%d/%m/%Y") if sinistre.date_reception_facture else "",
                sinistre.statut if sinistre.statut else "",
            ]
            data.append(data_item)

        for row_num, row in enumerate(data, 1):
            for col_num, cell_value in enumerate(row, 1):
                cell = worksheet.cell(row=row_num + 1, column=col_num)
                cell.value = cell_value

        workbook.save(response)
        return response

    else:
        return JsonResponse({
            "message": "Bénéficiaire non trouvé"
        }, status=404)


# Annulation de quittance
@method_decorator(login_required, name='dispatch')
class AnnulerQuittanceView(TemplateView):
    template_name = 'police/annuler_quittance.html'
    model = Quittance

    # traitement à l'appel du lien en get
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        context['breadcrumbs'] = [
            {'title': 'Factures', 'url': ''},
            {'title': 'Annulation', 'url': ''},
        ]
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        # recuperation de tout ce qui peut venir en post que ca soit pour la recherche ou la suppression
        btn_recherche = self.request.POST.get('recherche', None)
        submit_delete_item = self.request.POST.get('submit_delete_item', None)
        id_item = self.request.POST.get('id_item', None)
        motif_delete_item = self.request.POST.get('motif_delete_item', None)
        numero_quittance = self.request.POST.get('numero_quittance', None)
        context['breadcrumbs'] = [
            {'title': 'Factures', 'url': ''},
            {'title': 'Annulation', 'url': ''},
        ]
        dossier_reglement = None

        # cette condition précise que nous venons faire la recherche
        if btn_recherche and numero_quittance:
            quittance = Quittance.objects.filter(numero=numero_quittance, bureau=request.user.bureau, statut_validite=StatutValiditeQuittance.VALIDE).first()
            # dd(quittance)

            context['numero_quittance'] = numero_quittance
            context['quittance'] = quittance

        """
        # cette condition précise que nous venons faire l'annulation de la quittance
        if submit_delete_item and id_item:

            quittance = Quittance.objects.filter(id=id_item, bureau=request.user.bureau, statut=StatutQuittance.IMPAYE).first()

            if quittance:

                #récupérer les règlements sur la quittance
                reglements = Reglement.objects.filter(quittance=quittance, bureau=request.user.bureau)

                if reglements:
                    context['reglements_existants'] = True

                    '''
                    #TODO: Traitement à discuter et confirmer avec Marius
                    #vérifier s'il existe un règlement déjà reversé compagnie
                    if reglements.filter(statut_reversement_compagnie=StatutReversementCompagnie.REVERSE).first():
                        context['reverse_reglement'] = True
                        #Avoir l'accord de la finance (GILDAS)

                    else:
                        context['reglements_existants_annules'] = True
                        #Annuler les règlements sur la quittances
                        for reglement in reglements:
                            # traitement reglement
                            reglement.reg_deleted_by = request.user
                            reglement.statut_validite = StatutValidite.SUPPRIME
                            reglement.observation = motif_delete_item
                            #reglement.save #décommenter après

                            ActionLog.objects.create(done_by=request.user, action="annulation_reglement", description="Annulation d'un règlement", table="reglement", row=reglement.pk)
                            #

                        # Annuler la quittance
                        quittance.deleted_by = request.user
                        quittance.statut_validite = StatutValidite.SUPPRIME
                        quittance.observation = motif_delete_item
                        quittance.save()
                        context['old_quittance'] = quittance.numero
                        #
                    '''

                else:
                    context['reglements_existants'] = False

                    # Annuler la quittance
                    quittance.deleted_by = request.user
                    quittance.statut_validite = StatutValiditeQuittance.ANNULEE
                    quittance.observation = motif_delete_item
                    quittance.save()
                    context['old_quittance'] = quittance.numero
                    #

                    #Créer une ligne dans mouvement_quittances



                # enregistrer dans les log
                ActionLog.objects.create(done_by=request.user, action="annulation_quittance",
                                         description="Annulation d'une quittances", table="quittances",
                                         row=quittance.pk)
        """
        # print(code_dossier_police) """
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


# Annulation de la quittance
def add_annuler_quittance(request):
    if request.method == "POST":
        id_item = request.POST.get('id_item')
        motif_delete_item = request.POST.get('motif_delete_item')
        type_commission = "GESTION" if type == "courtage" else "COURTAGE"

        quittance = Quittance.objects.filter(id=id_item, bureau=request.user.bureau).first()

        if quittance:
            # Date de paiement
            date_annulation_quittance = datetime.now(tz=timezone.utc)

            # Récupération de la police associée à la quittance
            police = Police.objects.filter(id=quittance.police_id).first()

            # Récupérer les règlements sur la quittance
            reglements = Reglement.objects.filter(quittance=quittance, bureau=request.user.bureau)

            if reglements:
                # Annuler les règlements sur la quittance
                for reglement in reglements:
                    if reglement.statut_reversement_compagnie == "NON REVERSE":
                        # Créer un nouveau règlement et passer les données comme une quittance ristourne
                        reglement_ristourne = Reglement.objects.create(quittance_id=quittance.id,
                                                                       montant=-(reglement.montant),
                                                                       montant_compagnie=-(reglement.montant_compagnie),
                                                                       compagnie=reglement.compagnie,
                                                                       devise_id=reglement.devise_id,
                                                                       # banque_id=reglement.banque_id,
                                                                       banque_emettrice=reglement.banque_emettrice,
                                                                       compte_tresorerie_id=reglement.compte_tresorerie_id,
                                                                       numero_piece=reglement.numero_piece,
                                                                       montant_com_courtage=-(reglement.montant_com_courtage),
                                                                       montant_com_intermediaire=reglement.montant_com_intermediaire,
                                                                       mode_reglement=reglement.mode_reglement,
                                                                       created_by=reglement.created_by,
                                                                       statut_validite=StatutValidite.VALIDE,
                                                                       bureau=reglement.bureau)
                        reglement_ristourne.save()
                        # mettre à jour son numéro
                        reglement_ristourne.numero = 'R' + str(Date.today().year) + str(reglement_ristourne.pk).zfill(6)
                        reglement_ristourne.statut_reversement_compagnie = StatutReversementCompagnie.REVERSE
                        reglement_ristourne.statut_validite = StatutValidite.SUPPRIME
                        reglement_ristourne.save()

                    if reglement.statut_reversement_compagnie == "REVERSE":
                        if reglement.statut_commission == "ENCAISSEE":
                            encaiss_com = EncaissementCommission.objects.create(reglement=reglement,
                                                                                created_by=request.user,
                                                                                montant_com_courtage=-(reglement.montant_com_courtage),
                                                                                montant_com_gestion=-(reglement.montant_com_gestion) if reglement.montant_com_gestion else 0,
                                                                                type_commission=type_commission)
                            encaiss_com.save()

                        # Créer un nouveau règlement et passer les données comme une quittance ristourne
                        reglement_ristourne = Reglement.objects.create(quittance_id=quittance.id,
                                                                       montant=-(reglement.montant),
                                                                       montant_compagnie=-(reglement.montant_compagnie),
                                                                       compagnie=reglement.compagnie,
                                                                       devise_id=reglement.devise_id,
                                                                       # banque_id=reglement.banque_id,
                                                                       banque_emettrice=reglement.banque_emettrice,
                                                                       compte_tresorerie_id=reglement.compte_tresorerie_id,
                                                                       numero_piece=reglement.numero_piece,
                                                                       montant_com_courtage=-(reglement.montant_com_courtage),
                                                                       montant_com_intermediaire=reglement.montant_com_intermediaire,
                                                                       mode_reglement=reglement.mode_reglement,
                                                                       created_by=reglement.created_by,
                                                                       statut_validite=StatutValidite.VALIDE,
                                                                       bureau=reglement.bureau)
                        reglement_ristourne.save()
                        # mettre à jour son numéro
                        reglement_ristourne.numero = 'R' + str(Date.today().year) + str(reglement_ristourne.pk).zfill(6)
                        reglement_ristourne.statut_reversement_compagnie = StatutReversementCompagnie.REVERSE
                        reglement_ristourne.statut_validite = StatutValidite.SUPPRIME
                        reglement_ristourne.save()

                    # traitement reglement
                    reglement.reg_deleted_by = request.user
                    reglement.statut_reversement_compagnie = StatutReversementCompagnie.REVERSE
                    reglement.statut_validite = StatutValidite.SUPPRIME
                    reglement.observation = motif_delete_item
                    reglement.save()

                    # Créer une ligne d'acompte
                    acompte = Acompte(
                                    credit=reglement.montant,
                                    solde=reglement.montant,
                                    periode_debut=police.date_debut_effet,
                                    periode_fin=police.date_debut_effet,
                                    date_versement=datetime.now(),
                                    created_at=datetime.now(),
                                    observation=motif_delete_item,
                                )
                    acompte.client_id = police.client_id
                    acompte.police_id = police.id
                    acompte.quittance_id = quittance.id
                    acompte.save()

                # Créer une nouvelle quittance ristourne
                quittance_ristourne = Quittance.objects.create(police_id=quittance.police_id,
                                                     compagnie=quittance.compagnie,
                                                     devise=quittance.devise,
                                                     nature_quittance_id=quittance.nature_quittance_id,
                                                     type_quittance_id=quittance.type_quittance_id,
                                                     cout_police_courtier=quittance.cout_police_courtier,
                                                     cout_police_compagnie=quittance.cout_police_compagnie,
                                                     taxe=quittance.taxe,
                                                     autres_taxes=quittance.autres_taxes,
                                                     prime_ht=-(quittance.prime_ht),
                                                     prime_ttc=-(quittance.prime_ttc),
                                                     montant_regle=0,
                                                     solde=quittance.solde,
                                                     taux_com_courtage=quittance.taux_com_courtage,
                                                     commission_courtage=-(quittance.commission_courtage),
                                                     commission_intermediaires=quittance.commission_intermediaires,
                                                     date_emission=quittance.date_emission,
                                                     date_debut=quittance.date_debut,
                                                     date_fin=quittance.date_fin,
                                                     statut=quittance.statut,
                                                     created_by=quittance.created_by,
                                                     bureau=quittance.bureau
                                                     )

                # Mettre a jour le numero
                code_bureau = request.user.bureau.code
                numero = str(code_bureau) + str(Date.today().year)[-2:] + '-' + str(quittance_ristourne.pk).zfill(
                    7) + '-Q'
                quittance_ristourne.numero = numero
                quittance_ristourne.save()

                # mise à jour du solde de la quittance
                quittance_ristourne.montant_regle = quittance.prime_ttc
                quittance_ristourne.solde = 0
                quittance_ristourne.statut = StatutQuittance.PAYE
                quittance_ristourne.updated_at = date_annulation_quittance
                quittance_ristourne.save()

                # Annuler la quittance
                quittance.deleted_by = request.user
                quittance.statut_validite = StatutValiditeQuittance.ANNULEE
                quittance.observation = motif_delete_item
                quittance.save()

                return redirect(reverse('police_quittances', args=[police.id]))

            # Annuler la quittance
            quittance.deleted_by = request.user
            quittance.statut_validite = StatutValiditeQuittance.ANNULEE
            quittance.observation = motif_delete_item
            quittance.save()

            return redirect(reverse('police_quittances', args=[police.id]))

        else:
            return redirect(reverse('annuler_quittance'))

    return redirect(reverse('annuler_quittance'))


def generer_courrier(request , police_id, courrier_id, quittance_id=None):
    police = get_object_or_404(Police, id=police_id)
    courrier = get_object_or_404(Courrier, id=courrier_id)

    # Récupérer le dernier historique de la police
    historique_police = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()
    # Récupérer l'assureur associé à l'historique
    assureur_police = PoliceAssureur.objects.filter(historique_police_id=historique_police.id,type_compagnie_id=1).first()

    # Vérifier si une quittance est spécifiée
    if quittance_id:
        quittance = get_object_or_404(Quittance, id=quittance_id, police_id=police_id)
        numero_quittance = quittance.numero
    else:
        numero_quittance = None

    date_fin_effet_plus_un=''
    date_renouvellement=''
    if historique_police.date_fin_effet:
        date_fin_effet_plus_un = historique_police.date_fin_effet + timedelta(days=1)
        date_renouvellement = date_fin_effet_plus_un.strftime('%d/%m/%Y')

    site_logo_url = request.build_absolute_uri(static(settings.JAZZMIN_SETTINGS['site_logo']))
    print("Logo : ", site_logo_url)
    print("Client : ", police.client)
    print('date_renouvellement', date_renouvellement)

    # Configuration du locale pour le formatage
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

    template_content =  {
        'nom_client': police.client.nom,
        'code_client': police.client.code,
        'adress_client': police.client.adresse,
        'numero_police': police.numero,
        'nom_produit': police.produit.nom,
        'nom_courrier': courrier.designation,
        'numero_quittance':numero_quittance,
        'date_debut_effet': historique_police.date_debut_effet.strftime('%d/%m/%Y') if historique_police.date_debut_effet else '',
        'date_fin_effet': historique_police.date_fin_effet.strftime('%d/%m/%Y') if historique_police.date_fin_effet else '',
        'montant_renouvellement': f"{locale.format_string('%.0f', historique_police.prime_ttc, grouping=True)}",
        'montant_renouvellement_en_lettres': num2words(historique_police.prime_ttc, lang='fr').capitalize(),
        'date_jour': datetime.now().strftime('%d/%m/%Y'),
        'compagnie':assureur_police.compagnie,
        'date_renouvellement': date_renouvellement,
        'site_logo_url': site_logo_url
    }
    template_name = f"police/generation/{courrier.type_courrier.nom.lower().replace(' ', '_')}.html"

    pdf = render_pdf( template_name, template_content)
    # response = HttpResponse(File(pdf), content_type='application/pdf')
    # response['Content-Disposition'] = f'attachment; filename="courrier_{courrier.designation}.pdf"'
    return HttpResponse(File(pdf), content_type='application/pdf')


# generation de fichier word
def generer_word(request, police_id, courrier_id,quittance_id=None):
    # Vérifie que la police existe
    police = get_object_or_404(Police, id=police_id)
    courrier = get_object_or_404(Courrier, id=courrier_id)

    historique_police = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()
    # Récupérer l'assureur associé à l'historique
    assureur_police = PoliceAssureur.objects.filter(historique_police_id=historique_police.id,
                                                    type_compagnie_id=1).first()

    # Vérifier si une quittance est spécifiée
    if quittance_id:
        quittance = get_object_or_404(Quittance, id=quittance_id, police_id=police_id)
        numero_quittance = quittance.numero
    else:
        numero_quittance = None

    # Date actuelle
    date_du_jour = datetime.now().strftime('%d/%m/%Y')

    # Vérifier si le type de courrier a un template associé
    if not courrier.type_courrier:
        return HttpResponse("Erreur : Ce courrier n'a pas de type de courrier défini.", status=400)

    # Configuration du locale pour le formatage
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

    # Formatage de la prime
    prime_ttc = historique_police.prime_ttc
    prime_formatee = f"{locale.format_string('%.0f', prime_ttc, grouping=True)} F CFA"


    # Récupérer le type de document envoyé depuis le bouton
    type_document = request.GET.get('type_document', '').strip().lower()

    if not type_document:
        return HttpResponse("Erreur : Aucun type de document spécifié.", status=400)

    # Charger le modèle Word existant
    doc_path = os.path.join(settings.BASE_DIR, 'production', 'templates', 'police', 'courriers', f"{type_document}.docx")
    document = docx.Document(doc_path)

    # Dictionnaire des remplacements pour le texte
    base_replacements = {
        'NOM_CLIENT': police.client.nom,
        'NUMERO_POLICE': police.numero,
        'NOM_PRODUIT': police.produit.nom,
        'ADRESS_CLIENT': police.client.adresse,
        'QUITTANCE_NUMÉRO': numero_quittance,
        'DATE_DEBUT_EFFET': historique_police.date_debut_effet.strftime('%d/%m/%Y'),
        'DATE_FIN_EFFET': historique_police.date_fin_effet.strftime('%d/%m/%Y'),
        'MONTANT_RENOUVELLEMENT': prime_formatee,
        'LETTRES':  f"{num2words(historique_police.prime_ttc, lang='fr').capitalize()} F CFA",
        'DATE_JOUR': date_du_jour,
        'COMPAGNIE': assureur_police.compagnie,
    }

    replacements = {}
    for key, value in base_replacements.items():
        formats = [
            f'«{key}»', f'"{key}"', key
        ]
        for fmt in formats:
            replacements[fmt] = str(value) if value else ""


    # Fonction pour remplacer les placeholders dans les paragraphes
    def replace_placeholders_in_paragraph(paragraph):
        original_text = paragraph.text
        new_text = original_text

        for placeholder, value in replacements.items():
            if placeholder in new_text:
                new_text = new_text.replace(placeholder, value)

        if new_text != original_text:
            first_run = paragraph.runs[0] if paragraph.runs else paragraph.add_run()
            first_run.text = new_text
            for run in paragraph.runs[1:]:
                run.clear()

    # Fonction pour remplacer les placeholders dans le document entier (paragraphes et tables)
    def replace_placeholders_in_document(document):
        for paragraph in document.paragraphs:
            replace_placeholders_in_paragraph(paragraph)

        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        replace_placeholders_in_paragraph(paragraph)

        for section in document.sections:
            for paragraph in section.header.paragraphs + section.footer.paragraphs:
                replace_placeholders_in_paragraph(paragraph)
            for table in section.header.tables + section.footer.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            replace_placeholders_in_paragraph(paragraph)

    # Remplacement des placeholders dans le document
    replace_placeholders_in_document(document)


    # Sauvegarder le document Word dans une réponse HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename="courrier_{courrier.designation}.docx"'

    # Sauvegarde le document dans la réponse
    document.save(response)

    return response


@method_decorator(login_required, name='dispatch')
class PolicesEncoursView(TemplateView):
    permission_required = "production.view_clients"
    template_name = 'police/polices_en_cours.html'
    model = Police

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        user = User.objects.get(id=request.user.id)
        
        produits = Produit.objects.all().order_by('nom')
        clients = Client.objects.all().order_by('nom')

        commercials = []
        utilisateur = User.objects.all().order_by('-first_name').exclude(is_admin_group=1)
        for user in utilisateur:
            if user.is_commercial:
                commercials.append(user)

        context_perso = {'produits': produits, 'clients':clients, 'commercials':commercials}

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


#Chargement des lignes de police en cours
def polices_en_cours_datatable(request):
    items_per_page = 10
    page_number = request.GET.get('page')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', items_per_page))
    sort_column_index = int(request.GET.get('order[0][column]'))
    sort_direction = request.GET.get('order[0][dir]')
    search_client = request.GET.get('search_client', '').strip()
    search_numero_police = request.GET.get('search_numero_police', '').strip()
    search_produit = request.GET.get('search_produit', '').strip()
    search_commercial = request.GET.get('search_commercial', '').strip()
    today = now()

    user = request.user
    queryset = Police.objects.filter(Q(date_fin_effet__gt=today) | Q(date_fin_police__gt=today)).exclude(Q(statut="ANNULE") | Q(statut="INACTIF"))

    """
    if user.is_commercial:
        queryset = Police.objects.filter(date_fin_effet__gt=today, commercial_id=user.id)
    elif user.is_production:
        queryset = Police.objects.filter(date_fin_effet__gt=today)
    else:
        queryset = Police.objects.none
    """

    if search_client:
        queryset = queryset.filter(
            Q(client_id=search_client)
        )

    if search_numero_police:
        queryset = queryset.filter(
            Q(numero__icontains=search_numero_police)
        )


    if search_produit:
        queryset = queryset.filter(
            Q(produit_id=search_produit)
        )

    if search_commercial:
        queryset = queryset.filter(
            Q(commercial_id=search_commercial)
        )

    # Apply sorting
    queryset = queryset.order_by('-numero')

    paginator = Paginator(queryset, length)
    page_obj = paginator.get_page(page_number)

    # Prepare the data in the expected format
    data = []
    for c in page_obj:

        detail_url = reverse('police.details', args=[c.id])  # URL to the detail view
        numero_html = f'<a href="{detail_url}" class="text-center bouton_action" style="color:#F16623;" target="_blank">{c.numero}</a>&nbsp;&nbsp;'
        actions_html = f'<a href="{detail_url}" class="text-center" target="_blank"><span class="badge btn-sm btn-details rounded-pill"><i class="fa fa-eye"></i> {_("Détails")}</span></a>&nbsp;&nbsp;'

        if not c.client.nom: c.client.nom = ''
        if not c.client.prenoms: c.client.prenoms = ''
        if not c.client.code: c.client.code = ''

        data.append({
            "id": c.id,
            "num_police": numero_html,
            "nom_client": c.client.nom + ' ' + c.client.prenoms+ '- (' + c.client.code + ')',
            "nom_produit": c.produit.nom if c.produit else "",
            "date_debut": c.avenant_encours.date_effet if c.avenant_encours else "",
            "date_fin": c.avenant_encours.date_fin_periode_garantie if c.avenant_encours else "",
            "actions": actions_html,
        })

    return JsonResponse({
        "data": data,
        "recordsTotal": queryset.count(),
        "recordsFiltered": paginator.count,
        "draw": int(request.GET.get('draw', 1)),
    })


@method_decorator(login_required, name='dispatch')
class PolicesArrivantEcheanceView(TemplateView):
    permission_required = "production.view_clients"
    template_name = 'police/polices_arrivant_echeance.html'
    model = Police

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        produits = Produit.objects.all().order_by('nom')
        clients = Client.objects.all().order_by('nom')

        commercials = []
        utilisateur = User.objects.all().order_by('-first_name').exclude(is_admin_group=1)
        for user in utilisateur:
            if user.is_commercial:
                commercials.append(user)

        context_perso = {'produits': produits, 'clients':clients, 'commercials':commercials}

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


#Chargement des lignes de polices arrivant à échéance dans 90 jours
def polices_arrivant_echeance_datatable(request):
    items_per_page = 10
    page_number = request.GET.get('page')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', items_per_page))
    sort_column_index = int(request.GET.get('order[0][column]'))
    sort_direction = request.GET.get('order[0][dir]')
    search_client = request.GET.get('search_client', '').strip()
    search_numero_police = request.GET.get('search_numero_police', '').strip()
    search_produit = request.GET.get('search_produit', '').strip()
    search_commercial = request.GET.get('search_commercial', '').strip()
    today = now()
    in_90_days = today + timedelta(days=90)

    user = request.user
    queryset = Police.objects.filter(
        (Q(date_fin_effet__lte=in_90_days) & Q(date_fin_effet__gt=today)) |
        (Q(date_fin_police__lte=in_90_days) & Q(date_fin_police__gt=today))
    ).exclude(Q(statut="ANNULE") | Q(statut="INACTIF"))

    """
    if user.is_commercial:
        queryset = Police.objects.filter(date_fin_effet__lte=in_90_days, date_fin_effet__gt=today, commercial_id=user.id)
    elif user.is_production:
        queryset = Police.objects.filter(date_fin_effet__lte=in_90_days, date_fin_effet__gt=today)
    else:
        queryset = Police.objects.none
    """

    if search_client:
        queryset = queryset.filter(
            Q(client_id=search_client)
        )

    if search_numero_police:
        queryset = queryset.filter(
            Q(numero__icontains=search_numero_police)
        )

    if search_produit:
        queryset = queryset.filter(
            Q(produit_id=search_produit)
        )

    if search_commercial:
        queryset = queryset.filter(
            Q(commercial_id=search_commercial)
        )

    # Apply sorting
    queryset = queryset.order_by('-numero')

    paginator = Paginator(queryset, length)
    page_obj = paginator.get_page(page_number)

    # Prepare the data in the expected format
    data = []
    for c in page_obj:

        detail_url = reverse('police.details', args=[c.id])  # URL to the detail view
        numero_html = f'<a href="{detail_url}" class="text-center bouton_action" style="color:#F16623;" target="_blank">{c.numero}</a>&nbsp;&nbsp;'
        actions_html = f'<a href="{detail_url}" class="text-center" target="_blank"><span class="badge btn-sm btn-details rounded-pill"><i class="fa fa-eye"></i> {_("Détails")}</span></a>&nbsp;&nbsp;'

        if not c.client.nom: c.client.nom = ''
        if not c.client.prenoms: c.client.prenoms = ''
        if not c.client.code: c.client.code = ''

        data.append({
            "id": c.id,
            "num_police": numero_html,
            "nom_client": c.client.nom + ' ' + c.client.prenoms+ '- (' + c.client.code + ')',
            "nom_produit": c.produit.nom if c.produit else "",
            "date_debut": c.avenant_encours.date_effet if c.avenant_encours else "",
            "date_fin": c.avenant_encours.date_fin_periode_garantie if c.avenant_encours else "",
            "actions": actions_html,
        })

    return JsonResponse({
        "data": data,
        "recordsTotal": queryset.count(),
        "recordsFiltered": paginator.count,
        "draw": int(request.GET.get('draw', 1)),
    })


@method_decorator(login_required, name='dispatch')
class PolicesNonRenouvelleesResilieesView(TemplateView):
    permission_required = "production.view_clients"
    template_name = 'police/polices_non_renouvellees_resiliees.html'
    model = Police

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        produits = Produit.objects.all().order_by('nom')
        clients = Client.objects.all().order_by('nom')

        commercials = []
        utilisateur = User.objects.all().order_by('-first_name').exclude(is_admin_group=1)
        for user in utilisateur:
            if user.is_commercial:
                commercials.append(user)

        context_perso = {'produits': produits, 'clients':clients, 'commercials':commercials}

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


#Chargement des lignes de polices non résiliée et renouvelée
def polices_non_renouvellees_resiliees_datatable(request):
    items_per_page = 10
    page_number = request.GET.get('page')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', items_per_page))
    sort_column_index = int(request.GET.get('order[0][column]'))
    sort_direction = request.GET.get('order[0][dir]')
    search_client = request.GET.get('search_client', '').strip()
    search_numero_police = request.GET.get('search_numero_police', '').strip()
    search_produit = request.GET.get('search_produit', '').strip()
    search_commercial = request.GET.get('search_commercial', '').strip()
    today = now()

    user = request.user
    queryset = Police.objects.filter(Q(date_fin_effet__lt=today) | Q(date_fin_police__lt=today)).exclude(Q(statut="ANNULE") | Q(statut="INACTIF"))

    """
    if user.is_commercial:
        queryset = Police.objects.filter(Q(date_fin_effet__lt=today) | Q(date_fin_police__lt=today) , commercial_id=user.id)
    elif user.is_production:
        queryset = Police.objects.filter(date_fin_effet__lt=today)
    else:
        queryset = Police.objects.none
    """

    if search_client:
        queryset = queryset.filter(
            Q(client_id=search_client)
        )

    if search_numero_police:
        queryset = queryset.filter(
            Q(numero__icontains=search_numero_police)
        )


    if search_produit:
        queryset = queryset.filter(
            Q(produit_id=search_produit)
        )

    if search_commercial:
        queryset = queryset.filter(
            Q(commercial_id=search_commercial)
        )

    # Apply sorting
    queryset = queryset.order_by('-numero')

    paginator = Paginator(queryset, length)
    page_obj = paginator.get_page(page_number)

    # Prepare the data in the expected format
    data = []
    for c in page_obj:

        detail_url = reverse('police.details', args=[c.id])  # URL to the detail view
        numero_html = f'<a href="{detail_url}" class="text-center bouton_action" style="color:#F16623;" target="_blank">{c.numero}</a>&nbsp;&nbsp;'
        actions_html = f'<a href="{detail_url}" class="text-center" target="_blank"><span class="badge btn-sm btn-details rounded-pill"><i class="fa fa-eye"></i> {_("Détails")}</span></a>&nbsp;&nbsp;'

        if not c.client.nom: c.client.nom = ''
        if not c.client.prenoms: c.client.prenoms = ''
        if not c.client.code: c.client.code = ''

        data.append({
            "id": c.id,
            "num_police": numero_html,
            "nom_client": c.client.nom + ' ' + c.client.prenoms+ '- (' + c.client.code + ')',
            "nom_produit": c.produit.nom if c.produit else "",
            "date_debut": c.avenant_encours.date_effet if c.avenant_encours else "",
            "date_fin": c.avenant_encours.date_fin_periode_garantie if c.avenant_encours else "",
            "actions": actions_html,
        })

    return JsonResponse({
        "data": data,
        "recordsTotal": queryset.count(),
        "recordsFiltered": paginator.count,
        "draw": int(request.GET.get('draw', 1)),
    })
