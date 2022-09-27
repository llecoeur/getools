from django.db import models


class Config(models.Model):
    """
        Table de configuration. Contient des paramètres de configuration qui doivent pouvoir êr modifiés par des administrateurs
    """
    key = models.CharField("Clef", max_length=20, null=False, blank=False)
    str_val = models.CharField("Valeur Chaine", max_length=100, null=True, blank=True)
    int_val = models.IntegerField("Valeur Entière", null=True, blank=True)
    description = models.CharField("description", max_length=200, null=False, blank=False, default="")

    def __str__(self):
        return f"{self.description} ({self.key})"
