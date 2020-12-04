from django.urls import include, path
from releve import views

urlpatterns = [
    # path('prepa/', preparation_paie, name='prepa_paie'),
    path('', views.ReleveMensuelView.as_view(), name='releve_mensuel'),
    path('ajax_load_saisie_releve/<int:mois>/<int:annee>/', views.ajax_load_saisie_releve, name="ajax_load_saisie_releve"),
    path('releve_mensuel_print/', views.ReleveMensuelPrintView.as_view(), name="releve_mensuel_print"),
    path('releve_mensuel_print_pdf/<int:id_salarie>/', views.releve_mensuel_print_pdf, name="")
]