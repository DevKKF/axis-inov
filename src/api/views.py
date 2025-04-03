import datetime
from pprint import pprint
from sqlite3 import Date

import pyotp
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.files.storage import FileSystemStorage
from django.db.models import Sum
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, views
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import JsonResponse
from django.urls import reverse
from rest_framework import status



from api.api_helper import send_otp_mail, send_demande_rembours_mail
from api.paginations import SmartResultsSetPagination
from api.serializers import KeyValueDataSerializer, UserSerializer, AlimentSerializer, CreateUserSerializer, \
    ResetPasswordUserSerializer, UserDataSerializer, BarremeSerializer, SinisteSerializer, \
    ModeRemboursementSerializer, TypePrestataireSerializer, PrestataireSerializer, \
    PrestataireDataSerializer, ActeSerializer, BureauSerializer, \
    CarteDigitalDematerialiseeSerializer, TypeActeSerialiser, CiviliteSerializer, \
    QualiteBeneficiaireSerializer, PaysSerializer, ProfessionSerializer
from configurations.helper_config import verify_sql_query, execute_query
# from api.serializers import AlimentWaspitoSerialiser, PrestationWaspito

#Qui sera retiré à la longue
from configurations.models import Acte, ActeWaspito, Affection, Prescripteur, PrescripteurPrestataire, Prestataire, TypePrestataire, PrestataireReseauSoin, Profession
from production.models import Aliment, AlimentFormule, Bareme, Carte, FormuleGarantie, CarteDigitalDematerialisee
#Qui sera retiré à la longue

from configurations.models import Specialite, KeyValueData, Bureau, TypeActe, Civilite, \
    QualiteBeneficiaire, Pays, User, ModeReglement
from grh.helper import generate_uiid
from production.models import TypeDocument, Police
from shared.enum import EtatPolice, Statut, StatutSinistre, StatutEnrolement, StatutRemboursement
from shared.helpers import get_tarif_acte_from_bareme, generate_numero_carte
from shared.sinistres_repository import base_url
from sinistre.helper_sinistre import get_retenue_selon_contexte
from sinistre.models import DossierSinistre, Sinistre


def get_user_id_from_token(token):
    try:
        # Décoder le token pour obtenir les données de l'utilisateur
        decoded_token = AccessToken(token)

        pprint(decoded_token)
        user_id = decoded_token['user_id']
        return user_id
    except Exception as e:
        # Le token est invalide ou a expiré
        print(str(e))
        return None


