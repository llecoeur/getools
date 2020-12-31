from django.views.generic import TemplateView
from django.urls import path, include
from geauth import views

urlpatterns = [ 
    # path('login/', auth_views.LoginView.as_view(template_name='geauth/login.html')),
    # path('logout/', auth_views.LogoutView.as_view(template_name='geauth/logout.html')),
    path('create/', views.CreateUserView.as_view(), name="user_create"),
    path('list', views.GeAuthListUserView.as_view(), name='user_list'),
    path('reset/<uidb64>/<token>/', views.GeAuthPasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('ajax_send_reset_password/<int:user_id>/', views.ajax_send_reset_password, name='ajax_send_reset_password'),
    path('ajax_ban_unban_user/<int:user_id>/', views.ajax_ban_unban_user, name='ajax_ban_unban_user'),
    
]