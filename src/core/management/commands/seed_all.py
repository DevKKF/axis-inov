from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Execute tous les seeders'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING("⚙️  Démarrage des seeders..."))

        seeders = [
            'seed_responsabilite',
            'seed_mouvement',
            'seed_motif',
            #'',
            #'',
        ]

        for seeder in seeders:
            self.stdout.write(self.style.NOTICE(f"🔄 Exécution de {seeder}..."))
            call_command(seeder)

        self.stdout.write(self.style.SUCCESS("✅  Tous les seeders ont été exécutés avec succès !"))
