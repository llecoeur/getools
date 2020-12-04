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
    
    releve_dict = model_to_dict(releve)
    releve_dict['salarie'] = model_to_dict(salarie)
    releve_dict['mad_list'] = []
    mad_list = salarie.current_mad_list
    for mad in mad_list:
        m = model_to_dict(mad)
        m['adherent'] = model_to_dict(mad.adherent)
        releve_dict['mad_list'].append(m)

    releve_dict['jours_list'] = salarie.get_saisies_releve_mois_dict_all(mois, annee)
    
    # TODO : Créer la liste des jours. Voir get_saisies_from_mois_dict_all sans activite_mise a dispo   
    return JsonResponse(releve_dict) 


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
