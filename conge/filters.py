import django_filters
from .models import DemandeConge

class DemandeCongeFilter(django_filters.FilterSet):
    salarie = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = DemandeConge
        fields = ['price', 'release_date']