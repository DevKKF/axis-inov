from django.core.management.base import BaseCommand

from sinistre.models import Sinistre, DossierSinistre


class Command(BaseCommand):
    help = 'Execution de mise à jour des date de soins des sinistres avec séance'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Commande exécutée !'))
        try:
            # Filter sinistres based on the given criteria
            sinistres = Sinistre.objects.filter(acte__option_seance=1, dossier_sinistre_id__isnull=False)

            # Get unique dossier_sinistre_ids
            dossier_ids = sinistres.values_list('dossier_sinistre_id', flat=True).distinct()

            nombre_update = 0
            nombre_update_new = 0

            # Retrieve all related dossiers sinistres
            dossiers_sinistres = DossierSinistre.objects.filter(id__in=dossier_ids)

            for dossier in dossiers_sinistres:
                # Get sinistres related to the current dossier
                sinistre_objects = sinistres.filter(dossier_sinistre_id=dossier.id)

                # Find the sinistre with the date_survenance set
                sinistre_with_date = sinistre_objects.filter(date_survenance__isnull=False).first()

                if sinistre_with_date:
                    date_survenance = sinistre_with_date.date_survenance
                    for sinistre in sinistre_objects:
                        if sinistre.date_survenance is None:
                            self.stdout.write(self.style.SUCCESS(f'Mise à jour du sinistre N° {sinistre.numero} avec la date de survenance {date_survenance}'))
                            sinistre.date_survenance = date_survenance
                            sinistre.observation = str(sinistre.observation) + ' - update date_survenance on 31102024' if sinistre.observation else ' - update date_survenance on 31102024'
                            sinistre.save()
                            nombre_update += 1

            self.stdout.write(self.style.SUCCESS(
                f'Sinistre(s) {nombre_update} modifié(s) ({nombre_update_new} nouveau(x)) / {dossiers_sinistres.count()} dossier(s) parcouru(s) avec succès !'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))