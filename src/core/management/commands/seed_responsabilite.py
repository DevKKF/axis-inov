from django.core.management.base import BaseCommand
from configurations.models import Responsabilite  # adapte ce chemin à ton projet

class Command(BaseCommand):
    help = 'Seed initial data for Responsabilite'

    def handle(self, *args, **kwargs):
        data = [
            {"libelle": "Indéterminé", "taux_responsabilite": 0, "statut": True},
            {"libelle": "0%", "taux_responsabilite": 0, "statut": True},
            {"libelle": "50%", "taux_responsabilite": 50, "statut": True},
            {"libelle": "100%", "taux_responsabilite": 100, "statut": True},
            {"libelle": "Contestable", "taux_responsabilite": 0, "statut": True},
        ]

        for item in data:
            obj, created = Responsabilite.objects.get_or_create(
                libelle=item["libelle"],
                taux_responsabilite=item["taux_responsabilite"],
                defaults={"statut": item["statut"]}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"{item['libelle']} ajouté avec succès."))
            else:
                self.stdout.write(self.style.WARNING(f"{item['libelle']} existe déjà."))
