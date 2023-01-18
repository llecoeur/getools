from celery import shared_task
from activite.models import Adherent, SaisieActivite
from django.forms.models import model_to_dict
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML
from datetime import date
from zipfile import ZipFile
from conge.tasks import envoi_email
from config.models import Config
import locale
import os
import pwd
import grp


@shared_task
def test(*args, **kwargs):

    return f"mois={kwargs['mois']}, annee={kwargs['annee']}"


@shared_task
def generate_releve_adherent_old(*args, **kwargs):
    locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")
    mois = kwargs['mois']
    annee = kwargs['annee']
    print(f"génération du relevé {mois} - {annee}")
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

    context = {
        "mad_list": ret,
        "date_str": date_str.capitalize(),
    }
    f_content = render_to_string(template, context)
    html_path = f"{settings.STATIC_ROOT}releve_adherents/{annee}-{mois}.html" 
    pdf_path = f"{settings.STATIC_ROOT}releve_adherents/{annee}-{mois}.pdf"
    with open(html_path,"w") as f:
        f.write(f_content)
    HTML(html_path).write_pdf(pdf_path)
    return f"{html_path} généré"


@shared_task
def generate_releve_adherent(*args, **kwargs):
    locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")
    mois = kwargs['mois']
    annee = kwargs['annee']
    print(f"génération du relevé {mois} - {annee}")
    template = "adherent_releve_print.html"
    date_str = date(annee, mois, 1).strftime("%B") + " " + str(annee)

    # adherent_list = Adherent.objects.all().order_by("raison_sociale")
    # adherent_list = Adherent.objects.exclude(raison_sociale="PROGRESSIS").filter(raison_sociale__in=["MANUPLAST"])
    adherent_list = Adherent.objects.exclude(raison_sociale="PROGRESSIS").order_by("raison_sociale")
    zip_path = f"{settings.STATIC_ROOT}releve_adherents/{annee}-{mois}.zip"
    # suppression du zip si il existe
    try:
        os.remove(zip_path)
    except OSError:
        pass
    zipObj = ZipFile(zip_path, 'w')
    
    for adherent in adherent_list:
        # liste des mises a dispo de l'adhérent
        mad_list = adherent.mise_a_disposition_list.filter(cloturee=False).exclude(salarie__user_profile=None)
        ret = []
        
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
        if len(ret) != 0:
            print(f"{adherent.raison_sociale} - nbre de mad : {len(ret)}")
            # On ne genere que si il y a au moins une mad pour cet adhérent
            context = {
                "mad_list": ret,
                "date_str": date_str.capitalize(),
            }
            f_content = render_to_string(template, context)
            try:
                os.mkdir(f"{settings.STATIC_ROOT}releve_adherents/{annee}-{mois}")
            except FileExistsError:
                print("Création du répertoire impossible")
                pass
            html_path = f"{settings.STATIC_ROOT}releve_adherents/{annee}-{mois}/{adherent.raison_sociale}_{annee}-{mois}.html" 
            pdf_path = f"{settings.STATIC_ROOT}releve_adherents/{annee}-{mois}/{adherent.raison_sociale}_{annee}-{mois}.pdf"
            with open(html_path,"w") as f:
                f.write(f_content)
            HTML(html_path).write_pdf(pdf_path)
            
            zipObj.write(pdf_path, arcname=f"{adherent.raison_sociale}_{annee}-{mois}.pdf")
            os.remove(html_path)
            os.remove(pdf_path)
            # Création du ZIP

    zipObj.close()
    # modification des droits
    
    """    uid = pwd.getpwnam("www-data").pw_uid
    gid = grp.getgrnam("www-data").gr_gid
    os.chown(zip_path, uid, gid)
    zip_path"""
    os.chmod(zip_path, 0o777)
    try:
        os.rmdir(f"{settings.STATIC_ROOT}releve_adherents/{annee}-{mois}")
    except OSError:
        pass

    # Envoi du mail pour dire que c'est ok !
    subject = f"Le relevé adhérent {annee}-{mois}.zip a été généré"
    email_template_name = "email_releve_ok.txt"
    c = {
        'domain': Config.objects.get(key="SITE_DOMAIN").str_val,
        'port': Config.objects.get(key="SITE_PORT").str_val,
        'protocol': Config.objects.get(key="SITE_PROTOCOL").str_val,
        'file': f"{annee}-{mois}.zip"
    }
    body = render_to_string(email_template_name, c)
    envoi_email.delay(subject=subject, body=body, recipient=Config.objects.get(key="EMAIL_RELEVE_ADHEREN").str_val)

    return f"pdf généré"