from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from conge.models import DemandeConge, ValidationAdherent
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .forms import ValidationAdherentFormSet

# Create your views here.
class DemandeCongeListView(ListView):
    model = DemandeConge


class DemandeCongeAddFormView(CreateView):
    model = DemandeConge
    template_name = "FormulaireUtilisateurDemandeConge.html"
    fields = ["debut", "fin", "motif", "commentaire_salarie"]

    def form_valid(self, form):
        print(form)
        response = super().form_valid(form)

        print(self.request.user)
        return response

class ValidationAdherentAddView(TemplateView):
    template_name = "add_validation_adherent.html"

    # Define method to handle GET request
    def get(self, *args, **kwargs):
        # Create an instance of the formset
        formset = ValidationAdherentFormSet(queryset=ValidationAdherent.objects.none())
        return self.render_to_response({'validation_adherent_formset': formset})

    def post(self, *args, **kwargs):

        formset = ValidationAdherentFormSet(data=self.request.POST)

        # Check if submitted forms are valid
        if formset.is_valid():
            formset.save()
            return redirect(reverse_lazy("bird_list"))

        return self.render_to_response({'validation_adherent_formset': formset})