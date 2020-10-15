import os
import sys
sys.path.append('..')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "getools.settings")
import django
django.setup()
from cegid.cegid_premise import session, Salarie as SalarieCegid, Tiers, Affaire as CegidAffaire, Remuneration, Article as CegidArticle, CegidTarifGe, ChoixExt, ChoixCod
from activite.models import RubriquePaie, Salarie, Article, Adherent, MiseADisposition, TarifGe, Service, Poste, FamilleArticle
from tqdm import tqdm



if __name__ == "__main__":

    try:
        if sys.argv[1] == "del":
            print('Effacement des données...')
            Article.objects.all().delete()
            Salarie.objects.all().delete()
            RubriquePaie.objects.all().delete()
            Adherent.objects.all().delete()
            Service.objects.all().delete()
            Poste.objects.all().delete()
            TarifGe.objects.all().delete()
            MiseADisposition.objects.all().delete()
    except IndexError:
        pass

    """
    print("Mise a jour des famille articles")

    famille_list = ChoixCod.get_famille_article()
    for famille in famille_list:
        try:
            f = FamilleArticle.objects.get(code_erp=famille.code)
        except FamilleArticle.DoesNotExist:
            f = FamilleArticle()
        f.code_erp = famille.code
        f.libelle = famille.libelle
        if famille.code == "PRF":
            # marqué comme prime forfétaire
            f.forfaitaire = True
        f.save()

    print("Mise a jour des Services...")
    choix_list = session.query(ChoixExt).filter(ChoixExt.type_choix == "LF1")
    for choix in choix_list:
        try:
            s = Service.objects.get(code_erp=choix.code)
        except Service.DoesNotExist:
            # On ajoute
            s = Service()
        s.code_erp = choix.code
        s.libelle = choix.libelle
        s.save()

    print("Mise a jour des Postes")
    choix_list = session.query(ChoixExt).filter(ChoixExt.type_choix == "LF2")
    for choix in choix_list:
        try:
            s = Poste.objects.get(code_erp=choix.code)
        except Poste.DoesNotExist:
            # On ajoute
            s = Poste()
        s.code_erp = choix.code
        s.libelle = choix.libelle
        s.save()


    print("Mise a jour des Rubriques de paie...")
    rub_list = session.query(Remuneration).all()
    for rub_cegid in rub_list:
        try:
            rub = RubriquePaie.objects.get(code_erp=rub_cegid.code)
        except RubriquePaie.DoesNotExist:
            # On ajoute
            rub = RubriquePaie()
        rub.code_erp = rub_cegid.code
        rub.libelle = rub_cegid.libelle
        rub.abrege = rub_cegid.abrege
        rub.save()

    print("Mise a jour des Salariés...")
    salarie_list = session.query(SalarieCegid).all()
    for salarie_cegid in salarie_list:
        try:
            sal = Salarie.objects.get(code_erp=salarie_cegid.code)
        except Salarie.DoesNotExist:
            # On ajoute
            sal = Salarie()
        sal.code_erp = salarie_cegid.code
        sal.nom = salarie_cegid.nom
        sal.prenom = salarie_cegid.prenom
        sal.date_entree = salarie_cegid.date_entree
        sal.date_sortie = salarie_cegid.date_sortie
        sal.save()

    print("Mise a jour des Articles...")
    article_list = session.query(CegidArticle).all()
    for article_cegid in article_list:
        try:
            art = Article.objects.get(code_erp=article_cegid.code)
        except Article.DoesNotExist:
            art = Article()
        art.code_erp = article_cegid.code
        art.libelle = article_cegid.libelle
        art.type_article = article_cegid.type_article
        try:
            rub_paie = RubriquePaie.objects.get(code_erp=article_cegid.rubrique_paie.code)
        except AttributeError:
            pass
        except RubriquePaie.DoesNotExist:
            pass
        else:
            art.rubrique_paie = rub_paie
        # La famille
        try:
            famille = FamilleArticle.objects.get(code_erp=article_cegid.famille_code)
        except FamilleArticle.DoesNotExist:
            famille = None
        art.famille = famille
        art.save()

    print("Mise a jour des Adhérents...")
    tiers_list = session.query(Tiers).filter(Tiers.nature_auxiliaire == "CLI")
    for adherent_cegid in tiers_list:
        try:
            adh = Adherent.objects.get(code_erp=adherent_cegid.code)
        except Adherent.DoesNotExist:
            adh = Adherent()
        adh.code_erp = adherent_cegid.code
        adh.raison_sociale = adherent_cegid.libelle
        adh.save()

    print("Mise a jour des Mise d Dispositions...")
    aff_list = session.query(CegidAffaire).filter(CegidAffaire.code_1 == "MAD").filter(CegidAffaire._etat == "ENC").order_by(CegidAffaire.created)
    
    for affaire_cegid in aff_list:
        error = False

        try:
            adherent = Adherent.objects.get(code_erp=affaire_cegid.adherent.code)
        except AttributeError:
            print(f"l'affaire {affaire_cegid} n'a pas d'adhérent.")
            error = True
        except Adherent.DoesNotExist:
            print(f"L'adhérent {affaire_cegid.adherent} n'existe pas en base django: As-il été importé ?")
            error = True
        

        try:
            salarie = Salarie.objects.get(code_erp=affaire_cegid.salarie.code)
        except AttributeError:
            print(f"l'affaire {affaire_cegid} n'a pas de salarié.")
            error = True
        except Salarie.DoesNotExist:
            print(f"Le salarié {affaire_cegid.salarie} n'existe pas en base django: As-il été importé ?")
            error = True

        if not error:
            mad = MiseADisposition.get_mise_a_disposition(adherent.code_erp, salarie.code_erp)
            if mad is None:
                mad = MiseADisposition()
                mad.adherent = adherent
                mad.salarie = salarie
            mad.code_erp = affaire_cegid.code
            mad.cloturee = False
            mad.duree_travail_mensuel = affaire_cegid.duree_travail_mensuel
            mad.duree_travail_quotidien = affaire_cegid.duree_travail_quotidien
            mad.service = Service.objects.filter(code_erp=affaire_cegid.service_code).first()
            mad.poste = Poste.objects.filter(code_erp=affaire_cegid.poste_code).first()
            mad.coef_vente_soumis = affaire_cegid.coef_vente_soumis
            mad.coef_vente_non_soumis = affaire_cegid.coef_vente_non_soumis
            mad.save()
    """
    print("Mise a jour des tarifs TOUS ...")
    # Les tarifs sont obligatoirement recréés
    TarifGe.objects.all().delete()
    tarif_list = session.query(CegidTarifGe).filter(CegidTarifGe.adherent_code == "TOUS")
    mad_list = []

    for tarif_cegid in tarif_list:
        # On liste toutes les mises a dispo du salarié
        try:
            salarie = Salarie.objects.get(code_erp=tarif_cegid.salarie_code)
        except Salarie.DoesNotExist:
            # FIXME Peut etre qu'il faut tout de même ajouter a tout le monde ?
            print(f"Le salarié {tarif_cegid.salarie_code} du tarif {tarif_cegid.code} N'existe pas")
            error = False
        else:
            mad_list = MiseADisposition.objects.filter(salarie=salarie)
        
        for mad in mad_list:
            tar = TarifGe()
            error = False
            try:
                article = Article.objects.get(code_erp=tarif_cegid.article_code)
            except Article.DoesNotExist:
                print(f"Impossible de trouver l'article {tarif_cegid.article_code} ({tarif_cegid.code})")
                error = True
            # article 2
            try:
                article2 = Article.objects.get(code_erp=tarif_cegid.article2_code)
            except Article.DoesNotExist:
                article2 = None
            if not error:
                tar.code_erp = tarif_cegid.code
                tar.mise_a_disposition = mad
                tar.article = article
                tar.article2 = article2
                tar.poste = tarif_cegid.poste
                tar.tarif = tarif_cegid.tarif
                tar.exportable = tarif_cegid.exportable
                tar.element_reference = tarif_cegid.eltnat
                tar.coef = tarif_cegid.coefficient
                tar.mode_calcul = tarif_cegid.mode_calcul
                tar.coef_paie = tarif_cegid.coefficient_paie
                tar.article_a_saisir = tarif_cegid.article_saisir
                tar.save()

    print("Mise a jour des tarifs liés aux MADs...")

    tarif_list = session.query(CegidTarifGe).filter(CegidTarifGe.adherent_code != "TOUS")
    for tarif_cegid in tarif_list:
        error = False
        tar = TarifGe()
        mad = MiseADisposition.get_mise_a_disposition(tarif_cegid.adherent_code, tarif_cegid.salarie_code)
        if mad is None:
            # Si l'affaire n'est pas trouvé ici, c'est une erreur de coérence de table. On log et on ignore
            error = True
        
        # article
        try:
            article = Article.objects.get(code_erp=tarif_cegid.article_code)
        except Article.DoesNotExist:
            print(f"Impossible de trouver l'article {tarif_cegid.article_code} ({tarif_cegid.code})")
            error = True
        # article 2
        try:
            article2 = Article.objects.get(code_erp=tarif_cegid.article2_code)
        except Article.DoesNotExist:
            article2 = None

        if not error:
            tar.code_erp = tarif_cegid.code
            tar.mise_a_disposition = mad
            tar.article = article
            tar.article2 = article2
            tar.poste = tarif_cegid.poste
            tar.tarif = tarif_cegid.tarif
            tar.exportable = tarif_cegid.exportable
            tar.element_reference = tarif_cegid.eltnat
            tar.coef = tarif_cegid.coefficient
            tar.mode_calcul = tarif_cegid.mode_calcul
            tar.coef_paie = tarif_cegid.coefficient_paie
            tar.article_a_saisir = tarif_cegid.article_saisir
            tar.save()


    """
    tarif_list = session.query(CegidTarifGe).all()
    for tarif_cegid in tarif_list:
        error = False
        try:
            tar = TarifGe.objects.get(code_erp=tarif_cegid.code)
        except TarifGe.DoesNotExist:
            tar = TarifGe()

        # Affaire, qui peut être "TOUS". Cela veut dire que l'on prend toutes les affaires de ce salarié et on enregistre ce tarif
        if tarif_cegid.adherent_code == "TOUS":
            # il faut ajouter le tarif pour chaque mise a dispisition du salarie
            try:
                salarie = Salarie.objects.get(code_erp=tarif_cegid.salarie_code)
            except Salarie.DoesNotExist:
                error = True

            for mad in MiseADisposition.objects.filter(salarie=salarie):
                # article
                print(mad)
                try:
                    article = Article.objects.get(code_erp=tarif_cegid.article_code)
                except Article.DoesNotExist:
                    print(f"Impossible de trouver l'article {tarif_cegid.article_code} ({tarif_cegid.code})")
                    error = True
                # article 2
                try:
                    article2 = Article.objects.get(code_erp=tarif_cegid.article2_code)
                except Article.DoesNotExist:
                    article2 = None

                if not error:
                    tar.code_erp = tarif_cegid.code
                    tar.mise_a_disposition = mad
                    tar.article = article
                    tar.article2 = article2
                    tar.poste = tarif_cegid.poste
                    tar.tarif = tarif_cegid.tarif
                    tar.exportable = tarif_cegid.exportable
                    tar.element_reference = tarif_cegid.eltnat
                    tar.coef = tarif_cegid.coefficient
                    tar.mode_calcul = tarif_cegid.mode_calcul
                    tar.coef_paie = tarif_cegid.coefficient_paie
                    tar.article_a_saisir = tarif_cegid.article_saisir
                    tar.save()
                    print(tar.id)
                


        else :
            mad = MiseADisposition.get_mise_a_disposition(tarif_cegid.adherent_code, tarif_cegid.salarie_code)
            if mad is None:
                # Si l'affaire n'est pas trouvé ici, c'est une erreur de coérence de table. On log et on ignore
                error = True
        
        # article
        try:
            article = Article.objects.get(code_erp=tarif_cegid.article_code)
        except Article.DoesNotExist:
            print(f"Impossible de trouver l'article {tarif_cegid.article_code} ({tarif_cegid.code})")
            error = True
        # article 2
        try:
            article2 = Article.objects.get(code_erp=tarif_cegid.article2_code)
        except Article.DoesNotExist:
            article2 = None

        if not error:
            tar.code_erp = tarif_cegid.code
            tar.mise_a_disposition = mad
            tar.article = article
            tar.article2 = article2
            tar.poste = tarif_cegid.poste
            tar.tarif = tarif_cegid.tarif
            tar.exportable = tarif_cegid.exportable
            tar.element_reference = tarif_cegid.eltnat
            tar.coef = tarif_cegid.coefficient
            tar.mode_calcul = tarif_cegid.mode_calcul
            tar.coef_paie = tarif_cegid.coefficient_paie
            tar.article_a_saisir = tarif_cegid.article_saisir
            tar.save()
        

    """