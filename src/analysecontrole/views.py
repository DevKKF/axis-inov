# Create your views here.
import datetime
from pprint import pprint

from openpyxl.styles import Alignment
from collections import defaultdict
from io import BytesIO
import base64
from django.contrib import admin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView
from openpyxl import Workbook
from openpyxl.styles import Font, Border, Side
from datetime import datetime, timezone
from django.db.models import Q, Max, Count
from datetime import timedelta
import tempfile
import os
from openpyxl.utils import get_column_letter
from django.db.models import Subquery, OuterRef

from configurations.helper_config import verify_sql_query
from configurations.models import ActionLog, Prescripteur, PrescripteurPrestataire, Prestataire, Specialite, Secteur, \
    Bureau,TypeActe,BusinessUnit,Branche,Banque,Affection,Apporteur,ApporteurInternational,CategorieAffection,Devise,\
    TypePrestataire, User, AuthGroup, TypeEtablissement,Tarif, Rubrique, RegroupementActe, Acte, ReseauSoin, \
    PrestataireReseauSoin, WsBoby, ParamWsBoby, Affection, BackgroundQueryTask, ParamProduitCompagnie, Compagnie, \
    AlimentMatricule, ParamActe, TypeApporteur, TypePersonne, Pays, TypeCompagnie, TypeGarant, TauxCommission, Carosserie, \
    CategorieVehicule, Civilite, CompteTresorerie, ConditionsAssurance, Carburant, Formule, Fractionnement, Garantie, GarantieFormule, \
    Groupe, ModeReglement
from inov import settings
# Create your views here.
from production.models import TarifPrestataireClient, Client, Aliment, AlimentFormule, Mouvement, MouvementAliment, \
    Carte, Quittance, Reglement, Courrier, Produit, PoliceAssureur, Police, HistoriquePolice, MouvementPolice
from analysecontrole.models import AnalysePortefeuille, ControleCommission
from production.templatetags.my_filters import money_field, convertir_date_multiformat
from shared.enum import PasswordType, Statut, StatutValidite, BaseCalculTM, StatutPaiementSinistre, TypePortefeuille, \
    SatutBordereauDossierSinistres, StatutSinistre, ModeRenouvellement

from production.templatetags.my_filters import money_field, convertir_date_multiformat, supprimer_espaces, convertir_date_jj_mm_aaaa, format_montant, money_format_mille


class AnalysePortefeuilleView(PermissionRequiredMixin,TemplateView):
    template_name = 'analyse/analyse.html'
    permission_required = "analysecontrole.view_analyseportefeuille"
    model = AnalysePortefeuille

    def get(self, request, *args, **kwargs):
        context_original = self.get_context_data(**kwargs)

        analyseportefeuille = AnalysePortefeuille.objects.all().order_by('-id')

        today = datetime.now(tz=timezone.utc)
        compagnies = Compagnie.objects.order_by('nom')
        businessunit = BusinessUnit.objects.order_by('libelle')
        business_units = BusinessUnit.objects.all().order_by('libelle')
        mode_renouvellement = ModeRenouvellement

        commercials = []
        utilisateur = User.objects.all().order_by('-first_name').exclude(is_admin_group=1)
        for user in utilisateur:
            if user.is_commercial:
                commercials.append(user)

        context_perso = {'analyseportefeuille': analyseportefeuille, 'compagnies': compagnies, 'businessunit': businessunit, 'commercials': commercials, 'business_units': business_units, 'today': today, 'mode_renouvellement': mode_renouvellement}

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


# Portefeuille par compagnie
def generate_excel_portefeuille_compagnie(compagnies, date_requete):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Portefeuille"

    headers = [
        "POLICE", "COMPAGNIE", "CLIENT", "TYPE DE CLIENT", "BRANCHE", "PRODUIT",
        "RECONDUCTION", "STATUT", "DATE DE RENOUVELEMENT", "DATE DE FIN",
        "PRIME HT EX N-1", "PRIME HT EX N", "PRIME TTC EX N"
    ]

    # Largeur des colonnes
    for i, header in enumerate(headers, 1):
        col_letter = get_column_letter(i)
        if header in ["DATE DE RENOUVELEMENT", "DATE DE FIN", "PRIME HT EX N-1", "PRIME HT EX N", "PRIME TTC EX N"]:
            sheet.column_dimensions[col_letter].width = 23
        else:
            sheet.column_dimensions[col_letter].width = 28

    # Style d'en-tête
    header_font = Font(bold=True)
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )
    sheet.append(headers)
    for cell in sheet[1]:
        cell.font = header_font
        cell.border = thin_border
        cell.alignment = Alignment(horizontal="center")

    # 👉 Ajouter le filtre automatique ici :
    sheet.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"

    data_start_row = 2
    recap_data = defaultdict(lambda: {'count': 0, 'ht': 0, 'ttc': 0})
    row_index = data_start_row

    for compagnie in compagnies:
        polices_qs = Police.objects.filter(
            historique_polices__id__in=PoliceAssureur.objects.filter(
                compagnie_id=compagnie.id, type_compagnie_id=1
            ).values('historique_police_id')
        ).distinct()

        if not polices_qs.exists():
            continue

        for police in polices_qs:
            dernier_historique = HistoriquePolice.objects.filter(police_id=police.id).order_by('-date_du_jour').first()
            prime_ht = dernier_historique.prime_ht if dernier_historique and dernier_historique.prime_ht else 0
            prime_ttc = dernier_historique.prime_ttc if dernier_historique and dernier_historique.prime_ttc else 0

            historique_annee_precedente = HistoriquePolice.objects.filter(
                police_id=police.id,
                date_du_jour__year__lt=dernier_historique.date_du_jour.year if dernier_historique else datetime.now().year
            ).order_by('-date_du_jour').first()
            prime_ht_n = historique_annee_precedente.prime_ht if historique_annee_precedente else 0

            dernier_mouvement = MouvementPolice.objects.filter(police_id=police.id).order_by('-created_at').first()
            statut = "NON renouvelé"
            if dernier_mouvement and dernier_mouvement.date_fin_periode_garantie:
                diff = (dernier_mouvement.date_fin_periode_garantie - datetime.today().date()).days
                if diff > 90:
                    statut = police.etat_police
                elif diff > 0:
                    statut = "A renouveler"

            date_fin_effet = ''
            if dernier_historique and dernier_historique.mode_renouvellement == "Tacite Reconduction":
                date_fin_effet = dernier_historique.date_fin_effet.strftime("%d/%m/%Y") if dernier_historique.date_fin_effet else ''

            date_fin_police = ''
            if dernier_historique and dernier_historique.mode_renouvellement == "Sans Tacite Reconduction":
                date_fin_police = dernier_historique.date_fin_police.strftime("%d/%m/%Y") if dernier_historique.date_fin_police else ''

            row_data = [
                police.numero,
                compagnie.nom,
                police.client.nom if police.client else '',
                police.client.type_personne.libelle if police.client else '',
                police.produit.branche.nom if police.produit and police.produit.branche else '',
                police.produit.nom if police.produit else '',
                dernier_historique.mode_renouvellement if dernier_historique else '',
                statut,
                date_fin_effet,
                date_fin_police,
                prime_ht_n,
                prime_ht,
                prime_ttc
            ]
            sheet.append(row_data)

            # Format nombre en milliers
            for i in [11, 12, 13]:  # Colonnes 11,12,13 = "PRIME HT EX N-1", "PRIME HT EX N", "PRIME TTC EX N"
                cell = sheet.cell(row=row_index, column=i)
                cell.number_format = '#,##0'

            # Appliquer bordure à toute la ligne
            for col in range(1, len(headers) + 1):
                sheet.cell(row=row_index, column=col).border = thin_border

            # Mise à jour du récap
            recap_data[compagnie.nom]['count'] += 1
            recap_data[compagnie.nom]['ht'] += prime_ht
            recap_data[compagnie.nom]['ttc'] += prime_ttc

            row_index += 1

    # Position de départ du récapitulatif
    recap_start = row_index + 3

    # Titre "RÉCAPITULATIF PAR COMPAGNIE" fusionné sur B à E
    sheet.merge_cells(start_row=recap_start, start_column=2, end_row=recap_start, end_column=5)
    title_cell = sheet.cell(row=recap_start, column=2)
    title_cell.value = "RÉCAPITULATIF PAR COMPAGNIE"
    title_cell.font = Font(bold=True, size=12)
    title_cell.alignment = Alignment(horizontal="center")

    # Ligne d'en-tête
    recap_header_row = recap_start + 1
    recap_headers = ["", "COMPAGNIE", "NOMBRE DE POLICE", "MONTANT TOTAL HT EX N", "MONTANT TTC EX N"]
    sheet.append(recap_headers)

    # Appliquer le style à l'en-tête
    for col in range(2, 6):  # Colonnes B à E
        cell = sheet.cell(row=recap_header_row, column=col)
        cell.font = Font(bold=True)
        cell.border = thin_border
        cell.alignment = Alignment(horizontal="center")

    # Initialisation des totaux
    total_polices = total_ht = total_ttc = 0
    recap_data_row = recap_header_row

    # Remplissage des lignes de récapitulatif
    for compagnie, vals in recap_data.items():
        recap_data_row += 1
        sheet.cell(row=recap_data_row, column=2, value=compagnie)
        sheet.cell(row=recap_data_row, column=3, value=vals['count'])
        sheet.cell(row=recap_data_row, column=4, value=vals['ht'])
        sheet.cell(row=recap_data_row, column=5, value=vals['ttc'])

        for i in [4, 5]:  # Colonnes montants
            sheet.cell(row=recap_data_row, column=i).number_format = '#,##0'

        for col in range(2, 6):  # Appliquer bordure à toutes les cellules de la ligne
            sheet.cell(row=recap_data_row, column=col).border = thin_border

        total_polices += vals['count']
        total_ht += vals['ht']
        total_ttc += vals['ttc']

    # Ligne TOTAL GENERAL
    total_row = recap_data_row + 2
    sheet.cell(row=total_row, column=2, value="TOTAL GENERAL").font = Font(bold=True)
    sheet.cell(row=total_row, column=3, value=total_polices).font = Font(bold=True)
    sheet.cell(row=total_row, column=4, value=total_ht).font = Font(bold=True)
    sheet.cell(row=total_row, column=5, value=total_ttc).font = Font(bold=True)

    for i in [4, 5]:
        sheet.cell(row=total_row, column=i).number_format = '#,##0'

    for col in range(2, 6):
        sheet.cell(row=total_row, column=col).border = thin_border

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output


