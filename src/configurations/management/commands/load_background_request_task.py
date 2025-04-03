from django.core.management.base import BaseCommand, CommandError

from configurations.helper_config import execute_query, send_notification_background_task_mail, \
    send_dev_notification_background_task_mail
from configurations.models import BackgroundQueryTask, CronLog
from shared.helpers import generer_qrcode_carte
from sinistre.helper_sinistre import exportation_en_excel_avec_style, exportation_en_excel_avec_style_background_task
from django.core.files import File
from datetime import datetime
import os
class Command(BaseCommand):
    help = 'Executer les requêtes en background.'

    def handle(self, *args, **options):
        tasks = BackgroundQueryTask.objects.filter(status="ENATT").all()
        print("task")
        print(tasks)
        print(len(tasks))
        send_dev_notification_background_task_mail("a.tissi@inov.africa", f'Demarrage Executions requêtes en background {len(tasks)} taches en attente')
        for task in tasks:
            try:
                # mise a jour du status de la tache
                task.status = "ENCOURS"
                task.save()

                queryset, header = execute_query(task.query)

                print("queryset")
                print(queryset)

                print("header")
                print(header)
                themp_name = datetime.now().strftime("%Y%m%d%H%M%S")
                fichier_excel = exportation_en_excel_avec_style_background_task(themp_name, header, queryset)

                with open(f'{themp_name}.xlsx', 'rb') as f:
                    task.file.save("DONNEES_REQUETE_PLATEFORME_V2.xlsx", File(f), save=False)

                #  Suppression du fichier excel thempo
                if os.path.exists(f'{themp_name}.xlsx'):
                    os.remove(f'{themp_name}.xlsx')
                # mise a jour du status de la tache
                task.status = "TERMINEE"
                task.error_message = ""
                task.save()

                send_notification_background_task_mail(task.created_by.email, task)

                CronLog.objects.create(action="export", table="background_query_task", description=f'requête {task.id} | {task.name} effectué avec succès pour {task.created_by.username}').save()

                self.stdout.write(self.style.SUCCESS(f'requête {task.id} | {task.name} effectué avec succès pour {task.created_by.username}'))
            except Exception as e:
                try:
                    # mise a jour du status de la tache
                    task.status = "ECHOUEE"
                    task.error_message = str(e)
                    task.save()
                except Exception as e:
                    print(e)
                # send_notification_background_task_mail("a.tissi@inov.africa", task)
                send_dev_notification_background_task_mail("a.tissi@inov.africa", str(e))

        self.stdout.write(self.style.SUCCESS('Executions requêtes terminé avec succès'))
        send_dev_notification_background_task_mail("a.tissi@inov.africa", 'Executions requêtes terminé avec succès')