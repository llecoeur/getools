# Divers fonctions utiles...
from django.utils import timezone
from datetime import datetime, date, timedelta

def annee_mois_precedent():
    """
        Retourne un tuple (annee, mois) correspondant au mois précédent
    """
    actu = timezone.now()
    date_dernier_jour = date(actu.year, actu.month, 1) - timedelta(days=2)
    return (date_dernier_jour.year, date_dernier_jour.month)
