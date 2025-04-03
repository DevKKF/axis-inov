from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from configurations.models import AlimentMatricule
from production.models import Aliment


class Command(BaseCommand):
    help = 'Execution de mise à jour du matricule des aliments'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'Commande exécutée !'))
        try:
            
            aliments_matricules = AlimentMatricule.objects.filter(STATUT_IMPORT=False)

            nombre_import = 0
            nombre_update = 0

            for aliment_matricule in aliments_matricules:
                aliment = Aliment.objects.filter(veos_code_aliment=aliment_matricule.ID_ADH).first()
                
                if aliment:
                    
                    if aliment.matricule_employe is None or aliment.matricule_employe == "":
                        aliment.matricule_employe = aliment_matricule.MATRICULE
                        # print(aliment.matricule_employe+" then "+aliment_matricule.MATRICULE)
                        aliment.save()
                        nombre_update += 1
                    
                    aliment_matricule.STATUT_IMPORT = True
                    aliment_matricule.save()
                    nombre_import += 1

            self.stdout.write(self.style.SUCCESS(f'Aliment(s) {nombre_update} modifié(s) / Matricule(s) {nombre_import} importé(s) avec succès !'))
        except Exception as e:
            self.stdout.write(self.style.FAILURE(str(e)))
