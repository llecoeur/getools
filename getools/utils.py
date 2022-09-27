import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.models import Config

def send_mail(subject, body, to_emails):
    """
        Envoie un email
        Utilise les configs suivantes :
        O365_SMTP
        O365_EMAIL
        O365_PASSWORD
        O365_FROM
        O365_PORT
    """
    O365_SMTP = Config.objects.get(key="O365_SMTP").str_val
    O365_PORT = Config.objects.get(key="O365_PORT").int_val
    O365_EMAIL = Config.objects.get(key="O365_EMAIL").str_val
    O365_PASSWORD = Config.objects.get(key="O365_PASSWORD").str_val
    O365_FROM = Config.objects.get(key="O365_FROM").str_val

    # Récupération de la configuration email


    s = smtplib.SMTP(host=O365_SMTP, port=O365_PORT)
    s.starttls()
    print(f"{O365_EMAIL} : '{O365_PASSWORD}'")
    s.login(O365_EMAIL,O365_PASSWORD)
    msg = MIMEMultipart()
    msg['From'] = O365_FROM
    msg['To'] = to_emails
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    s.send_message(msg)
    del msg
    s.quit()
    return 1