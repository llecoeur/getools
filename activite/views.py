from django.shortcuts import render, get_object_or_404
from .models import Salarie
from django.db.models import Q
from django.utils import timezone
from .models import MiseADisposition, Salarie, Article, SaisieActivite, TarifGe, Adherent
from django.http import JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict
import json
import calendar
import pendulum
from jours_feries_france import JoursFeries
from datetime import date
from pprint import pprint
pendulum.set_locale('fr')

# Create your views here.


def preparation_paie(request):
    """
        Vue pour la page de préparation paie
    """
    template = "preparation_paie.html"
    salarie_list = Salarie.objects.filter(Q(date_sortie=None) | Q(date_sortie__gt=timezone.now())).order_by("date_entree").order_by("nom")
    context = {
        "salarie_list": salarie_list,
    }
    return render(request, template, context)

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

    # Tarifs liés au salarié (ie commun a tous les GE)
    tarif_ge_salarie_list_dict = mad.salarie.tarif_ge_list_dict
    tarif_ge_mad_list_dict = mad.tarif_ge_list_dict
    mad_dict['tarifs_ge'] = tarif_ge_salarie_list_dict + tarif_ge_mad_list_dict

    mad_dict['primes_forfaitaires'] = mad_primes_forfaitaires = mad.tarifs_ge_prime_forfaitaire_dict()


    # les valeurs saisies sur les mises tarifs
    saisies_array = mad.get_saisies_from_mois_dict(mois, annee)
    mad_dict['saisies'] = saisies_array


    # Les jours du mois
    jours = []
    start, end = calendar.monthrange(annee, mois)
    # print(calendar.monthrange(annee, mois))
    for num_jour in range(1, end + 1):
        pen_day = pendulum.date(annee, mois, num_jour)
        ferie = JoursFeries.is_bank_holiday(date(annee, mois, num_jour), zone="Métropole")
        samedi_dimanche = pen_day.day_of_week == pendulum.SUNDAY or pen_day.day_of_week == pendulum.SATURDAY
        d = {
            "num": num_jour,
            "str": pen_day.format("dddd D"),
            "non_travaille": samedi_dimanche or ferie,
        }
        jours.append(d)

    ret = {
        "mad": mad_dict,
        "jours": jours,
    }
    pprint(ret)

    return JsonResponse(ret)


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
        saisie.save()
        ret = {
            "result": "ok",
            "message": f"Valeur {saisie.quantite}, sur article {saisie.tarif.article} enregistrée",
        }
    return JsonResponse(ret)

def tarifs(request):
    """
        Page pour lister, modifier, créer, supprimer des tarifs
    """
    template = "tarifs.html"
    fsalarie_id = request.GET.get("fsalarie_id", "")
    fadherent_id = request.GET.get("fadherent_id", "")
    farticle_id = request.GET.get("farticle_id", "")
    if fsalarie_id == "":
        fsalarie = None
    else:
        fsalarie = get_object_or_404(Salarie, pk=fsalarie_id)
    if fadherent_id == "":
        fadherent = None
    else:
        fadherent = get_object_or_404(Adherent, pk=fadherent_id)
    if farticle_id == "":
        farticle = None
    else:
        farticle = get_object_or_404(Article, pk=farticle_id)

    
    tarif_list = TarifGe.objects.all()
    if fsalarie:
        tarif_list.filter(mise_a_disposition__salarie=fsalarie)
    if fadherent:
        tarif_list.filter(mise_a_disposition__adherent=fadherent)
    if farticle:
        tarif_list.filter(article=farticle)
    
    tarif_list.order_by("id")


    salarie_list = Salarie.objects.all().order_by("nom")
    adherent_list = Adherent.objects.all().order_by("raison_sociale")
    article_list = Article.objects.all().order_by("libelle")
    tarif_list = tarif_list[:50]
    context = {
        "tarif_list": tarif_list,
        "tarif_count": tarif_list.count(),
        "tarif_count_all": TarifGe.objects.all().count(),
        "salarie_list": salarie_list,
        "adherent_list": adherent_list,
        "article_list": article_list,
        "fsalarie_id": fsalarie_id,
        "fadherent_id": fadherent_id,
        "farticle_id": farticle_id,
    }
    return render(request, template, context)