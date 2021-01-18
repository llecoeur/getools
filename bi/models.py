from django.db import models

# Create your models here.

class MoisStats(models.Model):
    """
        Classe regroupant les stats mois par mois
    """
    mois = models.IntegerField(db_index=True)
    annee = models.IntegerField(db_index=True)
    # Chiffre d'affaires réalisé total
    ca_total = models.FloatField(db_index=True, default=0)
    # Chiffre d'affaires Progressis
    ca_progressis = models.FloatField(db_index=True, default=0)
    # Heures réalisées total
    heures_total = models.FloatField(db_index=True, default=0)
    # Heures progressis
    heures_progressis = models.FloatField(db_index=True, default=0)

    def update_heures_total(self):
        """
            
        """
        pass