from django.shortcuts import render
from .xrp_sprint import CegidCloud
from 

# Create your views here.

def ajax_update_famille_article(request):
    """
        Lit les familles XPR Print, et met a jour la table des familles articles
    """
    cegid = CegidCloud()
    famille_list = cegid.get_famille_article_list()
    count = len(famille_list)

    for famille in famille_list:
        try:
            f = FamilleArticle.objects.get(code_erp=famille['Key'])
        except FamilleArticle.DoesNotExist:
            f = FamilleArticle()
        f.code_erp = famille['Key']
        f.libelle = famille['Value']
        if famille['Key'] == "PRF":
            # marqué comme prime forfétaire
            f.forfaitaire = True
        f.save()
    ret = { "result": "ok", "count": count }
    return JsonResponse(ret)
    