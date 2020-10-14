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
from activite.models import Article, Salarie, RubriquePaie, Adherent, Service, Poste, FamilleArticle, MiseADisposition, SaisieActivite
from pprint import pprint
import requests
import json
from cegid.xrp_sprint import CegidCloud


if __name__ == "__main__":


    # Effacement des activités
    SaisieActivite.objects.all().delete()