from django.core.files.storage import FileSystemStorage
from django.db import connection
from django.core.files.base import File
from django.http import HttpResponse

from configurations.models import BackgroundQueryTask
from django.core.mail import send_mail
from configurations.models import BackgroundQueryTask, CronLog
from django.conf import settings
import pyotp
import datetime


def verify_sql_query(query):
    """
    Verify the SQL query
    """
    sql_tags_eception = ["INSERT ", "insert ", "UPDATE ", "update ", "DELETE ", "delete ", "DROP ", "drop ", "TRUNCATE ",
                         "truncate ", "ALTER ", "alter ", "CREATE ", "create ", "RENAME ", "rename ", "REPLACE ", "replace ",
                         "GRANT ", "grant ", "REVOKE ", "revoke ", "LOCK ", "lock ", "UNLOCK ", "unlock ", "COMMIT ", "commit ",
                         "ROLLBACK ", "rollback ", "SAVEPOINT ", "savepoint ", "SET ", "set ", "START ", "start ", "STOP ",
                         "stop ", "KILL ", "kill ", "SHUTDOWN ", "shutdown ", "SHOW ", "show ", "DESCRIBE ", "describe ",
                         "EXPLAIN ", "explain ", "USE ", "use ", "RESET ", "reset ", "PURGE ", "purge ", "FLUSH ",
                         "flush ", "ANALYZE ", "analyze ", "OPTIMIZE ", "optimize ", "REPAIR ", "repair ", "RESTORE ",
                         "restore ", "BACKUP ", "backup ", "SOURCE ", "source ", "LOAD ", "load ", "HANDLER ", "handler ",
                         "CALL ", "call ", "DO ", "do ", "PREPARE ", "prepare ", "EXECUTE ", "execute ", "DEALLOCATE ",
                         "deallocate ",
                         "HELP ", "help ", "CACHE ", "cache ", "INSTALL ", "install ", "UNINSTALL ", "uninstall "]

    for tag in sql_tags_eception:
        if tag in query:
            raise Exception(f"Invalid SQL query. The tag '{tag}' is not allowed in the query.")


def execute_query(db_query):
    with connection.cursor() as cursor:
        cursor.execute(db_query)
        columns = [col[0] for col in cursor.description]
        data = cursor.fetchall()
        # print(data)
    return data, columns

def execute_query_with_params(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
    return data, columns

def create_query_background_task(name,query,request):
    try:
        task = BackgroundQueryTask(
            name=name,
            query=query,
            created_by=request.user)
        task.save()
        request.session['task_id'] = task.id
        return task.id
    except Exception as e:
        print(e)
        return None


def send_notification_background_task_mail(email, task):
    if email :
        subject = 'INOV | Requête en arrière-plan notification'
        message = f'''<!DOCTYPE html>
                        <html lang="fr">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>INOV | Requête en arrière-plan</title>
                        </head>
                        <body>
                           <p style="color:red">Si cette action n'a pas été initiée par vous, veuillez ignorer ce message.</p>
    
                            <p>Bonjour,</p>
                            <p>Le traitement de votre requête vient d'être achevé. Veuillez vous connecter à votre interface "Requête en arrière-plan" sur l'application santé pour son extraction.</p>
    
                            <p>Cordialement,</p>
                        </body>
                        </html>
                    '''
        send_mail(
            subject=subject,
            message="",
            html_message=message,
            from_email=None,
            # auth_user=bureau.email_smtp,
            # auth_password=bureau.mot_de_passe_smtp,
            recipient_list=[email],
            fail_silently=True,
        )


def send_dev_notification_background_task_mail(email, notification):
    if email:
        subject = 'INOV | Requête en arrière-plan notification'
        message = f'''<!DOCTYPE html>
                        <html lang="fr">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>INOV | Requête en arrière-plan</title>
                        </head>
                        <body>
                           <p style="color:red">Si cette action n'a pas été initiée par vous, veuillez ignorer ce message.</p>

                            <p>Bonjour,</p>
                            <p>{notification}</p>

                            <p>Cordialement,</p>
                        </body>
                        </html>
                    '''
        send_mail(
            subject=subject,
            message="",
            html_message=message,
            from_email=None,
            # auth_user=bureau.email_smtp,
            # auth_password=bureau.mot_de_passe_smtp,
            recipient_list=[email],
            fail_silently=True,
        )


def send_verification_code(request, email):
    if 'verification_code_sent' not in request.session:

        # code = random_number_token(length=6)

        # generate the code
        hotp = pyotp.HOTP(settings.OTP_SECRET_KEY, digits=6)
        code_verification = int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        code = hotp.at(code_verification)

        request.session['verification_code'] = code
        request.session['email'] = email

        send_otp_mail(email, code)
        request.session['verification_code_sent'] = True

        return code
    else:
        return None


#########################################

def send_otp_mail(email, otp):
    subject = 'Code de Vérification'
    message = f'''<!DOCTYPE html>
                    <html lang="fr">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Code de Vérification</title>
                    </head>
                    <body>
                       <p style="color:red">Si cette action n'a pas été initiée par vous, veuillez ignorer ce message.</p>

                        <p>Bonjour,</p>
                        <p>Veuillez trouver ci-dessous votre code de vérification unique :</p>

                        <p>Code de vérification : <strong>{otp}</strong></p>

                        <p>Ce code est valable pour 5 minutes.</p>
                        <p>Cordialement,</p>
                    </body>
                    </html>
                '''
    send_mail(
        subject=subject,
        message="",
        html_message=message,
        from_email=None,
        recipient_list=[email],
        fail_silently=True,
    )

