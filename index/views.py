from django.shortcuts import render, redirect
from django.conf import settings
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import date, datetime, timedelta
from index.utils import annee_mois_precedent
from activite.models import Adherent, Article, Salarie
from activite.stats import get_total_heures_all_adherents, get_total_value_search
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import pytz
from monthdelta import monthdelta
from pprint import pprint


class IndexView(TemplateView):
    template_name="index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        annee, mois = annee_mois_precedent()
        context['date_mois_precedent'] = date(annee, mois, 1)

        # Articles nécessaires
        article_heures_normales = Article.objects.get(code_erp="H NORM")
        article_formation = Article.objects.get(code_erp="FORMATION")
        article_location_ordi = Article.objects.get(code_erp="LOCATION")
        adherent_progressis = Adherent.objects.get(raison_sociale="PROGRESSIS")
        adherent_la_poste_list = (Adherent.objects.get(code_erp='294'),Adherent.objects.get(code_erp='625'))
        salarie_gestion = list(Salarie.objects.filter(code_erp__in=["0000000224", "0000000393", "0000000400", "0000000004", "0000000074", "0000000334", "0000000280", "0000000008", "0000000191", "0000000516"]))
        article_intermission = Article.objects.get(code_erp="PANNE")

        # Heures réalisées chez progressis au mois précédent
        adherent_progressis = Adherent.objects.get(raison_sociale="PROGRESSIS")
        context['total_heures_progressis'] = adherent_progressis.total_heures_mois(annee, mois)
        context['total_heures_adherent'] = get_total_value_search(annee, mois, article_list=(article_heures_normales, ), progressis=False)
        if (context['total_heures_progressis'] + context['total_heures_adherent']) != 0:
            context['pourcent_heures_progressis'] = context['total_heures_progressis'] / (context['total_heures_progressis'] + context['total_heures_adherent']) * 100
        else:
            context['pourcent_heures_progressis'] = 0

        # Historique sur 1 an
        data = []
        mois = datetime.now().month
        annee = datetime.now().year
        # annee_cpt = datetime.now().year
        for mois_cpt in range (1, 14):
            # mois_actuel_int = (mois -  mois_cpt) % 12 + 1
            # mois_actuel = date(annee_cpt, mois, 1) -  relativedelta(months=mois_cpt)
            mois_actuel = date(annee, mois, 1) -  monthdelta(mois_cpt)
            # print(f"{mois_actuel}")
            d = {
                "month": mois_actuel,
                "heures_progressis": get_total_value_search(mois_actuel.year, mois_actuel.month, article_list=(article_heures_normales, ), adherent_list=(adherent_progressis, )),
                "heures_tps_partage": (
                    get_total_value_search(mois_actuel.year, mois_actuel.month, article_list=(article_heures_normales, ), progressis=False)
                    - get_total_value_search(mois_actuel.year, mois_actuel.month, article_list=(article_heures_normales, ), adherent_list=(adherent_la_poste_list, ))
                ),
                "heures_adherents": get_total_value_search(mois_actuel.year, mois_actuel.month, article_list=(article_heures_normales, ), progressis=False),
                "heures_formation": get_total_value_search(mois_actuel.year, mois_actuel.month, article_list=(article_formation, ), progressis=True),
                "loc_ordi": get_total_value_search(mois_actuel.year, mois_actuel.month, article_list=(article_location_ordi, ), progressis=True),
                "equipe_gestion": get_total_value_search(mois_actuel.year, mois_actuel.month, article_list=(article_heures_normales, ), salarie_list=salarie_gestion, adherent_list=(adherent_progressis, )),
                "intermission" : get_total_value_search(mois_actuel.year, mois_actuel.month, article_list=(article_intermission, )),
                "la_poste": get_total_value_search(mois_actuel.year, mois_actuel.month, article_list=(article_heures_normales, ), adherent_list=(adherent_la_poste_list)),
            }
            d['progressis_non_gestion'] = d["heures_progressis"] - d["equipe_gestion"]
            data.append(d)
        
        context['historique_mois'] = data
        print(data)

        return context