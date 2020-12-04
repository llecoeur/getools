from rest_framework import routers
from releve.views import SaisieSalarieViewSet, ReleveSalarieViewSet, ReleveSalarieCommentaireSerializerViewSet
# from article.viewsets import ArticleViewSet

router = routers.DefaultRouter()
router.register(r'saisie_salarie', SaisieSalarieViewSet)
router.register(r'releve_salarie', ReleveSalarieViewSet)
router.register(r'releve_salarie_commentaire', ReleveSalarieCommentaireSerializerViewSet)

# router.register(r'article', ArticleViewSet)