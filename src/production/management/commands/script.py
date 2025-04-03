from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from configurations.helper_config import send_dev_notification_background_task_mail
from configurations.models import AlimentBaobab
from production.models import Carte, Aliment, AlimentFormule, MouvementAliment
from shared.helpers import generer_qrcode_carte


class Command(BaseCommand):
    help = 'Execution de script'

    def handle(self, *args, **options):
        try:
            mouvement1 = [151665,
             151666,
             151667,
             151668,
             151669,
             151670,
             151676,
             151677,
             151678,
             151679,
             151680,
             151681,
             151692,
             151693,
             151700,
             151743,
             151744,
             151745,
             151753,
             151754,
             151755,
             151756,
             151757,
             151758,
             151759,
             151760,
             151774,
             151775,
             151776,
             151777,
             151778,
             151781,
             151782,
             151783,
             151784,
             151785,
             151786,
             151787,
             151788,
             151792,
             151793,
             151794,
             151795,
             151796,
             151797,
             151807,
             151808,
             151809,
             151810,
             151811,
             151812,
             151813,
             151814,
             151824,
             151825,
             151826,
             151827,
             151828,
             151829,
             151830,
             151831,
             151843,
             151844,
             151845,
             151846,
             151847,
             151848,
             151849,
             151850,
             151851,
             151852,
             151855,
             151856,
             151857,
             151858,
             151859,
             151860,
             151861,
             151862,
             151863,
             151864,
             151865,
             151866,
             151867,
             151868,
             151869,
             151870,
             151871,
             151872,
             151873,
             151874,
             151875,
             151879,
             151880,
             151881,
             151882,
             151883,
             151884,
             151885,
             151886,
             151893,
             151894,
             151902,
             151903,
             151904,
             151905,
             151906,
             151907,
             151908,
             151909,
             151943,
             151944,
             151945,
             151946,
             151947,
             151948,
             151949,
             151955,
             151956,
             151957,
             151958,
             151967,
             151968,
             151969,
             151970,
             151971,
             151972,
             151973,
             151974,
             151975,
             151977,
             151978,
             151991,
             151992,
             151993,
             151994,
             151995,
             151996,
             151997,
             151999,
             152000,
             152063,
             154218,
             154254,
             154255,
             154274,
             154275,
             154649,
             155214]
            nbr = 0
            for mvt in mouvement1:
              mov = MouvementAliment.objects.filter(aliment_id=mvt).first()
              if not mov:
                 MouvementAliment.objects.create(
                     date_effet="2024-03-05",
                     aliment_id=mvt,
                     mouvement_id=9,
                     statut_validite="VALIDE",
                     statut_traitement='TRAITE',
                     police_id=900
                 )
                 nbr += 1
                 self.stdout.write(self.style.SUCCESS(f'Mouvement aliment_id {mvt} cree avec succès'))

            mouvement2 = [151739,
             151740,
             151779,
             151804,
             151853]

            for mvt2 in mouvement2:
              mov = MouvementAliment.objects.filter(aliment_id=mvt2).first()
              if not mov:
                 MouvementAliment.objects.create(
                     date_effet="2024-04-17",
                     aliment_id=mvt2,
                     mouvement_id=9,
                     statut_validite="VALIDE",
                     statut_traitement='TRAITE',
                     police_id=900
                 )
                 nbr += 1
                 self.stdout.write(self.style.SUCCESS(f'Mouvement aliment_id {mvt2} cree avec succès'))

            self.stdout.write(self.style.SUCCESS(f'Mouvement nbr {nbr} !'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))