def add_portefeuille_compagnie(request):
    compagnie_id = request.POST.get('compagnie_id')
    date_requete = request.POST.get('date_requete') or datetime.today().strftime("%d/%m/%Y")

    if compagnie_id == "TOUT":
        compagnies = Compagnie.objects.all()

        if not compagnies.exists():
            return JsonResponse({
                'statut': 0,
                'message': "Aucune compagnie trouvée."
            })

        output = generate_excel_portefeuille_compagnie(compagnies, date_requete)

        # Enregistrement de génération du portefeuille
        """analyse_portefeuille = AnalysePortefeuille.objects.create(
            type_portefeuille=TypePortefeuille.ALL_CIE,
            created_at=datetime.now(),
            created_by=request.user
        )"""

        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_file.write(output.getvalue())
            tmp_file_path = tmp_file.name

        # Enregistrer le fichier dans le champ `fichier`
        """with open(tmp_file_path, 'rb') as file:
            analyse_portefeuille.fichier.save("Portefeuille_Global.xlsx", File(file))"""

        # Supprimer le fichier temporaire après l'avoir enregistré
        os.unlink(tmp_file_path)

        return JsonResponse({
            'statut': 1,
            'message': "Portefeuille global généré avec succès !",
            'data': {
                'filename': date_requete+'_'+"Portefeuille_Global_Compagnie.xlsx",
                'file_base64': base64.b64encode(output.getvalue()).decode()
            }
        })

    else:
        compagnie = Compagnie.objects.filter(id=compagnie_id).first()
        polices_qs = Police.objects.filter(
            historique_polices__id__in=PoliceAssureur.objects.filter(
                compagnie_id=compagnie_id, type_compagnie_id=1
            ).values('historique_police_id')
        ).distinct()

        if not polices_qs.exists():
            return JsonResponse({
                'statut': 0,
                'message': "Aucune police trouvée pour cette compagnie."
            })

        workbook = generate_excel_portefeuille_compagnie([compagnie], date_requete)

        # Enregistrement de génération du portefeuille
        """analyse_portefeuille = AnalysePortefeuille.objects.create(
            compagnie=compagnie,
            type_portefeuille=TypePortefeuille.PAR_CIE,
            created_at=datetime.now(),
            created_by=request.user
        )"""

        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_file.write(workbook.getvalue())
            tmp_file_path = tmp_file.name

        # Enregistrer le fichier dans le champ `fichier`
        """with open(tmp_file_path, 'rb') as file:
            analyse_portefeuille.fichier.save(f"Portefeuille_{compagnie.nom}.xlsx", File(file))"""

        # Supprimer le fichier temporaire après l'avoir enregistré
        os.unlink(tmp_file_path)

        return JsonResponse({
            'statut': 1,
            'message': "Portefeuille par compagnie généré avec succès !",
            'data': {
                'filename': f"{date_requete}_Portefeuille_{compagnie.nom}.xlsx",
                'file_base64': base64.b64encode(workbook.getvalue()).decode()
            }
        })


