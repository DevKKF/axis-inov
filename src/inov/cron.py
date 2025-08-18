import datetime
# import the logging library
import logging

from django.http import JsonResponse
from comptabilite.views import alert_consumption, create_periode_comptable
from django_dump_die.middleware import dd

from configurations.helper_config import send_notification_background_task_mail

from sinistre.models import Sinistre

# Get an instance of a logger
logger = logging.getLogger(__name__)


def cron_all_once(request):
    dd("EXECUTION DES TACHES CRONS A LA SUITE ")


def cron_periode_comptable(request):
    data = create_periode_comptable()

    return JsonResponse(data, safe=False)


def cron_backgroundrequesttask(request):
    send_notification_background_task_mail('a.tissi@inov.com', None)


def cron_alerte_consommation():
    data = alert_consumption()

    return JsonResponse(data, safe=False)


def cron_import_sinistre():
    data = import_sinistre_manuellement_cron()

    return JsonResponse(data, safe=False)
