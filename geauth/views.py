from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect
from geauth.forms import CreateUserForm
from geauth.models import User, UserProfile
from django.views.generic.edit import CreateView, FormView
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


def logout_view(request):
    logout(request)
    return redirect("home")

class CreateUserView(CreateView, PermissionRequiredMixin):
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
        # TODO : Mettre le salarié dans le bon groupe

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