# Chargement des polices liées à la compagnie
def get_client_by_compagnie(request):
    compagnie_id = request.GET.get('compagnie_id')
    search_mode_renouvellement = request.GET.get("mode_renouvellement")
    today = datetime.today().date()
    date_for_calcul = datetime.today().date()
    polices_par_compagnie = {}

    dernier_historique_subquery = HistoriquePolice.objects.filter(
        police_id=OuterRef('pk')
    ).order_by('-date_du_jour').values('mode_renouvellement')[:1]

    if compagnie_id == "TOUT":
        compagnies = Compagnie.objects.all().order_by('nom')

        for compagnie in compagnies:

            polices_qs = Police.objects.filter(
                historique_polices__id__in=PoliceAssureur.objects.filter(
                    compagnie_id=compagnie.id, type_compagnie_id=1
                ).values('historique_police_id')
            ).annotate(
                dernier_mode_renouvellement=Subquery(dernier_historique_subquery)
            ).distinct()

            if search_mode_renouvellement:
                polices_qs = polices_qs.filter(dernier_mode_renouvellement__iexact=search_mode_renouvellement)

            polices = []
            for plc in polices_qs:
                dernier_historique = HistoriquePolice.objects.filter(police_id=plc.id).order_by('-date_du_jour').first()
                dernier_mouvement = MouvementPolice.objects.filter(police_id=plc.id).order_by('-created_at').first()

                etat_police = None

                date_echeance_police = None
                if plc.date_fin_effet:
                    date_echeance_police = plc.date_fin_effet
                elif plc.date_fin_police:
                    date_echeance_police = plc.date_fin_police

                if plc.etat_police not in ["Annulé", "Résilié", "Suspendu"]:
                    if date_echeance_police and date_echeance_police > today:
                        difference_jours = (date_echeance_police - date_for_calcul).days
                        if difference_jours <= 90:
                            etat_police = f'<span class="badge badge-warning">A renouveler</span>'
                        else:
                            etat_police = f'<span class="badge badge-success">{plc.etat_police}</span>'
                    else:
                        etat_police = f'<span class="badge badge-danger">NON renouvelé</span>'
                else:
                    etat_police = f'<span class="badge badge-danger">{plc.etat_police}</span>'

                detail_url = reverse('police.details', args=[plc.id])
                numero_html = f'<a href="{detail_url}" class="text-center bouton_action" style="color:#F16623;" target="_blank">{plc.numero}</a>'

                polices.append({
                    'id': plc.id,
                    'nom': plc.client.nom if plc.client else '',
                    'prenoms': plc.client.prenoms if plc.client else '',
                    'numero': numero_html,
                    'produit': plc.produit.nom,
                    'date_debut_effet': plc.date_debut_effet.strftime("%d/%m/%Y") if plc.date_debut_effet else '',
                    'date_fin_effet': plc.date_fin_effet.strftime("%d/%m/%Y") if plc.date_fin_effet else (plc.date_fin_police.strftime("%d/%m/%Y") if plc.date_fin_police else None),
                    'date_resiliation': dernier_mouvement.date_effet.strftime("%d/%m/%Y") if plc.etat_police == "Résilié" and dernier_mouvement else '',
                    'statut': etat_police,
                    'mode_renouvellement': dernier_historique.mode_renouvellement if dernier_historique else '',
                    'prime_ht': money_field(dernier_historique.prime_ht) if dernier_historique else '',
                    'commission_courtage': money_field(dernier_historique.commission_courtage) if dernier_historique else '',
                })

            if polices:
                polices_par_compagnie[compagnie.nom] = {
                    "polices": polices,
                }

    else:
        compagnie = Compagnie.objects.filter(id=compagnie_id).first()

        polices_qs = Police.objects.filter(
            historique_polices__id__in=PoliceAssureur.objects.filter(
                compagnie_id=compagnie_id, type_compagnie_id=1
            ).values('historique_police_id')
        ).annotate(
            dernier_mode_renouvellement=Subquery(dernier_historique_subquery)
        ).distinct()

        if search_mode_renouvellement:
            polices_qs = polices_qs.filter(dernier_mode_renouvellement__iexact=search_mode_renouvellement)

        polices = []
        for plc in polices_qs:
            dernier_historique = HistoriquePolice.objects.filter(police_id=plc.id).order_by('-date_du_jour').first()
            dernier_mouvement = MouvementPolice.objects.filter(police_id=plc.id).order_by('-created_at').first()

            etat_police = None

            date_echeance_police = None
            if plc.date_fin_effet:
                date_echeance_police = plc.date_fin_effet
            elif plc.date_fin_police:
                date_echeance_police = plc.date_fin_police

            if plc.etat_police not in ["Annulé", "Résilié", "Suspendu"]:
                if date_echeance_police and date_echeance_police > today:
                    difference_jours = (date_echeance_police - date_for_calcul).days
                    if difference_jours <= 90:
                        etat_police = f'<span class="badge badge-warning">A renouveler</span>'
                    else:
                        etat_police = f'<span class="badge badge-success">{plc.etat_police}</span>'
                else:
                    etat_police = f'<span class="badge badge-danger">NON renouvelé</span>'
            else:
                etat_police = f'<span class="badge badge-danger">{plc.etat_police}</span>'

            detail_url = reverse('police.details', args=[plc.id])
            numero_html = f'<a href="{detail_url}" class="text-center bouton_action" style="color:#F16623;" target="_blank">{plc.numero}</a>'

            polices.append({
                'id': plc.id,
                'nom': plc.client.nom if plc.client else '',
                'prenoms': plc.client.prenoms if plc.client else '',
                'numero': numero_html,
                'produit': plc.produit.nom,
                'date_debut_effet': plc.date_debut_effet.strftime("%d/%m/%Y") if plc.date_debut_effet else '',
                'date_fin_effet': plc.date_fin_effet.strftime("%d/%m/%Y") if plc.date_fin_effet else (plc.date_fin_police.strftime("%d/%m/%Y") if plc.date_fin_police else None),
                'date_resiliation': dernier_mouvement.date_effet.strftime("%d/%m/%Y") if plc.etat_police == "Résilié" and dernier_mouvement else '',
                'statut': etat_police,
                'mode_renouvellement': dernier_historique.mode_renouvellement if dernier_historique else '',
                'prime_ht': money_field(dernier_historique.prime_ht) if dernier_historique else '',
                'commission_courtage': money_field(dernier_historique.commission_courtage) if dernier_historique else '',
            })

        if polices:
            polices_par_compagnie[compagnie.nom] = {
                "polices": polices,
            }

    print(f"Nombre de police {polices_par_compagnie}")
    return JsonResponse({
        'polices_par_compagnie': polices_par_compagnie,
    })


# Portefeuille par commercial
def generate_excel_portefeuille_commercial(polices_qs, commercial_nom=""):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Portefeuille"

    headers = [
        "POLICE", "COMMERCIAL", "CLIENT", "TYPE DE CLIENT", "BRANCHE", "PRODUIT",
        "RECONDUCTION", "STATUT", "DATE DE RENOUVELEMENT", "DATE DE FIN",
        "PRIME HT EX N-1", "PRIME HT EX N", "PRIME TTC EX N", "COM ENCAISSEE", "COM ATTENDUE"
    ]
    sheet.append(headers)

    # Style
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Largeur des colonnes
    for col_idx, header in enumerate(headers, start=1):
        col_letter = get_column_letter(col_idx)
        if header in ["DATE DE RENOUVELLEMENT", "DATE DE FIN", "PRIME HT EX N-1", "PRIME HT EX N", "PRIME TTC EX N"]:
            sheet.column_dimensions[col_letter].width = 23
        else:
            sheet.column_dimensions[col_letter].width = 28

    # Style en-tête
    for col_idx in range(1, len(headers) + 1):
        cell = sheet.cell(row=1, column=col_idx)
        cell.font = Font(bold=True)
        cell.border = thin_border
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Ajout du filtre
    sheet.auto_filter.ref = sheet.dimensions

    row_index = 2
    recap_data = {}

    def ajouter_police_dans_excel(police, titre):
        nonlocal row_index

        # Init des données du commercial
        if titre not in recap_data:
            recap_data[titre] = {"count": 0, "ht": 0, "ttc": 0}

        # Historique
        dernier_historique = HistoriquePolice.objects.filter(police=police).order_by('-date_du_jour').first()

        prime_ht_n = prime_ht = prime_ttc = police_com_att = 0
        if dernier_historique:
            annee_actuelle = dernier_historique.date_du_jour.year
            historique_annee_precedente = HistoriquePolice.objects.filter(
                police=police, date_du_jour__year__lt=annee_actuelle
            ).order_by('-date_du_jour').first()
            if historique_annee_precedente:
                prime_ht_n = historique_annee_precedente.prime_ht or 0
            prime_ht = dernier_historique.prime_ht or 0
            prime_ttc = dernier_historique.prime_ttc or 0
            police_com_att = dernier_historique.commission_courtage or 0

        dernier_mouvement = MouvementPolice.objects.filter(police=police).order_by('-created_at').first()
        date_for_calcul = datetime.today().date()
        today = datetime.today().date()

        date_echeance_police = None
        if police.date_fin_effet:
            date_echeance_police = police.date_fin_effet
        elif police.date_fin_police:
            date_echeance_police = police.date_fin_police

        if police.etat_police not in ["Annulé", "Résilié", "Suspendu"]:
            if date_echeance_police and date_echeance_police > today:
                difference_jours = (date_echeance_police - date_for_calcul).days
                if difference_jours <= 90:
                    statut = "A renouveler"
                else:
                    statut = police.etat_police
            else:
                statut = "NON renouvelé"
        else:
            statut = police.etat_police

        police_com_enc = sum(
            reglement.montant_com_courtage
            for quittance in Quittance.objects.filter(police=police)
            for reglement in Reglement.objects.filter(quittance=quittance, statut_commission="ENCAISSEE")
        )

        date_fin_effet = dernier_historique.date_fin_effet.strftime('%d/%m/%Y') \
            if dernier_historique and dernier_historique.mode_renouvellement == "Tacite Reconduction" \
            and dernier_historique.date_fin_effet else ''

        date_fin_police = dernier_historique.date_fin_police.strftime('%d/%m/%Y') \
            if dernier_historique and dernier_historique.mode_renouvellement == "Sans Tacite Reconduction" \
            and dernier_historique.date_fin_police else ''

        data = [
            police.numero,
            titre,
            police.client.nom if police.client else '',
            police.client.type_personne.libelle if police.client else '',
            police.produit.branche.nom if police.produit and police.produit.branche else '',
            police.produit.nom if police.produit else '',
            dernier_historique.mode_renouvellement if dernier_historique else '',
            statut,
            date_fin_effet,
            date_fin_police,
            prime_ht_n,
            prime_ht,
            prime_ttc,
            police_com_enc,
            police_com_att,
        ]
        sheet.append(data)

        # Formatage cellule
        for col_idx, val in enumerate(data, start=1):
            cell = sheet.cell(row=row_index, column=col_idx)
            cell.border = thin_border
            if col_idx in [11, 12, 13, 14, 15]:
                cell.number_format = '#,##0'
            if col_idx in [9, 10]:
                cell.alignment = Alignment(horizontal="center")

        # MAJ du récap
        recap_data[titre]["count"] += 1
        recap_data[titre]["ht"] += prime_ht
        recap_data[titre]["ttc"] += prime_ttc

        row_index += 1

    # Remplissage des données
    for police in polices_qs:
        commercial_nom_police = police.commercial.first_name + " " + police.commercial.last_name if police.commercial else "Aucun commercial"
        ajouter_police_dans_excel(police, commercial_nom_police)

    # Récapitulatif
    recap_start = row_index + 3

    sheet.merge_cells(start_row=recap_start, start_column=2, end_row=recap_start, end_column=5)
    title_cell = sheet.cell(row=recap_start, column=2)
    title_cell.value = "RÉCAPITULATIF PAR COMMERCIAL"
    title_cell.font = Font(bold=True, size=12)
    title_cell.alignment = Alignment(horizontal="center")

    recap_header_row = recap_start + 1
    recap_headers = ["", "COMMERCIAL", "NOMBRE DE POLICE", "MONTANT TOTAL HT EX N", "MONTANT TTC EX N"]
    sheet.append(recap_headers)

    for col in range(2, 6):
        cell = sheet.cell(row=recap_header_row, column=col)
        cell.font = Font(bold=True)
        cell.border = thin_border
        cell.alignment = Alignment(horizontal="center")

    total_polices = total_ht = total_ttc = 0
    recap_data_row = recap_header_row

    for commercial, vals in recap_data.items():
        recap_data_row += 1
        sheet.cell(row=recap_data_row, column=2, value=commercial)
        sheet.cell(row=recap_data_row, column=3, value=vals['count'])
        sheet.cell(row=recap_data_row, column=4, value=vals['ht']).number_format = '#,##0'
        sheet.cell(row=recap_data_row, column=5, value=vals['ttc']).number_format = '#,##0'

        for i in [4, 5]:  # Colonnes montants
            sheet.cell(row=recap_data_row, column=i).number_format = '#,##0'

        for col in range(2, 6):  # Appliquer bordure à toutes les cellules de la ligne
            sheet.cell(row=recap_data_row, column=col).border = thin_border

        total_polices += vals['count']
        total_ht += vals['ht']
        total_ttc += vals['ttc']

    # Ligne TOTAL GENERAL
    total_row = recap_data_row + 2
    sheet.cell(row=total_row, column=2, value="TOTAL GENERAL").font = Font(bold=True)

    cell_polices = sheet.cell(row=total_row, column=3, value=total_polices)
    cell_polices.font = Font(bold=True)

    cell_ht = sheet.cell(row=total_row, column=4, value=total_ht)
    cell_ht.font = Font(bold=True)
    cell_ht.number_format = '#,##0'  # Format en milliers

    cell_ttc = sheet.cell(row=total_row, column=5, value=total_ttc)
    cell_ttc.font = Font(bold=True)
    cell_ttc.number_format = '#,##0'  # Format en milliers

    for col in range(2, 6):
        sheet.cell(row=total_row, column=col).border = thin_border

    # Générer le fichier Excel
    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return output


