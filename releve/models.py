from django.db import models
from django.utils import timezone
from activite.models import Adherent, Salarie
from django.forms.models import model_to_dict
from django.conf import settings
from django.forms.models import model_to_dict
from django.db.models import Sum


class ReleveSalarie(models.Model):

    mois = models.IntegerField("Mois", db_index=True)
    annee = models.IntegerField("Année", db_index=True)
    salarie = models.ForeignKey(Salarie, verbose_name="Salarié", related_name="releve_heures_list", on_delete=models.CASCADE)
    # Un releve nele ne peut plus être modifié par le salarié, aussi bien les commentaires, les saisies, et metadata
    gele = models.BooleanField("La saisie est gelée ?", db_index=True, default=False)
    commentaire = models.TextField("Commentaires", default="", blank=True)

    created = models.DateTimeField("Date de création", db_index=True, editable=False)
    updated = models.DateTimeField("Date de modification", db_index=True, editable=False)

    class Meta:
        ordering = ['-annee', '-mois', '-created']

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

    def get_commentaire(self, jour):
        # Retourne le commentaire du jour donné
        try:
            return self.commentaire_list.get(jour=jour)
        except ReleveSalarieCommentaire.DoesNotExist:
            # On le crée et le retourne
            return self.commentaire_list.create(
                jour=jour,
            )
    
    def total_heures(self):
        """
            Retourne le temps total enregistré dans ce relevé
        """
        return self.saisie_salarie_list.all().aggregate(somme=Sum("heures"))['somme']



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


class ReleveSalarieCommentaire(models.Model):

    # Numéro du jour auquel est rattaché ce commentaire
    jour = models.IntegerField("Jour", db_index=True, null=False, default=1)
    text = models.TextField("Commentaire", default="", blank=True)
    releve = models.ForeignKey(ReleveSalarie, verbose_name="Relevé", related_name="commentaire_list", on_delete=models.CASCADE, db_index=True)
    # Champs automatiques
    created = models.DateTimeField("Date de création", db_index=True, editable=False)
    updated = models.DateTimeField("Date de modification", db_index=True, editable=False)

    def __str__(self):
        return self.commentaire

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.updated = timezone.now()
        super().save(*args, **kwargs)