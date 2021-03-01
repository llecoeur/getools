from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from salarie import models
from salarie import serializer
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin



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