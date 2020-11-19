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


if __name__ == "__main__":
    """
        ABSENCE
        ACCIDENT
        CONGES PAYES
    """
    TarifGe.objects.filter(article__libelle__startswith="ABSENCE").delete()
    TarifGe.objects.filter(article__libelle__startswith="ACCIDENT").delete()
    TarifGe.objects.filter(article__libelle__startswith="CONGES PAYES").delete()
    TarifGe.objects.filter(mise_a_disposition__cloturee=True).delete()
    MiseADisposition.objects.filter(cloturee=True).delete()
    salarie_list = Salarie.objects.all()
    for salarie in salarie_list:
        if salarie.sorti:
            print(f"{salarie} est sorti")
            salarie.delete()

