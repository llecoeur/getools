from django.db import models
from geauth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.utils import timezone
from collections import defaultdict
from pprint import pprint
from django.urls import reverse
from django.db.models import Q


class FamilleArticle(models.Model):
    """
        Contient les familles articles
    """
    code_erp = models.CharField("Code ERP", max_length=200, null=True, blank=True, default="", db_index=True)
    libelle = models.CharField("Libelle", max_length=70, db_index=True)
    forfaitaire = models.BooleanField("Forfaitaire", default=False, db_index=True)

    def __str__(self):
        return self.libelle

class Article(models.Model):
    """
    Contient la liste des articles.
    Les articles sont toutles les typ
    """
    # Identifiant unique de l'ERP
    code_erp = models.CharField("Code ERP", max_length=200, null=True, blank=True, default="", db_index=True)
    libelle = models.CharField("Libelle", max_length=70, db_index=True)
    type_article = models.CharField("Type", max_length=70, default="", db_index=True)
    rubrique_paie = models.ForeignKey("RubriquePaie", on_delete=models.CASCADE, null=True, blank=True, default=None, db_index=True)
    famille = models.ForeignKey("FamilleArticle", on_delete=models.CASCADE, null=True, blank=True, default=None, related_name="article_list", db_index=True)

    def __str__(self):
        return self.libelle


class Adherent(models.Model):
    # Identifiant unique de l'ERP
    code_erp = models.CharField("Code ERP", max_length=200, null=True, blank=True, default=None, db_index=True)
    raison_sociale = models.CharField("Code ERP", max_length=50)

    def __str__(self):
        return self.raison_sociale


class Salarie(models.Model):
    # Identifiant unique de l'ERP
    code_erp = models.CharField("Code ERP", max_length=200, null=True, blank=True, default=None, db_index=True)
    # Utilisateur associé, if any :)
    nom = models.CharField("Nom", max_length=200, default="")
    prenom = models.CharField("Prenom", max_length=200, default="")
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, default=None, db_index=True)

    date_entree = models.DateField("Date d'entrée", null=True, default=None, blank=True, db_index=True)
    date_sortie = models.DateField("Date de sortie", null=True, default=None, blank=True, db_index=True)

    def __str__(self):
        return "{} {}".format(self.nom, self.prenom)

    @staticmethod
    def get_salaries_actuels():
        """
            Retourne un queryset des salariés actuellement dans le grouppement
        """
        return Salarie.objects.filter(Q(date_sortie=None) | Q(date_sortie__gt=timezone.now())).order_by("date_entree").order_by("nom")


class Service(models.Model):
    """
        Table des services des entreprises adhérentes
    """
    code_erp = models.CharField("Code ERP", max_length=70, null=True, blank=True, default=None, db_index=True)
    libelle = models.CharField("Libelle", max_length=70)

    def __str__(self):
        return self.libelle

class Poste(models.Model):
    """
        Table contenant les postes des salariés dans les mises a dispositions
    """

    code_erp = models.CharField("Code ERP", max_length=70, null=True, blank=True, default=None, db_index=True)
    libelle = models.CharField("Libelle", max_length=70)

    def __str__(self):
        return self.libelle


class RubriquePaie(models.Model):
    code_erp = models.CharField("Code ERP", max_length=70, null=True, blank=True, default=None, db_index=True)
    libelle = models.CharField("Libelle", max_length=70)
    abrege = models.CharField("Abrégé", max_length=70, default="")

    def __str__(self):
        return "{} ({})".format(self.libelle, self.code_erp)


