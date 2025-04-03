from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from configurations.helper_config import send_dev_notification_background_task_mail
from production.models import Carte
from shared.helpers import generer_qrcode_carte


class Command(BaseCommand):
    help = 'Generer les qrcodes des cartes'

    def handle(self, *args, **options):
        try:
            cartes = Carte.objects.filter(Q(qrcode_file__isnull=True) | Q(qrcode_file=""))
            #if len(cartes) == 0:
            #    cartes = Carte.objects.filter(qrcode_file='')

            send_dev_notification_background_task_mail("a.tissi@olea.africa",
                                                       f'Demarrage Executions génération QRCODE en background {len(cartes)} générations en attente')

            print("cartes")
            print(cartes)
            print(len(cartes))
            for carte in cartes:
                # générer le qrcode
                qrcode_file = generer_qrcode_carte(carte.numero)
                print("qrcode_img")
                # print(qrcode_img)
                carte.qrcode_file.save(f'qrcode_image_{carte.numero}.png', qrcode_file)
                carte.save()
                info = "New"
                self.stdout.write(self.style.SUCCESS(f'Generation effectué avec succès pour {carte.numero}'))

            self.stdout.write(self.style.SUCCESS('Generation terminé avec succès'))
            send_dev_notification_background_task_mail("a.tissi@olea.africa",
                                                       f'Generation terminé avec succès')
        except Exception as e:
            self.stdout.write(self.style.FAILURE(str(e)))
            send_dev_notification_background_task_mail("a.tissi@olea.africa",
                                                       str(e))
