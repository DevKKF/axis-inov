from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from configurations.helper_config import send_dev_notification_background_task_mail
from configurations.models import AlimentBaobab
from production.models import Carte, Aliment, AlimentFormule, MouvementAliment, Quittance, ApporteurPolice
from shared.enum import StatutValidite
from shared.helpers import generer_qrcode_carte


class Command(BaseCommand):
    help = 'Execution de script de synchronisation apporteur'

    def handle(self, *args, **options):
        try:
            # Recuperation des quittances tous
            quittances = Quittance.objects.all()
            nbr = 0
            for quittance in quittances:
                # recuperation de l'apporteur police lie a la police de la quittance
                apporteur_police = ApporteurPolice.objects.filter(police_id=quittance.police_id, statut_validite=StatutValidite.VALIDE).first()


                # Verification si l'apporteur police existe
                if apporteur_police:
                    self.stdout.write(self.style.SUCCESS(f'Quittance {quittance.id} | apporteur {apporteur_police}'))
                    self.stdout.write(self.style.SUCCESS(f'Quittance {quittance.id} | commission_intermediaires {quittance.commission_intermediaires}'))

                    base_calcul = apporteur_police.base_calcul

                    # Verification si la commission_intermediaires est egale a 0
                    if quittance.commission_intermediaires ==0:

                        self.stdout.write(self.style.SUCCESS(f'Quittance {quittance.id} | nature_quittance_id {quittance.nature_quittance_id}'))
                        # montant_base_calcule = quittance.commission_courtage
                        if base_calcul.code == 'PRIME_HT':
                           montant_base_calcule= quittance.prime_ht
                        elif base_calcul.code == 'COM_COURT':
                            montant_base_calcule = quittance.commission_courtage
                        elif base_calcul.code == 'COM_GEST':
                            montant_base_calcule = quittance.commission_gestion
                        elif base_calcul.code == 'Com Total':
                            montant_base_calcule = quittance.commission_gestion + quittance.commission_courtage
                        else:
                            montant_base_calcule = quittance.commission_courtage


                        # Verification si la nature quittance est comptant id 1
                        if quittance.nature_quittance_id == 1:
                            self.stdout.write(self.style.SUCCESS(f'Quittance {quittance.id} | taux_com_affaire_nouvelle {apporteur_police.taux_com_affaire_nouvelle} | montant_base_calcule {montant_base_calcule}'))
                            quittance.commission_intermediaires = (apporteur_police.taux_com_affaire_nouvelle * montant_base_calcule)/100
                            quittance.observation = f'Calcule de retro apporteur par script effectué le {datetime.now()}'
                            nbr += 1
                        # Verification si la nature quittance est terme id 2
                        elif quittance.nature_quittance_id == 2:
                            self.stdout.write(self.style.SUCCESS(f'Quittance {quittance.id} | taux_com_affaire_nouvelle {apporteur_police.taux_com_renouvellement} | montant_base_calcule {montant_base_calcule}'))
                            quittance.commission_intermediaires = (apporteur_police.taux_com_renouvellement * montant_base_calcule)/100
                            quittance.observation = f'Calcule de retro apporteur par script effectué le {datetime.now()}'
                            nbr += 1

                        # Savegade de la quittance
                        self.stdout.write(self.style.SUCCESS(f'Quittance {quittance.id} | commission_intermediaires {quittance.commission_intermediaires}'))
                        self.stdout.write(self.style.SUCCESS(f'Quittance {quittance.id} modifié avec succès'))
                        quittance.save()

            self.stdout.write(self.style.SUCCESS(f'Quittance nbr {nbr} !'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))

