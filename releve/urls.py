from django.urls import include, path
from releve import views

urlpatterns = [
    # path('prepa/', preparation_paie, name='prepa_paie'),
    path('', views.ReleveMensuelView.as_view(), name='releve_mensuel'),
    path('ro/', views.ReleveMensuelReadOnlyView.as_view(), name='releve_mensuel_read_only'),
    path('list', views.ReleveMensuelListView.as_view(), name='releve_mensuel_list'),
    path('ajax_load_saisie_releve/<int:mois>/<int:annee>/', views.ajax_load_saisie_releve, name="ajax_load_saisie_releve"),
    path('ajax_load_saisie_releve_id/<int:id_releve>/', views.ajax_load_saisie_releve_id, name="ajax_load_saisie_releve_id"),
    path('releve_mensuel_print_pdf/<int:id_salarie>/', views.releve_mensuel_print_pdf, name="releve_mensuel_print_pdf"),
    path('releve_mensuel_print_all_pdf/<int:annee>/<int:mois>/', views.releve_mensuel_print_all_pdf, name="releve_mensuel_print_all_pdf"),
    path('gel_releve/<int:annee>/<int:mois>/', views.gel_releve, name="gel_releve"),
    path('degel_releve/<int:annee>/<int:mois>/', views.degel_releve, name="degel_releve"),
]