def add_portefeuille_commercial(request):
    commercial_id = request.POST.get('search_commercial')
    mode_renouvellement = request.POST.get("search_mode_renouvellement")
    date_requete = request.POST.get('date_requete') or datetime.today().strftime("%d/%m/%Y")

    dernier_historique_subquery = HistoriquePolice.objects.filter(
        police_id=OuterRef('pk')
    ).order_by('-date_du_jour').values('mode_renouvellement')[:1]

    polices_qs = Police.objects.filter(
        client__isnull=False,
        historique_polices__isnull=False,
    ).annotate(
        dernier_mode_renouvellement=Subquery(dernier_historique_subquery)
    )

    if commercial_id == "TOUT":
        pass  # On garde toutes les polices pour le récapitulatif dans l'Excel
    elif commercial_id == "AUCUN":
        polices_qs = polices_qs.filter(commercial__isnull=True)
    else:
        polices_qs = polices_qs.filter(commercial_id=commercial_id)

    if mode_renouvellement:
        polices_qs = polices_qs.filter(dernier_mode_renouvellement__iexact=mode_renouvellement)

    if not polices_qs.exists():
        return JsonResponse({
            'statut': 0,
            'message': "Aucune police trouvée avec ces critères."
        })

    workbook = generate_excel_portefeuille_commercial(polices_qs.distinct())

    # Créer un fichier temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        tmp_file.write(workbook.getvalue())
        tmp_file_path = tmp_file.name

    # Supprimer le fichier temporaire après l'avoir enregistré
    os.unlink(tmp_file_path)

    filename = f"{date_requete}_Portefeuille_Commercial.xlsx"
    if commercial_id and commercial_id != "TOUT":
        commercial = User.objects.filter(id=commercial_id).first()
        if commercial:
            filename = f"{date_requete}_Portefeuille_{commercial.first_name}_{commercial.last_name}.xlsx"
        elif commercial_id == "AUCUN":
            filename = f"{date_requete}_Portefeuille_Sans_Commercial.xlsx"
    elif mode_renouvellement:
        filename = f"{date_requete}_Portefeuille_Renouvellement_{mode_renouvellement}.xlsx"
    elif commercial_id == "TOUT":
        filename = f"{date_requete}_Portefeuille_Global.xlsx"


    return JsonResponse({
        'statut': 1,
        'message': "Portefeuille commercial généré avec succès !",
        'data': {
            'filename': filename,
            'file_base64': base64.b64encode(workbook.getvalue()).decode()
        }
    })


