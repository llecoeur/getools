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
from activite.models import Article, SaisieActivite, TarifGe
from pprint import pprint
import requests
import json
from cegid.xrp_sprint import CegidCloud


if __name__ == "__main__":


    # Purge des saisies et des tarifs
    SaisieActivite.objects.all().delete()
    TarifGe.objects.all().delete()

    """
    cegid = CegidCloud()
    pprint(cegid.get_motif_absence_list())
    """
    """
    print(len(cegid.get_odata_affaire_list()))

    salarie_list = session.query(Salarie).all()
    for salarie in salarie_list:
        print(salarie)
    """

    """
    adherent_list = session.query(Tiers).filter(Tiers.nature_auxiliaire == 'CLI')
    for adherent in adherent_list:
        print(adherent)
    """
    """
    affaire_list = session.query(Affaire).filter(Affaire.code_1 == 'MAD')
    for affaire in affaire_list:
        print("{} {}".format(affaire.salarie, affaire.adherent))
    """
    """
    rub_list = session.query(Remuneration).all()
    for rub in rub_list:
        print(rub)
    """
    """
    art_list = session.query(Article).all()
    for art in art_list:
        print("{} - {}".format(art, art.rubrique_paie))
    """
    """
    article_list = Article.objects.all()
    cpt = 1
    for article in article_list:
        article.ordre = cpt
        cpt = cpt + 1
        article.save()
    """

    """
    url = settings.XRP_PRINT_API_BASE_URL + settings.XRP_SPRINT_FOLDER_TRADE_FINANCE + "/users/getCurrentUserData"
    response = requests.get(url, auth=settings.XRP_PRINT_AUTH)
    print(response.text)
    """
    """
    url = settings.XRP_PRINT_API_BASE_URL + settings.XRP_SPRINT_FOLDER_TRADE_FINANCE + "/customers/list?$skip=0"
    response = requests.get(url, auth=settings.XRP_PRINT_AUTH, headers={"Accept": "application/json"})
    js = json.loads(response.text)
    print(js['NextPageLink'])
    print(js)
    """


    """
    url = "https://v11-y2mts-ondemand.cegid.com/CegidMTSWebAPI/api/v1/90262451%20-%20GE%20PROGRESSIS__90262451_101/users/getCurrentUserData"

    payload = {}
    headers = {
    'Authorization': 'Basic Z2Vwcm9ncmVzc2lzXHZzdG9sbDozQVw9ZHFkTSRvOig=',
    'Cookie': 'LdapAuth=cY2IQoBeihqkQiRDFynzvZkY2fQsE4MIdD6jrwvG0jo7VSev3nFAutGkPBOEyvEWAenbodmdDGnW155uQl+tsztKlb7JFyV9Pc4O4BSWf1E='
    }

    response = requests.request("GET", url, headers=headers, data = payload)

    print(response.text.encode('utf8'))

    """
