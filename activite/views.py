from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Salarie
from django.db.models import Q
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import RubriquePaie, MiseADisposition, Salarie, Article, SaisieActivite, TarifGe, Adherent, FamilleArticle, Service, Poste
from .forms import TarifGeEditForm
from .filters import TarifGeFilter
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.forms.models import model_to_dict
from django.contrib import messages
from django.urls import reverse_lazy
import json
import calendar
import pendulum
from jours_feries_france import JoursFeries
from datetime import date
from cegid.xrp_sprint import CegidCloud
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

@login_required
def ajax_load_article_list(request):
    """
        Charge les articles a ranger dans la page des articles
    """
    # TODO : Filter uniquement les artiches a lister dans le tableau de saisie ?
    article_list = list(Article.objects.all().order_by('ordre').values())
    return JsonResponse(article_list, safe=False)

@login_required
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
    salarie_list = Salarie.objects.all()
    context = {
        "salarie_list": salarie_list,
    }
    return render(request, template, context)


@login_required
def synchronisation(request):
    """
        Vue pour la page de synchronisation
    """
    template = "synchro.html"
    return render(request, template, {})


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
    # Infos supplémentaires des salariés
    salarie_info_sup = mad.salarie.get_info_sup(mois, annee)
    mad_dict['salarie']['infos_sup'] = model_to_dict(salarie_info_sup)
    mad_dict['salarie']['infos_sup']['heures_travaillees'] = salarie_info_sup.heures_travaillees

    # Liste des tarifs
    mad_dict['tarifs_ge'] = mad.tarif_ge_list_dict

    # Primes Fofaitaires
    mad_dict['primes_forfaitaires'] = mad.tarifs_ge_prime_forfaitaire_dict()

    # Liste des jours, des saisies, etc, pour construire le tableau de saisie
    mad_dict['jour_list'] = mad.get_saisies_from_mois_dict_all(mois, annee)

    # informations supplémentaires des mises a disposition
    mad_dict['infos_sup'] = model_to_dict(mad.get_info_sup(mois, annee))

    # Liste des primes forfaitaires enregistrées
    mad_dict['prime_forfaitaires_values'] = mad.prime_forfaitaire_values_list(annee, mois)

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

    saisie.quantite = valeur
    saisie.uploaded = False
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


@login_required
def ajax_update_famille_article(request):
    """
        Lit les familles XPR Print, et met a jour la table des familles articles
    """
    cegid = CegidCloud()
    famille_list = cegid.get_famille_article_list()
    count = len(famille_list)
    ajoute = 0

    for famille in famille_list:
        try:
            f = FamilleArticle.objects.get(code_erp=famille['Key'])
        except FamilleArticle.DoesNotExist:
            f = FamilleArticle()
            ajoute += 1
        f.code_erp = famille['Key']
        f.libelle = famille['Value']
        if famille['Key'] == "PRF" or famille['Key'] == "FOR":
            # marqué comme prime forfétaire
            f.forfaitaire = True
        f.save()
    ret = { "result": "ok", "count": count, "ajoute": ajoute, }
    return JsonResponse(ret)
    

@login_required
def ajax_update_service(request):
    """
        Mise a jour de a liste des services
    """
    cegid = CegidCloud()
    service_list = cegid.get_service_list()
    count = len(service_list)
    ajoute = 0
    for service in service_list:
        try:
            s = Service.objects.get(code_erp=service['Key'])
        except Service.DoesNotExist:
            # On ajoute
            s = Service()
            ajoute += 1
        s.code_erp = service['Key']
        s.libelle = service['Value']
        s.save()
    ret = { "result": "ok", "count": count, "ajoute": ajoute, }
    return JsonResponse(ret)


@login_required
def ajax_update_poste(request):
    """
        Mise a jour de a liste des services
    """
    cegid = CegidCloud()
    poste_list = cegid.get_poste_list()
    count = len(poste_list)
    ajoute = 0
    for poste in poste_list:
        try:
            s = Poste.objects.get(code_erp=poste['Key'])
        except Poste.DoesNotExist:
            # On ajoute
            s = Poste()
            ajoute += 1
        s.code_erp = poste['Key']
        s.libelle = poste['Value']
        s.save()
    ret = { "result": "ok", "count": count, "ajoute": ajoute, }
    return JsonResponse(ret)


