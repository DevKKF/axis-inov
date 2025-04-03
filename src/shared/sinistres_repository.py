from datetime import date

from django.http import JsonResponse
import json
import requests
import logging

logger = logging.getLogger(__name__)
# settings.py

# Define base URLs for different environments
BASE_URLS = {
    'default': 'https://inov.veos.iga.fr',
    'inov2': 'https://inov2.preprod-veos.iga.fr',
    'recSante': 'https://inov.rec-veos.iga.fr',
    'prod': 'https://inov.prod-veos.iga.fr/rs/rsExtranet2',
}
# utils.py

from django.conf import settings

def base_url(base='default'):
    """
    Get the base URL based on the provided environment base name.
    """
    #return settings.BASE_URLS.get(base, settings.BASE_URLS['default']) #commented

    return BASE_URLS.get('prod')



def post(self, request, *args, **kwargs):
    token = request.POST.get('token')
    vehicule = self.get_vehicule(token, request.POST)
    police = self.get_police(token, request.POST)
    domage = self.get_dommage(request.POST)
    ligne_domage = self.get_ligne_dommage(request.POST)

    exist_sinistre = self.get_sinistre_id(token, request.user, request.POST.get('num_sinistre'))

    if exist_sinistre:
        return self.response("Ce numéro de sinistre existe déjà", 409)
    else:
        if not domage:
            return self.response("code_dommage de véhicule invalide", 404)

        if not ligne_domage:
            return self.response("code_detail_dommage de véhicule invalide", 404)

        if not police:
            return self.response("Numéro de police invalide", 404)

        if not vehicule:
            return self.response("Numéro de parc ou immat invalide", 404)
        else:
            date_eff_pol = convert_date(police.get('dtEffet'))
            date_ech_pol = convert_date(police.get('prochaineEch'))
            date_surv = convert_date(request.POST.get('date_survenance'))

            if date_eff_pol and date_ech_pol and date_surv:
                dats = date_surv.timestamp()
                datech = date_ech_pol.timestamp()
                dateff = vehicule.get('DATE_VEH').timestamp()

                if dats >= dateff and dats <= datech:
                    param = {
                        "id": "",
                        "numCie": "",
                        "numCbt": "",
                        "numSoc": police.get('numSoc', ""),
                        "idPol": police.get('idPol'),
                        "idElem": vehicule.get('ID_VEH'),
                        "typeElem": "VEHICULE",
                        "refRisque": vehicule.get('IMMAT_VEH'),
                        "mouvement": "OUVSIN",
                        "motif": "DSINATT",
                        "numAuto": "O",
                        "numAutoCie": "",
                        "type": request.POST.get('code_type'),
                        "txResp": 1,
                        "circonstance": request.POST.get('code_circonstance'),
                        "causeCirconstance": request.POST.get('cause_circonstance'),
                        "userCalendrier": "",
                        "dateOuverture": date.today().strftime('%d/%m/%Y'),
                        "dateSurvenance": request.POST.get('date_survenance'),
                        "heureSurvenance": request.POST.get('heure_survenance'),
                        "dateDeclaration": date.today().strftime('%d/%m/%Y'),
                        "codeProduit": "FLAU",
                        "codeCie": "",
                        "dommages": f"{domage.get('designation')} ({ligne_domage})",
                        "risque1": "",
                        "risque2": request.POST.get('conducteur'),
                        "risque3": "",
                        "risque4": "",
                        "risque5": request.POST.get('lieu_sinistre'),
                        "libMvt": "Ouverture sinistre",
                        "libMotif": "Déclaration sinistre en attente",
                        "libCirconstance": "",
                        "loadAssure": "1",
                        "listInfos": [
                            {
                                "key": "PARAPH1",
                                "value": request.POST.get('cause_circonstance'),
                            },
                            {
                                "key": "REF_EXPERT",
                                "value": request.POST.get('num_sinistre'),
                            },
                            {
                                "key": "NCIE_SIN",
                                "value": request.POST.get('num_sinistre_cie')
                            },
                            {
                                "key": "NUMSINCLT",
                                "value": request.POST.get('num_sinistre_client', "")
                            }
                        ],
                        "listPer": [],
                        "historique": [
                            {
                                "idHistorique": "",
                                "dtHistorique": date.today().strftime('%d/%m/%Y'),
                                "mvtHistorique": "OUVSIN",
                                "motifHistorique": "DSINATT"
                            }
                        ]
                    }

                    logger.info('Sinistre::store', {'token': token, 'param': param, 'request-user': request.user})
                    return self.save_data(token, param, request.user)
                else:
                    return JsonResponse({'message': "La date de survenance est inférieure à la date d'effet"}, status=400)

            return JsonResponse({'message': "La date de survenance est incorrecte"}, status=404)


