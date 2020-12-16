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


if __name__ == "__main__":

    annee = 2020
    mois = 10
    adherent = Adherent.objects.get(raison_sociale="PROGRESSIS")
    print(adherent.total_heures_mois(annee, mois))
    adherent = Adherent.objects.get(raison_sociale="MANUPLAST")
    print(adherent.total_heures_mois(annee, mois))