from django.views.generic import TemplateView
from django.urls import path, include

urlpatterns = [ 
    path('login/', auth_views.LoginView.as_view(template_name='geauth/login.html')),
    path('logout/', auth_views.LogoutView.as_view(template_name='geauth/logout.html')),
]