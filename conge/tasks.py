from re import L
from django.utils import timezone
from celery import shared_task
from datetime import datetime, timedelta
from django.conf import settings
from django.template.loader import render_to_string
from getools.utils import send_mail
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)


@shared_task(name="valid_conges_14_jours")
def valid_conges_14_jours(*args, **kwargs):
    """
        Valide toutes les demandes de congés sans validations depuis 14 jours
    """
    from .models import DemandeConge, ValidationAdherent

    demande_list = DemandeConge.objects.filter(conge_valide=False, conge_envoye_date__lt=timezone.now() - settings.CONGE_DELTA_VALIDE)
    # print(f"nb_demandes_14jours={demande_list.count()}")
    for demande in demande_list:
        # print(f"demande = {demande}")
        validation_list = demande.validation_adherent_list.filter(is_valid=None, is_progressis=False)
        # print(validation_list)
        for validation in validation_list:
            print(f"Validation du congé pour délais d'acceptation dépassé pour {validation.id} : {validation.email}")
            validation.accept_by_delay()
            validation.is_valid = True
            validation.is_valid_timeout = True
            validation.slug_acceptation = ""
            validation.slug_refus = ""
            validation.save()
        demande.valid()

@shared_task(name="rappel_11_jours")
def rappel_11_jours(*args, **kwargs):
    from .models import DemandeConge, ValidationAdherent

    demande_list = DemandeConge.objects.filter(conge_valide=False, conge_envoye_date__lt=timezone.now() - settings.CONGE_DELTA_RAPPEL)
    for demande in demande_list:
        validation_list = demande.validation_adherent_list.filter(is_rappel_envoye=False, is_valid=None)
        for validation in validation_list:
            # print(f"envoi du rappel pour {validation.id} : {validation.email}")
            validation.send_email_rappel()


@shared_task(name="delete_demande_conge_brouillon")
def delete_demande_conge_brouillon(*args, **kwargs):
    """
        Efface les demandes de congés non envoyées qui trainent depuis 2 jours
    """
    from .models import DemandeConge, ValidationAdherent

    n = DemandeConge.objects.filter(conge_envoye=False, updated__lt=timezone.now() - settings.CONGE_DELTA_SUPPRIME_VIDE).delete()


@shared_task(name="envoi_conge_charge_dev")
def envoi_conge_charge_dev(*args, **kwargs):
    """
        Envoi des congés validés pour tout le monde au chargé de dev pour validation.
    """
    from .models import DemandeConge, ValidationAdherent

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

@shared_task(name="envoi_email")
def envoi_email(*args, **kwargs):
    """
        Envoi des email via la message queue.
    """
    ret = send_mail(
        kwargs['subject'],
        kwargs['body'],
        kwargs['recipient']
    )