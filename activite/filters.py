import django_filters
from .models import TarifGe, Salarie, Adherent, Article

class TarifGeFilter(django_filters.FilterSet):
    # mise_a_disposition__salarie = django_filters.ModelChoiceFilter(field_name='mise_a_disposition__salarie', queryset=Salarie.objects.all())
    # mise_a_disposition__adherent = django_filters.ModelChoiceFilter(field_name='mise_a_disposition__adherent', queryset=Adherent.objects.all())
    # article = django_filters.ModelChoiceFilter(field_name='article', queryset=Article.objects.all())
    # archive = django_filters.BooleanFilter(field_name='archive')

    class Meta:
        model = TarifGe
        fields = ['mise_a_disposition__salarie', 'mise_a_disposition__adherent', 'article', 'archive']