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



if __name__ == "__main__":

    # test.delay(mois=12, annee=2021)

    """
        Téléchargement des pdf a envoyer au adherents
    """
    """
    mois = 12
    annee = 2020
    ret = []
    template = "adherent_releve_print.html"
    # adherent_list = Adherent.objects.all().order_by("raison_sociale")
    # adherent_list = Adherent.objects.exclude(raison_sociale="PROGRESSIS").filter(raison_sociale__in=["MANUPLAST"])
    adherent_list = Adherent.objects.exclude(raison_sociale="PROGRESSIS").order_by("raison_sociale")
    for adherent in tqdm(adherent_list):
        # liste des mises a dispo de l'adhérent
        mad_list = adherent.mise_a_disposition_list.filter(cloturee=False)
        for mad in mad_list:
            
            # On regarde si il y a des saisies pour cette mad sur le mois
            saisie_count = SaisieActivite.objects.filter(tarif__mise_a_disposition=mad).filter(date_realisation__month=mois, date_realisation__year=annee).count()
            if saisie_count != 0:
                mad_dict = model_to_dict(mad)
                # releve
                # récupérétion du relevé du mois, et création si il n'existe pas

                # salarie = Salarie.objects.get(pk=salarie_id)
                salarie_dict = model_to_dict(mad.salarie)
                mad_dict['salarie'] = salarie_dict
                mad_dict['adherent'] = model_to_dict(adherent)  
                # Infos supplémentaires des salariés
                # salarie_info_sup = mad.salarie.get_info_sup(mois, annee)
                # mad_dict['salarie']['infos_sup'] = model_to_dict(salarie_info_sup)
                # mad_dict['salarie']['infos_sup']['heures_travaillees'] = salarie_info_sup.heures_travaillees

                # Liste des tarifs
                mad_dict['tarifs_ge'] = mad.tarif_ge_list_dict

                # Primes Fofaitaires
                # mad_dict['primes_forfaitaires'] = mad.tarifs_ge_prime_forfaitaire_dict()

                # Liste des jours, des saisies, etc, pour construire le tableau de saisie
                mad_dict['jour_list'] = mad.get_saisies_from_mois_dict_all(mois, annee)

                # informations supplémentaires des mises a disposition
                # mad_dict['infos_sup'] = model_to_dict(mad.get_info_sup(mois, annee))

                # Liste des primes forfaitaires enregistrées
                # mad_dict['prime_forfaitaires_values'] = mad.prime_forfaitaire_values_list(annee, mois)
                ret.append(mad_dict)

    context = {
        "mad_list": ret,
    }
    f_content = render_to_string(template, context)
    with open("test.html","w+") as f:
        f.write(f_content)

    """
    """
    annee = 2020
    mois = 10
    adherent = Adherent.objects.get(raison_sociale="PROGRESSIS")
    print(adherent.total_heures_mois(annee, mois))
    adherent = Adherent.objects.get(raison_sociale="MANUPLAST")
    print(adherent.total_heures_mois(annee, mois))
    """