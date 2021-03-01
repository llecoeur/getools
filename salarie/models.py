from django.db import models
from activite.models import Salarie, MiseADisposition, Adherent

# Create your models here.


class CalendrierSalarie(models.Model):

    """
        Classe calendrier salarié
        Cette classe permet d'assigner des mises a dispositions sur les jours de la semaine, associés a des commentaires.
        Le but est de crééer un planning hebdomadaire type pour chaque salarié, et retrouver ou il est mis a disposition.
    """
    salarie = models.ForeignKey(Salarie, on_delete=models.CASCADE, related_name="calendrier_salarie_list", db_index=True)
    commentaire = models.TextField("Notes", null=False, blank=True, default="")

    class Meta:
        ordering = ['salarie__nom']


class CalendrierSalariePeriode(models.Model):
    """
        Classe des périodes de journées, permettant de découper les jours
    """
    # Nom de la période, par exemple, matin, après midi, ou 9h-10h
    nom = models.CharField("Nom de la période", null=False, blank=False, unique=True, max_length=30)
    # Ordre dans le jour, pour classer le matin avant l'après midi
    ordre = models.IntegerField("ordre dans le jour")
    
    class Meta:
        ordering = ['nom', 'ordre']


class CalendrierSalarieMiseADisposition(models.Model):

    # Calendrier lié
    calendrier = models.ForeignKey("CalendrierSalarie", on_delete=models.CASCADE, related_name="mise_a_disposition_list", db_index=True)
    # commentaire éventuel
    commentaire = models.CharField("Notes", null=False, blank=True, default="", max_length=200)
    # Numéro du jour de la semaine. lundi=0, dimanche=6
    num_jour = models.IntegerField("Jour", null=False, blank=False, default=0)
    # Permet de dire sur quelle période de la journée est la mise a dispsition.
    # Si None, alors c'est toute la journée
    periode = models.ForeignKey("CalendrierSalariePeriode", on_delete=models.CASCADE, null=True, default=None)

    class Meta:
        ordering = ['num_jour', 'periode__ordre']
