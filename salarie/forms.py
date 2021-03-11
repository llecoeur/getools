from django import forms
from salarie.models import CalendrierSalarieMiseADisposition, CalendrierSalarie
from activite.models import Adherent
from pprint import pprint


class CreateCalendrierSalarieMiseADispositionForm(forms.ModelForm):

    JOURS_LIST = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]

    num_jour = forms.ChoiceField(choices=JOURS_LIST)
    
    class Meta:
        model = CalendrierSalarieMiseADisposition
        fields = ['num_jour', 'periode', 'recurence' , 'adherent', 'commentaire', 'calendrier']
        widgets = {'calendrier': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Recup du salarié en fonction du calendrier
        try:
            cal_id = kwargs["initial"]['calendrier']
        except (KeyError):
            cal_id = args[0]['calendrier']
        salarie_id = CalendrierSalarie.objects.get(id=cal_id).salarie.id
        # Ne lister dans le select que les missions du salarié
        adherent_list = Adherent.objects.filter(mise_a_disposition_list__salarie__id=salarie_id, mise_a_disposition_list__cloturee=False)
        self.fields['adherent'].queryset = adherent_list