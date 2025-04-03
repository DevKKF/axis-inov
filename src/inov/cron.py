import datetime
# import the logging library
import logging

from django.http import JsonResponse
from comptabilite.views import alert_consumption, create_periode_comptable
from django_dump_die.middleware import dd

from configurations.helper_config import send_notification_background_task_mail
from configurations.models import CronLog
from sinistre.helper_sinistre import load_backgroound_request_task

from sinistre.models import Sinistre

# Get an instance of a logger
logger = logging.getLogger(__name__)


def cron_all_once(request):
    dd("EXECUTION DES TACHES CRONS A LA SUITE ")


def cron_periode_comptable(request):
    data = create_periode_comptable()

    CronLog.objects.create(action="create", table="periode_comptable", description="Created accounting period succefully").save()
    return JsonResponse(data, safe=False)


def cron_backgroundrequesttask(request):
    CronLog.objects.create(action="export", table="background_query_task",
                           description="Background request task cron executed").save()
    send_notification_background_task_mail('a.tissi@inov.africa', None)
    # load_backgroound_request_task()
    # return JsonResponse({"message": "Background request task cron executed"}, safe=False)


def cron_alerte_consommation():
    data = alert_consumption()

    CronLog.objects.create(action="alert_mail", table="noname",
                           description="Alerte mail suivi de consommation garant").save()

    return JsonResponse(data, safe=False)


def cron_import_sinistre():
    data = import_sinistre_manuellement_cron()

    CronLog.objects.create(action="cron_sinistre", table="noname",
                           description="cron_sinistre").save()

    return JsonResponse(data, safe=False)
