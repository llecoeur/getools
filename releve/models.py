from django.db import models
from django.utils import timezone
from activite.models import Adherent, Salarie
from django.forms.models import model_to_dict
from django.conf import settings


class ReleveSalarie(models.Model):

    mois = models.IntegerField("Mois", db_index=True)
    annee = models.IntegerField("Année", db_index=True)
    salarie = models.ForeignKey(Salarie, verbose_name="Salarié", related_name="releve_heures_list", on_delete=models.CASCADE)
    saisie_complete = models.BooleanField("Saisie Complète ?", db_index=True, default=False)
    saisie_complete_date = models.DateTimeField("Date de Saisie Complete", null=True, default=None)
    commentaire = models.TextField("Commentaires", default="")

    created = models.DateTimeField("Date de création")
    updated = models.DateTimeField("Date de modification")

    def __str__(self):
        return f"{self.annee}-{self.mois} {self.salarie}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.updated = timezone.now()
        super().save(*args, **kwargs)

    def get_saisie(self, adherent, date_saisie):
        """
            Retourne l'objet saisie de l'adherent a cette date.
            Si ca n'existe pas en base, alors ca la cree avec 0 en quantite d'heures
        """
        try:
            saisie = self.saisie_salarie_list.get(adherent=adherent, date=date_saisie)
        except SaisieSalarie.DoesNotExist:
            saisie = SaisieSalarie()
            saisie.date = date_saisie
            saisie.adherent = adherent
            saisie.heures = 0
            saisie.releve = self
            saisie.save()

        return saisie


class SaisieSalarie(models.Model):
    date = models.DateField("Date", db_index=True)
    heures = models.FloatField("Heures", db_index=True, default=0, null=False)
    releve = models.ForeignKey(ReleveSalarie, verbose_name="Relevé", related_name="saisie_salarie_list", on_delete=models.CASCADE, db_index=True)
    adherent = models.ForeignKey(Adherent, verbose_name="Adhérent", related_name="saisie_salarie_list", on_delete=models.CASCADE, db_index=True)
    commentaire = models.TextField("Commentaire", null=False, default="")
    created = models.DateTimeField("Date de création", db_index=True)
    updated = models.DateTimeField("Date de modification", db_index=True)

    def __str__(self):
        return self.heures

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.updated = timezone.now()
        super().save(*args, **kwargs)


