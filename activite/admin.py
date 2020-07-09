from django.contrib import admin
from .models import RubriquePaie, Salarie, Article, Adherent, MiseADisposition, TarifGe, Service, Poste, SaisieActivite

# Register your models here.
admin.site.register(RubriquePaie)
admin.site.register(Salarie)
admin.site.register(Article)
admin.site.register(Adherent)
admin.site.register(MiseADisposition)
admin.site.register(TarifGe)
admin.site.register(Service)
admin.site.register(Poste)
admin.site.register(SaisieActivite)