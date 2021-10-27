from django.contrib import admin
from .models import DemandeConge, MotifDemandeConge


# Register your models here.
admin.site.register(DemandeConge)
admin.site.register(MotifDemandeConge)