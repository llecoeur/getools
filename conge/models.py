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
    # Le congé a été refusé
    conge_invalid = models.BooleanField(default=False)
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
    # Date d'envoi du congé aux personnes
    conge_envoye_date = models.DateTimeField("Date d'envoi du conge paye", null=True, default=None, db_index=True)
    # Date de création
    created = models.DateTimeField(auto_now_add=True)
    # Date de dernière modification
    updated = models.DateTimeField(auto_now=True)


    class Meta:
        permissions = [
            ('can_validate_conges', 'Peut valider les congés'),
            ('can_view_conges', 'Peut voir les congés'),
        ]

    def __str__(self):
        debut = self.debut.strftime("%d/%m/%Y")
        fin = self.fin.strftime("%d/%m/%Y")
        return f"{str(self.salarie)}: du {self.debut} au {self.fin}"

    @property
    def etat_str(self):
        """
            retourne l'état de la demande
            Estr soit : En cours, acceptée, refusée
        """
        if  self.conge_valide:
            return '<span class="bg-success">Validé</span>'
        if self.conge_invalid:
            return '<span class="bg-danger">Refusé</span>'
        else:
            return '<span class="bg-warning">En attente</span>'


    @property
    def reponses(self):
        """
            retourne une chaine correspondant a l'état de la demande
        """
        if self.conge_envoye is False:
            return '<span class="text-warning">Demande en brouillon'
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

    def valid(self):
        """
            Vérifie que toutes les validations ont été acceptées, et si c'est le cas, 
            envoie un mail au salarié et a Progressis pour dire que le congé a été accepté
        """
        nb_valid_attente_refus = self.validation_adherent_list.exclude(is_valid=True).count()
        print(f"nb_valid_attente_refus = {nb_valid_attente_refus}")
        if nb_valid_attente_refus == 0:
            # toutes les demandes ont été acceptées
            self.conge_valide = True
            self.save()
            # Envoi d'un mail au salarié et à progressis
            email_template_name = "email_conge_accepte_all.txt"
            subject = f"Votre demande de congé a été acceptée"
            c = {
                "nom_prenom_salarie": self.salarie,
                "debut": self.debut,
                "fin": self.fin,
            }
            email = render_to_string(email_template_name, c)
            ret = send_mail(
                subject,
                email,
                None,
                [self.salarie.email],
                fail_silently=False,
            )
            print(f"email envoyé : {ret}, {self.salarie.email}, {subject}")
            return ret


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
    # Rappel envoyé ?
    is_rappel_envoye = models.BooleanField("Rappel envoyé ?", null=False, default=False, blank=True)
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
            'rappel': False,
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

    def send_reject_email(self):
        email_template_name = "email_refus.txt"
        subject = f"{self.nom_prenom} a refusé votre demande de congé"
        c = {
            "nom_prenom_salarie": self.demande.salarie,
            "nom_prenom": self.nom_prenom,
            "email": self.email,
        }
        email = render_to_string(email_template_name, c)
        ret = send_mail(
            subject,
            email,
            None,
            [self.email],
            fail_silently=False,
        )
        return ret

    def accept_by_delay(self):
        email_template_name = "email_accept_delay.txt"
        subject = f"La demande de congé de {self.nom_prenom} a été acceptée"
        c = {
            "nom_prenom_salarie": self.demande.salarie,
            "nom_prenom": self.nom_prenom,
            "email": self.email,
        }
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
            return '<span class="text-warning">En attente</span>'
        elif self.is_valid:
            return '<span class="text-success">Accepté</span>'
        else:
            return '<span class="text-error">Refusé</span>'

    def send_email_rappel(self):
        """
            renvoie un email de rappel.
        """
        subject = "[Rappel] Un salarié Progressis aimerait prendre un congé"
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
            'rappel': True,
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
        self.is_rappel_envoye = True
        self.save()
        return ret