@login_required
def ajax_update_salaries(request):
    """
        Mise a joru de a liste des salariés
    """
    cegid = CegidCloud()
    salarie_list = cegid.get_salarie_list()
    count = len(salarie_list)
    ajoute = 0
    for salarie_cegid in salarie_list:
        try:
            sal = Salarie.objects.get(code_erp=salarie_cegid['EmployeeId'])
        except Salarie.DoesNotExist:
            # On ajoute
            sal = Salarie()
            ajoute += 1
        sal.code_erp = salarie_cegid['EmployeeId']
        sal.nom = salarie_cegid['Name']
        if salarie_cegid['Name'].strip() == "LEMUET":
            print(salarie_cegid)
        sal.prenom = salarie_cegid['FirstName']
        sal.date_entree = pendulum.parse(salarie_cegid['EntryDate']).to_date_string()
        sal.date_sortie = pendulum.parse(salarie_cegid['ExitDate']).to_date_string()
        sal.save()
    ret = { "result": "ok", "count": count, "ajoute": ajoute, }
    return JsonResponse(ret)

@login_required
def ajax_update_rubrique(request):
    """
        Mise a jour de la liste des rubriques
    """
    cegid = CegidCloud()
    rub_list = cegid.get_rubrique_list()
    count = len(rub_list)
    ajoute = 0
    for rub_cegid in rub_list:
        try:
            rub = RubriquePaie.objects.get(code_erp=rub_cegid['Rubric'])
        except RubriquePaie.DoesNotExist:
            # On ajoute
            rub = RubriquePaie()
            ajoute += 1
        rub.code_erp = rub_cegid['Rubric']
        rub.libelle = rub_cegid['RubricLabel']
        rub.abrege = rub_cegid['RubricLabel']
        rub.save()
    ret = { "result": "ok", "count": count, "ajoute": ajoute, }
    return JsonResponse(ret)

@login_required
def ajax_update_article(request):
    """
        Mise a jour de la liste des rubriques
    """
    cegid = CegidCloud()
    article_list = cegid.get_article_list()
    count = len(article_list)
    ajoute = 0
    for article_cegid in article_list:
        try:
            art = Article.objects.get(code_erp=article_cegid['ItemCode_GA'])
        except Article.DoesNotExist:
            # On ajoute
            art = Article()
            ajoute += 1
        art.code_erp = article_cegid['ItemCode_GA']
        art.libelle = article_cegid['Description_GA']
        art.type_article = article_cegid['ItemType_GA']
        art.unite = article_cegid['ActivityUnit'].strip()
        if article_cegid['UserFieldItem2_GA'].strip() == 'OUI':
            art.charges_soumises = True
        elif article_cegid['UserFieldItem2_GA'].strip() == 'NON':
            art.charges_soumises = False
        else:
            art.charges_soumises = None
        if article_cegid['UserFieldItem5_GA'].strip() == 'OUI':
            art.facturation_uniquement = True
        else:
            art.facturation_uniquement = False
        try:
            rub_paie = RubriquePaie.objects.get(code_erp=article_cegid['UserFieldItem1_GA'])
        except AttributeError:
            pass
        except RubriquePaie.DoesNotExist:
            pass
        else:
            art.rubrique_paie = rub_paie
        # La famille
        try:
            famille = FamilleArticle.objects.get(code_erp=article_cegid['FamilyLevel1_GA'])
        except FamilleArticle.DoesNotExist:
            famille = None
        art.famille = famille
        art.save()
    ret = { "result": "ok", "count": count, "ajoute": ajoute, }
    return JsonResponse(ret)

@login_required
def ajax_update_adherent(request):
    """
        Mise a jour de la liste des adhérents
    """
    cegid = CegidCloud()
    adherent_list = cegid.get_client_list()
    count = len(adherent_list)
    ajoute = 0
    for adh_cegid in adherent_list:
        try:
            adh = Adherent.objects.get(code_erp=adh_cegid['ThirdParty_T'])
        except Adherent.DoesNotExist:
            adh = Adherent()
            ajoute += 1
        adh.code_erp = adh_cegid['ThirdParty_T']
        adh.raison_sociale = adh_cegid['Name_T']
        adh.save()
    ret = { "result": "ok", "count": count, "ajoute": ajoute, }
    return JsonResponse(ret)

