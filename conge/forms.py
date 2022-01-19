from django.forms import modelformset_factory
from .models import ValidationAdherent

ValidationAdherentFormSet = modelformset_factory(
    ValidationAdherent, fields=("email", "nom_prenom"), extra=5
)