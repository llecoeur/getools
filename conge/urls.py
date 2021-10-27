from django.urls import include, path
from conge import views

urlpatterns = [
    # path('prepa/', preparation_paie, name='prepa_paie'),
    path('', views.DemandeCongeAddFormView.as_view(), name='demande'),
    path('addadherent', views.DemandeCongeAddFormView.as_view(), name="add_adherent"),
]