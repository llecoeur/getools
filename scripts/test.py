import os
import sys
sys.path.append('..')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "getools.settings")
import django
django.setup()
from datetime import datetime
import urllib.parse
import pyodbc 
from django.conf import settings
# from cegid.cegid_premise import session, Salarie, Tiers, Affaire, Remuneration, Article, TarifGe
from activite.models import Article, SaisieActivite, TarifGe, MiseADisposition, Salarie, RubriquePaie, Adherent, Service, Poste
from pprint import pprint
import requests
import json
from cegid.xrp_sprint import CegidCloud
from django.db.models import Q, Sum
from django.forms.models import model_to_dict
from tqdm import tqdm
from django.template.loader import render_to_string
from weasyprint import HTML
from activite.tasks import test, generate_releve_adherent
from sys import argv
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.encoding import smart_str


if __name__ == "__main__":

    email_template_name = "email_conge_accepte_all.txt"
    
    subject = f"Votre demande de congé a été acceptée"
    c = {
        "nom_prenom_salarie": "Salarié àèéï",
        "debut": "Date de début",
        "fin": "Date de fin",
    }

    from django.core.mail import EmailMultiAlternatives

    from_email, to = None, 'l.lecoeur@tempspartage.fr'
    text_content = 'Test de caractères accentués àö'
    html_content = '<h1>MESSAGE HTML</h1><BR /><p>Test de caractères accentués àö <strong>çç àà &eacute; </strong> message.</p>'

    html_content = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <title>Order received</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
</head>
<body style="margin: 0; padding: 0;">
  <table align="center" border="0" cellpadding="0" cellspacing="0" width="320" style="border: none; border-collapse: collapse; font-family:  Arial, sans-serif; font-size: 14px; line-height: 1.5;">
...
content
...
</table>
</body>
</html>


"""

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


    """email = str(render_to_string(email_template_name, c))
    print(email)
    ret = send_mail(
        subject,
        email,
        None,
        ["magic23@magic23.org"],
        fail_silently=False,
    )
    # print(f"email envoyé : {ret}, l.lecoeur@tempspartage.fr, {subject}")"""
    print(f"email envoyé : l.lecoeur@tempspartage.fr, {subject}")