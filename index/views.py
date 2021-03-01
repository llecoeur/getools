from django.shortcuts import render, redirect
from django.conf import settings
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import date, datetime, timedelta
from index.utils import annee_mois_precedent
from activite.models import Adherent
from activite.stats import get_total_heures_all_adherents
import pytz


class IndexView(TemplateView):
    template_name="index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        annee, mois = annee_mois_precedent()
        context['date_mois_precedent'] = date(annee, mois, 1)

        # Heures réalisées chez progressis
        adherent_progressis = Adherent.objects.get(raison_sociale="PROGRESSIS")
        context['total_heures_progressis'] = adherent_progressis.total_heures_mois(annee, mois)
        context['total_heures_adherent'] = get_total_heures_all_adherents(annee, mois)
        if (context['total_heures_progressis'] + context['total_heures_adherent']) != 0:
            context['pourcent_heures_progressis'] = context['total_heures_progressis'] / (context['total_heures_progressis'] + context['total_heures_adherent']) * 100
        else:
            context['pourcent_heures_progressis'] = 0
        return context