# Chargement des polices liées au commercial
def get_client_by_commercial(request):
    commercial_id = request.GET.get('commercial_id')
    search_mode_renouvellement = request.GET.get("mode_renouvellement")
    today = datetime.today().date()
    date_for_calcul = datetime.today().date()
    polices_par_commercial = {}

    dernier_historique_subquery = HistoriquePolice.objects.filter(
        police_id=OuterRef('pk')
    ).order_by('-date_du_jour').values('mode_renouvellement')[:1]

    if commercial_id == "TOUT":
        commercials = User.objects.all().order_by('first_name')

        for commercial in commercials:

            polices_qs = Police.objects.filter(
                client__isnull=False,
                historique_polices__isnull=False,
                commercial_id=commercial.id
            ).annotate(
                dernier_mode_renouvellement=Subquery(dernier_historique_subquery)
            ).distinct()

            if search_mode_renouvellement:
                polices_qs = polices_qs.filter(dernier_mode_renouvellement__iexact=search_mode_renouvellement)

            polices = []
            for plc in polices_qs:
                dernier_historique = HistoriquePolice.objects.filter(police_id=plc.id).order_by('-date_du_jour').first()
                dernier_mouvement = MouvementPolice.objects.filter(police_id=plc.id).order_by('-created_at').first()

                etat_police = None

                date_echeance_police = None
                if plc.date_fin_effet:
                    date_echeance_police = plc.date_fin_effet
                elif plc.date_fin_police:
                    date_echeance_police = plc.date_fin_police

                if plc.etat_police not in ["Annulé", "Résilié", "Suspendu"]:
                    if date_echeance_police and date_echeance_police > today:
                        difference_jours = (date_echeance_police - date_for_calcul).days
                        if difference_jours <= 90:
                            etat_police = f'<span class="badge badge-warning">A renouveler</span>'
                        else:
                            etat_police = f'<span class="badge badge-success">{plc.etat_police}</span>'
                    else:
                        etat_police = f'<span class="badge badge-danger">NON renouvelé</span>'
                else:
                    etat_police = f'<span class="badge badge-danger">{plc.etat_police}</span>'

                detail_url = reverse('police.details', args=[plc.id])
                numero_html = f'<a href="{detail_url}" class="text-center bouton_action" style="color:#F16623;" target="_blank">{plc.numero}</a>'

                polices.append({
                    'id': plc.id,
                    'nom': plc.client.nom if plc.client else '',
                    'prenoms': plc.client.prenoms if plc.client else '',
                    'numero': numero_html,
                    'produit': plc.produit.nom,
                    'date_debut_effet': plc.date_debut_effet.strftime("%d/%m/%Y") if plc.date_debut_effet else '',
                    'date_fin_effet': plc.date_fin_effet.strftime("%d/%m/%Y") if plc.date_fin_effet else (plc.date_fin_police.strftime("%d/%m/%Y") if plc.date_fin_police else None),
                    'date_resiliation': dernier_mouvement.date_effet.strftime("%d/%m/%Y") if plc.etat_police == "Résilié" and dernier_mouvement else '',
                    'statut': etat_police,
                    'mode_renouvellement': dernier_historique.mode_renouvellement if dernier_historique else '',
                    'prime_ht': money_field(dernier_historique.prime_ht) if dernier_historique else '',
                    'commission_courtage': money_field(dernier_historique.commission_courtage) if dernier_historique else '',
                })

            if polices:
                polices_par_commercial[commercial.first_name + ' ' + commercial.last_name] = {
                    "polices": polices,
                }

        polices_qs = Police.objects.filter(
            client__isnull=False,
            historique_polices__isnull=False,
            commercial_id__isnull=True
        ).annotate(
            dernier_mode_renouvellement=Subquery(dernier_historique_subquery)
        ).distinct()

        if search_mode_renouvellement:
            polices_qs = polices_qs.filter(dernier_mode_renouvellement__iexact=search_mode_renouvellement)

        autres_polices = []
        for plc in polices_qs:
            dernier_historique = HistoriquePolice.objects.filter(police_id=plc.id).order_by('-date_du_jour').first()
            dernier_mouvement = MouvementPolice.objects.filter(police_id=plc.id).order_by('-created_at').first()

            etat_police = None

            date_echeance_police = None
            if plc.date_fin_effet:
                date_echeance_police = plc.date_fin_effet
            elif plc.date_fin_police:
                date_echeance_police = plc.date_fin_police

            if plc.etat_police not in ["Annulé", "Résilié", "Suspendu"]:
                if date_echeance_police and date_echeance_police > today:
                    difference_jours = (date_echeance_police - date_for_calcul).days
                    if difference_jours <= 90:
                        etat_police = f'<span class="badge badge-warning">A renouveler</span>'
                    else:
                        etat_police = f'<span class="badge badge-success">{plc.etat_police}</span>'
                else:
                    etat_police = f'<span class="badge badge-danger">NON renouvelé</span>'
            else:
                etat_police = f'<span class="badge badge-danger">{plc.etat_police}</span>'

            detail_url = reverse('police.details', args=[plc.id])
            numero_html = f'<a href="{detail_url}" class="text-center bouton_action" style="color:#F16623;" target="_blank">{plc.numero}</a>'

            autres_polices.append({
                'id': plc.id,
                'nom': plc.client.nom if plc.client else '',
                'prenoms': plc.client.prenoms if plc.client else '',
                'numero': numero_html,
                'produit': plc.produit.nom,
                'date_debut_effet': plc.date_debut_effet.strftime("%d/%m/%Y") if plc.date_debut_effet else '',
                'date_fin_effet': plc.date_fin_effet.strftime("%d/%m/%Y") if plc.date_fin_effet else (plc.date_fin_police.strftime("%d/%m/%Y") if plc.date_fin_police else None),
                'date_resiliation': dernier_mouvement.date_effet.strftime("%d/%m/%Y") if plc.etat_police == "Résilié" and dernier_mouvement else '',
                'statut': etat_police,
                'mode_renouvellement': dernier_historique.mode_renouvellement if dernier_historique else '',
                'prime_ht': money_field(dernier_historique.prime_ht) if dernier_historique else '',
                'commission_courtage': money_field(dernier_historique.commission_courtage) if dernier_historique else '',
            })

        polices_par_commercial["Aucun commercial"] = {
            "polices": autres_polices,
        }

    elif commercial_id == "AUCUN":
        polices_qs = Police.objects.filter(
            client__isnull=False,
            historique_polices__isnull=False,
            commercial_id__isnull=True
        ).annotate(
            dernier_mode_renouvellement=Subquery(dernier_historique_subquery)
        ).distinct()

        if search_mode_renouvellement:
            polices_qs = polices_qs.filter(dernier_mode_renouvellement__iexact=search_mode_renouvellement)

        polices = []
        for plc in polices_qs:
            dernier_historique = HistoriquePolice.objects.filter(police_id=plc.id).order_by('-date_du_jour').first()
            dernier_mouvement = MouvementPolice.objects.filter(police_id=plc.id).order_by('-created_at').first()

            etat_police = None

            date_echeance_police = None
            if plc.date_fin_effet:
                date_echeance_police = plc.date_fin_effet
            elif plc.date_fin_police:
                date_echeance_police = plc.date_fin_police

            if plc.etat_police not in ["Annulé", "Résilié", "Suspendu"]:
                if date_echeance_police and date_echeance_police > today:
                    difference_jours = (date_echeance_police - date_for_calcul).days
                    if difference_jours <= 90:
                        etat_police = f'<span class="badge badge-warning">A renouveler</span>'
                    else:
                        etat_police = f'<span class="badge badge-success">{plc.etat_police}</span>'
                else:
                    etat_police = f'<span class="badge badge-danger">NON renouvelé</span>'
            else:
                etat_police = f'<span class="badge badge-danger">{plc.etat_police}</span>'

            detail_url = reverse('police.details', args=[plc.id])
            numero_html = f'<a href="{detail_url}" class="text-center bouton_action" style="color:#F16623;" target="_blank">{plc.numero}</a>'

            polices.append({
                'id': plc.id,
                'nom': plc.client.nom if plc.client else '',
                'prenoms': plc.client.prenoms if plc.client else '',
                'numero': numero_html,
                'produit': plc.produit.nom,
                'date_debut_effet': plc.date_debut_effet.strftime("%d/%m/%Y") if plc.date_debut_effet else '',
                'date_fin_effet': plc.date_fin_effet.strftime("%d/%m/%Y") if plc.date_fin_effet else (
                    plc.date_fin_police.strftime("%d/%m/%Y") if plc.date_fin_police else None),
                'date_resiliation': dernier_mouvement.date_effet.strftime(
                    "%d/%m/%Y") if plc.etat_police == "Résilié" and dernier_mouvement else '',
                'statut': etat_police,
                'mode_renouvellement': dernier_historique.mode_renouvellement if dernier_historique else '',
                'prime_ht': money_field(dernier_historique.prime_ht) if dernier_historique else '',
                'commission_courtage': money_field(
                    dernier_historique.commission_courtage) if dernier_historique else '',
            })

        polices_par_commercial["Aucun commercial"] = {
            "polices": polices,
        }

    else:
        commercial = User.objects.filter(id=commercial_id).first()

        polices_qs = Police.objects.filter(
            client__isnull=False,
            historique_polices__isnull=False,
            commercial_id=commercial_id
        ).annotate(
            dernier_mode_renouvellement=Subquery(dernier_historique_subquery)
        ).distinct()

        if search_mode_renouvellement:
            polices_qs = polices_qs.filter(dernier_mode_renouvellement__iexact=search_mode_renouvellement)

        polices = []
        for plc in polices_qs:
            dernier_historique = HistoriquePolice.objects.filter(police_id=plc.id).order_by('-date_du_jour').first()
            dernier_mouvement = MouvementPolice.objects.filter(police_id=plc.id).order_by('-created_at').first()

            etat_police = None

            date_echeance_police = None
            if plc.date_fin_effet:
                date_echeance_police = plc.date_fin_effet
            elif plc.date_fin_police:
                date_echeance_police = plc.date_fin_police

            if plc.etat_police not in ["Annulé", "Résilié", "Suspendu"]:
                if date_echeance_police and date_echeance_police > today:
                    difference_jours = (date_echeance_police - date_for_calcul).days
                    if difference_jours <= 90:
                        etat_police = f'<span class="badge badge-warning">A renouveler</span>'
                    else:
                        etat_police = f'<span class="badge badge-success">{plc.etat_police}</span>'
                else:
                    etat_police = f'<span class="badge badge-danger">NON renouvelé</span>'
            else:
                etat_police = f'<span class="badge badge-danger">{plc.etat_police}</span>'

            detail_url = reverse('police.details', args=[plc.id])
            numero_html = f'<a href="{detail_url}" class="text-center bouton_action" style="color:#F16623;" target="_blank">{plc.numero}</a>'

            polices.append({
                'id': plc.id,
                'nom': plc.client.nom if plc.client else '',
                'prenoms': plc.client.prenoms if plc.client else '',
                'numero': numero_html,
                'produit': plc.produit.nom,
                'date_debut_effet': plc.date_debut_effet.strftime("%d/%m/%Y") if plc.date_debut_effet else '',
                'date_fin_effet': plc.date_fin_effet.strftime("%d/%m/%Y") if plc.date_fin_effet else (
                    plc.date_fin_police.strftime("%d/%m/%Y") if plc.date_fin_police else None),
                'date_resiliation': dernier_mouvement.date_effet.strftime(
                    "%d/%m/%Y") if plc.etat_police == "Résilié" and dernier_mouvement else '',
                'statut': etat_police,
                'mode_renouvellement': dernier_historique.mode_renouvellement if dernier_historique else '',
                'prime_ht': money_field(dernier_historique.prime_ht) if dernier_historique else '',
                'commission_courtage': money_field(
                    dernier_historique.commission_courtage) if dernier_historique else '',
            })

        if polices:
            polices_par_commercial[commercial.first_name + ' ' + commercial.last_name] = {
                "polices": polices,
            }

    return JsonResponse({
        'polices_par_commercial': polices_par_commercial,
    })


