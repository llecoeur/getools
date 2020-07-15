from django.urls import include, path
from .views import preparation_paie, ajax_mad_for_salarie, ajax_load_saisie_mad, ajax_save_saisie, tarifs

urlpatterns = [
    path('prepa/', preparation_paie, name='prepa_paie'),
    path('tarif/', tarifs, name='tarifs'),
    path('ajax_mad_for_salarie/<int:salarie_id>/<str:termine>/', ajax_mad_for_salarie, name="ajax_mad_for_salarie"),
    path('ajax_load_saisie_mad/<int:mois>/<int:annee>/<int:mad_id>/', ajax_load_saisie_mad, name="ajax_load_saisie_mad"),
    path('ajax_save_saisie/<str:valeur>/<int:tarif_id>/<int:annee>/<int:mois>/<int:jour>/', ajax_save_saisie, name="ajax_save_saisie"),
]