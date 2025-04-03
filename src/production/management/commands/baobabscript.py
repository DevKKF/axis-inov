from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from configurations.helper_config import send_dev_notification_background_task_mail
from configurations.models import AlimentBaobab
from production.models import Carte, Aliment, AlimentFormule
from shared.helpers import generer_qrcode_carte


class Command(BaseCommand):
    help = 'Execution de script pour BAOBAB'

    def handle(self, *args, **options):
        try:
            aliments_baobab = AlimentBaobab.objects.filter(formule_id=5127, statut_traitement=0)
            print("aliments_baobab")
            print(len(aliments_baobab))
            nbr_deuxieme = 0
            nbr_troisieme = 0
            for aliment_baobab in aliments_baobab:
                aliment = Aliment.objects.filter(veos_code_aliment=aliment_baobab.num_benef).first()
                aliment_formule = AlimentFormule.objects.filter(aliment_id=aliment.id).order_by('id')
                print("aliment_formule")
                print(len(aliment_formule))
                if len(aliment_formule) == 3:

                    if aliment_formule[0].formule_id == 4164 and aliment_formule[1].formule_id == 5126 and aliment_formule[2].formule_id == 4173:

                        # Traitement pour les bénéficiaires ayant les formules 5127 et 4182

                        aliment_formule[1].date_debut = "2024-01-01"
                        aliment_formule[1].date_fin = "2024-01-01"
                        aliment_formule[1].observation = "TRAITEMENT BAOBAB 3 LIGNES"
                        aliment_formule[1].save()

                        aliment_formule[2].date_debut = "2024-01-01"
                        aliment_formule[2].date_fin = "2024-01-01"
                        aliment_formule[2].observation = "TRAITEMENT BAOBAB 3 LIGNES"
                        aliment_formule[2].statut_validite = "SUPPRIME"
                        aliment_formule[2].statut = "INACTIF"
                        aliment_formule[2].save()

                        # Ajout de la 4ème formule
                        new_formule_aliment = AlimentFormule.objects.create(
                            aliment_id=aliment.id,
                            formule_id=5127,
                            statut="ACTIF",
                            statut_validite="VALIDE",
                            date_debut="2024-01-01",
                            observation="TRAITEMENT BAOBAB 3 LIGNES"
                        )

                        aliment_baobab.statut_traitement = 1
                        aliment_baobab.save()
                        nbr_troisieme += 1
                        self.stdout.write(self.style.SUCCESS(f'Aliment {aliment_baobab.num_benef} modifié avec succès'))
                elif len(aliment_formule) == 2:
                    nbr_deuxieme += 1

            self.stdout.write(self.style.SUCCESS(f'Aliment nbr_deuxieme {nbr_deuxieme} ! nbr_troisieme {nbr_troisieme} '))

        except Exception as e:
            self.stdout.write(self.style.FAILURE(str(e)))

