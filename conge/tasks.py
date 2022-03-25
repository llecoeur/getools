from re import L
from celery import shared_task
from .models import DemandeConge, ValidationAdherent
from datetime import datetime, timedelta
from django.conf import settings




@shared_task
def delete_demande_conge_brouillon(*args, **kwargs):
    """
        Efface les demandes de congés non envoyées qui trainent depuis 2 jours
    """
    DemandeConge.objects.filter(conge_envoye=False, updated__lt=datetime.now() - timedelta(days=2)).delete()

@shared_task
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
