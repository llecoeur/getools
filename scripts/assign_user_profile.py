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
from geauth.models import User, UserProfile

"""
    Crée un profile pour chaque utilisateur qui n'en a pas
    Assigne un utilisateur Cegid pour chaque profil
"""

if __name__ == "__main__":
    user_list = User.objects.filter(profile=None)
    for user in user_list:
        print("Entrez code Cegid de {user} :")
        salarie_code = input()
        salarie = Salarie.objects.get(code_erp=salarie_code)
        profile = UserProfile()
        profile.salarie = salarie
        profile.user = user
        profile.save()


