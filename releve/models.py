from django.db import models
from django.utils import timezone
from activite.models import Adherent
from django.forms.models import model_to_dict
from django.conf import settings


class ReleveSalarie(models.Model):

    mois = models.IntegerField("Mois", db_index=True)
    annee = models.IntegerField("Année", db_index=True)
    salarie = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Salarié", related_name="releve_heures_list", on_delete=models.CASCADE)
    saisie_complete = models.BooleanField("Saisie Complète ?", db_index=True)
    saisie_complete_date = models.DateTimeField("Date de Saisie Complete")
    commentaire = models.TextField("Commentaires")

    created = models.DateTimeField("Date de création")
    updated = models.DateTimeField("Date de modification")

    def __str__(self):
        pass

    def save():
        if not self.id:
            self.created = timezone.now()
        self.updated = timezone.now()
        super().save()


class SaisieSalarie(models.Model):
    date = models.DateField("Date", db_index=True)
    heures = models.FloatField("Heures", db_index=True)
    releve = models.ForeignKey(ReleveSalarie, verbose_name="Relevé", related_name="saisie_salarie_list", on_delete=models.CASCADE)
    adherent = models.ForeignKey(Adherent, verbose_name="Adhérent", related_name="saisie_salarie_list", on_delete=models.CASCADE)
    created = models.DateTimeField("Date de création")
    updated = models.DateTimeField("Date de modification")

    def __str__(self):
        return self.heures

    def save():
        if not self.id:
            self.created = timezone.now()
        self.updated = timezone.now()
        super().save()
