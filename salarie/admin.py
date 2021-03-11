from django.contrib import admin
from salarie.models import CalendrierSalariePeriode, CalendrierSalarieMiseADisposition, CalendrierSalarieRecurence


# Register your models here.

admin.site.register(CalendrierSalariePeriode)
admin.site.register(CalendrierSalarieRecurence)
admin.site.register(CalendrierSalarieMiseADisposition)