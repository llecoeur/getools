from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.forms.models import model_to_dict
from releve.models import ReleveSalarie, SaisieSalarie, ReleveSalarieCommentaire
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from releve.serializers import SaisieSalarieSerializer, ReleveSalarieSerializer, ReleveSalarieCommentaireSerializer
from django.utils import timezone
from datetime import date
from django.http import HttpResponse
from django.template.loader import render_to_string
from activite.models import Salarie
from weasyprint import HTML
from io import BytesIO
import tempfile



class ReleveMensuelView(TemplateView, PermissionRequiredMixin):
    template_name = "releve_mensuel.html"
    permission_required = 'activite.add_saisieactivite'

    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    """

@permission_required('releve.add_relevesalarie')
def ajax_load_saisie_releve(request, mois, annee):
    salarie = request.user.profile.salarie
    # récupérétion du relevé du mois, et création si il n'existe pas
    try:
        releve = ReleveSalarie.objects.get(salarie=salarie, annee=annee, mois=mois)
    except ReleveSalarie.DoesNotExist:
        releve = ReleveSalarie()
        releve.salarie = salarie
        releve.mois = mois
        releve.annee = annee
        releve.save()
    """    
    releve_dict = model_to_dict(releve)
    releve_dict['salarie'] = model_to_dict(salarie)
    releve_dict['mad_list'] = []
    mad_list = salarie.current_mad_list
    for mad in mad_list:
        m = model_to_dict(mad)
        m['adherent'] = model_to_dict(mad.adherent)
        releve_dict['mad_list'].append(m)

    releve_dict['jours_list'] = salarie.get_saisies_releve_mois_dict_all(mois, annee)
    """
    releve_dict = salarie.get_releve_dict(releve, mois, annee)
    return JsonResponse(releve_dict) 


class ReleveMensuelPrintView(TemplateView, PermissionRequiredMixin):
    """
        Test de relevé mensuel. a a dapter et / ou supprimer
    """
    template_name = "releve_mensuel_print.html"
    permission_required = 'activite.add_saisieactivite'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ajout année et mois au context. Si pas spécifié, prend le mois et l'année courante
        mois = int(self.request.GET.get("mois", timezone.now().month))
        annee = int(self.request.GET.get("annee", timezone.now().year))
        salarie = salarie = self.request.user.profile.salarie
        releve = ReleveSalarie.objects.get(salarie=salarie, annee=annee, mois=mois)

        context["date_str"] = date(annee, mois, 1)
        context['releve'] = salarie.get_releve_dict(releve, mois, annee)
        return context


class SaisieSalarieViewSet(viewsets.ModelViewSet):
    queryset = SaisieSalarie.objects.all()
    serializer_class = SaisieSalarieSerializer

class ReleveSalarieViewSet(viewsets.ModelViewSet):
    queryset = ReleveSalarie.objects.all()
    serializer_class = ReleveSalarieSerializer

class ReleveSalarieCommentaireSerializerViewSet(viewsets.ModelViewSet):
    queryset = ReleveSalarieCommentaire.objects.all().order_by("jour")
    serializer_class = ReleveSalarieCommentaireSerializer

    def get_queryset(self):
        # Permet de filtrer par relevé salarié, en spécifiant dans l'url ?releve=pk
        id_releve = self.request.GET.get('releve', None)
        if id_releve:
            releve = get_object_or_404(ReleveSalarie, pk=id_releve)
            return ReleveSalarieCommentaire.objects.filter(releve=releve).order_by("jour")
        return super().get_queryset()


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
