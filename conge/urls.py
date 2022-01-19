from django.urls import include, path
from conge import views

urlpatterns = [
    path('', views.DemandeCongeListView.as_view(), name='list_conge'),
    path('new/', views.DemandeCongeAddFormView.as_view(), name='demande_conge'),
    path('new/step2/', views.ValidationAdherentFormView.as_view(), name="step2"),
    path('addadherent', views.DemandeCongeAddFormView.as_view(), name="add_adherent"),
    path('remove_validation/<int:id>/', views.remove_validation, name="remove_validation"),
    path('envoi/<int:id>/', views.finish, name="envoi_conge"),
    path('accept/<str:slug>/', views.accept, name="conge_accept"),
    path('rejest/<str:slug>/', views.reject, name="conge_reject"),
]