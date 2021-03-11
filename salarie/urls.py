from django.urls import include, path
from salarie import views

urlpatterns = [
    # path('prepa/', preparation_paie, name='prepa_paie'),
    path('', views.SalarieListView.as_view(), name='salarie_list'),
    path('<int:pk>/', views.SalarieDetailView.as_view(), name='salarie_detail'),
    path('<int:id>/addcalendar/', views.add_calendar, name='salarie_add_calendar'),
    path('addmad/', views.addmad, name="addmad"),
    path('delmadcalendar/<int:mad_id>/', views.delmadcalendar, name='delmadcalendar'),
]