# Portefeuille par business unit
def generate_excel_portefeuille_business_unit(business_units, date_requete, sans_business_unit):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Portefeuille"

    headers = [
        "POLICE", "BUSINESS UNIT", "CLIENT", "TYPE DE CLIENT", "BRANCHE", "PRODUIT",
        "RECONDUCTION", "STATUT", "DATE DE RENOUVELEMENT", "DATE DE FIN",
        "PRIME HT EX N-1", "PRIME HT EX N", "PRIME TTC EX N", "COM ENCAISSÉE", "COM ATTENDUE"
    ]
    sheet.append(headers)

    bold_font = Font(bold=True)
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    # Mise en forme de l'en-tête
    for col_index, header in enumerate(headers, 1):
        col_letter = get_column_letter(col_index)
        sheet[f"{col_letter}1"].font = bold_font
        sheet[f"{col_letter}1"].border = thin_border
        sheet[f"{col_letter}1"].alignment = Alignment(horizontal="center")
        sheet.auto_filter.ref = f"A1:O1"
        sheet.column_dimensions[col_letter].width = 20

    recap_data = {}

    def ajouter_polices_a_la_feuille(sheet, business_unit_label, polices_qs):
        if not polices_qs.exists():
            return

        for police in polices_qs:
            dernier_historique = HistoriquePolice.objects.filter(
                police_id=police.id
            ).order_by('-date_du_jour').first()

            prime_ht_n, prime_ht, prime_ttc = 0, 0, 0
            police_com_enc, police_com_att = 0, 0
            date_fin_effet, date_fin_police = "", ""

            if dernier_historique:
                annee_actuelle = dernier_historique.date_du_jour.year if dernier_historique.date_du_jour else None
                if annee_actuelle:
                    derniere_annee_precedente = HistoriquePolice.objects.filter(
                        police_id=police.id,
                        date_du_jour__year__lt=annee_actuelle
                    ).aggregate(Max('date_du_jour__year'))['date_du_jour__year__max']

                    if derniere_annee_precedente:
                        historique_annee_precedente = HistoriquePolice.objects.filter(
                            police_id=police.id,
                            date_du_jour__year=derniere_annee_precedente
                        ).order_by('-date_du_jour').first()
                        prime_ht_n = historique_annee_precedente.prime_ht if historique_annee_precedente else 0

                police_com_att = dernier_historique.commission_courtage or 0
                prime_ht = dernier_historique.prime_ht or 0
                prime_ttc = dernier_historique.prime_ttc or 0

                if dernier_historique.mode_renouvellement == "Tacite Reconduction":
                    date_fin_effet = dernier_historique.date_fin_effet.strftime("%d/%m/%Y") if dernier_historique.date_fin_effet else ''
                elif dernier_historique.mode_renouvellement == "Sans Tacite Reconduction":
                    date_fin_police = dernier_historique.date_fin_police.strftime("%d/%m/%Y") if dernier_historique.date_fin_police else ''

            dernier_mouvement = MouvementPolice.objects.filter(police_id=police.id).order_by('-created_at').first()
            date_for_calcul = datetime.today().date()
            statut = ""

            if dernier_mouvement and dernier_mouvement.date_fin_periode_garantie:
                date_fin = dernier_mouvement.date_fin_periode_garantie
                difference_jours = (date_fin - date_for_calcul).days
                if difference_jours > 90:
                    statut = police.etat_police
                elif difference_jours > 0:
                    statut = "A renouveler"
                else:
                    statut = "NON renouvelé"
            else:
                statut = police.etat_police if dernier_mouvement else ''

            quittances = Quittance.objects.filter(police_id=police.id)
            sum_quittance = sum(
                sum(reglement.montant_com_courtage for reglement in Reglement.objects.filter(
                    quittance_id=quittance.id, statut_commission="ENCAISSEE"
                )) for quittance in quittances
            )
            police_com_enc = sum_quittance

            row = [
                police.numero,
                business_unit_label,
                police.client.nom if police.client else '',
                police.client.type_personne.libelle if police.client else '',
                police.produit.branche.nom if police.produit and police.produit.branche else '',
                police.produit.nom if police.produit else '',
                dernier_historique.mode_renouvellement if dernier_historique else '',
                statut,
                date_fin_effet,
                date_fin_police,
                prime_ht_n,
                prime_ht,
                prime_ttc,
                police_com_enc,
                police_com_att,
            ]

            sheet.append(row)
            current_row = sheet.max_row

            for col_index, value in enumerate(row, 1):
                cell = sheet.cell(row=current_row, column=col_index)
                cell.border = thin_border

                if col_index == 9:  # date_fin_effet
                    cell.font = bold_font
                if col_index == 13:  # prime_ttc
                    cell.font = bold_font
                    cell.number_format = '#,##0'
                if col_index in [11, 12, 14, 15]:  # autres montants
                    cell.number_format = '#,##0'

            # Ajout au récapitulatif
            recap = recap_data.setdefault(business_unit_label, {"count": 0, "ht": 0, "ttc": 0})
            recap["count"] += 1
            recap["ht"] += prime_ht
            recap["ttc"] += prime_ttc

    if sans_business_unit == 0:
        polices_sans_bu = Police.objects.filter(
            client__business_unit_id__isnull=True,
            historique_polices__isnull=False
        ).distinct()
        ajouter_polices_a_la_feuille(sheet, "Aucun Business Unit", polices_sans_bu)
    elif sans_business_unit == 1:
        for bu in business_units:
            polices_bu = Police.objects.filter(
                client__business_unit_id=bu.id,
                historique_polices__isnull=False
            ).distinct()
            ajouter_polices_a_la_feuille(sheet, bu.libelle, polices_bu)

        polices_sans_bu = Police.objects.filter(
            client__business_unit_id__isnull=True,
            historique_polices__isnull=False
        ).distinct()
        ajouter_polices_a_la_feuille(sheet, "Aucun Business Unit", polices_sans_bu)
    else:
        for bu in business_units:
            polices_bu = Police.objects.filter(
                client__business_unit_id=bu.id,
                historique_polices__isnull=False
            ).distinct()
            ajouter_polices_a_la_feuille(sheet, bu.libelle, polices_bu)

    # === RÉCAPITULATIF PAR BUSINESS UNIT ===
    recap_start = sheet.max_row + 3
    sheet.merge_cells(start_row=recap_start, start_column=2, end_row=recap_start, end_column=5)
    title_cell = sheet.cell(row=recap_start, column=2)
    title_cell.value = "RÉCAPITULATIF PAR BUSINESS UNIT"
    title_cell.font = Font(bold=True, size=12)
    title_cell.alignment = Alignment(horizontal="center")

    recap_header_row = recap_start + 1
    recap_headers = ["", "BUSINESS UNIT", "NOMBRE DE POLICE", "MONTANT TOTAL HT EX N", "MONTANT TTC EX N"]
    sheet.append(recap_headers)

    for col in range(2, 6):
        cell = sheet.cell(row=recap_header_row, column=col)
        cell.font = bold_font
        cell.border = thin_border
        cell.alignment = Alignment(horizontal="center")

    total_polices = total_ht = total_ttc = 0
    recap_data_row = recap_header_row

    for unit, vals in recap_data.items():
        recap_data_row += 1
        sheet.cell(row=recap_data_row, column=2, value=unit)
        sheet.cell(row=recap_data_row, column=3, value=vals['count'])
        sheet.cell(row=recap_data_row, column=4, value=vals['ht']).number_format = '#,##0'
        sheet.cell(row=recap_data_row, column=5, value=vals['ttc']).number_format = '#,##0'

        for col in range(2, 6):
            sheet.cell(row=recap_data_row, column=col).border = thin_border

        total_polices += vals['count']
        total_ht += vals['ht']
        total_ttc += vals['ttc']

    # Ligne TOTAL GENERAL
    total_row = recap_data_row + 2
    sheet.cell(row=total_row, column=2, value="TOTAL GENERAL").font = Font(bold=True)

    cell_polices = sheet.cell(row=total_row, column=3, value=total_polices)
    cell_polices.font = Font(bold=True)

    cell_ht = sheet.cell(row=total_row, column=4, value=total_ht)
    cell_ht.font = Font(bold=True)
    cell_ht.number_format = '#,##0'  # Format en milliers

    cell_ttc = sheet.cell(row=total_row, column=5, value=total_ttc)
    cell_ttc.font = Font(bold=True)
    cell_ttc.number_format = '#,##0'  # Format en milliers

    for col in range(2, 6):
        sheet.cell(row=total_row, column=col).border = thin_border

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output