# Custom return json to custom_name in json like access to access_token
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        print(response.data)
        data = {
            'refresh_token': response.data['refresh'],
            'access_token': response.data['access'],
        }
        return Response(data)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def info(request):
    message = None
    status_code = None
    jResponse = {
        "message": message,
        "status_code": status_code
    }

    if request.method == 'POST':
        json_data = request.data

        numero_carte = json_data.get('numero_assure', None)
        codes_acte = json_data.get('code_acte', None)

        # dd(numero_carte)

        if not numero_carte or not codes_acte:
            message = "Bad request, veuillez renseignez le numero de l'assuré et le code de l'acte svp."
            status_code = 400

            jResponse = {
                "message": message,
                "status_code": status_code
            }

            return Response(jResponse, status_code, content_type="application/json; charset=utf-8")

        carte = Carte.objects.filter(numero=numero_carte, statut=Statut.ACTIF).first()
        actes_trouves = []

        for code_acte in codes_acte:

            acte = Acte.objects.filter(code=code_acte).first()

            if carte and acte:
                aliment = carte.aliment
                print(carte.aliment.nom)

                prestataire = Prestataire.objects.filter(code=9537).first()
                prestataire_id = prestataire.pk  # ID PRESTATAIRE WASPITO

                periode_couverture_encours = aliment.formule.police.periode_couverture_encours
                consommation_individuelle = \
                    Sinistre.objects.filter(periode_couverture_id=periode_couverture_encours.pk, aliment_id=aliment.id,
                                            statut=StatutSinistre.ACCORDE).aggregate(Sum('part_compagnie'))[
                        'part_compagnie__sum'] or 0
                consommation_famille = Sinistre.objects.filter(periode_couverture_id=periode_couverture_encours.pk,
                                                               adherent_principal_id=aliment.adherent_principal.id,
                                                               statut=StatutSinistre.ACCORDE).aggregate(
                    Sum('part_compagnie'))['part_compagnie__sum'] or 0

                formule = aliment.formule

                # son plafond chambre et plafond hospit
                bareme_plafond_chambre = Bareme.objects.filter(formulegarantie_id=aliment.formule.id,
                                                               acte__code="G66023CI01")
                plafond_chambre = bareme_plafond_chambre.first().plafond_acte if bareme_plafond_chambre else 0
                bareme_plafond_hospitalisation = Bareme.objects.filter(formulegarantie_id=aliment.formule.id,
                                                                       acte__code="G66027CI01")
                plafond_hospitalisation = bareme_plafond_hospitalisation.first().plafond_acte if bareme_plafond_hospitalisation else 0

                # vérifie s'il y a au moins 2 éléments dans la liste et
                #  si tous les éléments de la liste sont des chaînes de caractères. Si ces conditions sont remplies, 
                if isinstance(codes_acte, list) and len(codes_acte) >= 2 and all(
                        isinstance(code, str) for code in codes_acte):
                    type_prise_en_charge_id = 2
                    type_prise_en_charge_code = "AMBULAT"
                else:
                    type_prise_en_charge_id = 1
                    type_prise_en_charge_code = "CONSULT"

                # recherche en fonction de la date de survenance, date systeme pour le prestataire
                aliment_formule = AlimentFormule.objects.filter(aliment_id=aliment.id, statut=Statut.ACTIF).latest(
                    '-id')

                date_survenance = datetime.datetime.now(tz=datetime.timezone.utc)
                acte_id = acte.id
                prescripteur_id = 2232
                aliment_id = aliment.pk

                acte_waspito = ActeWaspito.objects.filter(acte_id=acte_id).first()

                if not acte_waspito or not acte_waspito.prix:
                    if acte_waspito is None or acte_waspito.prix is None:
                        message = "L'acte demandé est introuvable dans la table de correspondance ou aucun prix n'est configuré pour cet acte."

                    actes_trouves.append({
                        "status_code": 404,
                        "status_message": message,
                        "code": code_acte,
                        "acte": acte.libelle,
                        "garantie": False,
                    })
                else:

                    cout_acte = acte_waspito.prix;

                    nombre_jours = None

                    # pour plus de sécurité, récupérer les tarif à partir du fichier excel et nom du formulaire utilisateur
                    infos_acte = get_tarif_acte_from_bareme(type_prise_en_charge_code, date_survenance, acte_id,
                                                            prestataire.id,
                                                            prescripteur_id, aliment_id, cout_acte,
                                                            nombre_jours, consommation_individuelle,
                                                            consommation_famille)

                    if infos_acte:
                        if infos_acte['statut'] == 0:
                            message = infos_acte['message']
                            status_code = 401

                            jResponse = {
                                "message": message,
                                "status_code": status_code
                            }
                        else:
                            actes_trouves.append({
                                "status_code": 200,
                                "status_message": "Acte trouvé",
                                "code": infos_acte['data']['code'],
                                "acte": infos_acte['data']['libelle'],
                                "garantie": infos_acte['data']['garanti'],
                                "attente_prealable": False if acte.accord_automatique else True,
                                "coverage": infos_acte['data']['taux_couverture'] / 100,
                                "frais_reel": infos_acte['data']['frais_reel'],
                                "part_assure": infos_acte['data']['part_assure'],
                                "part_assureur": infos_acte['data']['part_compagnie'],
                                "numero_police": aliment.formule.police.numero,
                                "client": aliment.formule.police.client.nom,
                                "garant": formule.police.compagnie.nom,
                                "nom": aliment.nom,
                                "prenoms": aliment.prenoms,
                                "date_naissance": '/'.join(str(aliment.date_naissance).split('-')[::-1]),
                                "qualite": aliment.qualite_beneficiaire.libelle,
                            })

            else:
                actes_trouves.append({
                    "status_code": 404,
                    "status_message": "Non trouvé pour cet assuré",
                    "code": code_acte,
                    "garantie": False,
                })

        message = "Success"
        status_code = 200
        jResponse = {
            "status_code": status_code,
            "message": message,
            "body": actes_trouves,
        }

        return Response(jResponse, status_code, content_type="application/json; charset=utf-8")


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def service_save(request):
    token = request.headers.get('Authorization').split(' ')[1]
    message = None
    status_code = None
    jResponse = {
        "message": message,
        "status_code": status_code
    }

    if request.method == 'POST':
        json_data = request.data

        prestataire = Prestataire.objects.filter(code=9537).first()
        prestataire_id = prestataire.pk  # ID PRESTATAIRE WASPITO

        numero_carte = json_data.get('insurance_id', None)
        codes_acte = json_data.get('acte_code', None)
        medecin = json_data.get('medecin', None)
        affectionJson = json_data.get('affection', None)

        # GET PRESCRIPTEUR ID IF PRESCRIPTEUR ALREADY EXIST
        prescripteur = Prescripteur.objects.filter(numero_ordre=medecin['numero_ordre']).first();
        # IF PRESCRIPTEUR DON'T EXIST
        if not prescripteur:
            # GET SPECIALITE
            specialite = Specialite.objects.filter(code=medecin['code_specialite']).first();

            # CREATE PRESCRIPTEUR
            prescripteur = Prescripteur.objects.create(
                nom=medecin['nom'],
                prenoms=medecin['prenoms'],
                specialite_id=specialite.pk,
                numero_ordre=medecin['numero_ordre'],
                telephone=medecin['telephone'],
                email=medecin['email'])

            # LINK CREATED PRESCRIPTEUR TO PRESTATAIRE (INSERT LINE )
            PrescripteurPrestataire.objects.create(
                prestataire=prestataire,
                prescripteur=prescripteur
            )

        # GET AFFECTION BY CODE
        affection = Affection.objects.filter(code_cim_10=affectionJson['code_cim_10']).first()
        # IF AFFECTION DON'T EXIST
        if not affection:
            affection = Affection.objects.create(
                libelle=affectionJson['libelle'],
                short_name=affectionJson['short_name'],
                code_cim_10=affectionJson['code_cim_10'],
            )

        rc = json_data.get('rc', None)

        # is all fields filled ?
        if not numero_carte or not codes_acte:
            message = "Bad request, veuillez renseignez le numero de l'assuré et le code de l'acte svp."
            status_code = 400

            jResponse = {
                "message": message,
                "status_code": status_code
            }

            return Response(jResponse, status_code, content_type="application/json; charset=utf-8")

        carte = Carte.objects.filter(numero=numero_carte, statut=Statut.ACTIF).first()

        # CREATION DU DOSSIER SINISTRE
        # création des sinistres (acte)
        # for code_acte in codes_acte:

        date_survenance = datetime.datetime.now(tz=datetime.timezone.utc)
        date_prestation = datetime.datetime.now(tz=datetime.timezone.utc)
        date_entree = request.POST.get('date_entree')
        date_sortie = request.POST.get('date_sortie')

        # dd(acte)

        if carte:
            aliment = carte.aliment
            periode_couverture_encours = aliment.formule.police.periode_couverture_encours
            consommation_individuelle = \
                Sinistre.objects.filter(periode_couverture_id=periode_couverture_encours.pk, aliment_id=aliment.id,
                                        statut=StatutSinistre.ACCORDE).aggregate(Sum('part_compagnie'))[
                    'part_compagnie__sum'] or 0
            consommation_famille = Sinistre.objects.filter(periode_couverture_id=periode_couverture_encours.pk,
                                                           adherent_principal_id=aliment.adherent_principal.id,
                                                           statut=StatutSinistre.ACCORDE).aggregate(
                Sum('part_compagnie'))['part_compagnie__sum'] or 0

            formule = aliment.formule

            # son plafond chambre et plafond hospit
            bareme_plafond_chambre = Bareme.objects.filter(formulegarantie_id=aliment.formule.id,
                                                           acte__code="G66023CI01")
            plafond_chambre = bareme_plafond_chambre.first().plafond_acte if bareme_plafond_chambre else 0
            bareme_plafond_hospitalisation = Bareme.objects.filter(formulegarantie_id=aliment.formule.id,
                                                                   acte__code="G66027CI01")
            plafond_hospitalisation = bareme_plafond_hospitalisation.first().plafond_acte if bareme_plafond_hospitalisation else 0

            # vérifie s'il y a au moins 2 éléments dans la liste et
            #  si tous les éléments de la liste sont des chaînes de caractères. Si ces conditions sont remplies, 
            if isinstance(codes_acte, list) and len(codes_acte) >= 2 and all(
                    isinstance(code, str) for code in codes_acte):
                type_prise_en_charge_id = 2
                type_prise_en_charge_code = "AMBULAT"
            else:
                type_prise_en_charge_id = 1
                type_prise_en_charge_code = "CONSULT"

            # recherche en fonction de la date de survenance, date systeme pour le prestataire
            aliment_formule = AlimentFormule.objects.filter(aliment_id=aliment.id, statut=Statut.ACTIF).latest('-id')

            date_survenance = datetime.datetime.now(tz=datetime.timezone.utc)
            prescripteur_id = prescripteur.pk
            prestataire_id = prestataire.pk
            aliment_id = aliment.pk
            affection_id = affection.pk

            # CREATION DU DOSSISER SINISTRE
            # api_user_id = 1  # user Richmond, à remplacer par un user api ...
            api_user_id = get_user_id_from_token(token)
            users = User.objects.filter(id=api_user_id)
            bureau_id = users.first().bureau_id if users else None

            dossier_sinistre = DossierSinistre.objects.create(
                created_by_id=api_user_id,
                bureau_id=bureau_id,
                prestataire_id=prestataire_id,
                centre_prescripteur_id=prestataire.id,  # a confirmer
                aliment_id=aliment.id,
                formulegarantie_id=aliment.formule.id,
                police_id=aliment.formule.police.id,
                compagnie_id=aliment.formule.police.compagnie.id,
                prescripteur_id=prescripteur_id,
                type_priseencharge_id=type_prise_en_charge_id,
                renseignement_clinique=rc,
                plafond_chambre=plafond_chambre,
                plafond_hospit=plafond_hospitalisation,
                affection_id=affection.pk
            )

            # mettre a jour le total frais reel
            dossier_sinistre.numero = 'BS' + str(Date.today().year) + str(dossier_sinistre.id).zfill(6)
            dossier_sinistre.save()

            sinistres = []
            for code_acte in codes_acte:
                acte = Acte.objects.filter(code=code_acte).first()

                if (acte):

                    acte_id = acte.id

                    acte_waspito = ActeWaspito.objects.filter(acte_id=acte_id).first()

                    if not acte_waspito or not acte_waspito.prix:

                        if acte_waspito is None or acte_waspito.prix is None:
                            message = "L'acte demandé est introuvable dans la table de correspondance ou aucun prix n'est configuré pour cet acte."

                        status_code = 404
                        sinistres.append({
                            "status_code": status_code,
                            "status_message": message,
                            "acte": code_acte,
                            "garantie": False,
                        })
                    else:

                        cout_acte = acte_waspito.prix;
                        nombre_jours = None

                        # pour plus de sécurité, récupérer les tarif à partir du fichier excel et nom du formulaire utilisateur
                        infos_acte = get_tarif_acte_from_bareme(type_prise_en_charge_code, date_survenance, acte_id,
                                                                prestataire.id, prescripteur_id, aliment_id, cout_acte,
                                                                nombre_jours, consommation_individuelle,
                                                                consommation_famille)

                        if infos_acte:
                            if infos_acte['statut'] == 0:
                                message = infos_acte['message']
                                status_code = 401

                                sinistres.append({
                                    "status_code": 404,
                                    "status_message": "Erreur sur l'acte (" + code_acte + ") sinistre non créé pour ce cas ",
                                    "acte": code_acte,
                                    "garantie": False,
                                })
                            else:
                                frais_reel = infos_acte['data']['frais_reel']
                                part_compagnie = infos_acte['data']['part_compagnie']
                                part_assure = infos_acte['data']['part_assure']
                                ticket_moderateur = infos_acte['data']['ticket_moderateur']
                                depassement = infos_acte['data']['depassement']

                                plafond_acte = infos_acte['data']['plafond_acte']
                                nombre_acte = infos_acte['data']['nombre_acte']
                                frequence = infos_acte['data']['frequence']
                                unite_frequence = infos_acte['data']['unite_frequence']
                                garanti = infos_acte['data']['garanti']
                                bareme_id = infos_acte['data']['bareme_id']

                                # statut = "ACCORDE" if acte.accord_automatique else "EN ATTENTE"

                                statut = "ACCORDE" if acte.accord_automatique == 1 else "EN ATTENTE"

                                sinistre = Sinistre.objects.create(
                                    type_sinistre="acte",
                                    created_by_id=api_user_id,
                                    prestataire_id=prestataire.id,
                                    aliment_id=aliment.id,
                                    adherent_principal_id=aliment.adherent_principal.id,
                                    police_id=aliment.formule.police.id,
                                    periode_couverture_id=aliment.formule.police.periode_couverture_encours.pk,
                                    formulegarantie_id=aliment.formule.id,
                                    bareme_id=bareme_id,
                                    compagnie_id=aliment.formule.police.compagnie.id,
                                    prescripteur_id=prescripteur_id,
                                    affection_id=affection_id,
                                    acte_id=acte_id,
                                    frais_reel=frais_reel,
                                    part_compagnie=part_compagnie,
                                    part_assure=part_assure,
                                    ticket_moderateur=ticket_moderateur,
                                    depassement=depassement,

                                    montant_plafond=plafond_acte,
                                    nombre_plafond=nombre_acte,
                                    frequence=frequence,
                                    unite_frequence=unite_frequence,

                                    taux_retenue = get_retenue_selon_contexte(prestataire.id),

                                    date_survenance=date_prestation,
                                    date_entree=date_entree,
                                    date_sortie=date_sortie,
                                    nombre_demande=nombre_jours,  # en hospit
                                    statut=statut,
                                    dossier_sinistre_id=dossier_sinistre.pk
                                )

                                # sinistre_created = Sinistre.objects.get(id=sinistre.pk)

                                sinistre.numero = 'S' + str(Date.today().year) + str(sinistre.pk).zfill(6)
                                sinistre.save()

                                sinistres.append({
                                    "status_code": 200,
                                    "status_message": "Sinistre créé avec succès dans le dossier : " + str(
                                        sinistre.dossier_sinistre_id),
                                    "code": infos_acte['data']['code'],
                                    "acte": infos_acte['data']['libelle'],
                                    "garantie": infos_acte['data']['garanti'],
                                    "coverage": infos_acte['data']['taux_couverture'] / 100,
                                    "frais_reel": infos_acte['data']['frais_reel'],
                                    "part_assure": infos_acte['data']['part_assure'],
                                    "part_assureur": infos_acte['data']['part_compagnie'],
                                    "numero_sinistre": sinistre.numero,
                                    "numero_dossier_sinistre": sinistre.dossier_sinistre.numero,
                                    "numero_police": sinistre.police.numero
                                })
                else:
                    sinistres.append({
                        "status_code": 404,
                        "status_message": "Erreur sur l'acte (" + code_acte + ") sinistre non créé pour ce cas ",
                        "acte": code_acte,
                        "garantie": False,
                    })

    else:
        status_code = 400
        message = "Bad Request"
        body = "{}"

        jResponse = {
            "status_code": status_code,
            "message": message,
            "body": body,
        }

    jResponse = {
        "status_code": 200,
        "message": "success",
        "body": sinistres,
    }

    return Response(jResponse, status_code, content_type="application/json; charset=utf-8")


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_status_sinistre(request):
    json_data = request.data
    numero_sinistre = json_data.get('numero_sinistre', None)

    sinistre = Sinistre.objects.filter(numero=numero_sinistre).first()

    if sinistre:

        status_code = 200
        message = "Informartions sinistre"
        body = {
            "statut_sinistre": sinistre.statut,
            "code_acte": sinistre.acte.code,
            "libelle_acte": sinistre.acte.libelle,
            "frais_reel": sinistre.frais_reel,
            "part_assure": sinistre.part_assure,
            "part_assureur": sinistre.part_compagnie,
            "numero_sinistre": sinistre.numero,
            "numero_dossier_sinistre": sinistre.dossier_sinistre.numero,
            "numero_police": sinistre.police.numero
        }

        jResponse = {
            "status_code": status_code,
            "message": message,
            "body": body,
        }
    else:
        status_code = 400
        jResponse = {
            "status_code": status_code,
            "message": "Bad request!",
        }

    return Response(jResponse, status_code, content_type="application/json; charset=utf-8")


