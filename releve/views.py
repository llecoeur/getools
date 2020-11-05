from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from django.views.generic.base import TemplateView
from django.forms.models import model_to_dict



class ReleveMensuelView(TemplateView):
    template_name = "releve_mensuel.html"

    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    """

def ajax_load_saisie_releve(request, mois, annee, user_id):
    pass