def add_portefeuille_business_unit(request):
    business_unit_id = request.POST.get('search_business_unit')
    mode_renouvellement = request.POST.get("search_mode_renouvellement")
    date_requete = request.POST.get('date_requete') or datetime.today().strftime("%d/%m/%Y")
    print(request.POST)
    if business_unit_id == "TOUT":
        business_units = BusinessUnit.objects.all()
        sans_business_unit=1

        if not business_units.exists():
            return JsonResponse({
                'statut': 0,
                'message': "Aucun business unit trouvé."
            })

        output = generate_excel_portefeuille_business_unit(business_units, date_requete, sans_business_unit)

        # Enregistrement de génération du portefeuille
        """analyse_portefeuille = AnalysePortefeuille.objects.create(
            type_portefeuille=TypePortefeuille.ALL_COM,
            created_at=datetime.now(),
            created_by=request.user
        )"""

        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_file.write(output.getvalue())
            tmp_file_path = tmp_file.name

        # Enregistrer le fichier dans le champ `fichier`
        """with open(tmp_file_path, 'rb') as file:
            analyse_portefeuille.fichier.save("Portefeuille_Global.xlsx", File(file))"""

        # Supprimer le fichier temporaire après l'avoir enregistré
        os.unlink(tmp_file_path)

        return JsonResponse({
            'statut': 1,
            'message': "Portefeuille global généré avec succès !",
            'data': {
                'filename': date_requete+'_'+"Portefeuille_Global_business_unit.xlsx",
                'file_base64': base64.b64encode(output.getvalue()).decode()
            }
        })

    elif business_unit_id == "AUCUN":
        business_units = {}
        sans_business_unit = 0

        output = generate_excel_portefeuille_business_unit(business_units, date_requete, sans_business_unit)

        # Enregistrement de génération du portefeuille
        """analyse_portefeuille = AnalysePortefeuille.objects.create(
            type_portefeuille=TypePortefeuille.ALL_COM,
            created_at=datetime.now(),
            created_by=request.user
        )"""

        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_file.write(output.getvalue())
            tmp_file_path = tmp_file.name

        # Enregistrer le fichier dans le champ `fichier`
        """with open(tmp_file_path, 'rb') as file:
            analyse_portefeuille.fichier.save("Portefeuille_Global_aucun_business_unit.xlsx", File(file))"""

        # Supprimer le fichier temporaire après l'avoir enregistré
        os.unlink(tmp_file_path)

        return JsonResponse({
            'statut': 1,
            'message': "Portefeuille global sans business unit généré avec succès !",
            'data': {
                'filename': date_requete+'_'+"Portefeuille_Global_aucun_business_unit.xlsx",
                'file_base64': base64.b64encode(output.getvalue()).decode()
            }
        })

    else:
        business_unit = BusinessUnit.objects.filter(id=business_unit_id).first()
        sans_business_unit = 2

        polices_qs = Police.objects.filter(
            id__in=Police.objects.filter(
                client__isnull=False,
                historique_polices__isnull=False,  # Correction ici
                business_unit_id=business_unit.id
            ).values_list('id', flat=True)
        ).distinct()

        if not polices_qs.exists():
            return JsonResponse({
                'statut': 0,
                'message': "Aucune police trouvée pour ce business unit."
            })

        workbook = generate_excel_portefeuille_business_unit([business_unit], date_requete, sans_business_unit)

        # Enregistrement de génération du portefeuille
        """analyse_portefeuille = AnalysePortefeuille.objects.create(
            business_unit=business_unit,
            type_portefeuille=TypePortefeuille.PAR_COM,
            created_at=datetime.now(),
            created_by=request.user
        )"""

        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_file.write(workbook.getvalue())
            tmp_file_path = tmp_file.name

        # Enregistrer le fichier dans le champ `fichier`
        """with open(tmp_file_path, 'rb') as file:
            analyse_portefeuille.fichier.save(f"Portefeuille_{business_unit.libelle}.xlsx", File(file))"""

        # Supprimer le fichier temporaire après l'avoir enregistré
        os.unlink(tmp_file_path)

        return JsonResponse({
            'statut': 1,
            'message': "Portefeuille par business unit généré avec succès !",
            'data': {
                'filename': f"{date_requete}_Portefeuille_{business_unit.libelle}.xlsx",
                'file_base64': base64.b64encode(workbook.getvalue()).decode()
            }
        })


