from django.forms import modelformset_factory, ModelForm
from .models import ValidationAdherent

ValidationAdherentFormSet = modelformset_factory(
    ValidationAdherent, fields=("email", "nom_prenom"), extra=5
)

class ValidationAdherentChangeEmailForm(ModelForm):
    model = ValidationAdherent
    class Meta:
        fields = ['email',]