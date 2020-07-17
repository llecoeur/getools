from django.forms import ModelForm
from .models import TarifGe
from django.forms import HiddenInput

class TarifGeEditForm(ModelForm):

    article = HiddenInput()
    mise_a_disposition = HiddenInput()

    class Meta:
        model = TarifGe
        fields = ['article', 'mise_a_disposition', 'tarif', 'coef_paie', 'coef']
