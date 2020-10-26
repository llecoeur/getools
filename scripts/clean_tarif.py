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
    tarifs_list = TarifGe.objects.filter(mise_a_disposition__cloturee=True)

    for tarif in tarifs_list:
        print(f"suppression du tarif Mise a dispo {tarif.mise_a_disposition.salarie} - {tarif.mise_a_disposition.adherent} - {tarif.article}")
        tarif.delete()

    print(f"Tarifs supprimés : {len(tarifs_list)} / {len(TarifGe.objects.all())}")
