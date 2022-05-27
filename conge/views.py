from django.core.checks import messages
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from conge.models import DemandeConge, ValidationAdherent
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .forms import ValidationAdherentFormSet
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import Http404
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from smtplib import SMTPRecipientsRefused
from datetime import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404




# Create your views here.
class DemandeCongeListView(ListView):
    """
        Affiche une liste de la totalité des demandes de congés dont la date de fin n'est pas dépassée
    """
    # DOTO : Faire le template de la liste
    model = DemandeConge
    template_name = "demande_list.html"

    def get_queryset(self, *args, **kwargs ):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(fin__gte=timezone.now()).order_by("-created")
        return qs


class DemandeCongePasseListView(ListView):
    """
        Affiche une liste de la totalité des demandes de congés en cours, donc envoyées
    """
    # DOTO : Faire le template de la liste
    model = DemandeConge
    template_name = "demande_list.html"

    

    def get_queryset(self, *args, **kwargs ):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(fin__lt=timezone.now()).order_by("-created")
        return qs

class DemandeCongeAttenteListView(ListView):
    """
        Affiche une liste de la totalité des demandes en attente de validation
    """
    # DOTO : Faire le template de la liste
    model = DemandeConge
    template_name = "demande_list.html"
   

    def get_queryset(self, *args, **kwargs ):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(conge_valide=False).filter(conge_invalid=False).order_by("-created")
        return qs


class DemandeCongePersosListView(ListView):
    """
        Retourne toutes les demandes de congés de l'utilisateur connecté
    """

    model = DemandeConge
    template_name = "demande_list.html"

    def get_queryset(self, *args, **kwargs ):
        qs = super().get_queryset(*args, **kwargs)
        if not self.request.user.id:
            raise Http404

        print(f"salarie={salarie}={self.request.user.id}")
        qs.filter(salarie=self.request.user)
        return qs


class DemandeCongeAddFormView(CreateView):
    model = DemandeConge
    template_name = "FormulaireUtilisateurDemandeConge.html"
    fields = ["debut", "fin", "motif", "commentaire_salarie"]
    success_url = "add_adherent"

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.salarie = self.request.user
        obj.save()
        return redirect(f"step2/?id={ obj.id }")


class ValidationAdherentFormView(CreateView):
    model = ValidationAdherent
    template_name = "step2.html"
    fields = ['email', "nom_prenom"]

    def get_context_data(self, **kwargs):
        id = self.request.GET.get("id", None)
        if not id:
            return Http404
        try:
            demande = DemandeConge.objects.get(id=id)
        except DemandeConge.DoesNotExist:
            return Http404
        context = super().get_context_data(**kwargs)
        context['validation_list'] = ValidationAdherent.objects.filter(demande=demande)
        context['id'] = id
        return context

    def form_valid(self, form):
        id = self.request.GET.get("id", None)
        if not id:
            return Http404
        try:
            demande = DemandeConge.objects.get(id=id)
        except DemandeConge.DoesNotExist:
            return Http404
        obj = form.save(commit=False)
        obj.demande = demande
        obj.save()
        messages.success(self.request, "Destinataire ajouté")
        return redirect(f"/conge/new/step2/?id={ id }")


def remove_validation(request, id):
    print(id)
    validation = ValidationAdherent.objects.get(id=id)
    id_demande = validation.demande.id
    validation.delete()
    messages.success(request, "Valdation supprimée")
    return redirect(f"/conge/new/step2/?id={ id_demande }")


def finish(request, id):
    """
        Envoie la demande de congé :
        Génère les urls
        Envois des mails a chaque personne
    """
    demande = DemandeConge.objects.get(id=id)
    # On ajoute Progressis comme adhérent
    va = ValidationAdherent()
    va.demande = demande
    va.nom_prenom = settings.PROGRESSIS_CONGE_NOM
    va.email = settings.PROGRESSIS_CONGE_EMAIL
    va.is_progressis = True
    va.save()
    va.send_email()
    for validation in demande.validation_adherent_list.all():
        try:
            validation.send_email()
        except SMTPRecipientsRefused:
            messages.error(request, f"Email à {validation.nom_prenom} Echoué : Mauvais destinataire")
        messages.success(request, f"Email à {validation.nom_prenom} envoyé")
    demande.conge_envoye = True
    demande.conge_envoye_date = timezone.now()
    demande.save()
    return redirect("/conge/")


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
            return redirect(reverse_lazy("step2"))

        return self.render_to_response({'validation_adherent_formset': formset})


def accept(request, slug):
    if slug == "" or slug is None:
        messages.error(request, f"Demande invalide")
    try:
        valid = ValidationAdherent.objects.get(slug_acceptation=slug)
    except ValidationAdherent.DoesNotExist:
        messages.error(request, f"Cette demande n'existe pas ou a expiré")
    else:
        valid.is_valid = True
        valid.valid_manuel_date = timezone.now()
        valid.slug_acceptation = ""
        valid.slug_refus = ""
        valid.save()
        valid.demande.valid()
        messages.success(request, f"Merci ! La demande de congé a été acceptée.")
    return redirect("/")


def reject(request, slug):
    if slug == "" or slug is None:
        messages.error(request, f"Demande invalide")
    try:
        valid = ValidationAdherent.objects.get(slug_refus=slug)
    except ValidationAdherent.DoesNotExist:
        messages.error(request, f"Cette demande n'existe pas ou a expiré")
    else:
        valid.is_valid = False
        valid.refus_manuel_date = timezone.now()
        valid.slug_acceptation = ""
        valid.slug_refus = ""
        valid.save()
        valid.demande.conge_invalid = True
        valid.demande.save()
        # Envoi de l'email
        messages.success(request, f"La demande de congé a été refusée.")
    
    return redirect("/")

def delete_conge(request, id):
    """
        Efface la demande
    """
    dc = get_object_or_404(DemandeConge, id=id)
    ValidationAdherent.objects.filter(demande=dc).delete()
    dc.delete()
    messages.success(request, f"La demande de congé a été supprimée.")
    return redirect("/conge/")