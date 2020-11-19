from django.views.generic import TemplateView
from django.urls import path, include
from geauth import views

urlpatterns = [ 
    # path('login/', auth_views.LoginView.as_view(template_name='geauth/login.html')),
    # path('logout/', auth_views.LogoutView.as_view(template_name='geauth/logout.html')),
    path('create/', views.CreateUserView.as_view(), name="user_create"),
    path('reset/<uidb64>/<token>/', views.GeAuthPasswordResetConfirmView.as_view(),name='password_reset_confirm'),
]