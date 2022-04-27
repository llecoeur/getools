from re import L
from django.utils import timezone
from celery import shared_task
from .models import DemandeConge, ValidationAdherent
from datetime import datetime, timedelta
from django.conf import settings



@shared_task(name="valid_conges_14_jours")
def valid_conges_14_jours(*args, **kwargs):
    """
        Valide toutes les demandes de congés sans validations depuis 14 jours
    """
    demande_list = DemandeConge.objects.filter(conge_valide=False, conge_envoye_date__lt=timezone.now() - settings.CONGE_DELTA_VALIDE)
    for demande in demande_list:
        validation_list = demande.validation_adherent_list(is_valid=None, is_progressis=False)
        for validation in validation_list:
            print(f"Validation du congé pour délais d'acceptation dépassé pour {validation.id} : {validation.email}")
            validation.is_valid = False
            validation.is_valid_timeout = True
            validation.slug_acceptation = ""
            validation.slug_refus = ""
            validation.save()
        demande.valid()

@shared_task(name="rappel_11_jours")
def rappel_11_jours(*args, **kwargs):
    demande_list = DemandeConge.objects.filter(conge_valide=False, conge_envoye_date__lt=timezone.now() - settings.CONGE_DELTA_RAPPEL)
    for demande in demande_list:
        validation_list = demande.validation_adherent_list(is_valid=None)
        for validation in validation_list:
            print(f"envoi du rappel pour {validation.id} : {validation.email}")
            validation.send_email_rappel()





@shared_task(name="delete_demande_conge_brouillon")
def delete_demande_conge_brouillon(*args, **kwargs):
    """
        Efface les demandes de congés non envoyées qui trainent depuis 2 jours
    """
    n = DemandeConge.objects.filter(conge_envoye=False, updated__lt=timezone.now() - settings.CONGE_DELTA_SUPPRIME_VIDE).delete()
    print(f"Demandes en brouillon supprimées {n}")

@shared_task(name="envoi_conge_charge_dev")
def envoi_conge_charge_dev(*args, **kwargs):
    """
        Envoi des congés validés pour tout le monde au chargé de dev pour validation.
    """

    qs = DemandeConge.objects.filter(responsable_en_cours=False)
    for demande in qs:
        if demande.is_all_accepted():
            # ajout d'une demande de validation au chargé de dev
            va = ValidationAdherent()
            va.demande = demande
            va.email = settings.CHARGE_DEV_CONGE_EMAIL
            va.nom_prenom = settings.CHARGE_DEV_CONGE_NOM
            va.save()
            va.send_email()
            demande.responsable_en_cours = True
            demande.save()
