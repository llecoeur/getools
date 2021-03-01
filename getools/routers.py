from rest_framework import routers
from releve.views import SaisieSalarieViewSet, ReleveSalarieViewSet, ReleveSalarieCommentaireSerializerViewSet
from geauth.views import UserViewSet
from salarie import views as salarieView
from activite import views as activiteView
# from article.viewsets import ArticleViewSet

router = routers.DefaultRouter()
router.register(r'saisie_salarie', SaisieSalarieViewSet)
router.register(r'releve_salarie', ReleveSalarieViewSet, basename="releve_salarie")
router.register(r'releve_salarie_commentaire', ReleveSalarieCommentaireSerializerViewSet)
router.register(r'user', UserViewSet)
router.register(r'salarie', activiteView.SalarieViewSet)
router.register(r'calendrier_salarie', salarieView.CalendrierSalarieViewSet)
router.register(r'calendrier_salarie_periode', salarieView.CalendrierSalariePeriodeViewSet)
router.register(r'calendrier_salarie_mise_a_disposition', salarieView.CalendrierSalarieMiseADispositionViewSet)


