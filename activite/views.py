from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Salarie
from django.db.models import Q, Sum
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from .models import InfosSupMoisMad, InfosSupMoisSalarie, RubriquePaie, MiseADisposition, Salarie, Article, SaisieActivite, TarifGe, Adherent, FamilleArticle, Service, Poste
from releve.models import ReleveSalarie
from .forms import TarifGeEditForm
from .filters import TarifGeFilter
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.forms.models import model_to_dict
from django.contrib import messages
from django.urls import reverse_lazy
import json
import calendar
import pendulum
from jours_feries_france import JoursFeries
from datetime import date, timedelta
from cegid.xrp_sprint import CegidCloud
from pprint import pprint
from django.forms.models import modelform_factory
from django.forms import ModelChoiceField
from django.views.decorators.csrf import csrf_exempt
import unicodedata
from tqdm import tqdm
from activite.tasks import generate_releve_adherent
from activite.serializers import SalarieSerializer
from rest_framework import viewsets

pendulum.set_locale('fr')


# Create your views here.
@permission_required('activite.add_saisieactivite')
def sort_article(request):
    """
        Page permettant de définir l'ordre des articles a afficher dans la page de préparation paie
    """
    template = "sort_article.html"
    return render(request, template, {})


@permission_required('activite.add_saisieactivite')
def ajax_load_article_list(request):
    """
        Charge les articles a ranger dans la page des articles
    """
    # TODO : Filter uniquement les artiches a lister dans le tableau de saisie ?
    article_list = list(Article.objects.all().order_by('ordre').values())
    return JsonResponse(article_list, safe=False)


@permission_required('activite.add_saisieactivite')
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


@permission_required('activite.add_saisieactivite')
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


@permission_required('activite.add_saisieactivite')
def synchronisation(request):
    """
        Vue pour la page de synchronisation
    """
    template = "synchro.html"
    return render(request, template, {})


@permission_required('activite.add_saisieactivite')
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


@permission_required('activite.add_saisieactivite')
def ajax_load_saisie_mad(request, mois, annee, mad_id):
    """
        Retourne un json avec :
        * Les informations complètes de la mise a dispo, y compris les articles liés
        * Les jours du mois
        
        Tout doit assez complet pour construire le tableau de saisie
    """
    mad = MiseADisposition.objects.get(pk=mad_id)

    # salarie = request.user.profile.salarie

    mad_dict = model_to_dict(mad)

    # releve
    # récupérétion du relevé du mois, et création si il n'existe pas
    try:
        releve = ReleveSalarie.objects.get(salarie=mad.salarie, annee=annee, mois=mois)
    except ReleveSalarie.DoesNotExist:
        releve = ReleveSalarie()
        releve.salarie = mad.salarie
        releve.mois = mois
        releve.annee = annee
        releve.save()
    
    mad_dict['releve'] = model_to_dict(releve)

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


@permission_required('activite.add_saisieactivite')
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
        if saisie == 0:
            ret = {
                "result": "ok",
                "message": f"Valeur {valeur}, sur article {saisie.tarif.article} enregistrée",
            }
            return JsonResponse(ret)
        saisie = SaisieActivite()
        saisie.tarif = tarif
        saisie.date_realisation = date_realisation
    else:
        if saisie == 0:
            saisie.delete()
            ret = {
                "result": "ok",
                "message": f"Valeur {valeur}, sur article {saisie.tarif.article} enregistrée",
            }
            return JsonResponse(ret)

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


@permission_required('activite.add_saisieactivite')
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


class TarifGeCreate(PermissionRequiredMixin, CreateView):
    model = TarifGe
    template_name = "tarifs_form.html"
    success_url = "/act/tarif/add/"
    success_message = "Tarif ajouté 👏"
    permission_required = 'activite.add_saisieactivite'

    fields = ['article', 'mise_a_disposition', 'tarif']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create'] = True
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        return response



