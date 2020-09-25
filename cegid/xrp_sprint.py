import requests
import json
from django.conf import settings
from pprint import pprint
from time import sleep

"""
    Classe XRP Print permettant de se connecter a l'API Cegid pour la lecture et l'écriture d'infos dans l'ERP.

    Doc :

    Trade, Services, CRM : https://v11-y2mts-ondemand.cegid.com/CegidMTSWebAPI/swagger/ui/index
    Finances :  https://v11-y2finance-ondemand.cegid.com/CegidFinanceWebApi/swagger/ui/index
    RH : https://y2cbrh-ondemand.cegid.com/CegidRHWebApi/swagger/ui/index

    Odata : 


"""

class CegidCloud:

    ###
    #   Gestion des clients
    ###

    def _get_api_data(self, url_param, debug=False):
        """
            Retourne un tableau de dict contenant toutes les données de la requete ODATA url
            @url : url de la requete odata
        """
        items = []
        skip = 0
        url = url_param
        while url:
            if url[:5] == "http:":
                # Parfois, le NextPageLink est en http au lieu de https. C'est un bug Cegid
                url = url.replace("http://", "https://", 1)
            if debug:
                print(f"GET : {url}")
            response = requests.get(url, auth=settings.XRP_PRINT_AUTH, headers={"Accept": "application/json"})
            if debug:
                print(response.text)
            js = json.loads(response.text)
            try:
                items += js["value"]
            except KeyError:
                # n'est pas un odata
                try:
                    items += js["Items"]
                except KeyError:
                    # Pas sur API non plus, on arrete la boucle et on retourne ce qu'on a trouvé d'ici la
                    url = False
            try:
                url = js["@odata.nextLink"]
            except KeyError:
                # N'est pas sur Odata
                if debug:
                    print("Pas de Odata Next page")
                try:
                    url = js["NextPageLink"]
                except KeyError:
                    if debug:
                        print("Pas de API Next page")
                    # pas sur API non plus, on arrete la aussi
                    url = False
            
            # sleep(settings.API_TIME_SLEEP)
        return items

    def get_odata_client_list(self):
        """
            Retourne la liste des affaires en dict
        """
        return self._get_api_data(settings.ODATA_CLIENT_LIST_URL)

    def get_odata_article_list(self):
        """
            Retourle na liste des articles de prestation en dict
        """
        return self._get_api_data(settings.ODATA_ARTICLE_LIST_URL)

    def get_famille_article_list(self):
        """
            Retourne la liste des familles articles
        """
        return self._get_api_data(settings.API_FAMILLE_ARTICLE_LIST)

    def get_affaire_list(self):
        """
            Retourne la liste des affaires, sous forme de dict
        """
        return self._get_api_data(settings.ODATA_AFFAIRE_LIST_URL)

    def get_service_list(self):
        """
            Retourne la liste des services, sous forme de dict

        """
        return self._get_api_data(settings.API_SERVICE_LIST)

    def get_poste_list(self):
        """
            Retourne la liste des postes, sous forme de dict

        """
        return self._get_api_data(settings.API_POSTE_LIST)