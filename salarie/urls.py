from django.urls import include, path
from salarie import views

urlpatterns = [
    # path('prepa/', preparation_paie, name='prepa_paie'),
    path('', views.SalarieListView.as_view(), name='salarie_list'),
]