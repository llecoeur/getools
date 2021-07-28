"""
    Regroupe des fonctions de statistiques, pour par exemple afficher les écrans d'accueil
    Ce snt soit des indicateurs, soit des données pour des graphiques
"""

from activite.models import SaisieActivite
from django.db.models import Q, Sum


def get_total_heures_all_adherents(annee, mois):
    """
        Retourne le nombre total d'heures passées chez des adhérents pour le mois donné
        Comprend les heures normales uniquement, les heures complémentaires sont exclues des stats, HORS adhérent prgressis
    """
    q = (
        SaisieActivite.objects
        .filter(date_realisation__month=mois, date_realisation__year=annee)
        .filter(tarif__article__libelle="HEURES NORMALES")
        .exclude(tarif__mise_a_disposition__adherent__raison_sociale="PROGRESSIS")
        .exclude(tarif__article__famille__forfaitaire=True)
        .aggregate(Sum("quantite"))
    )
    if q['quantite__sum'] is not None:
        return q['quantite__sum']
    else:
        return 0


def get_total_value_search(annee, mois, article_list=None, adherent_list=None, salarie_list=None, salarie_exclude=None, progressis=True):
    """
        Retourne toutes les heures du mois donné, pour chaque paramètre passé
    """

    q = SaisieActivite.objects.filter(date_realisation__month=mois, date_realisation__year=annee)
    if article_list:
        q = q.filter(tarif__article__in=article_list)
    if adherent_list:
        q = q.filter(tarif__mise_a_disposition__adherent__in=adherent_list)
    if salarie_list:
        q = q.filter(tarif__mise_a_disposition__salarie__in=salarie_list)
    if salarie_exclude:
        q = q.exclude(tarif__mise_a_disposition__salarie__in=salarie_exclude)
    if progressis is False:
        q = q.exclude(tarif__mise_a_disposition__adherent__raison_sociale="PROGRESSIS")
    q = q.aggregate(Sum("quantite"))
    if q['quantite__sum'] is not None:
        return q['quantite__sum']
    else:
        return 0