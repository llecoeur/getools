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

    created = models.DateTimeField("Date de création", db_index=True, editable=False)
    updated = models.DateTimeField("Date de modification", db_index=True, editable=False)

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
            Si adherent est None, alors c'est une absence
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
    """
        Saisie de temps pour le relevé salarié
    """
    # Date de la saisie
    date = models.DateField("Date", db_index=True)
    # Nombre d'heures passées sur la MAD ou en absence
    heures = models.FloatField("Heures", db_index=True, default=0, null=False)
    # Relevé associé
    releve = models.ForeignKey(ReleveSalarie, verbose_name="Relevé", related_name="saisie_salarie_list", on_delete=models.CASCADE, db_index=True)
    # Adhérent associé. Si None, alors c'est une absence
    adherent = models.ForeignKey(Adherent, verbose_name="Adhérent", related_name="saisie_salarie_list", on_delete=models.CASCADE, db_index=True, null=True, default=None)
    # Commentaire éventuel. Surtout utilisé pour les absences
    commentaire = models.TextField("Commentaire", null=True, default="", blank=True)
    # La saisie a été sauvegardée
    saved = models.BooleanField("Sauvegardé ?", null=False, default=False)

    # Champs automatiques
    created = models.DateTimeField("Date de création", db_index=True, editable=False)
    updated = models.DateTimeField("Date de modification", db_index=True, editable=False)

    def __str__(self):
        return self.heures

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.updated = timezone.now()
        super().save(*args, **kwargs)


