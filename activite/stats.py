"""
    Regroupe des fonctions de statistiques, pour par exemple afficher les écrans d'accueil
    Ce snt soit des indicateurs, soit des données pour des graphiques
"""

from activite.models import SaisieActivite
from django.db.models import Q, Sum


def get_total_heures_all_adherents(annee, mois):
    """
        Retourne le nombre total d'heures passées chez des adhérents pour le mois donné
        Comprend les heures normales et heures supplémentaires, HORS adhérent prgressis
    """
    q = (
        SaisieActivite.objects
        .filter(date_realisation__month=mois, date_realisation__year=annee)
        .filter(Q(tarif__article__libelle="HEURES NORMALES") | Q(tarif__article__libelle__startswith="HEURES SUPPLEMENTAIRES") )
        .exclude(tarif__mise_a_disposition__adherent__raison_sociale="PROGRESSIS")
        .exclude(tarif__article__famille__forfaitaire=True)
        .aggregate(Sum("quantite"))
    )
    if q['quantite__sum'] is not None:
        return q['quantite__sum']
    else:
        return 0




