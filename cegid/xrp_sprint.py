import requests
import json
from django.conf import settings
from pprint import pprint
from time import sleep
from config.models import Config

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
        count_error = 0
        while url:
            if url[:5] == "http:":
                # Parfois, le NextPageLink est en http au lieu de https. C'est un bug Cegid
                url = url.replace("http://", "https://", 1)
            if debug:
                print(f"GET : {url}")
            XRP_PRINT_AUTH = (Config.objects.get(key="XRP_AUTH_LOGIN").str_val, Config.objects.get(key="XRP_AUTH_PASSWORD").str_val)
            print(XRP_PRINT_AUTH)
            response = requests.get(url, auth=XRP_PRINT_AUTH, headers={"Accept": "application/json"})
            if debug:
                print(f"{response.status_code} - {response.text}")
            try:
                js = json.loads(response.text)
            except json.decoder.JSONDecodeError:
                print(response.text)
                exit()
            code = js.get("Code", None)
            if code == "AuthorizationRequired":
                # retry
                count_error += 1
                print(f"nouvel essai : {count_error}")
                # {"Code":"AuthorizationRequired","Message":"Vous n'avez pas accès à cette fonctionnalité."}
                if count_error == 10:
                    # trop d'erreur...
                    return js
            else:
                count_error = 0
                try:
                    items += js["value"]
                except TypeError:
                    # On a directement un tableau, les valeurs ne sont pas dans la propriété "value". Bravo les exceptions CEGID !
                    items += js
                except KeyError:
                    # n'est pas un odata
                    try:
                        items += js["Items"]
                    except KeyError:
                        # Pas sur API non plus, on arrete la boucle et on retourne ce qu'on a trouvé d'ici la
                        url = False
                try:
                    url = js["@odata.nextLink"]
                except TypeError:
                    # pas de pagination
                    url = False
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
                
            sleep(settings.API_TIME_SLEEP)
        return items

    def _set_api_data(self, url_param, data, debug=False):

        XRP_PRINT_AUTH = (Config.objects.get(key="XRP_AUTH_LOGIN").str_val, Config.objects.get(key="XRP_AUTH_PASSWORD").str_val)
        print(XRP_PRINT_AUTH)
        response = requests.post(url_param, auth=XRP_PRINT_AUTH, headers={"Accept": "application/json"}, json=data)
        if debug:
            print(response.status_code)
        return response


    def get_client_list(self):
        """
            Retourne la liste des affaires en dict
        """
        return self._get_api_data(settings.ODATA_CLIENT_LIST_URL)

    def get_article_list(self):
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

    def get_salarie_list(self):
        """
            Retourne la liste des salariés, sous forme de dict
        """
        return self._get_api_data(settings.API_SALARIE_LIST)

    def get_rubrique_list(self):
        """
            Retourne la liste des salariés, sous forme de dict
        """
        return self._get_api_data(settings.API_RUBRIQUE_LIST)

    def get_motif_absence_list(self):
        """
            Retourne la liste des salariés, sous forme de dict
        """
        return self._get_api_data(settings.API_MOTIF_ABSENCE_LIST)
    
    def save_activite_list(self, activite_list):
        """
            Eregistre la liste des activités passées en param
            @param : liste des activités a enregistrer, en dict
        """
        return self._set_api_data(settings.API_POST_ACTIVITY_LIST, activite_list)

    def save_paie_list(self, paie_list):
        """
            Eregistre la liste des rubriques de paie du mois
            @param : liste des paies a enregistrer, en dict
        """
        return self._set_api_data(settings.API_POST_RUBRIC_LIST, paie_list)