class MiseADisposition(models.Model):
    # Identifiant unique ERP
    code_erp = models.CharField("Code ERP", max_length=18, db_index=True)
    # Adhérent de la mise a disposition 
    adherent = models.ForeignKey(Adherent, on_delete=models.CASCADE, related_name="mise_a_disposition_list", null=True, default=None, blank=True, db_index=True)
    # Salarié mis a disposition
    salarie = models.ForeignKey(Salarie, on_delete=models.CASCADE, related_name="mise_a_disposition_list", db_index=True)
    # Est ce que la mad est terminée ?
    cloturee = models.BooleanField("Mise à disposition cloturée ?", default=False, db_index=True)

    # Temps de travail mensuel sur la mad :
    duree_travail_mensuel = models.FloatField("Temps de travail mensuel", default=0)
    # Temps de travail quotidien sur la mad
    duree_travail_quotidien = models.FloatField("Temps de travail quotidien", default=0)
    
    # Service dans lequel est rattaché le salarié dans l'entreprise adhérente
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="mise_a_disposition_list", null=True, default=None, blank=True)

    # Poste occupé par le salarié pour cette mad
    poste = models.ForeignKey(Poste, on_delete=models.CASCADE, related_name="mise_a_disposition_list", null=True, default=None, blank=True)
    coef_vente_soumis = models.FloatField("Coef de vente soumis", default=0)
    coef_vente_non_soumis = models.FloatField("Coef de vente non soumis", default=0)

    @property
    def tarif_ge_list_dict(self):
        d = []
        for tarif in self.tarif_ge_list.all().exclude(article__famille__forfaitaire=True).order_by("id"):
            d.append(tarif.to_dict())
        return d

    def tarifs_ge_prime_forfaitaire_dict(self):
        d = []
        for tarif in self.tarif_ge_list.filter(article__famille__forfaitaire=True).order_by("id"):
            print(tarif.to_dict())
            d.append(tarif.to_dict())
        return d

    @staticmethod
    def get_mise_a_disposition(adherent_code_erp, salarie_code_erp):
        """
            Retourne la mise a dispo correspondant a l'adherent et salarié passé en paramètre
        """
        try:
            salarie = Salarie.objects.get(code_erp = salarie_code_erp)
            adherent = Adherent.objects.get(code_erp = adherent_code_erp)
        except ObjectDoesNotExist:
            return None
        try:
            mad = MiseADisposition.objects.get(adherent=adherent, salarie=salarie)
        except MiseADisposition.MultipleObjectsReturned:
            print(f"Il existe plusieurs Mise a disposition {adherent} - {salarie}")
            return None
        except MiseADisposition.DoesNotExist:
            return None
        return mad

    def get_saisies_from_mois_dict(self, mois, annee):
        """
            Retourne un tableau a deux dimenstions:
            valeur[jour][tarif_id] pour remplir les champs de saisie
        """
        # Les saisies liées a une mad
        saisie_list = SaisieActivite.objects.filter(date_realisation__year=annee, date_realisation__month=mois, tarif__mise_a_disposition=self)
        d = defaultdict(dict)
        for saisie in saisie_list:
            d[saisie.date_realisation.day][saisie.tarif.id] = saisie.quantite
        return d

    def __str__(self):
        return f"{self.adherent} - {self.salarie}"
    

class TarifGe(models.Model):
    """
        Equivalent de la table ZTARIFSGE de Cegid v9
        Certaines relations sont adaptées
    """
    # Code ERP du tarif. Ici c'est un integer. Allez savoir pouquoi...
    code_erp = models.IntegerField(default=0, db_index=True)
    # L'article concerné
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="tarif_ge_list", db_index=True)
    # La mise a disposition, qui permet ensuite de faire la liaison avec l'adhérent et le salarié. Si None, le code s'applique a tous les adhérents, et le code salarié est a prendre dnas le champ suivant
    mise_a_disposition = models.ForeignKey(MiseADisposition, on_delete=models.CASCADE, related_name="tarif_ge_list", null=True, default=None, blank=True, db_index=True)
    # ???
    poste = models.CharField("Poste", max_length=17, blank=True)
    # Tarif horaire ?
    tarif = models.FloatField("Tarif", default=0)
    # Case a cocher. Pas sur que ce soit utilisé
    exportable = models.BooleanField("Exportable ?", default=False, null=True)
    # ??? Pourquoi un second article ?
    article2 = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, default=None, blank=True)
    # ???
    element_reference = models.CharField("Elt Nationnal de Référence", max_length=17, blank=True)
    # Les hamps suivants existent en base Cegid, a expliquer ou supprimer si pas utiles.
    coef = models.FloatField("Coefficient", default=0)
    mode_calcul = models.IntegerField("Mode de Calcul")
    coef_paie = models.FloatField("Coefficient de paie", default=0)
    article_a_saisir = models.BooleanField("Article a saisir ?", default=False)

    archive = models.BooleanField("Archivé", default=False)

    def get_absolute_url(self):
        return reverse('tarifge-update', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.mise_a_disposition} - {self.article}"

    def to_dict(self):
        d = model_to_dict(self)
        d['article'] = model_to_dict(self.article)
        return d

