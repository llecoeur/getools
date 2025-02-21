from django.core.checks import messages
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic import TemplateView, DetailView
from conge.models import DemandeConge, ValidationAdherent
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from .forms import ValidationAdherentFormSet
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from smtplib import SMTPRecipientsRefused
from datetime import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin
import logging

from django.db.models import Q
logger = logging.getLogger(__name__)

# Create your views here.
class DemandeCongeListView(PermissionRequiredMixin, ListView):
    """
        Affiche une liste de la totalité des demandes de congés dont la date de fin n'est pas dépassée
    """
    # DOTO : Faire le template de la liste
    model = DemandeConge
    template_name = "demande_list.html"
    paginate_by = 20
    permission_required = "conge.can_view_conges"

    def get_queryset(self, *args, **kwargs ):
        qs = super().get_queryset(*args, **kwargs)
        try:
            q = self.request.GET["q"]
            qs = qs.filter(Q(salarie__first_name__icontains=q) | Q(salarie__last_name__icontains=q) | Q(salarie__email__icontains=q))
        except KeyError:
            pass
        qs = qs.filter(fin__gte=timezone.now()).order_by("-debut")
        return qs

class DemandeCongeListAllView(PermissionRequiredMixin, ListView):
    """
        Affiche une liste de la totalité des demandes de congés dont la date de fin n'est pas dépassée
    """
    # DOTO : Faire le template de la liste
    model = DemandeConge
    template_name = "demande_list.html"
    paginate_by = 20
    permission_required = "conge.can_view_conges"


    def get_queryset(self, *args, **kwargs ):
        qs = super().get_queryset(*args, **kwargs)
        try:
            q = self.request.GET["q"]
            qs = qs.filter(Q(salarie__first_name__icontains=q) | Q(salarie__last_name__icontains=q) | Q(salarie__email__icontains=q))
        except KeyError:
            pass
        qs = qs.order_by("-debut")
        return qs

class DemandeCongePasseListView(PermissionRequiredMixin, ListView):
    """
        Affiche une liste de la totalité des demandes de congés en cours, donc envoyées
    """
    # DOTO : Faire le template de la liste
    model = DemandeConge
    template_name = "demande_list.html"
    paginate_by = 20
    permission_required = "conge.can_view_conges"
    

    def get_queryset(self, *args, **kwargs ):
        qs = super().get_queryset(*args, **kwargs)
        try:
            q = self.request.GET["q"]
            qs = qs.filter(Q(salarie__first_name__icontains=q) | Q(salarie__last_name__icontains=q) | Q(salarie__email__icontains=q))
        except KeyError:
            pass
        qs = qs.filter(fin__lt=timezone.now()).order_by("-debut")
        return qs


class DemandeCongeAttenteListView(PermissionRequiredMixin, ListView):
    """
        Affiche une liste de la totalité des demandes en attente de validation
    """
    # DOTO : Faire le template de la liste
    model = DemandeConge
    template_name = "demande_list.html"
    paginate_by = 20
    permission_required = "conge.can_view_conges"
   

    def get_queryset(self, *args, **kwargs ):
        qs = super().get_queryset(*args, **kwargs)
        try:
            q = self.request.GET["q"]
            qs = qs.filter(Q(salarie__first_name__icontains=q) | Q(salarie__last_name__icontains=q) | Q(salarie__email__icontains=q))
        except KeyError:
            pass
        qs = qs.filter(conge_valide=False).filter(conge_invalid=False).order_by("-debut")
        return qs


class DemandeCongePersosListView(ListView):
    """
        Retourne toutes les demandes de congés de l'utilisateur connecté
    """

    model = DemandeConge
    template_name = "demande_list.html"
    paginate_by = 20
    

    def get_queryset(self, *args, **kwargs ):
        qs = super().get_queryset(*args, **kwargs)
        if not self.request.user.id:
            raise Http404

        qs = qs.filter(salarie=self.request.user).order_by("-debut")
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
        context['demande'] = demande
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
    for validation in demande.validation_adherent_list.all():
        try:
            validation.send_email()
        except SMTPRecipientsRefused:
            messages.error(request, f"Email à {validation.nom_prenom} Echoué : Mauvais destinataire")
    va = ValidationAdherent()
    va.demande = demande
    va.nom_prenom = settings.PROGRESSIS_CONGE_NOM
    va.email = settings.PROGRESSIS_CONGE_EMAIL
    va.is_progressis = True
    va.save()
    va.send_email()
    demande.conge_envoye = True
    demande.conge_envoye_date = timezone.now()
    demande.save()
    logger.warning(f"Demande créée, ID={id}, demandeur={demande.salarie}")
    messages.success(request, f"Votre demande de congé a été envoyée")
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
        template = "link_error.html"
        return render(request, template, {})
    else:
        valid.is_valid = True
        valid.valid_manuel_date = timezone.now()
        valid.slug_acceptation = ""
        valid.slug_refus = ""
        valid.save()
        valid.demande.valid()
        logger.warning(f"ACCEPT : Demande ID={valid.demande.id} validée par {valid.nom_prenom} <{valid.email}>")
        messages.success(request, f"Merci ! La demande de congé a été acceptée.")
    return redirect("/")


def reject(request, slug):
    if slug == "" or slug is None:
        messages.error(request, f"Demande invalide")
    try:
        valid = ValidationAdherent.objects.get(slug_refus=slug)
    except ValidationAdherent.DoesNotExist:
        template = "link_error.html"
        return render(request, template, {})
    else:
        valid.is_valid = False
        valid.refus_manuel_date = timezone.now()
        valid.slug_acceptation = ""
        valid.slug_refus = ""
        valid.save()
        valid.demande.conge_invalid = True
        valid.demande.save()
        # Envoi de l'email
        logger.warning(f"REJECT : Demande ID={valid.demande.id} rejetée par {valid.nom_prenom} <{valid.email}>")

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


class AdherentAcceptOrRejectDetailView(DetailView):
    template_name = "accept_reject.html"
    model = ValidationAdherent

    def get_object(self):
        
        try:
            obj = self.model.objects.get(slug_acceptation=self.kwargs['slug'])
        except ValidationAdherent.DoesNotExist:
            obj = None
        return obj



class CalendarView(TemplateView):
    template_name = "calendar.html"

    def get_context_data(self, **kwargs):
        # Charge les congés validés dans le calendrier
        qs = DemandeConge.objects.filter(conge_valide=True)
        context = super().get_context_data(**kwargs)
        context['conge_list'] = qs
        return context

class ValidationAdherentChangeEmailView(UpdateView):
    model = ValidationAdherent
    template_name = "validation_adherent_change_email.html"
    fields = ['email',]

    def get_success_url(self):
        # return HttpResponseRedirect('/foo/')
        self.object.send_email()
        messages.success(self.request, f"Email pour {self.object} mis à jour.")
        return reverse("list_conge_perso")


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context