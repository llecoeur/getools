from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from conge.models import DemandeConge

# Create your views here.
class DemandeCongeListView(ListView):
    model = DemandeConge


class DemandeCongeAddFormView(CreateView):
    model = DemandeConge
    template_name = "FormulaireUtilisateurDemandeConge.html"
    fields = ["debut", "fin", "motif", "commentaire_salarie"]

