from django.core.management.base import BaseCommand

from shared.helpers import recalcule_montant_refacture_compagnie_et_client
from sinistre.models import Sinistre


class Command(BaseCommand):
    help = 'Execution de mise à jour des montants à refacture au garants et aux clients'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'Commande exécutée !'))
        try:
            sinistres = Sinistre.objects.filter(dossier_sinistre_id__isnull=False, recalcule_mt_refact_garant_client=False, type_prefinancement_id=1) #
            nombre_update = 0
            for sinistre in sinistres:
                self.stdout.write(self.style.SUCCESS(f'Sinistre ' + str(sinistre.numero) + " en cours de recalcule"))

                recalcule_montant_refacture_compagnie_et_client(sinistre)
                nombre_update += 1

            self.stdout.write(self.style.SUCCESS(f'Sinistre(s) {nombre_update} modifié(s) / {sinistres.count()} parcouru(s) avec succès !'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
