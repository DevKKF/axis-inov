from django.core.mail import send_mail
from django.core.mail import EmailMessage

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
                        <p>L'équipe Inov</p>
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

def send_cron_state_mail(email, cron_name, frequency, state, message):
    
    subject = str(cron_name) + " | CRON TASK"
    message = f'''<!DOCTYPE html>
                    <html lang="fr">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>{subject}</title>
                    </head>
                    <body>
                       <p style="color:red">Ceci est une alerte système, ne repondez pas à ce message.</p>

                        <p>Tâche cron: {cron_name}, 
                        exécutée {frequency}</p>
                        
                        <p>État: <strong>{state}</strong><br>                        
                        {message}</p>                        
                        <p>Merci
                        <br>L'équipe Inov</p>
                    </body>
                    </html>
                '''
    send_mail(
        subject=subject,
        message='',
        html_message=message,
        from_email=None,
        recipient_list=[email],
        fail_silently=True,
    )

def send_demande_rembours_mail(email, context, file_paths):
    subject = 'Nouvelle demande de remboursement'
    message = f'''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Nouvelle demande de remboursement</title>
    </head>
    <body>
        <p>Bonjour,</p>
        <p>Vous avez une nouvelle demande de remboursement de {context['beneficiaire']}:</p>
        <ul>
            <li>Date de la prestation : {context['date_sinistre']}</li>
            <li>Acte : {context['acte']}</li>
            <li>Prestataire : {context['prestataire']}</li>
            <li>Montant : {context['montant_a_rembourser']}</li>
            <li>Mode de remboursement : {context['mode_remboursement']}</li>
            <li>Numéro de remboursement : {context['numero_remboursement']}</li>
            <li>Adhérent principal : {context['adherent_principal']}</li>
        </ul>
        <p>Documents attachés :</p>
        <ul>
            <li>Prescription médicale</li>
            <li>Facture normalisée</li>
            <li>Acquittée de laboratoire</li>
            <li>Autre document</li>
        </ul>
        <p>Équipe de Gestion des Remboursements</p>
        <p>Cordialement,</p>
    </body>
    </html>
    '''

    email_message = EmailMessage(
        subject=subject,
        body=message,
        to=[email],
    )
    email_message.content_subtype = "html"  # Rend le message au format HTML

    # Attacher les fichiers
    for file_path in file_paths:
        if file_path:  # Vérifie si le chemin du fichier n'est pas None ou vide
            email_message.attach_file(file_path)

    email_message.send(fail_silently=True)
