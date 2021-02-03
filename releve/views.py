from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.forms.models import model_to_dict
from django.db.models import Q, Sum
from releve.models import ReleveSalarie, SaisieSalarie, ReleveSalarieCommentaire
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from releve.serializers import SaisieSalarieSerializer, ReleveSalarieSerializer, ReleveSalarieCommentaireSerializer
from django.utils import timezone
from datetime import date
from django.http import HttpResponse
from django.template.loader import render_to_string
from activite.models import Salarie, MiseADisposition, Adherent
from weasyprint import HTML
from io import BytesIO
import tempfile
import calendar
from jours_feries_france import JoursFeries
import pendulum
from pprint import pprint



class ReleveMensuelView(PermissionRequiredMixin, TemplateView):
    template_name = "releve_mensuel.html"
    permission_required = 'activite.add_saisieactivite'

    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    """

class ReleveMensuelReadOnlyView(PermissionRequiredMixin, TemplateView):
    template_name = "releve_mensuel_read_only.html"
    # can_view_ro_releve_salarie
    permission_required = 'releve.can_view_ro_releve_salarie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        releve_id = self.request.GET.get("id", None)
        context['releve_id'] = releve_id
        return context

class ReleveMensuelListView(PermissionRequiredMixin, TemplateView):
    template_name = "releve_mensuel_list.html"
    permission_required = 'releve.can_view_ro_releve_salarie'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['salarie_list'] = Salarie.objects.all()
        return context


@permission_required('releve.add_relevesalarie')
def ajax_load_saisie_releve_id(request, id_releve):
    """
        Charge le relevé d'id passé en paramètre
        404 si non trouvé
    """
    releve  = get_object_or_404(ReleveSalarie, id=id_releve)
    salarie = releve.salarie
    mois = releve.mois
    annee = releve.annee
    releve_dict = salarie.get_releve_dict(releve, mois, annee)
    return JsonResponse(releve_dict)


@permission_required('releve.add_relevesalarie')
def ajax_load_saisie_releve(request, mois, annee):
    """
        Charge le relevé du salarié connecté, pour le jour et le mois donné
        Si i ln'existe pas, il le crée

       
    """
    salarie = request.user.profile.salarie
    try:
        releve = ReleveSalarie.objects.get(salarie=salarie, annee=annee, mois=mois)
    except ReleveSalarie.DoesNotExist:
        releve = ReleveSalarie()
        releve.salarie = salarie
        releve.mois = mois
        releve.annee = annee
        releve.save()

    # récupérétion du relevé du mois, et création si il n'existe pas

    releve_dict = salarie.get_releve_dict(releve, mois, annee)
    return JsonResponse(releve_dict) 


class SaisieSalarieViewSet(viewsets.ModelViewSet):
    queryset = SaisieSalarie.objects.all()
    serializer_class = SaisieSalarieSerializer

    def partial_update(self, request, *args, **kwargs):
        # On applique un save() sur le relevé correspondant, pour mettre a jour le nombre d'heures
        response_with_updated_instance = super().partial_update(request, *args, **kwargs)
        saisie = self.get_object()
        saisie.releve.save()
        return response_with_updated_instance


class ReleveSalarieViewSet(viewsets.ModelViewSet):
    queryset = ReleveSalarie.objects.all()
    serializer_class = ReleveSalarieSerializer

    def get_queryset(self):
        qs = ReleveSalarie.objects.all()
        salarie_id = self.request.query_params.get('salarie_id', None)
        no_saisie = self.request.query_params.get('no_saisie', None)

        if salarie_id is not None:
            qs = qs.filter(salarie__id=salarie_id)

        if no_saisie is not None:
            qs = qs.exclude(total_h=0)
        
        return qs

class ReleveSalarieCommentaireSerializerViewSet(viewsets.ModelViewSet):
    queryset = ReleveSalarieCommentaire.objects.all().order_by("jour")
    serializer_class = ReleveSalarieCommentaireSerializer

@permission_required('activite.add_saisieactivite')
def releve_mensuel_print_pdf(request, id_salarie):
    """
        Génère un PDF du relevé d'activité du salarié
    """
    
    # ajout année et mois au context. Si pas spécifié, prend le mois et l'année courante
    mois = int(request.GET.get("mois", timezone.now().month))
    annee = int(request.GET.get("annee", timezone.now().year))

    salarie = get_object_or_404(Salarie, id=id_salarie)
    releve = get_object_or_404(ReleveSalarie, salarie=salarie, annee=annee, mois=mois)
    context = {
        "date_str": date(annee, mois, 1),
        'releve': salarie.get_releve_dict(releve, mois, annee),
    }
    html_string = render_to_string('releve_mensuel_print.html', context)
    html = HTML(string=html_string)
    in_memory_pdf = BytesIO(html.write_pdf())
    pdf = in_memory_pdf.getvalue()
    in_memory_pdf.close()

    response = HttpResponse(content_type='application/pdf; charset=utf-8')
    response['Content-Disposition'] = 'inline; filename=releve.pdf'
    response['Content-Transfer-Encoding'] = 'binary'
    response.write(pdf)
    # response['Content-Transfer-Encoding'] = 'binary'
    return response

@permission_required('activite.add_saisieactivite')
def gel_releve(request, annee, mois):
    """
        Gèle tous les relevés du mois, pour empêcher la modification
    """
    num_rows = ReleveSalarie.objects.filter(annee=annee, mois=mois).update(gele=True)
    ret = {
        "num_rows": num_rows,
    }
    return JsonResponse(ret)

@permission_required('activite.add_saisieactivite')
def degel_releve(request, annee, mois):
    """
        dégèle tous les relevés du mois, pour empêcher la modification
    """
    num_rows = ReleveSalarie.objects.filter(annee=annee, mois=mois).update(gele=False)
    ret = {
        "num_rows": num_rows,
    }
    return JsonResponse(ret)

@permission_required('activite.add_saisieactivite')
def releve_mensuel_print_all_pdf(request, annee, mois):
    """
        Génère un PDF de tous les relevés des salariés, pour toutes les mises a disposition ou du du temps a été saisi
    """
    # On récupère tous les adhérents pour lesquelles du temps a été saisi
    output = request.GET.get("t", None)
    adh_list = []
    adherent_list = (Adherent.objects
        .filter(saisie_salarie_list__date__month=mois, saisie_salarie_list__date__year=annee)
        .annotate(somme_saisies=Sum('saisie_salarie_list__heures'))
        .exclude(somme_saisies=0)
        .exclude(somme_saisies=None)
        .exclude(raison_sociale="PROGRESSIS")
        .order_by("raison_sociale")
    )
    for adherent in adherent_list:

        # Liste des relevés ayant des saisies
        # print(f"{adherent.raison_sociale}, {adherent.somme_saisies}")
        releve_list = adherent.get_releve_list(annee, mois)
        start, end = calendar.monthrange(annee, mois)
        jour_list = []
        for num_jour in range(1, end + 1):
            date_saisie = date(annee, mois, num_jour)
            d = []
            pen_day = pendulum.date(annee, mois, num_jour)
            ferie = JoursFeries.is_bank_holiday(date(annee, mois, num_jour), zone="Métropole")
            samedi_dimanche = pen_day.day_of_week == pendulum.SUNDAY or pen_day.day_of_week == pendulum.SATURDAY
            for releve in releve_list:
                saisie = releve.get_saisie(adherent, date_saisie)
                # print(saisie.heures)
                d.append(saisie.heures)

            jour = {
                "jour": date_saisie,
                "non_travaille": samedi_dimanche or ferie,
                "saisie_list": d,
            }
            jour_list.append(jour)
        adh = {
            "adherent": adherent,
            "jour_list": jour_list,
            "releve_list": releve_list,
        }
        adh_list.append(adh)

    context = {
        "date_impression": date(annee, mois, 1),
        "adherent_list": adh_list,
    }
    if output == "html":
        return render(request, 'releve_mensuel_print_all.html', context)
    else:
        html_string = render_to_string('releve_mensuel_print_all.html', context)
        html = HTML(string=html_string)
        in_memory_pdf = BytesIO(html.write_pdf())
        pdf = in_memory_pdf.getvalue()
        in_memory_pdf.close()

        response = HttpResponse(content_type='application/pdf; charset=utf-8')
        response['Content-Disposition'] = 'inline; filename=releve.pdf'
        response['Content-Transfer-Encoding'] = 'binary'
        response.write(pdf)
        # response['Content-Transfer-Encoding'] = 'binary'
        return response