from .forms import GeAuthLoginForm

def login_form_processor(request):
    auth_form = GeAuthLoginForm()
    return {'auth_form': auth_form}
    