def update(self, request, *args, **kwargs):
    token = request.POST.get('token')
    sinistre = self.get_sinistre_by_id(token, request.user, kwargs['id_sin'])
    if sinistre:
        sinistre['motif'] = request.POST.get('code_motif')
        logger.info('Sinistre::update', {'sinistre': sinistre, 'token': token, 'request-user': request.user, 'id_sin': kwargs['id_sin']})
        return self.save_data(token, sinistre, request.user, kwargs['id_sin'])
    else:
        return self.response("Oups une erreur s'est produite. veuillez réessayer plus tard", 404)

def get_sinistre_id(self, token, user, num_sinistre):
    sinistre_response = None
    param = [
        {
            "name": "WS_GET_INFO_SIN",
            "params": {
                "REF_EXPERT": num_sinistre
            }
        }
    ]

    try:
        headers = {'Authorization': 'Bearer ' + token}
        response = requests.post(f"{base_url(user.base)}/rs/rsExtranet2/boBy/list", json={'requests': param}, headers=headers)
        ws_response = response.json()
        sinistre_response = ws_response['responses'][0]['beans'][0]['ID_SIN']
    except Exception as e:
        return None

    return sinistre_response

def get_vehicule(self, token, request_data):
    vehicule_response = None
    param = [
        {
            "name": "WS_GET_INFO_VEHICULE",
            "params": {
                "NUM_PARC": request_data.get('num_parc'),
                "NUMPOL": request_data.get('num_police'),
                "IMMAT_VEH": request_data.get('immat_veh')
            }
        }
    ]

    error_data = {
        'user': request_data.user,
        'param': json.dumps(param),
        'url': f"{base_url(request_data.user.base)}/rs/rsExtranet2/boBy/list"
    }

    try:
        headers = {'Authorization': 'Bearer ' + token}
        response = requests.post(f"{base_url(request_data.user.base)}/rs/rsExtranet2/boBy/list", json={'requests': param}, headers=headers)
        ws_response = response.json()
        vehicule_response = ws_response['responses'][0]['beans'][0]
    except Exception as e:
        error_data['error'] = str(e)
        self.exception_mail_repository.send_mail_to_admin(error_data)
        return None

    return vehicule_response

def get_dommage(self, request_data):
    dommage = Dommage.objects.filter(code=request_data.get('code_dommage')).first()
    if dommage:
        return dommage.to_dict()
    return None

def get_ligne_dommage(self, request_data):
    dommages = request_data.get('code_detail_dommage')
    dom_array = list(set(dommages.split(";")))
    lignes_dommage = LigneDommage.objects.filter(id__in=dom_array)

    if lignes_dommage.count() > 0:
        thmp = [value['description'] for value in lignes_dommage.values('description')]
        return "; ".join(thmp)
    return None

def get_police(self, token, request_data):
    police_response = None
    param = [
        {
            "name": "WS_GET_INFO_POLICE",
            "params": {
                "NUMPOL": request_data.get('num_police')
            }
        }
    ]

    error_data = {
        'user': request_data.user,
        'param': json.dumps(param),
        'url': f"{base_url(request_data.user.base)}/rs/rsExtranet2/boBy/list"
    }

    try:
        headers = {'Authorization': 'Bearer ' + token}
        response = requests.post(f"{base_url(request_data.user.base)}/rs/rsExtranet2/boBy/list", json={'requests': param}, headers=headers)
        ws_response = response.json()
        police_response = ws_response['responses'][0]['beans'][0]
    except Exception as e:
        error_data['error'] = str(e)
        self.exception_mail_repository.send_mail_to_admin(error_data)
        return None

    return police_response

def get_sinistre_by_id(self, token, user, id):
    error_data = {
        'user': user,
        'param': id,
        'url': f"{base_url(user.base)}/rs/rsExtranet2/sinistre/{id}"
    }

    sinistre_response = None
    try:
        headers = {'Authorization': 'Bearer ' + token}
        response = requests.get(f"{base_url(user.base)}/rs/rsExtranet2/sinistre/{id}", headers=headers)
        sinistre_response = response.json()
    except Exception as e:
        error_data['error'] = str(e)
        self.exception_mail_repository.send_mail_to_admin(error_data)
        return None

    return sinistre_response

def save_data(self, token, param, user, id=None):
    error_data = {
        'user': user,
        'param': json.dumps(param),
        'url': f"{base_url(user.base)}/rs/rsExtranet2/sinistre"
    }

    try:
        headers = {'Authorization': 'Bearer ' + token}
        message = None

        response = requests.post(f"{base_url(user.base)}/rs/rsExtranet2/sinistre", json=param, headers=headers)
        message = "Sinistre déclaré avec succès"

        return self.response(message)
    except requests.RequestException as e:
        error_data['error'] = str(e)
        self.exception_mail_repository.send_mail_to_admin(error_data)
        return self.response("Oups une erreur s'est produite. veuillez réessayer plus tard", 500)
    except Exception as e:
        error_data['error'] = str(e)
        self.exception_mail_repository.send_mail_to_admin(error_data)
        return self.response("Oups une erreur s'est produite. veuillez réessayer plus tard", 500)



def response(self, message, code=200):
    if code == 200:
        return JsonResponse({'message': message}, status=code)
    else:
        return JsonResponse({'error': message}, status=code)
