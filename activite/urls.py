from django.urls import include, path
from .views import ajax_upload_activite, ajax_update_mad, ajax_update_adherent, ajax_update_article, preparation_paie, ajax_mad_for_salarie, ajax_load_saisie_mad, ajax_save_saisie, tarifs, synchronisation
from .views import TarifGeCreate, TarifGeDelete, TarifGeUpdate, sort_article, ajax_load_article_list, ajax_switch_article_ordre, ajax_update_famille_article, ajax_update_service, ajax_update_poste, ajax_update_salaries, ajax_update_rubrique
from .views import ajax_maj_heures_travaillees, ajax_get_mad_to_upload, update_memo, ajax_upload_paie

urlpatterns = [
    path('prepa/', preparation_paie, name='prepa_paie'),
    path('tarif/', tarifs, name='tarifs'),
    path('tarif/add/', TarifGeCreate.as_view(), name='tarifge-add'),
    path('tarif/<int:pk>/', TarifGeUpdate.as_view(), name='tarifge-update'),
    path('tarif/<int:pk>/delete/', TarifGeDelete.as_view(), name='tarifge-delete'),
    path('ajax_mad_for_salarie/<int:salarie_id>/<str:termine>/', ajax_mad_for_salarie, name="ajax_mad_for_salarie"),
    path('ajax_load_saisie_mad/<int:mois>/<int:annee>/<int:mad_id>/', ajax_load_saisie_mad, name="ajax_load_saisie_mad"),
    path('ajax_save_saisie/<str:valeur>/<int:tarif_id>/<int:annee>/<int:mois>/<int:jour>/', ajax_save_saisie, name="ajax_save_saisie"),
    path('sort_article/', sort_article, name="sort_article"),
    path('ajax_load_article_list/', ajax_load_article_list, name="ajax_load_article_list"),
    path('ajax_switch_article_ordre/<int:article1_id>/<int:article2_id>/', ajax_switch_article_ordre, name="ajax_switch_article_ordre"), 
    path('ajax_update_famille_article/', ajax_update_famille_article, name="ajax_update_famille_article"),
    path('ajax_update_service/', ajax_update_service, name="ajax_update_service"),
    path('ajax_update_poste/', ajax_update_poste, name="ajax_update_poste"),
    path('ajax_update_salaries/', ajax_update_salaries, name="ajax_update_salaries"),
    path('ajax_update_rubrique/', ajax_update_rubrique, name="ajax_update_rubrique"),
    path('synchronisation/', synchronisation, name="synchronisation"),
    path('ajax_update_article/', ajax_update_article, name="ajax_update_article"),
    path('ajax_update_adherent/', ajax_update_adherent, name="ajax_update_adherent"),
    path('ajax_update_mad/', ajax_update_mad, name="ajax_update_mad"),
    path('ajax_upload_activite/<int:mad_id>/', ajax_upload_activite, name="ajax_upload_activite"),
    path('ajax_maj_heures_travaillees/<int:mad_id>/<int:annee>/<int:mois>/', ajax_maj_heures_travaillees, name="ajax_maj_heures_travaillees"),
    path('ajax_get_mad_to_upload/', ajax_get_mad_to_upload, name="ajax_get_mad_to_upload"),
    path('update_memo/<int:id_salarie>/', update_memo, name='update_memo'),
    path('ajax_upload_paie/<int:annee>/<int:mois>/', ajax_upload_paie, name="ajax_upload_paie"),
]