# APPLICATION MOBILE SANTE API VIEWS

# AllowAny to allow all users to access this view
class LoginUserView(views.APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        # print(request.data)
        user = authenticate(username=request.data["uid"], password=request.data["passwd"])
        if user is not None:
            # print(user.aliments.all())
            # print(user.aliment)
            if user.aliment is not None:
                config = KeyValueData.objects.filter(key='SANTE_MOBILE_BUREAU_V2').first()
                if user.aliment.bureau.code in config.data['bureau_v2']:
                    refresh = RefreshToken.for_user(user)

                    return Response(data={
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    })
                else:
                    return Response(data={
                        'detail': "Cette carte n'est pas active sur la v2",
                    }, status=status.HTTP_501_NOT_IMPLEMENTED)
            else:
                return Response(data={
                    'detail': "Aucun compte actif n'a été trouvé avec les identifiants fournis",
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data={
                'detail': "Aucun compte actif n'a été trouvé avec les identifiants fournis",
            }, status=status.HTTP_401_UNAUTHORIZED)


class LoginPrestataireView(views.APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        # print(request.data)
        user = authenticate(username=request.data["uid"], password=request.data["passwd"])
        if user is not None:
            # print(user.aliments.all())
            # print(user.aliment)
            if user.prestataire is not None:
                config = KeyValueData.objects.filter(key='SANTE_MOBILE_BUREAU_V2').first()
                if user.prestataire.bureau.code in config.data['bureau_v2']:
                    refresh = RefreshToken.for_user(user)

                    return Response(data={
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    })
                else:
                    return Response(data={
                        'detail': "Cette carte n'est pas active sur la v2",
                    }, status=status.HTTP_501_NOT_IMPLEMENTED)
            else:
                return Response(data={
                    'detail': "Aucun compte prestataire actif n'a été trouvé avec les identifiants fournis",
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data={
                'detail': "Aucun compte prestataire actif n'a été trouvé avec les identifiants fournis",
            }, status=status.HTTP_401_UNAUTHORIZED)


class LoginGlobalView(views.APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        print(request.data)
        user = authenticate(username=request.data["uid"], password=request.data["passwd"])
        if user is not None:
            # print(user.aliments.all())
            # print(user.aliment)
            refresh = RefreshToken.for_user(user)

            return Response(data={
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response(data={
                'detail': "Aucun compte actif n'a été trouvé avec les identifiants fournis",
            }, status=status.HTTP_401_UNAUTHORIZED)

class ConfigurationView(views.APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def get(self, request, key):
        keyValueData = get_object_or_404(KeyValueData, key=key, statut=True)
        serializer = KeyValueDataSerializer(keyValueData)
        return Response(serializer.data)

class ConfigurationBureauView(views.APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def get(self, request, key):
        key_value_data = get_object_or_404(KeyValueData, key=key, statut=True)
        data = key_value_data.data

        if 'bureau_v2' in data:
            bureau_codes = data['bureau_v2']
            bureaux = Bureau.objects.filter(code__in=bureau_codes)
            bureau_serializer = BureauSerializer(bureaux, many=True)
            return Response(bureau_serializer.data)

        return Response([])


class ModeRemboursementListView(views.APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def get(self, request):
        modes = ModeReglement.objects.filter(libelle__in=['Cheque', 'Mobile money'])
        if not modes.exists():
            return Response(data={"detail": "Aucun mode de remboursement trouvé."}, status=404)

        serializer = ModeRemboursementSerializer(modes, many=True)
        return Response(serializer.data)


class DemandeRemboursementView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        user = self.request.user

        serializer = ""
        if serializer.is_valid():
            # Vérifier si l'utilisateur est un adherent principal
            if user.aliment.adherent_principal_id:
                mode_remboursement = ModeReglement.objects.get(id=serializer.validated_data['mode_remboursement'].id)

                if mode_remboursement.libelle == 'Mobile money' and not serializer.validated_data.get(
                        'numero_remboursement'):
                    return Response({'detail': 'Le numéro de remboursement est requis pour le mode Mobile money.'},
                                    status=status.HTTP_400_BAD_REQUEST)

                # Ajouter les données supplémentaires à la demande
                demande = serializer.save(
                    bureau=user.bureau,
                    adherent_principal_id=user.aliment.id,
                    statut=StatutRemboursement.ATTENTE
                )

                # Préparer le contenu de l'email
                context = {
                    'date_sinistre': demande.date_sinistre,
                    'acte': demande.acte,
                    'prestataire': demande.prestataire,
                    'montant_a_rembourser': demande.montant_a_rembourser,
                    'beneficiaire': demande.beneficiaire,
                    'adherent_principal': demande.adherent_principal,
                    'mode_remboursement': demande.mode_remboursement.libelle,
                    'numero_remboursement': demande.numero_remboursement,
                    'prescription_medical': demande.prescription_medical,
                    'facture_normalisee': demande.facture_normalisee,
                    'acquittee_laboratoire': demande.acquittee_laboratoire,
                    'autre_document': demande.autre_document,
                }

                # Chemins des fichiers à attacher
                file_paths = [
                    demande.prescription_medical.path if demande.prescription_medical else None,
                    demande.facture_normalisee.path if demande.facture_normalisee else None,
                    demande.acquittee_laboratoire.path if demande.acquittee_laboratoire else None,
                    demande.autre_document.path if demande.autre_document else None
                ]

                send_demande_rembours_mail(request.user.email, context, file_paths)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'detail': 'Utilisateur connecté n\'est pas autorisé à effectuer une demande de remboursement.'},
                    status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = self.request.user

        if user.aliment.adherent_principal:
            demande = DemandeRemboursementMobile.objects.filter(adherent_principal_id=user.aliment.adherent_principal)

        elif user.aliment:
            demande = DemandeRemboursementMobile.objects.filter(beneficiaire_id=user.aliment)

        else:
            return Response(
                {'detail': "Utilisateur non autorisé à accéder aux demandes de remboursement."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ""
        return Response(serializer.data)

class RegisterUserView(views.APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        try:
            serializer = CreateUserSerializer(data=request.data)
            if serializer.is_valid():
                carte = Carte.objects.filter(numero=request.data['username']).first()
                config = KeyValueData.objects.filter(key='SANTE_MOBILE_BUREAU_V2').first()
                print(config.data)
                if carte is not None:
                    if carte.statut == Statut.ACTIF:

                        aliment = carte.aliment
                        if aliment.bureau.code in config.data['bureau_v2']:
                            user_instance = serializer.save()

                            user_instance.first_name = aliment.prenoms
                            user_instance.last_name = aliment.nom
                            user_instance.bureau = aliment.bureau
                            user_instance.save()

                            user_object = User.objects.get(id=user_instance.id)
                            aliment.user_extranet = user_object
                            aliment.save()

                            serializer_aliment = AlimentSerializer(aliment)
                            return Response(serializer_aliment.data)
                        else:
                            return Response({'detail': 'Cette carte n\'est pas active sur la v2'},
                                            status=status.HTTP_501_NOT_IMPLEMENTED)
                    else:
                        return Response({'detail': 'Cette carte n\'est plus active'},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'detail': 'Aucun assuré trouvé avec ce numéro de carte'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors)
        except Exception as e:
            print(e)
            return Response({'detail': 'Un compte existe déjà avec ce numéro de carte'},
                            status=status.HTTP_400_BAD_REQUEST)


class RequestResetPasswordView(views.APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        try:
            if not request.data.get('username', None):
                return Response({"username": ["Ce champ est obligatoire."]}, status=status.HTTP_400_BAD_REQUEST)

            carte = Carte.objects.filter(numero=request.data['username']).first()
            config = KeyValueData.objects.filter(key='SANTE_MOBILE_BUREAU_V2').first()
            if carte is not None:
                if carte.statut == Statut.ACTIF:
                    aliment = carte.aliment
                    if aliment.bureau.code in config.data['bureau_v2']:
                        if aliment.user_extranet is not None:
                            serializer = UserDataSerializer(aliment.user_extranet)
                            return Response(serializer.data)
                        else:
                            return Response({
                                'detail': 'Aucun compte n\'a été trouvé avec ce numéro de carte. Veuillez creer un compte.'},
                                status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'detail': 'Cette carte n\'est pas active sur la v2'},
                                        status=status.HTTP_501_NOT_IMPLEMENTED)
                else:
                    return Response({'detail': 'Cette carte n\'est plus active'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'Aucun assuré trouvé avec ce numéro de carte'},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'detail': 'Une erreur est survenue lors de la réinitialisation du mot de passe'},
                            status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(views.APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        try:
            # VERIFICATION SI USER EXISTE
            if not request.data.get('username', None):
                return Response({"username": ["Ce champ est obligatoire."]}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(username=request.data['username']).first()
            if user is None:
                return Response(
                    {'detail': 'Aucun compte n\'a été trouvé avec ce numéro de carte. Veuillez creer un compte.'},
                    status=status.HTTP_400_BAD_REQUEST)

            # VERIFICATION SI CODE EST VALIDE
            serializer = ResetPasswordUserSerializer(user, data=request.data)
            if serializer.is_valid():
                # MISE A JOUR DU MOT DE PASSE
                serializer.save()
                return Response({'detail': 'Mot de passe réinitialisé avec succès'})
            else:
                return Response(serializer.errors)
        except Exception as e:
            print(e)
            return Response({'detail': 'Erreur lors de la mise à jour du profil utilisateur'},
                            status=status.HTTP_400_BAD_REQUEST)


class OTPRequestView(views.APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]
    hotp = pyotp.HOTP(settings.OTP_SECRET_KEY, digits=4)

    def get(self, request):
        try:
            print(request.query_params.get('username', None))
            print(request.query_params.get('is_v2', None))
            print(request.query_params.get('email', None))
            print(pyotp.random_base32())

            if request.query_params.get('is_v2', None) == 'true':
                user = User.objects.filter(username=request.query_params.get('username', None)).first()

                if user:
                    code_verification = int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
                    # send otp mail
                    send_otp_mail(user.email, self.hotp.at(code_verification))

                    return Response({'otp': self.hotp.at(code_verification), 'code_verification': code_verification,
                                     'detail': 'Code OTP envoyé avec succès'})
                else:
                    return Response(
                        {'detail': 'Aucun compte n\'a été trouvé avec ce numéro de carte. Veuillez creer un compte.'},
                        status=status.HTTP_400_BAD_REQUEST)
            else:
                if request.query_params.get('email', None) is None:
                    return Response({'detail': 'Veuillez renseigner votre email'}, status=status.HTTP_400_BAD_REQUEST)

                code_verification = int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
                # send otp mail
                send_otp_mail(request.query_params.get('email', None), self.hotp.at(code_verification))

                return Response({'otp': self.hotp.at(code_verification), 'code_verification': code_verification,
                                 'detail': 'Code OTP envoyé avec succès'})

        except Exception as e:
            print(e)
            return Response({'detail': 'Erreur lors de la envoi de l\'OTP'},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        otp = request.data.get('otp', None)
        code_verification = request.data.get('code_verification', None)
        # Verification des champs
        if not otp:
            return Response({"otp": ["Ce champ est obligatoire."]}, status=status.HTTP_400_BAD_REQUEST)

        if not code_verification:
            return Response({"code_verification": ["Ce champ est obligatoire."]}, status=status.HTTP_400_BAD_REQUEST)

        # Verification du code OTP
        if self.hotp.verify(otp, code_verification):
            return Response({'detail': 'Code OTP valide'})
        else:
            return Response({'detail': 'Code OTP invalide'}, status=status.HTTP_400_BAD_REQUEST)


# IsAuthenticated to allow only authenticated users to access this view
class UserView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        user = self.request.user
        serializer = AlimentSerializer(user.aliment)
        return Response(serializer.data)

    def put(self, request):
        try:
            user = self.request.user
            serializer = UserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                serializer_aliment = AlimentSerializer(user.aliment)
                return Response(serializer_aliment.data)
            else:
                return Response(serializer.errors)
        except Exception as e:
            print(e)
            return Response({'message': 'Erreur lors de la mise à jour du profil utilisateur'},
                            status=status.HTTP_400_BAD_REQUEST)


class PrestataireView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        user = self.request.user
        serializer = PrestataireDataSerializer(user)
        return Response(serializer.data)


class BeneficiariesView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        user = self.request.user
        membres_famille = Aliment.objects.filter(adherent_principal_id=user.aliment.adherent_principal_id)
        serializer = AlimentSerializer(membres_famille, many=True)
        return Response(serializer.data)


class BeneficiariesByIdView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, beneficiary_id):
        beneficiary = Aliment.objects.get(id=beneficiary_id)
        serializer = AlimentSerializer(beneficiary)
        return Response(serializer.data)


class BeneficiariesByCarteView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, carte):
        carte = Carte.objects.filter(numero=carte).first()
        print(carte)
        prestataire_id = request.query_params.get('prestataire_id', None)

        if carte is not None:
            if carte.statut == Statut.ACTIF:
                aliment = carte.aliment
                police = aliment.formule.police if aliment.formule else None
                etat_police = police.etat_police if police else 'INEXISTANT'
                is_echue = police.is_echue if police else False
                etat_beneficiaire = aliment.etat_beneficiaire

                # Verification du si beneficiaire est suspendu
                print(aliment.etat_beneficiaire)
                if etat_beneficiaire == 'SUSPENDU':
                    return Response({
                        'detail': "Ce bénéficiaire est actuellement suspendu de sa police d'assurance santé. Nous vous invitons à prendre les mesures nécessaires en conséquence."
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Verification du si beneficiaire est sorti
                if etat_beneficiaire == 'SORTI':
                    return Response({
                        'detail': "Ce bénéficiaire est sorti de sa police d'assurance santé. Nous vous invitons à prendre les mesures nécessaires en conséquence."
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Check if the police is active (i.e., "en cours")
                print(police)
                print(police.etat_police)
                print(police.is_echue)
                if etat_police == 'En cours':

                    if is_echue:
                        return Response({
                            'detail': "La police d'assurance de cet assuré n'est pas en cours. Merci de prendre les dispositions nécessaires en fonction de cette situation."
                        }, status=status.HTTP_400_BAD_REQUEST)

                    # Police is active, return OK
                    if prestataire_id is not None:
                        formule_garantie = FormuleGarantie.objects.get(id=aliment.formule.id)
                        print(formule_garantie)
                        print(formule_garantie.code)
                        print(formule_garantie.reseau_soin)

                        if formule_garantie.reseau_soin is not None:
                            reseau_soin = formule_garantie.reseau_soin
                            prestataires = PrestataireReseauSoin.objects.filter(
                                reseau_soin_id=reseau_soin.id, 
                                prestataire_id=prestataire_id
                            )
                            print(prestataires)
                        else:
                            prestataires = Prestataire.objects.filter(
                                bureau=formule_garantie.police.bureau,
                                id=prestataire_id
                            )

                        if len(prestataires) == 0:
                            return Response({
                                'detail': "Nous constatons que vous ne faites pas partie du réseau de soins de cet assuré. Veuillez vérifier les informations fournies et nous en informer si nécessaire."
                            }, status=status.HTTP_400_BAD_REQUEST)

                    # Serialize and return aliment data
                    serializer = AlimentSerializer(aliment)
                    return Response(serializer.data)

                else:
                    # Police is not active, return KO
                    return Response({
                        'detail': "La police d'assurance de cet assuré n'est pas en cours. Merci de prendre les dispositions nécessaires en fonction de cette situation."
                    }, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({
                    'detail': 'Cette carte n\'est plus active.'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'detail': 'Aucun assuré trouvé avec ce numéro de carte.'
            }, status=status.HTTP_400_BAD_REQUEST)


class BarremeView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, formul_id):
        barrem = Bareme.objects.filter(formulegarantie_id=formul_id, statut=Statut.ACTIF)
        serializer = BarremeSerializer(barrem, many=True)
        return Response(serializer.data)


class SinistreView(views.APIView, SmartResultsSetPagination):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    # serializer_class = SinisteSerializer
    # pagination_class = SmartResultsSetPagination
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['aliment', 'date_survenance', 'acte']
    # queryset = Sinistre.objects.filter(statut=StatutSinistre.ACCORDE).order_by('-id')

    def get(self, request):
        print(request.query_params)
        aliment = request.query_params.get('aliment', None)
        date_survenance = request.query_params.get('date_survenance', None)
        acte = request.query_params.get('acte', None)

        # print(aliment)
        # print(date_survenance)
        # print(acte)

        if aliment is not None:
            queryset = Sinistre.objects.filter(statut=StatutSinistre.ACCORDE, aliment_id=aliment).order_by('-id')

            if date_survenance is not None:
                date_survenance = datetime.datetime.strptime(date_survenance, "%Y-%m-%d").date()
                # print(date_survenance)
                # print(date_survenance.year)
                # print(date_survenance.day)
                # print(date_survenance.month)
                # print(type(date_survenance))
                queryset = Sinistre.objects.filter(statut=StatutSinistre.ACCORDE, aliment_id=aliment,
                                                   date_survenance__year=date_survenance.year,
                                                   date_survenance__day=date_survenance.day,
                                                   date_survenance__month=date_survenance.month).order_by('-id')
        else:
            queryset = Sinistre.objects.filter(statut=StatutSinistre.ACCORDE).order_by('-id')
        serializer = self.paginate_queryset(queryset, self.request)
        serializer = SinisteSerializer(serializer, many=True)

        return self.get_paginated_response(serializer.data)


class ReseauSoinsView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    # serializer_class = PrestataireSerializer
    # pagination_class = SmartResultsSetPagination
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['aliment', 'date_survenance', 'acte']
    # queryset = Sinistre.objects.filter(statut=StatutSinistre.ACCORDE).order_by('-id')
    def get(self, request, formul_id):
        print(request.query_params)
        type_prestataire = request.query_params.get('type_prestataire', None)

        formule_garantie = FormuleGarantie.objects.get(id=formul_id)

        if formule_garantie.reseau_soin is not None:
            reseau_soin = formule_garantie.reseau_soin
            prestataire_reseau_soin = PrestataireReseauSoin.objects.filter(reseau_soin_id=reseau_soin.id, statut_validite="VALIDE")
            if type_prestataire is not None:
                prestataire_reseau_soin = prestataire_reseau_soin.filter(
                    prestataire__type_prestataire_id=type_prestataire)

            serializer = PrestataireSerializer([x.prestataire for x in prestataire_reseau_soin if x.prestataire.status],
                                               many=True)
        else:
            prestataires = Prestataire.objects.filter(bureau=formule_garantie.police.bureau, status=True)
            if type_prestataire is not None:
                prestataires = prestataires.filter(type_prestataire_id=type_prestataire)

            serializer = PrestataireSerializer(prestataires, many=True)

        return Response(serializer.data)


class TypePrestataireView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        type_prestataire = TypePrestataire.objects.all()
        serializer = TypePrestataireSerializer(type_prestataire, many=True)
        return Response(serializer.data)


class PrestataireDataView(views.APIView, SmartResultsSetPagination):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        search = request.query_params.get('search', None)
        bureau = request.user.bureau
        queryset = Prestataire.objects.filter(status=True, bureau=bureau).order_by('name')
        if search is not None:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(type_prestataire__name__icontains=search)
            )
        self.page_size = 20
        serializer = self.paginate_queryset(queryset, self.request)
        serializer = PrestataireSerializer(serializer, many=True)

        return self.get_paginated_response(serializer.data)


class ActeDataView(views.APIView, SmartResultsSetPagination):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        search = request.query_params.get('search', None)
        type_acte = request.query_params.get('type_acte', None)
        queryset = Acte.objects.filter(status=True).order_by('libelle')

        if type_acte is not None:
            queryset = queryset.filter(type_acte_id=type_acte)

        if search is not None:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(libelle__icontains=search) |
                Q(code__icontains=search) |
                Q(rubrique__libelle__icontains=search) |
                Q(regroupement_acte__libelle__icontains=search) |
                Q(type_acte__libelle__icontains=search)
            )


        self.page_size = 20
        serializer = self.paginate_queryset(queryset, self.request)
        serializer = ActeSerializer(serializer, many=True)

        return self.get_paginated_response(serializer.data)


class TestNumCartView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        user = self.request.user
        numer_cart = generate_numero_carte(user.aliment)
        return Response(data={"numero_carte": numer_cart})


class AddAyantDroitView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        aliment = user.aliment
        formules = FormuleGarantie.objects.get(id=aliment.formule.id)
        polices = formules.police

        pprint('Hello Joseph')

        # Step 1 : Vérifier ou créer une campagne pour l'utilisateur connecté
        campagne = CampagneAppmobile.objects.filter(created_by=user).first()
        if not campagne:
            campagne = CampagneAppmobile.objects.create(
                created_by=user,
                police=polices,
                formulegarantie=formules,
                statut=StatutEnrolement.VALIDE
            )

        # Step 2 : Préparer les données du Prospect

        data = request.data
        bureau = user.bureau
        formulegarantie = formules
        police = polices
        aliment_adherent_principal = user.aliment.adherent_principal

        data['bureau'] = bureau.id
        data['formulegarantie'] = formulegarantie.id
        data['police'] = police.id
        data['aliment_adherent_principal'] = aliment_adherent_principal.id
        data['statut_enrolement'] = StatutEnrolement.SOUMIS
        # VERIFI IF date_affiliation EXIST IN DATA
        try:
            data['date_affiliation'] = data['date_affiliation']
        except Exception as e:
            data['date_affiliation'] = datetime.datetime.now().date()



        # Step 3 : Sérialisation et validation des données du Prospect
        serializer = ""
        if serializer.is_valid():
            prospect = serializer.save()
            # uiid = generate_uiid(request)
            # url = f'{base_url}/grh/enrolement/{campagne.pk}/{uiid}/{aliment.pk}/'
            # Step 4 : Créer une entrée dans CampagneAppmobileProspect
            CampagneAppmobileProspect.objects.create(
                campagne_appmobile=campagne,
                prospect=prospect,
                statut_enrolement=StatutEnrolement.SOUMIS,
                # iuid=uiid,
                # lien=url,
                mouvement_id=7
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListProspectsView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        user = request.user

        # Step 1 : Récupérer la CampagneAppmobile associée à l'utilisateur connecté
        campagne = CampagneAppmobile.objects.filter(created_by=user).first()
        if not campagne:
            return Response({'error': 'No campaign found for the user'}, status=status.HTTP_404_NOT_FOUND)

        # Step 2 : Récupérer les Prospects avec les statuts 'VALIDE' et 'ATTENTE'
        prospects = CampagneAppmobileProspect.objects.filter(
            campagne_appmobile=campagne,
            statut_enrolement__in=[StatutEnrolement.VALIDE, StatutEnrolement.ATTENTE, StatutEnrolement.SOUMIS]
        ).select_related('prospect')

        # Sérialiser les données des prospects
        serialized_prospects = []
        for liste in prospects:
            data = ""
            data['statut_enrolement'] = liste.statut_enrolement
            data['mouvement'] = liste.mouvement_id
            serialized_prospects.append(data)

        return Response(serialized_prospects, status=status.HTTP_200_OK)


## INOV API MOBILE

class FetchDigitalCard(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    # @method_decorator(csrf_exempt)
    def get(self, request, format=None):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = request.user.id
        try:
            digital_card = CarteDigitalDematerialisee.objects.filter(user__id=user_id).order_by('-id')[0]
            serializer = CarteDigitalDematerialiseeSerializer(digital_card)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except CarteDigitalDematerialisee.DoesNotExist:
            return Response({'error': 'Carte digitale introuvable pour cet utilisateur.'},
                            status=status.HTTP_404_NOT_FOUND)


class CreateDigitalCard(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    # @method_decorator(csrf_exempt)
    def post(self, request, format=None):
        user_id = request.user.id
        existing_card = CarteDigitalDematerialisee.objects.filter(
            user__id=user_id).first()
        if existing_card:
            return Response({'error': 'Une carte digital existe déjà pour cet utilisateur.'},
                            status=status.HTTP_400_BAD_REQUEST)

        request.data['user'] = user_id
        serializer = CarteDigitalDematerialiseeSerializer(data=request.data)
        if serializer.is_valid():
            digital_card = serializer.save()
            # print(digital_card)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateDigitalCard(views.APIView):
    permission_classes = [IsAuthenticated]

    # @method_decorator(csrf_exempt)
    def put(self, request, digital_card_id, format=None):
        try:
            digital_card = CarteDigitalDematerialisee.objects.get(id=digital_card_id, user=request.user)
        except CarteDigitalDematerialisee.DoesNotExist:
            return Response({'error': 'Carte digitale introuvable pour cet utilisateur.'},
                            status=status.HTTP_404_NOT_FOUND)

        update_data = {
            'has_digital_card': request.data.get('has_digital_card'),
            'digital_card_url': request.data.get('digital_card_url')
        }
        update_data = {k: v for k, v in update_data.items() if v is not None}
        serializer = CarteDigitalDematerialiseeSerializer(digital_card, data=update_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# TODO: API PRISE EN CHARGE APP MOBILE
class PriseEnChargeView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        user = self.request.user
        aliment = user.aliment

        carte = aliment.carte_active() if aliment.carte_active() else None
        numero_carte = carte.numero if carte else None
        prescripteur_id = 2873  # par default DR KOUSSOUBE ERIC
        affection_id = 1  # par default AUTRE AFFECTION
        type_document_id = 1 # par defaut AUTRE

        formules = FormuleGarantie.objects.get(id=aliment.formule.id)
        polices = formules.police

        json_data = request.data

        prestataire_id = json_data.get('prestataire_id', None)
        commentaire = json_data.get('commentaire', None)
        acte_id = json_data.get('acte_id', None)

        type_remboursement = json_data.get('type_remboursement', None)

        if prestataire_id is None:
            message = "Bad request, le champ prestataire_id est requis"
            status_code = 400
            jResponse = {
                "status_code": status_code,
                "message": message,
            }
            return Response(jResponse, status_code, content_type="application/json; charset=utf-8")

        if acte_id is None:
            message = "Bad request, le champ acte_id est requis"
            status_code = 400
            jResponse = {
                "status_code": status_code,
                "message": message,
            }
            return Response(jResponse, status_code, content_type="application/json; charset=utf-8")

        if type_remboursement is None:
            message = "Bad request, le champ type_remboursement est requis"
            status_code = 400
            jResponse = {
                "status_code": status_code,
                "message": message,
            }
            return Response(jResponse, status_code, content_type="application/json; charset=utf-8")





        if type_remboursement == "TP":
            type_remboursement = 1
        elif type_remboursement == "RD":
            type_remboursement =2
        else:

            message = "Bad request, le type de remboursement est invalide.Les valeurs autorisées sont TP et RD"
            status_code = 400
            jResponse = {
                "status_code": status_code,
                "message": message,
            }
            return Response(jResponse, status_code, content_type="application/json; charset=utf-8")

        acte = get_object_or_404(Acte, id=acte_id)
        # medecin = json_data.get('medecin', None)
        # affectionJson = json_data.get('affection', None)

        prestataire = Prestataire.objects.get(id=prestataire_id)

        # GET PRESCRIPTEUR ID IF PRESCRIPTEUR ALREADY EXIST
        prescripteur = Prescripteur.objects.get(id=prescripteur_id)

        # GET AFFECTION BY CODE
        affection = Affection.objects.get(id=affection_id)


        # rc = json_data.get('commentaire', None)

        # is all fields filled ?
        if not numero_carte or not acte_id:
            message = "Bad request, le numero de l'assuré et le code de l'acte est invalide."
            status_code = 400

            jResponse = {
                "message": message,
                "status_code": status_code
            }

            return Response(jResponse, status_code, content_type="application/json; charset=utf-8")

        # carte = Carte.objects.filter(numero=numero_carte, statut=Statut.ACTIF).first()

        # CREATION DU DOSSIER SINISTRE
        # création des sinistres (acte)
        # for code_acte in codes_acte:

        date_survenance = datetime.datetime.now(tz=datetime.timezone.utc)
        date_prestation = datetime.datetime.now(tz=datetime.timezone.utc)
        date_entree = request.POST.get('date_entree')
        date_sortie = request.POST.get('date_sortie')

        status_code = 400
        message = "Bad request"

        # dd(acte)

        if carte:
            # aliment = carte.aliment
            periode_couverture_encours = aliment.formule.police.periode_couverture_encours
            consommation_individuelle = \
                Sinistre.objects.filter(periode_couverture_id=periode_couverture_encours.pk, aliment_id=aliment.id,
                                        statut=StatutSinistre.ACCORDE).aggregate(Sum('part_compagnie'))[
                    'part_compagnie__sum'] or 0
            consommation_famille = Sinistre.objects.filter(periode_couverture_id=periode_couverture_encours.pk,
                                                           adherent_principal_id=aliment.adherent_principal.id,
                                                           statut=StatutSinistre.ACCORDE).aggregate(
                Sum('part_compagnie'))['part_compagnie__sum'] or 0

            formule = aliment.formule

            # son plafond chambre et plafond hospit
            bareme_plafond_chambre = Bareme.objects.filter(formulegarantie_id=aliment.formule.id,
                                                           acte__code="G66023CI01")
            plafond_chambre = bareme_plafond_chambre.first().plafond_acte if bareme_plafond_chambre else 0
            bareme_plafond_hospitalisation = Bareme.objects.filter(formulegarantie_id=aliment.formule.id,
                                                                   acte__code="G66027CI01")
            plafond_hospitalisation = bareme_plafond_hospitalisation.first().plafond_acte if bareme_plafond_hospitalisation else 0

            # vérifie s'il y a au moins 2 éléments dans la liste et
            #  si tous les éléments de la liste sont des chaînes de caractères. Si ces conditions sont remplies,

            type_prise_en_charge = acte.rubrique.type_priseencharge
            type_prise_en_charge_id = type_prise_en_charge.id
            type_prise_en_charge_code = type_prise_en_charge.code

            # recherche en fonction de la date de survenance, date systeme pour le prestataire
            aliment_formule = AlimentFormule.objects.filter(aliment_id=aliment.id, statut=Statut.ACTIF).latest('-id')

            date_survenance = datetime.datetime.now(tz=datetime.timezone.utc)
            prescripteur_id = prescripteur.pk
            prestataire_id = prestataire.pk
            aliment_id = aliment.pk
            affection_id = affection.pk

            # CREATION DU DOSSISER SINISTRE
            bureau_id = user.bureau_id if user else None

            dossier_sinistre = DossierSinistre.objects.create(
                created_by_id=user.id,
                bureau_id=bureau_id,
                prestataire_id=prestataire_id,
                centre_prescripteur_id=prestataire.id,  # a confirmer
                aliment_id=aliment.id,
                formulegarantie_id=aliment.formule.id,
                police_id=aliment.formule.police.id,
                compagnie_id=aliment.formule.police.compagnie.id,
                prescripteur_id=prescripteur_id,
                type_priseencharge_id=type_prise_en_charge_id,
                renseignement_clinique=f'COMMENTAIRE APPLIMOBILE:{commentaire}',
                plafond_chambre=plafond_chambre,
                plafond_hospit=plafond_hospitalisation,
                affection_id=affection.pk,
                mode_creation_id=3,
                type_remboursement_id=type_remboursement
                # commentaire=commentaire
            )

            # mettre a jour le total frais reel
            dossier_sinistre.numero = 'BS' + str(Date.today().year) + str(dossier_sinistre.id).zfill(6)
            dossier_sinistre.save()


            # document
            documents = []
            try:

                document1 = request.FILES['document1']
                document2 = request.FILES['doccument2']

                fs = FileSystemStorage()
                # file_name_renamed = 'doc_' + str(dossier_sinistre_id) + '_' + str(uuid.uuid4()) +'_'+ file.name.replace(" ", "_")
                file_name_renamed1 = 'doc_' + str(dossier_sinistre.id) + '_' + document1.name.replace(" ", "_")
                file_name_renamed2 = 'doc_' + str(dossier_sinistre.id) + '_' + document2.name.replace(" ", "_")
                file_upload_path1 = 'dossiers_sinistres/documents/' + file_name_renamed1
                file_upload_path2 = 'dossiers_sinistres/documents/' + file_name_renamed2

                fs.save(file_upload_path1, document1)
                fs.save(file_upload_path2, document2)

                type_document = TypeDocument.objects.get(id=type_document_id)

            except MultiValueDictKeyError:
                file_upload_path = ''

            sinistres = None
            if acte:

                acte_id = acte.id

                # acte_waspito = ActeWaspito.objects.filter(acte_id=acte_id).first()

            cout_acte = None
            nombre_jours = None

            # pour plus de sécurité, récupérer les tarif à partir du fichier excel et nom du formulaire utilisateur
            infos_acte = get_tarif_acte_from_bareme(type_prise_en_charge_code, date_survenance, acte_id,
                                                    prestataire.id, prescripteur_id, aliment_id, cout_acte,
                                                    nombre_jours, consommation_individuelle,
                                                    consommation_famille)

            if infos_acte:
                if infos_acte['statut'] == 0:
                    message = infos_acte['message']
                    # status_code = 401
                    # message = "L'acte demandé est introuvable dans la table de correspondance ou aucun prix n'est configuré pour cet acte."
                    status_code = 400
                    sinistres = {
                        "status_code": status_code,
                        "status_message": "Erreur sur l'acte (" + acte.code + ") sinistre non créé pour ce cas : " +  message,
                        "acte": acte.code,
                        "garantie": False,
                    }
                else:
                    frais_reel = infos_acte['data']['frais_reel']
                    part_compagnie = infos_acte['data']['part_compagnie']
                    part_assure = infos_acte['data']['part_assure']
                    ticket_moderateur = infos_acte['data']['ticket_moderateur']
                    depassement = infos_acte['data']['depassement']

                    plafond_acte = infos_acte['data']['plafond_acte']
                    nombre_acte = infos_acte['data']['nombre_acte']
                    frequence = infos_acte['data']['frequence']
                    unite_frequence = infos_acte['data']['unite_frequence']
                    garanti = infos_acte['data']['garanti']
                    bareme_id = infos_acte['data']['bareme_id']

                    # statut = "ACCORDE" if acte.accord_automatique else "EN ATTENTE"

                    statut = "ACCORDE" if acte.accord_automatique == 1 else "EN ATTENTE"

                    sinistre = Sinistre.objects.create(
                        type_sinistre="acte",
                        created_by_id=user.id,
                        prestataire_id=prestataire.id,
                        aliment_id=aliment.id,
                        adherent_principal_id=aliment.adherent_principal.id,
                        police_id=aliment.formule.police.id,
                        periode_couverture_id=aliment.formule.police.periode_couverture_encours.pk,
                        formulegarantie_id=aliment.formule.id,
                        bareme_id=bareme_id,
                        compagnie_id=aliment.formule.police.compagnie.id,
                        prescripteur_id=prescripteur_id,
                        affection_id=affection_id,
                        acte_id=acte_id,
                        frais_reel=frais_reel,
                        part_compagnie=part_compagnie,
                        part_assure=part_assure,
                        ticket_moderateur=ticket_moderateur,
                        depassement=depassement,

                        montant_plafond=plafond_acte,
                        nombre_plafond=nombre_acte,
                        frequence=frequence,
                        unite_frequence=unite_frequence,

                        taux_retenue=get_retenue_selon_contexte(prestataire.id),

                        date_survenance=date_prestation,
                        date_entree=date_entree,
                        date_sortie=date_sortie,
                        nombre_demande=nombre_jours,  # en hospit
                        statut=statut,
                        dossier_sinistre_id=dossier_sinistre.pk
                    )

                    # sinistre_created = Sinistre.objects.get(id=sinistre.pk)

                    sinistre.numero = 'S' + str(Date.today().year) + str(sinistre.pk).zfill(6)
                    sinistre.save()
                    status_code = 200
                    sinistres = {
                        "status_code": status_code,
                        "status_message": "Sinistre créé avec succès dans le dossier : " + str(
                            sinistre.dossier_sinistre_id),
                        "code": infos_acte['data']['code'],
                        "acte": infos_acte['data']['libelle'],
                        "garantie": infos_acte['data']['garanti'],
                        "coverage": infos_acte['data']['taux_couverture'] / 100,
                        "frais_reel": infos_acte['data']['frais_reel'],
                        "part_assure": infos_acte['data']['part_assure'],
                        "part_assureur": infos_acte['data']['part_compagnie'],
                        "numero_sinistre": sinistre.numero,
                        "numero_dossier_sinistre": sinistre.dossier_sinistre.numero,
                        "numero_police": sinistre.police.numero
                    }



            else:
                status_code = 400
                sinistres = {
                    "status_code": status_code,
                    "status_message": "Erreur sur l'acte (" + acte.code + ") sinistre non créé pour ce cas ",
                    "acte": acte.code,
                    "garantie": False,
                }

        else:
            status_code = 404
            message = "Bad request, le numero de l'assuré est invalide."


        jResponse = {
            "status_code": status_code,
            "message": message,
            "data": sinistres,
        }

        return Response(jResponse, status_code, content_type="application/json; charset=utf-8")

    def get(self, request, *args, **kwargs):
        status_code = 400
        message = "Bad Request"
        body = "{}"

        jResponse = {
            "status_code": status_code,
            "message": message,
            "data": body,
        }

        return Response(jResponse, status_code, content_type="application/json; charset=utf-8")


class PriseEnChargeActeInfoView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, acte_id):

        message = None
        status_code = None

        jResponse = {
            "message": message,
            "status_code": status_code,
        }

        acte = get_object_or_404(Acte, id=acte_id)
        user = self.request.user
        aliment = user.aliment
        carte = aliment.carte_active() if aliment.carte_active() else None
        num_carte = carte.numero if carte else None
        # jResponse = {
        #     "status_code": status_code,
        #     "message": message,
        #     'carte' : carte.numero,
        #     "data": AlimentSerializer(aliment).data,
        # }
        #
        # return Response(jResponse, status_code, content_type="application/json; charset=utf-8")

        actes_trouve = None

        if carte and acte:
            # aliment = carte.aliment
            print(carte.aliment.nom)

            prestataire = Prestataire.objects.filter(code=9537).first()
            prestataire_id = prestataire.pk  # ID PRESTATAIRE WASPITO

            periode_couverture_encours = aliment.formule.police.periode_couverture_encours
            consommation_individuelle = \
                Sinistre.objects.filter(periode_couverture_id=periode_couverture_encours.pk, aliment_id=aliment.id,
                                        statut=StatutSinistre.ACCORDE).aggregate(Sum('part_compagnie'))[
                    'part_compagnie__sum'] or 0
            consommation_famille = Sinistre.objects.filter(periode_couverture_id=periode_couverture_encours.pk,
                                                           adherent_principal_id=aliment.adherent_principal.id,
                                                           statut=StatutSinistre.ACCORDE).aggregate(
                Sum('part_compagnie'))['part_compagnie__sum'] or 0

            formule = aliment.formule

            # son plafond chambre et plafond hospit
            bareme_plafond_chambre = Bareme.objects.filter(formulegarantie_id=aliment.formule.id,
                                                           acte__code="G66023CI01")
            plafond_chambre = bareme_plafond_chambre.first().plafond_acte if bareme_plafond_chambre else 0
            bareme_plafond_hospitalisation = Bareme.objects.filter(formulegarantie_id=aliment.formule.id,
                                                                   acte__code="G66027CI01")
            plafond_hospitalisation = bareme_plafond_hospitalisation.first().plafond_acte if bareme_plafond_hospitalisation else 0

            # vérifie s'il y a au moins 2 éléments dans la liste et
            #  si tous les éléments de la liste sont des chaînes de caractères. Si ces conditions sont remplies,
            type_prise_en_charge = acte.rubrique.type_priseencharge
            type_prise_en_charge_id = type_prise_en_charge.id
            type_prise_en_charge_code = type_prise_en_charge.code

            # recherche en fonction de la date de survenance, date systeme pour le prestataire
            aliment_formule = AlimentFormule.objects.filter(aliment_id=aliment.id, statut=Statut.ACTIF).latest(
                '-id')

            date_survenance = datetime.datetime.now(tz=datetime.timezone.utc)
            acte_id = acte.id
            prescripteur_id = 2232
            aliment_id = aliment.pk

            # acte_waspito = ActeWaspito.objects.filter(acte_id=acte_id).first()

            cout_acte = None

            nombre_jours = None

            # pour plus de sécurité, récupérer les tarif à partir du fichier excel et nom du formulaire utilisateur
            infos_acte = get_tarif_acte_from_bareme(type_prise_en_charge_code, date_survenance, acte_id,
                                                    prestataire.id,
                                                    prescripteur_id, aliment_id, cout_acte,
                                                    nombre_jours, consommation_individuelle,
                                                    consommation_famille)

            if infos_acte:
                if infos_acte['statut'] == 0:
                    message = infos_acte['message']
                    status_code = 404

                    message = "L'acte demandé est introuvable dans la table de correspondance ou aucun prix n'est configuré pour cet acte."

                    actes_trouve = {
                        "status_code": status_code,
                        "status_message": message,
                        "code": acte.code,
                        "acte": acte.libelle,
                        "garantie": False,
                    }

                    # jResponse = {
                    #     "message": message,
                    #     "status_code": status_code
                    # }
                else:
                    actes_trouve = {
                        "status_code": 200,
                        "status_message": "Acte trouvé",
                        "code": infos_acte['data']['code'],
                        "acte": infos_acte['data']['libelle'],
                        "garantie": infos_acte['data']['garanti'],
                        "attente_prealable": False if acte.accord_automatique else True,
                        "coverage": infos_acte['data']['taux_couverture'] / 100,
                        "frais_reel": infos_acte['data']['frais_reel'],
                        "part_assure": infos_acte['data']['part_assure'],
                        "part_assureur": infos_acte['data']['part_compagnie'],
                        "numero_police": aliment.formule.police.numero,
                        "client": aliment.formule.police.client.nom,
                        "garant": formule.police.compagnie.nom,
                        "nom": aliment.nom,
                        "prenoms": aliment.prenoms,
                        "date_naissance": '/'.join(str(aliment.date_naissance).split('-')[::-1]),
                        "qualite": aliment.qualite_beneficiaire.libelle,
                    }

        else:
            status_code = 404
            actes_trouve = {
                "status_code": status_code,
                "status_message": "Non trouvé pour cet assuré",
                "code": acte.code,
                "garantie": False,
            }



        # message = "Success"
        # status_code = 200
        jResponse = {
            "status_code": status_code,
            "message": message,
            "data": actes_trouve,
        }

        return Response(jResponse, status_code, content_type="application/json; charset=utf-8")


class ConstantesView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        type_acte = TypeActe.objects.all()
        civilite = Civilite.objects.all()
        qualite_beneficiaire = QualiteBeneficiaire.objects.all()
        pays = Pays.objects.all()
        profession = Profession.objects.all()

        typeacte_serializer = TypeActeSerialiser(type_acte, many=True)
        civilite_serializer = CiviliteSerializer(civilite, many=True)
        qualite_beneficiaire_serializer = QualiteBeneficiaireSerializer(qualite_beneficiaire, many=True)
        pays_serializer = PaysSerializer(pays, many=True)
        profession_serializer = ProfessionSerializer(profession, many=True)

        data = {
            "type_actes": typeacte_serializer.data,
            "civilites": civilite_serializer.data,
            "qualite_beneficiaires": qualite_beneficiaire_serializer.data,
            "professions": profession_serializer.data,
            "pays": pays_serializer.data

        }
        return Response(data)


#Suggestion lors de la recherche des polices
def suggestions(request):
    query = request.GET.get('numero', '')
    if query:
        # Récupérer l'utilisateur
        user = request.user

        # Vérifier si l'utilisateur a un rôle valide
        if not (user.is_commercial or user.is_production):
            return JsonResponse([], safe=False)

        # Recherche des résultats pour les utilisateurs commerciaux ou de production
        if user.is_commercial:
            results = (
                Police.objects.filter(numero__icontains=query, commercial_id=user.id)
                .select_related('client')  # Optimisation pour inclure les données du client
                .values(
                    'id',  # Pour générer le lien
                    'numero',
                    'client__nom',
                )[:10]
            )
        else:  # Si l'utilisateur est de type 'production' ou un autre type valide
            results = (
                Police.objects.filter(numero__icontains=query)
                .select_related('client')  # Optimisation pour inclure les données du client
                .values(
                    'id',  # Pour générer le lien
                    'numero',
                    'client__nom',
                )[:10]
            )

        print("Police : ", results)

        # Ajouter les données formatées pour chaque police
        results_with_links = [
            {
                'numero_police': item['numero'],
                'client_nom': item['client__nom'],
                'details_url': reverse('police.details', args=[item['id']])
            }
            for item in results
        ]


