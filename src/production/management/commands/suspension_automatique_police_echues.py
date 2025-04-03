import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone

from configurations.models import AlimentMatricule
from production.models import Aliment, Police


class Command(BaseCommand):
    help = 'Execution de la suspension automatique des polices à échéance'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'Commande exécutée !'))
        #try:

        today = datetime.datetime.now(tz=timezone.utc)
        polices = Police.objects.filter(date_fin_effet__lte=today)

        nombre_import = 0
        nombre_update = 0

        for police in polices:

            #police.statut = "ECHU"
            #police.save()
            nombre_import += 1

        self.stdout.write(self.style.SUCCESS(f'Import de {nombre_import} police(s) effectué avec succès !'))
        #except Exception as e:
        #    self.stdout.write(self.style.FAILURE(str(e)))
