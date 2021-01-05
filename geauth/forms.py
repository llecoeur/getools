from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile
from activite.models import Salarie
from datetime import datetime, date
from django.utils import timezone
from django.db.models import Q, Sum
from django.forms import PasswordInput


class GeAuthLoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control form-control-navbar', 'placeholder': _('Username')}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control form-control-navbar', 'placeholder': _('Password')}),
    )


class CreateUserForm(forms.ModelForm):
    """
        Formulaire de création d'utilisateur, accessible uniquement aux admins
        Crée l'utilisateur avec login + mot de passe, et envoie un email de réinitialisation de mot de passe
    """
    salarie_cegid = forms.ModelChoiceField(queryset=Salarie.objects.all())

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On exclut du select salariés ceux qui ont déjà été sélectionnés
        exclude_list = []
        date_compare = ((timezone.now().replace(day=1) - timedelta(days=62)).replace(day=1)).date()
        # date_compare = date(timezone.now().year, timezone.now().month - 2, 1)
        # Salariés déjà sélectionnés
        selected_salarie_profile_list = UserProfile.objects.exclude(salarie=None)
        for salarie_profile in selected_salarie_profile_list:
            # print(f"Exclus car sélectionné :{salarie_profile.salarie}")
            exclude_list.append(salarie_profile.salarie.id)
        # salariés sortis
        salarie_sorti_list = Salarie.objects.exclude(Q(date_sortie=date(1900,1,1)) | Q(date_sortie__gt=date_compare))
        # id_list = Salarie.objects.exclude().exclude(date_sortie__lt=date_compare).values('id')
        for salarie_sorti in salarie_sorti_list:
            # print(f"Exclus car sorti {salarie_sorti} date : {salarie_sorti.date_sortie}")
            exclude_list.append(salarie_sorti.id)
        # print(exclude_list)
        self.fields['salarie_cegid'].queryset = Salarie.objects.exclude(id__in=exclude_list)


