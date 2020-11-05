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
        return f"{self.first_name} {self.last_name}"

    @property
    def svg_avatar_mini(self):
        try:
            txt = self.first_name[0] + self.last_name[0]
        except IndexError:
            txt = "??"
        svg = '''<svg width="24" height="24">
        <circle cx="12" cy="12" r="12" fill="#004eFF" />
        <text x="6" y="16" style="font-family: Arial; fill: #FFFFFF;font-size : 12px;">{}</text>
        </svg>'''.format(txt)
        return svg


class UserProfile(models.Model):
    user = models.OneToOneField(User, verbose_name="Utilisateur", related_name="profile", on_delete=models.CASCADE)
    salarie = models.OneToOneField(Salarie, verbose_name="Salarié", related_name="user_profile", on_delete=models.SET_NULL, null=True, default=None)
