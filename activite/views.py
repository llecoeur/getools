from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Salarie
from django.db.models import Q
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import MiseADisposition, Salarie, Article, SaisieActivite, TarifGe, Adherent
from .forms import TarifGeEditForm
from .filters import TarifGeFilter
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict
from django.contrib import messages
from django.urls import reverse_lazy
import json
import calendar
import pendulum
from jours_feries_france import JoursFeries
from datetime import date
from pprint import pprint
pendulum.set_locale('fr')

# Create your views here.
@login_required
def sort_article(request):
    """
        Page permettant de définir l'ordre des articles a afficher dans la page de préparation paie
    """
    template = "sort_article.html"
    return render(request, template, {})

def ajax_load_article_list(request):
    """
        Charge les articles a ranger dans la page des articles
    """
    # TODO : Filter uniquement les artiches a lister dans le tableau de saisie ?
    article_list = list(Article.objects.all().order_by('ordre').values())
    return JsonResponse(article_list, safe=False)

def ajax_switch_article_ordre(request, article1_id, article2_id):
    """
        Inverse la position des articles 1 et 2.
        retourne la liste des articles mis a jour
    """
    article1 = Article.objects.get(id=article1_id)
    article2 = Article.objects.get(id=article2_id)
    article1_ordre = article1.ordre
    article2_ordre = article2.ordre
    article1.ordre = article2_ordre
    article2.ordre = article1_ordre
    article1.save()
    article2.save()
    article_list = list(Article.objects.all().order_by('ordre').values())
    return JsonResponse(article_list, safe=False)

@login_required
def preparation_paie(request):
    """
        Vue pour la page de préparation paie
    """
    template = "preparation_paie.html"
    salarie_list = Salarie.get_salaries_actuels()
    context = {
        "salarie_list": salarie_list,
    }
    return render(request, template, context)

@login_required
def ajax_mad_for_salarie(request, salarie_id, termine):
    """
        Retourne un json avec la liste des mise a dispo du salarié donné.
        @salarie_id : id du salarie
        @termine : false -> uniquement les mads ouvertes, true -> toutes les mads
    """
    salarie = get_object_or_404(Salarie, pk=salarie_id)
    mad_list = MiseADisposition.objects.filter(salarie=salarie)
    if termine == "false":
        # seleuement les mads  ouvertes
        mad_list = mad_list.filter(cloturee=False)
    ret = []
    for mad in mad_list:
        ret.append({
            "id": mad.id,
            "text": f"{mad.adherent}",
        })
    return JsonResponse(ret, safe=False)

@login_required
def ajax_load_saisie_mad(request, mois, annee, mad_id):
    """
        Retourne un json avec :
        * Les informations complètes de la mise a dispo, y compris les articles liés
        * Les jours du mois
        
        Tout doit assez complet pour construire le tableau de saisie
    """
    mad = MiseADisposition.objects.get(pk=mad_id)
    mad_dict = model_to_dict(mad)
    
    # salarie = Salarie.objects.get(pk=salarie_id)
    salarie_dict = model_to_dict(mad.salarie)
    mad_dict['salarie'] = salarie_dict

    # Tarifs liés au salarié 
    mad_dict['tarifs_ge'] = mad.tarif_ge_list_dict

    mad_dict['primes_forfaitaires'] = mad.tarifs_ge_prime_forfaitaire_dict()


    mad_dict['jour_list'] = mad.get_saisies_from_mois_dict_all(mois, annee)

    ret = {
        "mad": mad_dict,
    }

    return JsonResponse(ret)


@login_required
def ajax_save_saisie(request, valeur, tarif_id, annee, mois, jour):
    """
        Enregistre ou met a jour la valeur pour la saisie d'activité souhaitée.
        retourne une erreur et un message si problème
    """
    tarif = TarifGe.objects.get(id=tarif_id)
    date_realisation = date(annee, mois, jour)
    # print(date_realisation)
    saisie = SaisieActivite.get_saisie(tarif, date_realisation)
    if saisie == None:
        saisie = SaisieActivite()
        saisie.tarif = tarif
        saisie.date_realisation = date_realisation
    if valeur == "0":
        try:
            saisie.delete()
        except AssertionError:
            pass
        ret = {
            "result": "ok",
            "message": f"Valeur sur article {saisie.tarif.article} effacée",
        }
    else:
        saisie.quantite = valeur
        try:
            saisie.save()
        except ValueError:
            ret = {
                "result": "error",
                "message": f"Impossible d'enregistrer la valeur {valeur} sur l'article {saisie.tarif.article}. La valeur entrée n'est pas un nombe",
            }
        else:
            ret = {
                "result": "ok",
                "message": f"Valeur {valeur}, sur article {saisie.tarif.article} enregistrée",
            }
    return JsonResponse(ret)


@login_required
def tarifs(request):
    """
        Page pour lister, modifier, créer, supprimer des tarifs
    """
    template = "tarifs.html"

    f = TarifGeFilter(request.GET, queryset=TarifGe.objects.all())
    tarif_list = f.qs[:50]
    context = {
        "tarif_list": tarif_list,
        "filter": f,
        "tarif_count": tarif_list.count(),
        "tarif_count_all": TarifGe.objects.all().count(),
        "tarif_count_filter" : f.qs.count(),
    }
    return render(request, template, context)


class TarifGeCreate(LoginRequiredMixin, CreateView):
    model = TarifGe
    template_name = "tarifs_form.html"

    fields = ['article', 'mise_a_disposition', 'tarif', 'coef_paie', 'coef']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create'] = True
        return context


class TarifGeUpdate(LoginRequiredMixin, UpdateView):
    model = TarifGe
    # form_class = TarifGeEditForm
    template_name = "tarifs_form.html"
    fields = ['tarif', 'coef_paie', 'coef', 'archive']


class TarifGeDelete(LoginRequiredMixin, DeleteView):
    model = TarifGe
    template_name = "tarifge_confirm_delete.html"
    success_url = reverse_lazy('tarifs')
    success_message = "Le tarif a été supprimé."
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

