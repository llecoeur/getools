from django.db import models
from activite.models import Salarie, MiseADisposition, Adherent
from calendar import Calendar

# Create your models here.


class CalendrierSalarie(models.Model):

    """
        Classe calendrier salarié
        Cette classe permet d'assigner des mises a dispositions sur les jours de la semaine, associés a des commentaires.
        Le but est de crééer un planning hebdomadaire type pour chaque salarié, et retrouver ou il est mis a disposition.
    """
    salarie = models.OneToOneField(Salarie, on_delete=models.SET_NULL, related_name="calendrier", db_index=True, null=True, blank=True, default=None)
    commentaire = models.TextField("Notes", null=False, blank=True, default="")

    jour_name = ['Lundi', "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    class Meta:
        ordering = ['salarie__nom']

    def __str__(self):
        return str(self.salarie)

    @property
    def calendar(self):
        cal = Calendar()
        
        week = []
        for day in cal.iterweekdays():
            d = {
                "txt": self.jour_name[day],
                "num": day,
                "mad_list": self.get_mads(day),
            }
            if day in [0, 1, 2, 3, 4]:
                week.append(d)
            else:
                if d['mad_list'].count() != 0:
                    week.append(d)
        return week

    def get_mads(self, num_jour):
        """
            Retourne les mads du jour, groupés et ordonnés par Période
        """
        qs = (
            self.mise_a_disposition_list
            .filter(num_jour=num_jour)
            .order_by("periode__ordre", "periode__nom")
        )
        return qs




class CalendrierSalariePeriode(models.Model):
    """
        Classe des périodes de journées, permettant de découper les jours
    """
    # Nom de la période, par exemple, matin, après midi, ou 9h-10h
    nom = models.CharField("Nom de la période", null=False, blank=False, unique=True, max_length=30)
    # Ordre dans le jour, pour classer le matin avant l'après midi
    ordre = models.IntegerField("ordre dans le jour")

    class Meta:
        ordering = ['ordre', 'nom']

    def __str__(self):
        return self.nom

class CalendrierSalarieRecurence(models.Model):
    """
        Classe des périodes de journées, permettant de découper les jours
    """
    # Nom de la période, par exemple, matin, après midi, ou 9h-10h
    nom = models.CharField("Nom de la période", null=False, blank=False, unique=True, max_length=30)
    # Ordre dans le jour, pour classer le matin avant l'après midi
    ordre = models.IntegerField("ordre dans le jour")

    class Meta:
        ordering = ['ordre', 'nom']

    def __str__(self):
        return self.nom


class CalendrierSalarieMiseADisposition(models.Model):

    
    # commentaire éventuel
    commentaire = models.CharField("Notes", null=False, blank=True, default="", max_length=200)
    # Si None, alors c'est toute la journée
    periode = models.ForeignKey("CalendrierSalariePeriode", on_delete=models.CASCADE, null=False, blank=False, default=1)
    # Récurence. C'est juste un texte sur une table liée
    recurence = models.ForeignKey("CalendrierSalarieRecurence", on_delete=models.SET_NULL, null=True, blank=True, default=None)
    # Mise a disposition
    adherent = models.ForeignKey(Adherent, on_delete=models.CASCADE, null=True, blank=True, db_index=True, default=None)
    # Calendrier lié
    calendrier = models.ForeignKey("CalendrierSalarie", on_delete=models.CASCADE, related_name="mise_a_disposition_list", db_index=True, null=True, default=None)
    # Numéro du jour de la semaine. lundi=0, dimanche=6
    num_jour = models.IntegerField("Jour", null=False, blank=False, default=0)



    class Meta:
        ordering = ["periode"]

    def __str__(self):
        txt =  ""
        if self.adherent:
            txt += f"{self.adherent.raison_sociale}"
        txt += f" ({self.periode.nom})"
        if self.commentaire != "":
            txt += f" : {self.commentaire}"
        return txt