class TarifGeUpdate(PermissionRequiredMixin, UpdateView):
    model = TarifGe
    # form_class = TarifGeEditForm
    template_name = "tarifs_form.html"
    fields = ['tarif', 'coef_paie', 'tarif_pere', 'coef', 'archive']
    success_message = "Tarif modifié 👏"
    permission_required = 'activite.add_saisieactivite'

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields['tarif_pere'].queryset = TarifGe.objects.filter(
            mise_a_disposition=self.object.mise_a_disposition,
            tarif_pere=None
        )
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class TarifGeDelete(PermissionRequiredMixin, DeleteView):
    model = TarifGe
    template_name = "tarifge_confirm_delete.html"
    success_url = reverse_lazy('tarifs')
    success_message = "Le tarif a été supprimé."
    permission_required = 'activite.add_saisieactivite'
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@permission_required('activite.add_saisieactivite')
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
    

@permission_required('activite.add_saisieactivite')
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


@permission_required('activite.add_saisieactivite')
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


@permission_required('activite.add_saisieactivite')
def ajax_update_salaries(request):
    """
        Mise a joru de a liste des salariés
    """
    cegid = CegidCloud()
    salarie_list = cegid.get_salarie_list()
    # print(salarie_list)
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
        sal.prenom = salarie_cegid['FirstName']
        sal.date_entree = pendulum.parse(salarie_cegid['EntryDate']).to_date_string()
        sal.date_sortie = pendulum.parse(salarie_cegid['ExitDate']).to_date_string()
        sal.save()
    ret = { "result": "ok", "count": count, "ajoute": ajoute, }
    return JsonResponse(ret)

@permission_required('activite.add_saisieactivite')
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


