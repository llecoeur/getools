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
    mois = 11
    # sal = Salarie.objects.get(code_erp="0000000001")
    sal = Salarie.objects.get(code_erp="0000000146")
    paie = sal.get_paie(annee, mois)
    """
    # sal = Salarie.objects.get(code_erp="0000000146")
    tarif_list = (
        TarifGe.objects
        .filter(mise_a_disposition__salarie=sal)
        .filter(mise_a_disposition__cloturee=False)
        .filter(article__facturation_uniquement=False)
        # .filter(saisie_activite_list__date_realisation__year=annee)
        # .filter(saisie_activite_list__date_realisation__month=mois)
        .exclude(article__rubrique_paie=None)
        # .annotate(quantites = Sum('saisie_activite_list__quantite'))
        # .exclude(quantites=None)
        # .exclude(quantites=0)
        .order_by("mise_a_disposition__adherent__raison_sociale")
        
    )
    
    print(tarif_list.query)
    for tarif in tarif_list:
        saisie_list = tarif.saisie_activite_list.filter(date_realisation__year=annee, date_realisation__month=mois).aggregate(quantites = Sum('quantite'))
        print(saisie_list)
        # for saisie in saisie_list:
        #     print(saisie.quantites)
        print(f"{tarif.id} - {tarif.mise_a_disposition.adherent} - {tarif.article.rubrique_paie.libelle}")
    """
    """
    tarif_list = (
        TarifGe.objects
        .filter(mise_a_disposition__salarie=sal)
        .filter(mise_a_disposition__cloturee=False)
        .filter(article__facturation_uniquement=False)
        .filter(saisie_activite_list__date_realisation__year=annee, saisie_activite_list__date_realisation__month=mois)
        # .filter(saisie_activite_list__date_realisation__year=annee)
        # .filter(saisie_activite_list__date_realisation__month=mois)
        .exclude(article__rubrique_paie=None)
        .annotate(quantites = Sum('saisie_activite_list__quantite'))
        .exclude(quantites=None)
        .exclude(quantites=0)
        .order_by("mise_a_disposition__adherent__raison_sociale")
        
    )
    for tarif in tarif_list:
        print(f"{tarif.id} - {tarif.mise_a_disposition.adherent} - {tarif.article.rubrique_paie.libelle} - {tarif.quantites}")
    """
    """
    # print(sal)
    paie = sal.get_paie(annee, mois)
    # print(paie)
    for salarie in salarie_list:
        sal = Salarie.objects.get(id=salarie['mise_a_disposition__salarie'])
        print(sal)
    """
    """
    c = CegidCloud()
    print(f"Tentative de récupération des articles ODATA : {settings.ODATA_ARTICLE_LIST_URL}")
    art = c.get_article_list()
    print(f"Réponse ODATA : {art}")
    print(f"Tentative de récupération des clients ODATA : {settings.ODATA_CLIENT_LIST_URL}")
    cli = c.get_client_list()
    print(f"Réponse ODATA : {cli}")
    print(f"Tentative de récupération des affaires ODATA : {settings.ODATA_AFFAIRE_LIST_URL}")
    aff = c.get_affaire_list()
    print(f"Réponse ODATA : {aff}")
    # r = c._get_api_data("https://cegid-data-service.cegid.com/CegidDataService/odata/90262451%20-%20GE%20PROGRESSIS__90262451_101/ARTICLES_PRESTA", debug=True)
    # print(r)
    """
    """
    loic = Salarie.objects.get(code_erp="0000000008")
    print(loic)
    pprint(loic.get_paie(2020,10))
    """
    # pprint(loic.get_paie(2020,10))
    """
    # Purge des saisies et des tarifs
    SaisieActivite.objects.all().delete()
    TarifGe.objects.all().delete()
    MiseADisposition.objects.all().delete()
    Article.objects.all().delete()
    Salarie.objects.all().delete()
    RubriquePaie.objects.all().delete()
    Adherent.objects.all().delete()
    Service.objects.all().delete()
    Poste.objects.all().delete()
    """
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
