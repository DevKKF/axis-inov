from django.core.management.base import BaseCommand
from configurations.models import TypeRecours  # adapte ce chemin si besoin

class Command(BaseCommand):
    help = 'Seed initial data for TypeRecours'

    def handle(self, *args, **kwargs):
        data = [
            {"code": "R001", "libelle": "Recours contre un tiers responsable"},
            {"code": "R002", "libelle": "Recours entre assureurs"},
            {"code": "R003", "libelle": "Recours contre l’assuré"},
            {"code": "R004", "libelle": "Recours judiciaire"},
            {"code": "R005", "libelle": "Recours en garantie"},
            {"code": "R006", "libelle": "Recours amiable / expertise"},
        ]

        for item in data:
            obj, created = TypeRecours.objects.get_or_create(
                code=item["code"],
                defaults={"libelle": item["libelle"]}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"{item['libelle']} ajouté avec succès."))
            else:
                self.stdout.write(self.style.WARNING(f"{item['libelle']} existe déjà."))