# Chargement des polices liées au business unit
def get_client_by_business_unit(request):
    business_unit_id = request.GET.get('business_unit_id')
    search_mode_renouvellement = request.GET.get("mode_renouvellement")
    today = datetime.today().date()
    date_for_calcul = datetime.today().date()
    polices_par_business_unit = {}

    dernier_historique_subquery = HistoriquePolice.objects.filter(
        police_id=OuterRef('pk')
    ).order_by('-date_du_jour').values('mode_renouvellement')[:1]

    if business_unit_id == "TOUT":
        business_units = BusinessUnit.objects.all().order_by('libelle')

        for business_unit in business_units:

            polices_qs = Police.objects.filter(
                client__business_unit_id=business_unit.id,
                historique_polices__isnull=False
            ).annotate(
                dernier_mode_renouvellement=Subquery(dernier_historique_subquery)
            ).distinct()

            if search_mode_renouvellement:
                polices_qs = polices_qs.filter(dernier_mode_renouvellement__iexact=search_mode_renouvellement)

            polices = []
            for plc in polices_qs:
                dernier_historique = HistoriquePolice.objects.filter(police_id=plc.id).order_by('-date_du_jour').first()
                dernier_mouvement = MouvementPolice.objects.filter(police_id=plc.id).order_by('-created_at').first()

                etat_police = None

                date_echeance_police = None
                if plc.date_fin_effet:
                    date_echeance_police = plc.date_fin_effet
                elif plc.date_fin_police:
                    date_echeance_police = plc.date_fin_police

                if plc.etat_police not in ["Annulé", "Résilié", "Suspendu"]:
                    if date_echeance_police and date_echeance_police > today:
                        difference_jours = (date_echeance_police - date_for_calcul).days
                        if difference_jours <= 90:
                            etat_police = f'<span class="badge badge-warning">A renouveler</span>'
                        else:
                            etat_police = f'<span class="badge badge-success">{plc.etat_police}</span>'
                    else:
                        etat_police = f'<span class="badge badge-danger">NON renouvelé</span>'
                else:
                    etat_police = f'<span class="badge badge-danger">{plc.etat_police}</span>'

                detail_url = reverse('police.details', args=[plc.id])
                numero_html = f'<a href="{detail_url}" class="text-center bouton_action" style="color:#F16623;" target="_blank">{plc.numero}</a>'

                polices.append({
                    'id': plc.id,
                    'nom': plc.client.nom if plc.client else '',
                    'prenoms': plc.client.prenoms if plc.client else '',
                    'numero': numero_html,
                    'produit': plc.produit.nom,
                    'date_debut_effet': plc.date_debut_effet.strftime("%d/%m/%Y") if plc.date_debut_effet else '',
                    'date_fin_effet': plc.date_fin_effet.strftime("%d/%m/%Y") if plc.date_fin_effet else (plc.date_fin_police.strftime("%d/%m/%Y") if plc.date_fin_police else None),
                    'date_resiliation': dernier_mouvement.date_effet.strftime("%d/%m/%Y") if plc.etat_police == "Résilié" and dernier_mouvement else '',
                    'statut': etat_police,
                    'mode_renouvellement': dernier_historique.mode_renouvellement if dernier_historique else '',
                    'prime_ht': money_field(dernier_historique.prime_ht) if dernier_historique else '',
                    'commission_courtage': money_field(dernier_historique.commission_courtage) if dernier_historique else '',
                })

            if polices:
                polices_par_business_unit[business_unit.libelle] = {
                    "polices": polices,
                }

        polices_qs = Police.objects.filter(
            client__business_unit_id__isnull=True,
            historique_polices__isnull=False
        ).annotate(
            dernier_mode_renouvellement=Subquery(dernier_historique_subquery)
        ).distinct()

        if search_mode_renouvellement:
            polices_qs = polices_qs.filter(dernier_mode_renouvellement__iexact=search_mode_renouvellement)

        autres_polices = []
        for plc in polices_qs:
            dernier_historique = HistoriquePolice.objects.filter(police_id=plc.id).order_by('-date_du_jour').first()
            dernier_mouvement = MouvementPolice.objects.filter(police_id=plc.id).order_by('-created_at').first()

            etat_police = None

            date_echeance_police = None
            if plc.date_fin_effet:
                date_echeance_police = plc.date_fin_effet
            elif plc.date_fin_police:
                date_echeance_police = plc.date_fin_police

            if plc.etat_police not in ["Annulé", "Résilié", "Suspendu"]:
                if date_echeance_police and date_echeance_police > today:
                    difference_jours = (date_echeance_police - date_for_calcul).days
                    if difference_jours <= 90:
                        etat_police = f'<span class="badge badge-warning">A renouveler</span>'
                    else:
                        etat_police = f'<span class="badge badge-success">{plc.etat_police}</span>'
                else:
                    etat_police = f'<span class="badge badge-danger">NON renouvelé</span>'
            else:
                etat_police = f'<span class="badge badge-danger">{plc.etat_police}</span>'

            detail_url = reverse('police.details', args=[plc.id])
            numero_html = f'<a href="{detail_url}" class="text-center bouton_action" style="color:#F16623;" target="_blank">{plc.numero}</a>'

            autres_polices.append({
                'id': plc.id,
                'nom': plc.client.nom if plc.client else '',
                'prenoms': plc.client.prenoms if plc.client else '',
                'numero': numero_html,
                'produit': plc.produit.nom,
                'date_debut_effet': plc.date_debut_effet.strftime("%d/%m/%Y") if plc.date_debut_effet else '',
                'date_fin_effet': plc.date_fin_effet.strftime("%d/%m/%Y") if plc.date_fin_effet else (plc.date_fin_police.strftime("%d/%m/%Y") if plc.date_fin_police else None),
                'date_resiliation': dernier_mouvement.date_effet.strftime("%d/%m/%Y") if plc.etat_police == "Résilié" and dernier_mouvement else '',
                'statut': etat_police,
                'mode_renouvellement': dernier_historique.mode_renouvellement if dernier_historique else '',
                'prime_ht': money_field(dernier_historique.prime_ht) if dernier_historique else '',
                'commission_courtage': money_field(dernier_historique.commission_courtage) if dernier_historique else '',
            })

        polices_par_business_unit["Aucun business unit"] = {
            "polices": autres_polices,
        }

    elif business_unit_id == "AUCUN":
        polices_qs = Police.objects.filter(
            client__business_unit_id__isnull=True,
            historique_polices__isnull=False
        ).annotate(
            dernier_mode_renouvellement=Subquery(dernier_historique_subquery)
        ).distinct()

        if search_mode_renouvellement:
            polices_qs = polices_qs.filter(dernier_mode_renouvellement__iexact=search_mode_renouvellement)

        polices = []
        for plc in polices_qs:
            dernier_historique = HistoriquePolice.objects.filter(police_id=plc.id).order_by('-date_du_jour').first()
            dernier_mouvement = MouvementPolice.objects.filter(police_id=plc.id).order_by('-created_at').first()

            etat_police = None

            date_echeance_police = None
            if plc.date_fin_effet:
                date_echeance_police = plc.date_fin_effet
            elif plc.date_fin_police:
                date_echeance_police = plc.date_fin_police

            if plc.etat_police not in ["Annulé", "Résilié", "Suspendu"]:
                if date_echeance_police and date_echeance_police > today:
                    difference_jours = (date_echeance_police - date_for_calcul).days
                    if difference_jours <= 90:
                        etat_police = f'<span class="badge badge-warning">A renouveler</span>'
                    else:
                        etat_police = f'<span class="badge badge-success">{plc.etat_police}</span>'
                else:
                    etat_police = f'<span class="badge badge-danger">NON renouvelé</span>'
            else:
                etat_police = f'<span class="badge badge-danger">{plc.etat_police}</span>'

            detail_url = reverse('police.details', args=[plc.id])
            numero_html = f'<a href="{detail_url}" class="text-center bouton_action" style="color:#F16623;" target="_blank">{plc.numero}</a>'

            polices.append({
                'id': plc.id,
                'nom': plc.client.nom if plc.client else '',
                'prenoms': plc.client.prenoms if plc.client else '',
                'numero': numero_html,
                'produit': plc.produit.nom,
                'date_debut_effet': plc.date_debut_effet.strftime("%d/%m/%Y") if plc.date_debut_effet else '',
                'date_fin_effet': plc.date_fin_effet.strftime("%d/%m/%Y") if plc.date_fin_effet else (
                    plc.date_fin_police.strftime("%d/%m/%Y") if plc.date_fin_police else None),
                'date_resiliation': dernier_mouvement.date_effet.strftime(
                    "%d/%m/%Y") if plc.etat_police == "Résilié" and dernier_mouvement else '',
                'statut': etat_police,
                'mode_renouvellement': dernier_historique.mode_renouvellement if dernier_historique else '',
                'prime_ht': money_field(dernier_historique.prime_ht) if dernier_historique else '',
                'commission_courtage': money_field(
                    dernier_historique.commission_courtage) if dernier_historique else '',
            })

        polices_par_business_unit["Aucun business unit"] = {
            "polices": polices,
        }

    else:
        business_unit = BusinessUnit.objects.filter(id=business_unit_id).first()

        polices_qs = Police.objects.filter(
            client__isnull=False,
            historique_polices__isnull=False,
            business_unit_id=business_unit_id
        ).annotate(
            dernier_mode_renouvellement=Subquery(dernier_historique_subquery)
        ).distinct()

        if search_mode_renouvellement:
            polices_qs = polices_qs.filter(dernier_mode_renouvellement__iexact=search_mode_renouvellement)

        polices = []
        for plc in polices_qs:
            dernier_historique = HistoriquePolice.objects.filter(police_id=plc.id).order_by('-date_du_jour').first()
            dernier_mouvement = MouvementPolice.objects.filter(police_id=plc.id).order_by('-created_at').first()

            etat_police = None

            date_echeance_police = None
            if plc.date_fin_effet:
                date_echeance_police = plc.date_fin_effet
            elif plc.date_fin_police:
                date_echeance_police = plc.date_fin_police

            if plc.etat_police not in ["Annulé", "Résilié", "Suspendu"]:
                if date_echeance_police and date_echeance_police > today:
                    difference_jours = (date_echeance_police - date_for_calcul).days
                    if difference_jours <= 90:
                        etat_police = f'<span class="badge badge-warning">A renouveler</span>'
                    else:
                        etat_police = f'<span class="badge badge-success">{plc.etat_police}</span>'
                else:
                    etat_police = f'<span class="badge badge-danger">NON renouvelé</span>'
            else:
                etat_police = f'<span class="badge badge-danger">{plc.etat_police}</span>'

            detail_url = reverse('police.details', args=[plc.id])
            numero_html = f'<a href="{detail_url}" class="text-center bouton_action" style="color:#F16623;" target="_blank">{plc.numero}</a>'

            polices.append({
                'id': plc.id,
                'nom': plc.client.nom if plc.client else '',
                'prenoms': plc.client.prenoms if plc.client else '',
                'numero': numero_html,
                'produit': plc.produit.nom,
                'date_debut_effet': plc.date_debut_effet.strftime("%d/%m/%Y") if plc.date_debut_effet else '',
                'date_fin_effet': plc.date_fin_effet.strftime("%d/%m/%Y") if plc.date_fin_effet else (plc.date_fin_police.strftime("%d/%m/%Y") if plc.date_fin_police else None),
                'date_resiliation': dernier_mouvement.date_effet.strftime("%d/%m/%Y") if plc.etat_police == "Résilié" and dernier_mouvement else '',
                'statut': etat_police,
                'mode_renouvellement': dernier_historique.mode_renouvellement if dernier_historique else '',
                'prime_ht': money_field(dernier_historique.prime_ht) if dernier_historique else '',
                'commission_courtage': money_field(dernier_historique.commission_courtage) if dernier_historique else '',
            })

        if polices:
            polices_par_business_unit[business_unit.libelle] = {
                "polices": polices,
            }

    return JsonResponse({
        'polices_par_business_unit': polices_par_business_unit,
    })


