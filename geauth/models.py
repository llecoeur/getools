from django.contrib.auth.models import AbstractUser
from django.db import models
from activite.models import Salarie
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail



class User(AbstractUser):

    """
        Champs pour les Salariés
    """
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        permissions = [('can_view_indicators', 'Peut voir les indicateurs')]

    def __str__(self):
        """
            Si salarié Cegid, on prend ce nom/prénom.
            Sinon, on prend le nom, prenom enregistré dans l'utilisateur,
            enfin, on prend le login
        """
        if self.profile.salarie:
            return f"{self.profile.salarie.prenom.title()} {self.profile.salarie.nom.title()}"
        elif self.first_name == "" and self.last_name == "":
            return self.username
        else:
            return f"{self.first_name.title()} {self.last_name.title()}"


    @property
    def svg_avatar_mini(self):
        if self.profile.salarie:
            txt = self.profile.salarie.prenom[0] + self.profile.salarie.nom[0]
        else:
            try:
                txt = (self.first_name[0] + self.last_name[0]).capitalize()
            except IndexError:
                txt = self.username[:2].capitalize()
        svg = '''<svg width="24" height="24">
        <circle cx="12" cy="12" r="12" fill="#004eFF" />
        <text x="6" y="16" style="font-family: Arial; fill: #FFFFFF;font-size : 12px;">{}</text>
        </svg>'''.format(txt)
        return svg

    def send_reset_password_email(self):
        """
            Envoie un email pour réinitialiser le mot de passe
        """
        subject = "Réinitialisation de mot de passe pour GeTools Progressis"
        email_template_name = "email_password_create.txt"
        c = {
            "username": self.username,
            "nom": self.profile.salarie.nom.title(),
            "prenom": self.profile.salarie.prenom.title(),
            'domain': settings.EMAIL_NEW_USER_SET_PASSWORD_DOMAIN_LINK,
            "uid": urlsafe_base64_encode(force_bytes(self.pk)),
            'token': default_token_generator.make_token(self),
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


class UserProfile(models.Model):
    user = models.OneToOneField(User, verbose_name="Utilisateur", related_name="profile", on_delete=models.CASCADE, null=True, defaut=None)
    salarie = models.OneToOneField(Salarie, verbose_name="Salarié", related_name="user_profile", on_delete=models.SET_NULL, null=True, default=None)
    # Cet utilisateur déclare les heures la poste pour les salariés sous sa responsabilité
    is_declarant_la_poste = models.BooleanField("Declarant La Poste", verbose_name="Déclarant La Poste", default=False)
    # si != None et positionné sur un autre salarié ayant le status de déclarant "La Poste":
    #   Il ne peut se connecter
    #   ses heures sont déclarée par son responsable via le formulaire dédié
    manager_la_poste = models.M("Salarié La Poste", verbose_name="Salarié La Poste", on_delete=models.SET_NULL, default=False)
