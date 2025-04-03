from django.core.management.base import BaseCommand, CommandError

from configurations.helper_config import execute_query, send_notification_background_task_mail
from configurations.models import BackgroundQueryTask, CronLog
from shared.helpers import generer_qrcode_carte
from sinistre.helper_sinistre import exportation_en_excel_avec_style, exportation_en_excel_avec_style_background_task
from django.core.files import File
from datetime import datetime
import os
class Command(BaseCommand):
    help = 'Executer les requêtes en background.'

    def handle(self, *args, **options):
        send_notification_background_task_mail('a.tissi@inov.africa', None)