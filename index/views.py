from django.shortcuts import render, redirect
from django.conf import settings
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import date, datetime, timedelta
from index.utils import annee_mois_precedent
from activite.models import Adherent
from activite.stats import get_total_heures_all_adherents
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import pytz


class IndexView(TemplateView):
    template_name="index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        annee, mois = annee_mois_precedent()
        context['date_mois_precedent'] = date(annee, mois, 1)

        # Heures réalisées chez progressis au mois précédent
        adherent_progressis = Adherent.objects.get(raison_sociale="PROGRESSIS")
        context['total_heures_progressis'] = adherent_progressis.total_heures_mois(annee, mois)
        context['total_heures_adherent'] = get_total_heures_all_adherents(annee, mois)
        if (context['total_heures_progressis'] + context['total_heures_adherent']) != 0:
            context['pourcent_heures_progressis'] = context['total_heures_progressis'] / (context['total_heures_progressis'] + context['total_heures_adherent']) * 100
        else:
            context['pourcent_heures_progressis'] = 0
        

        # Historique sur 1 an
        data = []
        mois = datetime.now().month
        for mois_cpt in range (1, 13):
            # mois_actuel_int = (mois -  mois_cpt) % 12 + 1
            mois_actuel = date(annee, mois, 1) -  relativedelta(months=mois_cpt)
            print(f"{mois_actuel}")
            d = {
                "month": mois_actuel,
                "heures_progressis": adherent_progressis.total_heures_mois(mois_actuel.year, mois_actuel.month),
                "heures_adherents": get_total_heures_all_adherents(mois_actuel.year, mois_actuel.month),
            }
            data.append(d)
        
        context['historique_mois'] = data
        print(data)

        return context