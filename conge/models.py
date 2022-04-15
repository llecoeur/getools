from django.db import models
from geauth.models import User
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib import messages



import uuid

# Create your models here.

class MotifDemandeConge(models.Model):
    libelle = models.CharField("Libellé", max_length=30, null=False, blank=False)

    def __str__(self):
        return self.libelle


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
    # Est ce que a demande de congé est complète et envoyée
    conge_envoye = models.BooleanField(null=False, default=False, db_index=True)
    
    # Date de création
    created = models.DateTimeField(auto_now_add=True)
    # Date de dernière modification
    updated = models.DateTimeField(auto_now=True)


    class Meta:
        permissions = [('can_validate_conges', 'Peut valider les congés')]

    def __str__(self):
        debut = self.debut.strftime("%d/%m/%Y")
        fin = self.fin.strftime("%d/%m/%Y")
        return f"{str(self.salarie)}: du {self.debut} au {self.fin}"

    @property
    def etat_str(self):
        """
            retourne une chaine correspondant a l'état de la demande
        """
        if self.conge_valide:
            return "Congé validé"
        if self.conge_envoye is False:
            return "demande en brouillon"
        str_status = ""
        for valid in self.validation_adherent_list.all():
            if valid.is_valid:
                str_status += f'<span class="text-success" data-toggle="tooltip" data-placement="top" title="{valid.nom_prenom}">{valid.email} : {valid.valid_oui_non_str}</span><br />'
            else:
                str_status += f'<span class="text-danger" data-toggle="tooltip" data-placement="top" title="{valid.nom_prenom}">{valid.email} : {valid.valid_oui_non_str}</span><br />'
        return str_status

    @property
    def is_all_accepted(self):
        """
            Est ce que cette demande de congé est totalement validée par les personnes, en dehors du chargé de dev ?
        """
        validation_list = self.validation_adherent_list.objects.filter(is_progressis=False)
        for val in validation_list:
            if val.is_valid is False:
                return False
        else:
            return True

    @property
    def validation_progressis(self):
        try:
            return self.validation_adherent_list.get(is_progressis=True)
        except ValidationAdherent.DoesNotExist:
            return None


class ValidationAdherent(models.Model):
    # Demande pour laquelle cette validation existe
    demande = models.ForeignKey(DemandeConge, on_delete=models.CASCADE, db_index=True, null=False, blank=False, related_name="validation_adherent_list")
    # Email du contact adherent devant valider
    email = models.EmailField("Email", max_length=100, null=False, blank=False)
    # Nom et prénom de la personne devant valider
    nom_prenom = models.CharField("Prénom et nom", max_length=150, null=False, blank=False)
    # Est ce que la validation a été acceptée ? null : en attente, True : acceptée, False : refusée
    is_valid = models.BooleanField("Validé ?", null=True, default=None, blank=True)
    # Date de validation de la demande
    valid_manuel_date = models.DateTimeField("Date de validation manuelle", null=True, db_index=True, default=None, blank=True)
    # Date de refus de la demande
    refus_manuel_date = models.DateTimeField("Date de validation manuelle", null=True, db_index=True, default=None, blank=True)
    # Si la demande a été validée par dépassement du délais
    is_valid_timeout = models.BooleanField("Validé par expiration du délais ?", null=False, default=False, blank=True)
    # Slug de acceptation de la demande
    slug_acceptation = models.CharField("Slug de Validation", max_length=32, null=True, blank=True, default="")
    # Slug de refus de la demande
    slug_refus = models.CharField("Slug de refus", max_length=32, null=True, blank=True, default="")
    # Est ec que cette validation est Progressis ?
    is_progressis = models.BooleanField("Progressis ?", null=False, default=False, blank=True)
    # Date de création
    created = models.DateTimeField(auto_now_add=True)
    # Date de dernière modification
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom_prenom

    def gen_uuids(self):
        """
            Génère des uuid, sans tiret, pour les slugs de validation et de refus.
        """
        self.slug_acceptation = str(uuid.uuid4()).replace("-","")
        self.slug_refus = str(uuid.uuid4()).replace("-","")
        self.save()

    def send_email(self):
        """
            (re)regenere les uuid et renvoie le mail de validation
        """
        self.gen_uuids()
        subject = "Un salarié Progressis aimerait prendre un congé"
        if self.is_progressis:
            email_template_name = "email_demande_progressis.txt"
        else:
            email_template_name = "email_demande_conge_adherent.txt"
        c = {
            "nom_prenom": self.nom_prenom,
            "nom_prenom_salarie": str(self.demande.salarie),
            "date_debut": self.demande.debut,
            "date_fin": self.demande.fin,
            "motif": self.demande.motif,
            "commentaire": self.demande.commentaire_salarie,
            'domain': settings.EMAIL_NEW_USER_SET_PASSWORD_DOMAIN_LINK,
            'slug_acceptation': self.slug_acceptation,
            'slug_refus': self.slug_refus,
            'protocol': settings.EMAIL_NEW_USER_SET_PASSWORD_PROTOCOL_LINK,
        }
        # TODO : Générer le template, envoyer l'email, etc...
        email = render_to_string(email_template_name, c)
        ret = send_mail(
            subject,
            email,
            None,
            [self.email],
            fail_silently=False,
        )
        return ret

    @property
    def valid_oui_non_str(self):
        if self.is_valid is None:
            return "En attente"
        elif self.is_valid:
            return "Accepté"
        else:
            return "Refusé"

    '''
    @property
    def is_progressis(self):
        """
            Cette demande est une progressis ou non ?
        """
        if self.demande.validation_progressis == self:
            return True
        else:
            return False
    '''