class SaisieActivite(models.Model):
    """
        Table des saisies effectuées sur activité
    """
    # Tarif correspondant a cette saisie
    tarif = models.ForeignKey(TarifGe, on_delete=models.CASCADE, related_name="saisie_activite_list", default=None)
    # la date a laquelle cette saisie est associée
    date_realisation = models.DateField("Date")
    # la quantité, la plupart du temps en heure, de cette saisie
    quantite = models.FloatField("Quantité")
    


    created = models.DateTimeField("Creation")
    updated = models.DateTimeField("Modification")

    def save(self):
        # positionnement automatique a l'enregistrement des champs created et updated
        if not self.id:
            self.created = timezone.now()
        self.updated = timezone.now()
        super().save()


    @staticmethod
    def get_saisie(tarif, date_realisation):
        """
            retourne un objet tarif pour une saisie a une date donnée. Si n'existe pas, retourne None
        """
        try:
            return SaisieActivite.objects.get(tarif=tarif, date_realisation=date_realisation)
        except SaisieActivite.DoesNotExist:
            return None

"""
Les tables suivantes existent dans les pécifiques Cegid, et doivent servir a saisir les activités.
Elles peuvent je pense être remplacéers par quelque chose de plus utilisable.

"""

class CreditTemps(models.Model):
    """
        Equivalent de la table ZCREDITTEMPS de Cegid V9
        A Documenter
    """
    salarie = models.ForeignKey(Salarie, on_delete=models.CASCADE, related_name="credit_temps")
    mois = models.IntegerField("Mois")
    année = models.IntegerField("Année")
    heures_travaillees = models.FloatField("Heures Travaillées")
    heures_theoriques = models.FloatField("heures Théoriques")
    # ???
    id_detail = models.IntegerField("")


class DetailCreditTemps(models.Model):
    """
        Equivalent de la taille ZDETAILCREDITTEMPS de Cegid 
    """
    mise_a_disposition = models.ForeignKey(MiseADisposition, on_delete=models.CASCADE, related_name="detail_credit_temps_list", default=None)
    heures_travaillees = models.FloatField("Heures Travaillées")
    heures_mensuelles = models.FloatField("heures mensuelles")
    saisiecomplete = models.BooleanField("Saise Comlète ?")



"""
class SaisieActiviteOld(models.Model):
    mise_a_disposition = models.ForeignKey(MiseADisposition, on_delete=models.CASCADE, related_name="saisie_activite_list", default=None)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="saisie_activite_list")
    quantite = models.FloatField("Quantité")
    # Origine : Pas sur que ce soit uilisé. C'est positionné à Saisie sur la totalité de la table dabs Cegid
    origine = models.CharField("Origine", max_length=17)
    prix_revient = models.FloatField("Prix de Revient")
    prix_vente = models.FloatField("Prix de Vente")
    # Ce champ a 3 valeurs, 0-1-2. A quoi ca sert ?
    exporte = models.IntegerField("Exporte")
    type_ligne = models.CharField("type_ligne", max_length=11)
    created = models.DateTimeField("Creation")
"""