@permission_required('activite.add_saisieactivite')
def ajax_update_article(request):
    """
        Mise a jour de la liste des rubriques
        TODO : Exclure les articles fermés
        TODO : Gérer les articles fermés
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
            rub_paie = None
        except RubriquePaie.DoesNotExist:
            rub_paie = None
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


@permission_required('activite.add_saisieactivite')
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


@permission_required('activite.add_saisieactivite')
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
            print(f"L'adhérent {affaire_cegid['ThirdParty_AFF']} pour l'affaire {affaire_cegid['Project_AFF']} n'existe pas en base django: As-il été importé ?")
            error = True
            error_count += 1
        

        try:
            salarie = Salarie.objects.get(code_erp=affaire_cegid['Manager_AFF'])
        except AttributeError:
            print(f"l'affaire {affaire_cegid['Project_AFF']} n'a pas de salarié.")
            error = True
            error_count += 1
        except Salarie.DoesNotExist:
            print(f"l'affaire {affaire_cegid['Project_AFF']} ne sera pas ajoutée : Le salarié {affaire_cegid['Manager_AFF']} est sorti")
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

            # On vérifie le code. Si différent, il faudra voir quelle mad on garde
            if mad.code_erp != affaire_cegid['Project_AFF']:
                # On abandonne la suite si l'affaire est close
                print(f"EE:{affaire_cegid['Project_AFF']} : Une affaire porte déja ce nom avec un code différent : {mad.code_erp}")
                if affaire_cegid['State_AFF'] == "CLO":
                    print(f"EE : L'affaire {affaire_cegid['Project_AFF']} est fermée. On ne l'enregistre pas")
                    pprint(affaire_cegid)
                    continue
            mad.code_erp = affaire_cegid['Project_AFF']
            mad.duree_travail_mensuel = affaire_cegid['UserFieldNumeric2_AFF']
            mad.duree_travail_quotidien = affaire_cegid['UserFieldNumeric3_AFF']
            mad.service = Service.objects.filter(code_erp=affaire_cegid['UserField1_AFF']).first()
            mad.poste = Poste.objects.filter(code_erp=affaire_cegid['UserField2_AFF']).first()
            if affaire_cegid['State_AFF'] == "CLO":
                mad.cloturee = True
            else:
                mad.cloturee = False
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


@permission_required('activite.add_saisieactivite')
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
    pprint(activite_dict_array)
    response = cegid.save_activite_list(activite_dict_array)
    if response.status_code == 200:
        # On est ok, on marque les activités comme envoyées
        for activite in activite_list:
            activite.uploaded = True
            activite.save()
    else:
        print(response.status_code)
        print(response.text)
    return HttpResponse(response.text)


@permission_required('activite.add_saisieactivite')
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


@permission_required('activite.add_saisieactivite')
def ajax_upload_paie(request, annee, mois):
    # liste les salariés, puis envoie la paie
    sal_list = Salarie.objects.all()
    paie_list = []
    for sal in sal_list:
        paie_list += sal.get_paie(annee, mois)

    cegid = CegidCloud()
    pprint(paie_list)
    response = cegid.save_paie_list(paie_list)
    if response.status_code == 200 or response.status_code == 204:
        ret = {
            "class": "bg-success",
            "title": "Paie envoyée",
            "body": f"Les rubriques de paie ont été envoyées vers Y2",
        }
    else:
        ret = {
            "class": "bg-error",
            "title": "Echec",
            "body": f"Echec d'envoi de la paie : {response.status_code}\n{response.text}",
        }
    return JsonResponse(ret)


@permission_required('activite.add_saisieactivite')
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


@csrf_exempt
@permission_required('activite.add_saisieactivite')
def update_memo(request, id_info_sup):
    print(str(request.body))
    data = json.loads(request.body.decode("utf-8"))
    try:
        ismm = InfosSupMoisSalarie.objects.get(id=id_info_sup)
    except InfosSupMoisSalarie.DoesNotExist:
        ret = {
            "class": "bg-error",
            "title": "Erreur",
            "body": "Info Sup n'existe pas",
        }
    else:
        ismm.memo = data['memo']
        ismm.save()
        ret = {
            "class": "bg-success",
            "title": "memo mis à jour",
            "body": f"Le mémo a été mis à jour.",
        }
    return JsonResponse(ret)


@csrf_exempt
@permission_required('activite.add_saisieactivite')
def update_infosup_salarie(request, salarie_id, annee, mois):
    """
        Sauvegarde les infosup du salarié avec le json passé en paramètre
        Champs pris en compe :
    """
    data = json.loads(request.body.decode("utf-8"))
    try:
        sal = Salarie.objects.get(id=salarie_id)
    except Salarie.DoesNotExist:
        return JsonResponse({
            "class": "bg-error",
            "title": "Erreur",
            "body": "Le salarié n'existe pas",
        })
    infosup = sal.get_info_sup(mois, annee)
    infosup.heures_theoriques = round(float(data['heures_theoriques']), 2)
    infosup.difference_heures = round(data['difference_heures'], 2)
    infosup.save()
    return JsonResponse({
        "class": "bg-success",
        "title": "Données mises à jour",
        "body": "Les infos du salarié relatives a cette période ont été enregistrées",
    })

@permission_required('activite.add_saisieactivite')
def infosup_salarie_mois_precedent(request, salarie_id, annee, mois):
    """
        Retourne le mémo du mois précédent, si il y a. 
    """
    date_actu = date(annee, mois, 1)
    date_precedent = date_actu - timedelta(days=3)
    # Récupération de l'infosup correpondant
    try:
        salarie = Salarie.objects.get(id=salarie_id)
    except Salarie.DoesNotExist:
        return JsonResponse({"memo": ""})
    try:
        infosup = InfosSupMoisSalarie.objects.get(salarie=salarie, mois=date_precedent.month, annee=date_precedent.year)
    except InfosSupMoisSalarie.DoesNotExist:
        return JsonResponse({"memo": ""})
    
    return JsonResponse({"memo": infosup.memo})


@permission_required('activite.add_saisieactivite')
def ajax_envoi_paie(request, salarie_id, annee, mois):
    """
        Envoie la paie du salarié vers Y2
    """
    try:
        sal = Salarie.objects.get(id=salarie_id)
    except Salarie.DoesNotExist:
        return JsonResponse({
            "class": "bg-error",
            "title": "Erreur",
            "body": "Le salarié n'existe pas",
            "error": True,
        })
    infosup = sal.get_info_sup(mois, annee)
    paie = sal.get_paie(annee, mois)
    cloud = CegidCloud()
    response = cloud.save_paie_list(paie)
    if response.status_code == 200 or response.status_code == 204:
        infosup.paie_envoyee = True
        infosup.save()
        return JsonResponse({
            "class": "bg-success",
            "title": "Paie envoyée",
            "body": f"la paie du salarié {sal} pour la période {mois}/{annee} a été envoyée",
            "error": False,
        })
    else:
        return JsonResponse({
            "class": "bg-error",
            "title": "Erreur",
            "body": f"Erreur d'envoi vers l'ERP<br />{response.text}",
            "error": True,
        })


@permission_required('activite.add_saisieactivite')
def download_paie(request, annee, mois):
    """
        Télécharge un fichier de paie a importer dans Y2
    """
    # Salariés ayant fait des saisies dans le mois
    buletin_lines = f"***DEBUT***\r\n000;000000;01/01/{annee};31/12/{annee}\r\n"
    salarie_list = (
        TarifGe.objects
        .filter(mise_a_disposition__cloturee=False)
        .filter(article__facturation_uniquement=False)
        .filter(saisie_activite_list__date_realisation__year=annee)
        .filter(saisie_activite_list__date_realisation__month=mois)
        .exclude(article__rubrique_paie=None)
        .annotate(quantites = Sum('saisie_activite_list__quantite'))
        .exclude(quantites=None)
        .exclude(quantites=0)
        .values('mise_a_disposition__salarie')
        .distinct()
    )
    for salarie in salarie_list:
        sal = Salarie.objects.get(id=salarie['mise_a_disposition__salarie'])
        b = sal.get_paie(annee, mois)
        for line in b:
            debut = line['BeginDatePayroll'][8:10] + "/" + line['BeginDatePayroll'][5:7]+ "/" + line['BeginDatePayroll'][:4]
            fin = line['EndDatePayroll'][8:10] + "/" + line['EndDatePayroll'][5:7]+ "/" + line['EndDatePayroll'][:4]
            print(debut)
            buletin_lines += f"{line['ImportType']};{line['EmployeeId']};{debut};{fin};{line['NumberOrder']};{line['Rubric']};{line['RubricLabelSubstitution']};{line['TypeSupplyRubric']};{line['PayrollBase']};{line['PayrollRate']};;\r\n"
    buletin_lines += "***FIN***\r\n"
    print(buletin_lines)
    resp = HttpResponse(content_type='application/force-download')
    resp['Content-Disposition'] = f"attachment; filename={annee}-{mois}-paie.trt"
    resp.write(unicodedata.normalize('NFKD', buletin_lines).encode('iso-8859-1', 'ignore'))
    return resp


@permission_required('activite.add_saisieactivite')
def download_releve_adherent(request, mois, annee):
    """
        Téléchargement des pdf a envoyer au adherents
    """
    ret = []
    template = "adherent_releve_print.html"
    date_str = date(annee, mois, 1).strftime("%B") + " " + str(annee)
    # adherent_list = Adherent.objects.all().order_by("raison_sociale")
    # adherent_list = Adherent.objects.exclude(raison_sociale="PROGRESSIS").filter(raison_sociale__in=["MANUPLAST"])
    adherent_list = Adherent.objects.exclude(raison_sociale="PROGRESSIS").order_by("raison_sociale")
    for adherent in adherent_list:
        # liste des mises a dispo de l'adhérent
        mad_list = adherent.mise_a_disposition_list.filter(cloturee=False).exclude(salarie__user_profile=None)
        for mad in mad_list:
            
            # On regarde si il y a des saisies pour cette mad sur le mois
            saisie_count = SaisieActivite.objects.filter(tarif__mise_a_disposition=mad).filter(date_realisation__month=mois, date_realisation__year=annee).count()
            if saisie_count != 0:
                mad_dict = model_to_dict(mad)
                # releve
                # récupérétion du relevé du mois, et création si il n'existe pas

                # salarie = Salarie.objects.get(pk=salarie_id)
                salarie_dict = model_to_dict(mad.salarie)
                mad_dict['salarie'] = salarie_dict
                mad_dict['adherent'] = model_to_dict(adherent)  
                # Infos supplémentaires des salariés
                # salarie_info_sup = mad.salarie.get_info_sup(mois, annee)
                # mad_dict['salarie']['infos_sup'] = model_to_dict(salarie_info_sup)
                # mad_dict['salarie']['infos_sup']['heures_travaillees'] = salarie_info_sup.heures_travaillees

                # Liste des tarifs
                mad_dict['tarifs_ge'] = mad.tarif_ge_list_dict

                # Primes Fofaitaires
                # mad_dict['primes_forfaitaires'] = mad.tarifs_ge_prime_forfaitaire_dict()

                # Liste des jours, des saisies, etc, pour construire le tableau de saisie
                mad_dict['jour_list'] = mad.get_saisies_from_mois_dict_all(mois, annee)

                # informations supplémentaires des mises a disposition
                # mad_dict['infos_sup'] = model_to_dict(mad.get_info_sup(mois, annee))

                # Liste des primes forfaitaires enregistrées
                # mad_dict['prime_forfaitaires_values'] = mad.prime_forfaitaire_values_list(annee, mois)
                ret.append(mad_dict)


    """
    ret = []
    template = "adherent_releve_print.html"
    # adherent_list = Adherent.objects.all().order_by("raison_sociale")
    # adherent_list = Adherent.objects.exclude(raison_sociale="PROGRESSIS").filter(raison_sociale__in=["MANUPLAST"])
    adherent_list = Adherent.objects.exclude(raison_sociale="PROGRESSIS").order_by("raison_sociale")
    for adherent in adherent_list:
        # liste des mises a dispo de l'adhérent
        mad_list = adherent.mise_a_disposition_list.filter(cloturee=False)
        for mad in mad_list:
            
            # On regarde si il y a des saisies pour cette mad sur le mois
            saisie_count = SaisieActivite.objects.filter(tarif__mise_a_disposition=mad).filter(date_realisation__month=mois, date_realisation__year=annee).count()
            if saisie_count != 0:
                mad_dict = model_to_dict(mad)
                # releve
                # récupérétion du relevé du mois, et création si il n'existe pas

                # salarie = Salarie.objects.get(pk=salarie_id)
                salarie_dict = model_to_dict(mad.salarie)
                mad_dict['salarie'] = salarie_dict
                mad_dict['adherent'] = model_to_dict(adherent)  
                # Infos supplémentaires des salariés
                # salarie_info_sup = mad.salarie.get_info_sup(mois, annee)
                # mad_dict['salarie']['infos_sup'] = model_to_dict(salarie_info_sup)
                # mad_dict['salarie']['infos_sup']['heures_travaillees'] = salarie_info_sup.heures_travaillees

                # Liste des tarifs
                mad_dict['tarifs_ge'] = mad.tarif_ge_list_dict

                # Primes Fofaitaires
                # mad_dict['primes_forfaitaires'] = mad.tarifs_ge_prime_forfaitaire_dict()

                # Liste des jours, des saisies, etc, pour construire le tableau de saisie
                mad_dict['jour_list'] = mad.get_saisies_from_mois_dict_all(mois, annee)

                # informations supplémentaires des mises a disposition
                # mad_dict['infos_sup'] = model_to_dict(mad.get_info_sup(mois, annee))

                # Liste des primes forfaitaires enregistrées
                # mad_dict['prime_forfaitaires_values'] = mad.prime_forfaitaire_values_list(annee, mois)
                ret.append(mad_dict)

    """
    context = {
        "mad_list": ret,
        "date_str": date_str,
    }
    return render(request, template, context)

def gen_releve_adherent(request, annee, mois):
    generate_releve_adherent.delay(mois=mois, annee=annee)
    return JsonResponse({"status": "ok"})


class SalarieViewSet(viewsets.ModelViewSet):
    queryset = Salarie.objects.all()
    serializer_class = SalarieSerializer

    def get_queryset(self):
        qs = Salarie.get_salaries_actuels()
        salarie_nom_prenom = self.request.query_params.get('salarie_nom_prenom', None)
        code_cegid = self.request.query_params.get('code_cegid', None)
        if salarie_nom_prenom is not None:
            qs = qs.filter(Q(nom__icontains=salarie_nom_prenom) | Q(prenom__icontains=salarie_nom_prenom))

        if code_cegid is not None:
            qs = qs.filter(code_erp__contains=code_cegid)
        
        return qs