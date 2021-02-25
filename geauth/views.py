from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect
from geauth.forms import CreateUserForm
from geauth.models import User, UserProfile
from geauth import serializers
from django.views.generic.edit import CreateView, FormView
from django.views.generic import TemplateView
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.template import Context, Template
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework import permissions
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q



def logout_view(request):
    logout(request)
    return redirect("home")

class CreateUserView(PermissionRequiredMixin, CreateView):
    form_class = CreateUserForm
    template_name = "create_user.html"
    model = User
    success_message = "Utilisateur ajouté."
    permission_required = 'geauth.add_user'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.password = User.objects.make_random_password()
        self.object.save()
        profile = UserProfile()
        profile.user = self.object
        profile.salarie = form.cleaned_data['salarie_cegid']
        profile.save()
        group = Group.objects.get(name='Salarié')
        self.object.groups.add(group)
        self.object.save()

        messages.success(self.request, self.success_message)
        subject = "Création de mot de passe pour GeTools Progressis"
        email_template_name = "email_password_create.txt"
        c = {
            "username": self.object.username,
            "nom": self.object.profile.salarie.nom.title(),
            "prenom": self.object.profile.salarie.prenom.title(),
            'domain': settings.EMAIL_NEW_USER_SET_PASSWORD_DOMAIN_LINK,
            "uid": urlsafe_base64_encode(force_bytes(self.object.pk)),
            'token': default_token_generator.make_token(self.object),
            'protocol': settings.EMAIL_NEW_USER_SET_PASSWORD_PROTOCOL_LINK,
        }
        # TODO : Générer le template, envoyer l'email, etc...
        email = render_to_string(email_template_name, c)
        print(email)
        ret = send_mail(
            subject,
            email,
            None,
            [self.object.email],
            fail_silently=False,
        )
        if  ret != 1:
            messages.error(self.request, "Echec d'envoi de l'email")
        return redirect("user_create")

class GeAuthPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_form.html'
    success_url = reverse_lazy('home')


class GeAuthListUserView(PermissionRequiredMixin, TemplateView):
    template_name = "user_list.html"
    permission_required = 'geauth.add_user'

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("date_joined")
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        qs = User.objects.all().order_by("date_joined")
        salarie_nom_prenom = self.request.query_params.get('salarie_nom_prenom', None)
        code_cegid = self.request.query_params.get('code_cegid', None)
        if salarie_nom_prenom is not None:
            qs = qs.filter(Q(profile__salarie__nom__icontains=salarie_nom_prenom) | Q(profile__salarie__prenom__icontains=salarie_nom_prenom))

        if code_cegid is not None:
            qs = qs.filter(profile__salarie__code_erp__contains=code_cegid)
        
        return qs


@permission_required('activite.add_saisieactivite')
def ajax_send_reset_password(request, user_id):
    """
        Réenvoie un email a l'utilisateur pour réinitialiser le mot de passe
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({ "success": False, "message": "Utilisateur non trouvé"})
    if user.send_reset_password_email() != 1:
        return JsonResponse({ "success": False, "message": "Echec d'envoi de l'email"})
    else:
        return JsonResponse({ "success": True, "message": "Email envoyé"})


@permission_required('activite.add_saisieactivite')
def ajax_ban_unban_user(request, user_id):
    """
        Réenvoie un email a l'utilisateur pour réinitialiser le mot de passe
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({ "success": False, "message": "Utilisateur non trouvé"})
    if user.is_superuser:
        return JsonResponse({ "success": False, "message": f"Impossible de désactiver un superuser."})
    if user.is_active:
        user.is_active = False
        user.save()
        return JsonResponse({ "success": True, "message": f"L'utilisateur {user} désactivé : Il ne peut plus se connecter a GeTools."})
    else:
        user.is_active = True
        user.save()
        return JsonResponse({ "success": True, "message": f"L'utilisateur {user} activé : Il peut se connecter a GeTools"})