from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework import permissions
from salarie import models
from salarie import serializer
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from activite.models import Salarie
from django.contrib import messages
from django.shortcuts import redirect
from salarie.forms import CreateCalendrierSalarieMiseADispositionForm

# Apis

class CalendrierSalarieViewSet(viewsets.ModelViewSet):
    queryset = models.CalendrierSalarie.objects.all()
    serializer_class = serializer.CalendrierSalarieSerializer


class CalendrierSalariePeriodeViewSet(viewsets.ModelViewSet):
    queryset = models.CalendrierSalarie.objects.all()
    serializer_class = serializer.CalendrierSalariePeriodeSerializer


class CalendrierSalarieMiseADispositionViewSet(viewsets.ModelViewSet):
    queryset = models.CalendrierSalarieMiseADisposition.objects.all()
    serializer_class = serializer.CalendrierSalarieMiseADispositionSerializer

class SalarieListView(PermissionRequiredMixin, TemplateView):
    template_name = "salarie_list.html"
    # can_view_ro_releve_salarie
    permission_required = 'releve.can_view_ro_releve_salarie'


class SalarieDetailView(PermissionRequiredMixin, DetailView):
    template_name = "salarie_detail.html"
    model = Salarie
    # can_view_ro_releve_salarie
    permission_required = 'releve.can_view_ro_releve_salarie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.object, 'calendrier'):
            context['mad_add_form'] = CreateCalendrierSalarieMiseADispositionForm(initial={'calendrier': self.object.calendrier.id})
        return context


def add_calendar(request, id):
    try:
        salarie = Salarie.objects.get(id=id)
    except Salarie.DoesNotExist:
        messages.error(request, 'Salarié inconnu')
        return redirect('/salarie/')
    if hasattr(salarie, 'calendrier'):
        messages.error(request, 'Le salarié a déjà un calendrier')
        return redirect(f'/salarie/{salarie.id}/')
    else:
        cal = models.CalendrierSalarie()
        cal.salarie = salarie
        cal.save()
        messages.success(request, 'Calendrier ajouté')
        return redirect(f'/salarie/{salarie.id}/')

def addmad(request):
    if request.method == 'POST':
        form = CreateCalendrierSalarieMiseADispositionForm(request.POST)
        if form.is_valid():
            mad = form.save()
            salarie_id = mad.calendrier.salarie.id
            # messages.success(request, 'Ajouté')
            return redirect(f'/salarie/{salarie_id}/')

def delmadcalendar(request, mad_id):
    mad = get_object_or_404(models.CalendrierSalarieMiseADisposition, id=mad_id)
    salarie_id = mad.calendrier.salarie.id
    mad.delete()
    return redirect(f'/salarie/{salarie_id}/')
