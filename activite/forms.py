from django.forms import ModelForm
from .models import TarifGe, MiseADisposition
from django.forms import HiddenInput

class TarifGeEditForm(ModelForm):

    article = HiddenInput()
    mise_a_disposition = HiddenInput()

    class Meta:
        model = TarifGe
        fields = ['article', 'mise_a_disposition', 'tarif', 'coef_paie', 'coef']


class TarifGeAddForm(ModelForm):

    class Meta:
        model = TarifGe
        fields = ['article', 'mise_a_disposition', 'tarif', 'coef_paie', 'coef']

    def __init__(self):
        self.fields['mise_a_disposition'].queryset = MiseADisposition.objects.filter(cloturee=False)
