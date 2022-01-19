from celery import shared_task
from .models import DemandeConge
from datetime import datetime, timedelta




@shared_task
def delete_demande_conge_brouillon(*args, **kwargs):
    """
        Efface les demandes de congés non envoyées qui trainent depuis 2 jours
    """
    DemandeConge.objects.filter(conge_envoye=False, updated__lt=datetime.now() - timedelta(days=2)).delete()
