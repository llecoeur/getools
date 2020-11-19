from django.contrib.auth.models import AbstractUser
from django.db import models
from activite.models import Salarie



class User(AbstractUser):

    """
        Champs pour les Salariés
    """
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        """
            Si salarié Cegid, on prend ce nom/prénom.
            Sinon, on prend le nom, prenom enregistré dans l'utilisateur,
            enfin, on prend le login
        """
        try:
            if self.profile.salarie:
                return f"{self.profile.salarie.prenom.title()} {self.profile.salarie.nom.title()}"
            elif self.first_name == "" and self.last_name == "":
                return self.username
            else:
                return f"{self.first_name.title()} {self.last_name.title()}"
        except self.RelatedObjectDoesNotExist:
            return self.username

    @property
    def svg_avatar_mini(self):
        try:
            if self.profile.salarie:
                txt = self.profile.salarie.prenom[0] + self.profile.salarie.nom[0]
            else:
                try:
                    txt = (self.first_name[0] + self.last_name[0]).capitalize()
                except IndexError:
                    txt = self.username[:2].capitalize()
        except self.RelatedObjectDoesNotExist:
            txt = self.username[:2].capitalize()
        svg = '''<svg width="24" height="24">
        <circle cx="12" cy="12" r="12" fill="#004eFF" />
        <text x="6" y="16" style="font-family: Arial; fill: #FFFFFF;font-size : 12px;">{}</text>
        </svg>'''.format(txt)
        return svg


class UserProfile(models.Model):
    user = models.OneToOneField(User, verbose_name="Utilisateur", related_name="profile", on_delete=models.CASCADE)
    salarie = models.OneToOneField(Salarie, verbose_name="Salarié", related_name="user_profile", on_delete=models.SET_NULL, null=True, default=None)
