from django.db import models
from geauth.models import User

# Create your models here.

class MotifDemandeConge(models.Model):
    libelle = models.CharField("Libellé", max_length=30, null=False, blank=False)


class DemandeConge(models.Model):

    # https://progressisge.sharepoint.com/sites/GestionSalaris/Documents%20partages/General/Vie%20du%20salari%C3%A9/CONGES%20SALARIE/FEN%20003%200%20Demande%20de%20cong%C3%A9_%20Progressis.pdf
    # Salarie qui fait la demande
    salarie = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True, null=False, blank=False, related_name="demande_conge_list")
    # True si le congé est accepté par toutes les parties, y compris Progressis
    conge_valide = models.BooleanField(null=False, default=False, db_index=True)
    # En cas de refus, raison
    conge_invalid_motif = models.TextField(null=False, blank=True, default="")
    # Date acceptation du congé
    conge_valid_date = models.DateTimeField(null=True, db_index=True)
    # Personne Progressis ayant validé le congé
    conge_valid_responsable = models.ForeignKey(User, on_delete=models.SET_NULL, db_index=True, null=True, blank=True, default=None, related_name="demande_conge_valide_list")
    # date de début du congé
    debut = models.DateField(db_index=True, null=False, blank=False)
    # Date de fin du congé
    fin = models.DateField(db_index=True, null=False, blank=False)
    # Motif de la demande de congé
    motif = models.ForeignKey(MotifDemandeConge, on_delete=models.CASCADE, db_index=True, null=False, blank=False, related_name="demande_conge_list")
    # Commentaire du salarié attaché a la demande
    commentaire_salarie = models.TextField(null=False, blank=True, default="")
    # Commentaire Progressis
    commentaire_responsable = models.TextField(null=False, blank=True, default="")

    # Date de création
    created = models.DateTimeField(auto_now_add=True)
    # Date de dernière modification
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        debut = self.debut.strftime("%d/%m/%Y")
        fin = self.fin.strftime("%d/%m/%Y")
        return f"{str(self.salarie.nom)}: du {debut} au {fin}"


class ValidationAdherent(models.Model):
    # Demande pour laquelle cette validation existe
    id_demande = models.ForeignKey(DemandeConge, on_delete=models.CASCADE, db_index=True, null=False, blank=False, related_name="validation_adherent_list")
    # Email du contact adherent devant valider
    email = models.CharField("Email", max_length=100, null=False, blank=False)
    # Nom et prénom de la personne devant valider
    nom_prenom = models.CharField("Prénom et nom", max_length=150, null=False, blank=False)
    # Si la demande a été validée par la personne ou non dans les temps manuellement
    is_valid_manuel = models.BooleanField("Validé manuellement ?", null=False, default=False, blank=True)
    # Date de validation de la demande
    valid_manuel_date = models.DateTimeField("Date de validation manuelle", null=True, db_index=True)
    # Si la demande a été validée par dépassement du délais
    is_valid_timeout = models.BooleanField("Validé par expiration du délais ?", null=False, default=False, blank=True)

    # Date de création
    created = models.DateTimeField(auto_now_add=True)
    # Date de dernière modification
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom_prenom