@login_required
def ajax_update_mad(request):
    """
        Mise a jour des mises à disposition
    """
    cegid = CegidCloud()
    aff_list = cegid.get_affaire_list()
    count = len(aff_list)
    ajoute = 0
    error_count = 0
    for affaire_cegid in aff_list:
        error = False

        try:
            adherent = Adherent.objects.get(code_erp=affaire_cegid['ThirdParty_AFF'])
        except AttributeError:
            print(f"l'affaire {affaire_cegid['Project_AFF']} n'a pas d'adhérent.")
            error = True
            error_count += 1
        except Adherent.DoesNotExist:
            print(f"L'adhérent {affaire_cegid['ThirdParty_AFF']} n'existe pas en base django: As-il été importé ?")
            error = True
            error_count += 1
        

        try:
            salarie = Salarie.objects.get(code_erp=affaire_cegid['Manager_AFF'])
        except AttributeError:
            print(f"l'affaire {affaire_cegid['Project_AFF']} n'a pas de salarié.")
            error = True
            error_count += 1
        except Salarie.DoesNotExist:
            print(f"Le salarié {affaire_cegid['Manager_AFF']} n'existe pas en base django: As-il été importé ?")
            error = True
            error_count += 1

        if not error:
            mad = MiseADisposition.get_mise_a_disposition(adherent.code_erp, salarie.code_erp)
            if mad is None:
                mad = MiseADisposition()
                mad.adherent = adherent
                mad.salarie = salarie
                mad.cloturee = False
                ajoute += 1
            mad.code_erp = affaire_cegid['Project_AFF']
            mad.duree_travail_mensuel = affaire_cegid['UserFieldNumeric2_AFF']
            mad.duree_travail_quotidien = affaire_cegid['UserFieldNumeric3_AFF']
            mad.service = Service.objects.filter(code_erp=affaire_cegid['UserField1_AFF']).first()
            mad.poste = Poste.objects.filter(code_erp=affaire_cegid['UserField2_AFF']).first()
            if affaire_cegid['State_AFF'] == "CLO":
                mad.cloturee = True
            if affaire_cegid['UserField3_AFF'] != '':
                mad.coef_vente_soumis = affaire_cegid['UserField3_AFF']
            else:
                mad.coef_vente_soumis = 0
            if affaire_cegid['UserField4_AFF'] != '':
                mad.coef_vente_non_soumis = affaire_cegid['UserField4_AFF']
            else:
                mad.coef_vente_non_soumis = 0
            mad.save()
    ret = { "result": "ok", "count": count, "error_count": error_count, "ajoute": ajoute, }
    return JsonResponse(ret)

@login_required
def ajax_upload_activite(request, mad_id):
    """
        Envoie les activités non envoyées pour l'instant vers XRP Sprint, pour la mad en paramètre
        TODO : DEPRECIE lors de la suppression des uploads dans la pag de saisie des mads
    """
    try:
        mad = MiseADisposition.objects.get(id=mad_id)
    except MiseADisposition.DoesNotExist:
        return JsonResponse({ "result": "Error", "message" : "La mise a disposition n'existe pas" })

    activite_list = SaisieActivite.objects.filter(tarif__mise_a_disposition=mad, uploaded=False)
    activite_dict_array = []
    for activite in activite_list:
        if activite.quantite != 0:
            activite_dict_array.append(activite.to_xrp_dict())
    
    # print(json.dumps(activite_dict_array))
    cegid = CegidCloud()
    response = cegid.save_activite_list(activite_dict_array)
    if response.status_code == 200:
        # On est ok, on marque les activités comme envoyées
        for activite in activite_list:
            activite.uploaded = True
            activite.save()
    # 
    return HttpResponse(response.text)


@login_required
def ajax_get_mad_to_upload(request):
    """
        Envoie les activités non envoyées pour l'instant vers XRP Sprint, pour la mad en paramètre
    """

    # Récupération de toutes les mises a dispos qui ont des activités non envoyées
    mad_list = MiseADisposition.objects.filter(cloturee=False)
    mad_array = []
    for mad in mad_list:
        activites_list = mad.get_activites_to_upload()
        if len(activites_list) != 0:
            mad_array.append(model_to_dict(mad))
    return JsonResponse(mad_array, safe=False)
    

def ajax_maj_heures_travaillees(request, mad_id, annee, mois):
    """
        Retourne un json contenant des infos sup a mettre a jour
        {
            salarie:{
                heures_travaillees:val,
            }
            mise_a_disposition:{
                heures_travaillees:val,
            }
        }
    """
    mad = MiseADisposition.objects.get(id=mad_id)
    ret = {
        "salarie": {
            "heures_travaillees": mad.salarie.get_heures_travail_mois(annee, mois),
        },
        "mise_a_disposition": {
            "heures_travaillees": mad.get_heures_travail_mois(annee, mois),
        },
    }
    return JsonResponse(ret)