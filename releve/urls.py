from django.urls import include, path
from releve import views

urlpatterns = [
    # path('prepa/', preparation_paie, name='prepa_paie'),
    path('', views.ReleveMensuelView.as_view(), name='releve_mensuel'),
]