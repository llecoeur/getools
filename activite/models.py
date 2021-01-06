from django.db import models
# from geauth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.utils import timezone
from collections import defaultdict, namedtuple
from pprint import pprint
from django.urls import reverse
import calendar
from datetime import date, datetime, timedelta
from jours_feries_france import JoursFeries
import pendulum
pendulum.set_locale('fr')
from django.db.models import Q, Sum
from django.core.exceptions import ObjectDoesNotExist


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
    ordre = models.IntegerField("Ordre", default=0, null=True, db_index=True)
    unite = models.CharField("Unité", default="", max_length=10)
    charges_soumises = models.BooleanField("Charges soumises ?", null=True, default=True)
    facturation_uniquement = models.BooleanField("Facturation uniquement", null=True, default=False)

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return self.libelle

    def _next_ordre(self):
        article = Article.objects.all().order_by("-ordre").first()
        if article is None:
            return 1
        else:
            return article.ordre + 1


    def save(self):
        if not self.id:
            self.ordre = self._next_ordre()
        super().save()


class Adherent(models.Model):
    # Identifiant unique de l'ERP
    code_erp = models.CharField("Code ERP", max_length=200, null=True, blank=True, default=None, db_index=True)
    raison_sociale = models.CharField("Code ERP", max_length=50)

    def __str__(self):
        return "{} ({})".format(self.raison_sociale, self.code_erp)

    def get_releve_list(self, annee, mois):
        """
            Retourne tous les relevés salariés ou cet adhérent est listé, trié par nom de salarié
        """
        saisie_list = self.saisie_salarie_list.filter(date__month=mois, date__year=annee).distinct("releve")
        releve_list = []
        for saisie in saisie_list:
            releve_list.append(saisie.releve)
        return releve_list

    def total_heures_mois(self, annee, mois):
        """
            retourne le nombre d'heures total passé chez cet adhérent dans le mois donné en heures normales et heures supplémentaires
            
        """
        q = (
            SaisieActivite.objects
            .filter(date_realisation__month=mois, date_realisation__year=annee)
            .filter(tarif__mise_a_disposition__adherent=self)
            .filter(Q(tarif__article__libelle="HEURES NORMALES") | Q(tarif__article__libelle__startswith="HEURES SUPPLEMENTAIRES") )
            .exclude(tarif__article__famille__forfaitaire=True)
            .aggregate(Sum("quantite"))
        )
        return q['quantite__sum']


class Salarie(models.Model):
    # Identifiant unique de l'ERP
    code_erp = models.CharField("Code ERP", max_length=200, null=True, blank=True, default=None, db_index=True)
    # Utilisateur associé, if any :)
    nom = models.CharField("Nom", max_length=200, default="")
    prenom = models.CharField("Prenom", max_length=200, default="")
    # user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, default=None, db_index=True, related_name="salarie_cegid")
    memo = models.TextField("Mémo", null=True, blank=True, default=None)

    date_entree = models.DateField("Date d'entrée", null=True, default=None, blank=True, db_index=True)
    date_sortie = models.DateField("Date de sortie", null=True, default=None, blank=True, db_index=True)

    class Meta:
        ordering = ['nom']

    def __str__(self):
        return "{} {} ({})".format(self.nom, self.prenom, self.code_erp)

    def get_saisies_releve_mois_dict_all(self, mois, annee):
        """
            returne le calendrier et les valeurs de saisies des relevés mensuels pour le mois donné en param
        """
        start, end = calendar.monthrange(annee, mois)

        # CHargement du relevé, et création si il n'existe pas
        try:
            releve = self.releve_heures_list.get(mois=mois, annee=annee)
        except ObjectDoesNotExist:
            releve = self.releve_heures_list.create(mois=mois, annee=annee)

        d = []
        for num_jour in range(1, end + 1):
            date_saisie = date(annee, mois, num_jour)
            # Liste des saisies du jour

            s = []
            mad_list = self.current_mad_list
            for mad in mad_list:
                saisie = releve.get_saisie(mad.adherent, date_saisie)
                s.append(model_to_dict(saisie))
            # Ajout des absences
            absence = releve.get_saisie(None, date_saisie)
            s.append(model_to_dict(absence))
            pen_day = pendulum.date(annee, mois, num_jour)
            ferie = JoursFeries.is_bank_holiday(date(annee, mois, num_jour), zone="Métropole")
            samedi_dimanche = pen_day.day_of_week == pendulum.SUNDAY or pen_day.day_of_week == pendulum.SATURDAY
            commentaire = model_to_dict(releve.get_commentaire(num_jour))
            j = {
                "num": num_jour,
                "str": pen_day.format("dddd D").capitalize(),
                "non_travaille": samedi_dimanche or ferie,
                "saisie_list": s,
                "commentaire": commentaire,
            }
            d.append(j)
        return d


    @property
    def current_mad_list(self):
        """
            retourne la liste des mads ouvertes du salarié
        """
        return self.mise_a_disposition_list.filter(cloturee=False).order_by('adherent__raison_sociale')

    def get_info_sup(self, mois, annee):
        """
            Retourne l'objet InfoSupMois associé au salarié
            Si n'existe pas, alos ca la crée et l'initialise
        """

        try:
            infos_sup = self.infos_sup_list.get(mois=mois, annee=annee)
        except (InfosSupMoisSalarie.DoesNotExist, AttributeError):
            infos_sup = InfosSupMoisSalarie()
            infos_sup.salarie = self
            infos_sup.mois = mois
            infos_sup.annee = annee
            # TODO : Initialiser ces valeurs
            infos_sup.heures_theoriques = 0
            infos_sup.save()
        return infos_sup

    def get_heures_travail_mois(self, annee, mois):
        """
            Retourne le nombre d'heures total travaillées par le salarié dans le mois, quelque soit les mises a dispos
        """
        # saisies du salarié
        qs = SaisieActivite.objects.filter(tarif__mise_a_disposition__salarie=self)
        # sur le mois en cours
        qs = qs.filter(date_realisation__year=annee,date_realisation__month=mois)
        # Uniquement ls heures normales
        qs = qs.filter(tarif__article__code_erp="H NORM")
        # Exclure les primes forfaitaires
        qs = qs.exclude(tarif__article__famille__forfaitaire=True)
        val = qs.aggregate(Sum('quantite')).get('quantite__sum')
        if val is None:
            val = 0
        return round(val, 2)

    def get_releve_dict(self, releve, mois, annee):
        """
            Retourne le relevé et les infos associées, sous forme de dict
        """
        
        releve_dict = model_to_dict(releve)
        releve_dict['salarie'] = model_to_dict(self)
        releve_dict['mad_list'] = []
        mad_list = self.current_mad_list
        for mad in mad_list:
            m = model_to_dict(mad)
            m['adherent'] = model_to_dict(mad.adherent)
            releve_dict['mad_list'].append(m)

        releve_dict['jours_list'] = self.get_saisies_releve_mois_dict_all(mois, annee)
        return releve_dict

    @staticmethod
    def get_salaries_actuels():
        """
            Retourne un queryset des salariés dans le groupement
            Les salariés sortis apres le 1er jour du mois N-2 est considéré comme sorti
            ex : On est au mois de novembre. Un salarié non listé aura une date de sortie avant le 1er septembre (Mois-2).
        
        """
        # date_compare = date(timezone.now().year, timezone.now().month - 2, 1)
        date_compare = ((timezone.now().replace(day=1) - timedelta(days=62)).replace(day=1)).date()
        return Salarie.objects.filter(Q(date_sortie=date(1900,1,1)) | Q(date_sortie__gt=date_compare)).order_by("date_entree").order_by("nom")
        # return Salarie.objects.filter(Q(date_sortie=date(1900,1,1)) | Q(date_sortie__gt=timezone.now())).order_by("date_entree").order_by("nom")

    def get_paie(self, annee, mois):
        """
            Crée le tableau de paie du salarié
        """
        mad_list = self.mise_a_disposition_list.filter(cloturee=False).order_by("adherent__raison_sociale")
        # stockage de tous les dicts des rubriques a envoyer en paie
        rub_list = []
        # Compteur de rubrique, pour gérer les incréments
        compteur_rubrique_paie = RubriquePaieCodeCompteur()
        for mad in mad_list:
            # on liste les tarifs avec leurs sommes pour cette mad
            # print(f"Adhérent : {mad.adherent.raison_sociale}")
            tarif_list = (
                TarifGe.objects
                .filter(mise_a_disposition=mad)
                .filter(article__facturation_uniquement=False)
                .filter(saisie_activite_list__date_realisation__year=annee, saisie_activite_list__date_realisation__month=mois)
                .exclude(article__rubrique_paie=None)
                .annotate(quantites = Sum('saisie_activite_list__quantite'))
                .exclude(quantites=None)
                .exclude(quantites=0)
                .order_by("mise_a_disposition__adherent__raison_sociale")
            )

            for tarif in tarif_list:
                # On est forfaitaire ?
                try:
                    forfaitaire = tarif.article.famille.forfaitaire
                except AttributeError:
                    forfaitaire = False

                if forfaitaire:
                    base = 1
                    rate = tarif.quantites
                else:
                    if tarif.tarif_pere:
                        base = tarif.quantites
                        rate = tarif.tarif_pere.tarif * tarif.coef
                    else:
                        base = tarif.quantites
                        rate = tarif.tarif

                rubrique_code = compteur_rubrique_paie.get_code(tarif.article.rubrique_paie.code_erp)
                # On prend le libelle de la nouvelle rubrique
                label_rubrique = RubriquePaie.get_libelle(rubrique_code, tarif.article.rubrique_paie.code_erp)
                label_substitution = (label_rubrique + " " + tarif.mise_a_disposition.adherent.raison_sociale)[:35]
                # print(f"{rubrique_code} : {label_substitution}")
                d ={
                    # "ImportType": "MH2",
                    "ImportType": "MHE",
                    "EmployeeId": self.code_erp,
                    "BeginDatePayroll": date(annee, mois, 1).strftime("%Y-%m-%d"),
                    "EndDatePayroll": date(annee, mois, 1).strftime("%Y-%m-") + str(calendar.monthrange(annee, mois)[1]),
                    "NumberOrder": 1,
                    "Rubric": rubrique_code,
                    "RubricLabelSubstitution": label_substitution,
                    "TypeSupplyRubric": "BT",
                    "PayrollBase": round(base, 2),
                    "PayrollRate": rate,
                    "BeginDateDSN": date(annee, mois, 1).strftime("%Y-%m-%d"),
                    "EndDateDSN": date(annee, mois, 1).strftime("%Y-%m-") + str(calendar.monthrange(annee, mois)[1]),
                }
                rub_list.append(d)

        # Ajout des rublriques standard : 9903, etc...
        info_sup = self.get_info_sup(mois, annee)
        # 9901 et 9903
        tmp_rub_list = RubriquePaie.objects.filter(code_erp__in=["9901", "9903"])
        for rub in tmp_rub_list:
            d ={
                # "ImportType": "MH2",
                "ImportType": "MHE",
                "EmployeeId": self.code_erp,
                "BeginDatePayroll": date(annee, mois, 1).strftime("%Y-%m-%d"),
                "EndDatePayroll": date(annee, mois, 1).strftime("%Y-%m-") + str(calendar.monthrange(annee, mois)[1]),
                "NumberOrder": 1,
                "Rubric": rub.code_erp,
                "RubricLabelSubstitution": rub.libelle,
                "TypeSupplyRubric": "BT",
                "PayrollBase": round(info_sup.heures_travaillees, 2),
                "PayrollRate": 0,
                "BeginDateDSN": date(annee, mois, 1).strftime("%Y-%m-%d"),
                "EndDateDSN": date(annee, mois, 1).strftime("%Y-%m-") + str(calendar.monthrange(annee, mois)[1]),
                
            }
            rub_list.append(d)
        if info_sup.difference_heures < 0:
            # Différence d'heure négatif
            rub = RubriquePaie.objects.get(code_erp="9913")
            d ={
                # "ImportType": "MH2",
                "ImportType": "MHE",
                "EmployeeId": self.code_erp,
                "BeginDatePayroll": date(annee, mois, 1).strftime("%Y-%m-%d"),
                "EndDatePayroll": date(annee, mois, 1).strftime("%Y-%m-") + str(calendar.monthrange(annee, mois)[1]),
                "NumberOrder": 1,
                "Rubric": rub.code_erp,
                "RubricLabelSubstitution": rub.libelle,
                "TypeSupplyRubric": "BT",
                "PayrollBase": round(abs(info_sup.difference_heures), 2),
                "PayrollRate": 0,
                "BeginDateDSN": date(annee, mois, 1).strftime("%Y-%m-%d"),
                "EndDateDSN": date(annee, mois, 1).strftime("%Y-%m-") + str(calendar.monthrange(annee, mois)[1]),
                
            }
            rub_list.append(d)
        if info_sup.difference_heures > 0:
            # différence heures positif
            rub = RubriquePaie.objects.get(code_erp="9911")
            d ={
                # "ImportType": "MH2",
                "ImportType": "MHE",
                "EmployeeId": self.code_erp,
                "BeginDatePayroll": date(annee, mois, 1).strftime("%Y-%m-%d"),
                "EndDatePayroll": date(annee, mois, 1).strftime("%Y-%m-") + str(calendar.monthrange(annee, mois)[1]),
                "NumberOrder": 1,
                "Rubric": rub.code_erp,
                "RubricLabelSubstitution": rub.libelle,
                "TypeSupplyRubric": "BT",
                "PayrollBase": round(abs(info_sup.difference_heures), 2),
                "PayrollRate": 0,
                "BeginDateDSN": date(annee, mois, 1).strftime("%Y-%m-%d"),
                "EndDateDSN": date(annee, mois, 1).strftime("%Y-%m-") + str(calendar.monthrange(annee, mois)[1]),
                
            }
            rub_list.append(d)
        # pprint(rub_list)
        return rub_list

    @property
    def sorti(self):
        """
            True si sorti, False sinon
        """
        date_compare = ((timezone.now().replace(day=1) - timedelta(days=62)).replace(day=1)).date()
        if self.date_sortie == date(1900,1,1):
            return False
        elif self.date_sortie > date_compare:
            return False
        else:
            return True

 

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

    @staticmethod
    def get_libelle(code_erp, code_defaut):
        """
            Retourne le libellé du code_erp. Si non trovué, retourne le libellé de la rubrique par défaut
        """
        try:
            rub = RubriquePaie.objects.get(code_erp=code_erp)
        except RubriquePaie.DoesNotExist:
            try:
                rub = RubriquePaie.objects.get(code_erp=code_defaut)
            except RubriquePaie.DoesNotExist:
                return "ERREUR : RURBIQUES INCONNUES"
        return rub.libelle



class RubriquePaieCodeCompteur():
    """
        Classe servant a générer les codes des rubriques incrémentés pour la paie
        rubrique_dict est un dictionnaire des codes. La clef est le code de rubrique, la valeur est le prochain code a utiliser
    """
    
    def __init__(self):
        self.rubrique_code_dict = {}

    def increment(self, code):
        """
            incrémente le code de 2, et le positionne si il n'existe pas, et complété avec des 0 si < en longueur
        """
        inc_code = self.rubrique_code_dict[code]

        inc_code = str(int(inc_code) + 2)
        # On complète les 0 initiaux pour faire 4 caractères
        while len(inc_code) != 4:
            inc_code = '0' + inc_code

        self.rubrique_code_dict[code] = inc_code
        return inc_code
        


    def get_code(self, code):
        """
            Retourne le code de rubrique a utiliser pour le code initial donné
        """
        try:
            next_code = self.rubrique_code_dict[code]
        except KeyError:
            # Le code n'existe pas, on le positionne, et on retourne le code actuel
            self.rubrique_code_dict[code] = code
            next_code = code
        # On incrémente le code
        self.increment(code)
        return next_code


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
        for tarif in self.tarif_ge_list.filter(archive=False).exclude(article__famille__forfaitaire=True).order_by("article__ordre"):
            d.append(tarif.to_dict())
        return d

    def tarifs_ge_prime_forfaitaire_dict(self):
        """
            Retourne ls primes forfaitaires
        """
        d = []
        for tarif in self.tarif_ge_list.filter(article__famille__forfaitaire=True).order_by("id"):
            d.append(tarif.to_dict())
        return d

    def prime_forfaitaire_values_list(self, annee, mois):
        """
            retourne la liste des values primes forfaitaires du mois
        """
        d = []
        saisie_list = SaisieActivite.objects.filter(tarif__mise_a_disposition=self, date_realisation=date(annee, mois, 1)).order_by("id")
        for saisie in saisie_list:
            tarif_dict = saisie.tarif.to_dict()
            saisie_dict = {
                "date_realisation": saisie.date_realisation,
                "quantite": saisie.quantite,
                "id": saisie.id,
                "tarif_id": saisie.tarif_id,
                "tarif": tarif_dict,
                "uploaded": saisie.uploaded,
            }
            d.append(saisie_dict)
        return d

    def get_activites_to_upload(self):
        """
            Renvoie un tableau de la liste des activités a uploader our cette MAD
        """
        activite_list = SaisieActivite.objects.filter(tarif__mise_a_disposition=self, uploaded=False)
        activite_dict_array = []
        for activite in activite_list:
            if activite.quantite != 0:
                activite_dict_array.append(activite.to_xrp_dict())
        return activite_dict_array



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

    def get_saisies_from_mois_dict_all(self, mois, annee):

        # Listes des jours du mois
        start, end = calendar.monthrange(annee, mois)
        # print(calendar.monthrange(annee, mois))
        d = []

        # Récupération du relevé :
        # CHargement du relevé, et création si il n'existe pas
        try:
            releve = self.salarie.releve_heures_list.get(mois=mois, annee=annee)
        except ObjectDoesNotExist:
            releve = self.salarie.releve_heures_list.create(mois=mois, annee=annee)
       

        # releve = self.salarie.releve_heures_list.get(mois=mois, annee=annee)

        for num_jour in range(1, end + 1):
            date_saisie = date(annee, mois, num_jour)
            # récupérer les tarids de la mise a disposition
            
            s = []
            for tarif in self.tarif_ge_list.filter(archive=False).exclude(article__famille__forfaitaire=True).order_by("article__ordre"):
                saisie = SaisieActivite.get_saisie(tarif, date_saisie)
                if saisie is None:
                    s.append({ "tarif": tarif.id, "valeur": 0, "saved": False, })
                else:
                    s.append({ "tarif": tarif.id, "valeur": saisie.quantite, "saved": True, "uploaded": saisie.uploaded, })

            pen_day = pendulum.date(annee, mois, num_jour)
            ferie = JoursFeries.is_bank_holiday(date(annee, mois, num_jour), zone="Métropole")
            samedi_dimanche = pen_day.day_of_week == pendulum.SUNDAY or pen_day.day_of_week == pendulum.SATURDAY

            j = {
                "num": num_jour,
                "str": pen_day.format("dddd D").capitalize(),
                "non_travaille": samedi_dimanche or ferie,
                "releve_adherent": model_to_dict(releve.get_saisie(self.adherent, date_saisie)),
                "releve_commentaire": model_to_dict(releve.get_commentaire(num_jour)),
                "releve_absence": model_to_dict(releve.get_saisie(None, date_saisie)),
                "saisie_list": s, 
            }
            d.append(j)

        # pprint(d)
        return d

    def get_info_sup(self, mois, annee):
        """
            Retourne l'objet InfoSupMois associé à la MAD
            Si n'existe pas, alos ca la crée et l'initialise
        """
        try:
            infos_sup_mad = self.infos_sup_list.get(mois=mois, annee=annee)
        except (InfosSupMoisMad.DoesNotExist, AttributeError):
            infos_sup_mad = InfosSupMoisMad()
            infos_sup_mad.mise_a_disposition = self
            infos_sup_mad.mois = mois
            infos_sup_mad.annee = annee
            # TODO : Initialiser ces valeurs
            infos_sup_mad.heures_theoriques = 0
            infos_sup_mad.heures_travaillees = 0
            infos_sup_mad.saisie_complete = False
            infos_sup_mad.save()
        return infos_sup_mad

    def get_heures_travail_mois(self, annee, mois):
        """
            Retourne le nombre d'heures total travaillées sur la MAD dans le mois
        """
        # saisies du salarié
        qs = SaisieActivite.objects.filter(tarif__mise_a_disposition=self)
        # sur le mois en cours
        qs = qs.filter(date_realisation__year=annee,date_realisation__month=mois)
        # Uniquement des heures
        qs = qs.filter(tarif__article__unite="H")
        # Exclure les primes forfaitaires
        qs = qs.exclude(tarif__article__famille__forfaitaire=True)
        val = qs.aggregate(Sum('quantite')).get('quantite__sum')
        if val is None:
            val = 0
        return val

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
    poste = models.CharField("Poste", max_length=17, blank=True, db_index=True)
    # Tarif horaire ?
    tarif = models.FloatField("Montant", default=0, db_index=True)
    # Case a cocher. Pas sur que ce soit utilisé
    exportable = models.BooleanField("Exportable ?", default=False, null=True, db_index=True)
    # Tarif fils de référence
    tarif_pere = models.ForeignKey("TarifGe", on_delete=models.CASCADE, null=True, default=None, blank=True)
    # Coef en cas de tarif fils
    coef = models.FloatField("Coefficient appliqué au père", default=0)
    # ???
    element_reference = models.CharField("Elt Nationnal de Référence", max_length=17, blank=True)
    # Les hamps suivants existent en base Cegid, a expliquer ou supprimer si pas utiles.
    
    mode_calcul = models.IntegerField("Mode de Calcul", default=None, null=True, blank=True)
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
    tarif = models.ForeignKey(TarifGe, on_delete=models.CASCADE, related_name="saisie_activite_list", default=None, db_index=True)
    # la date a laquelle cette saisie est associée
    date_realisation = models.DateField("Date", db_index=True)
    # la quantité, la plupart du temps en heure, de cette saisie
    quantite = models.FloatField("Quantité")
    # Est ce que la saisie a été envoyée vers l'activité correspondante de XRP Sprint ?
    uploaded = models.BooleanField("Envoyée", default=False, db_index=True)
    created = models.DateTimeField("Creation", db_index=True)
    updated = models.DateTimeField("Modification", db_index=True)

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


    def to_xrp_dict(self):
        """
            Retourne les données de l'activité sous forme de dictionnaire intégrable directement dans XRP sprint si trnasformé en json
        """
        try:
            forfaitaire = self.tarif.article.famille.forfaitaire
        except AttributeError:
            forfaitaire = False

        if forfaitaire == True:
            if self.tarif.article.charges_soumises is True:
                selling_price = self.quantite * (int(self.tarif.mise_a_disposition.coef_vente_soumis) / 1000)
            elif self.tarif.article.charges_soumises is False:
                selling_price = self.quantite * (int(self.tarif.mise_a_disposition.coef_vente_non_soumis) / 1000)
            else:
                selling_price = self.quantite
            qte = 1
            cost = self.quantite

        else:
            if self.tarif.tarif_pere is None:
                if self.tarif.article.charges_soumises is True:
                    selling_price = self.tarif.tarif * (int(self.tarif.mise_a_disposition.coef_vente_soumis) / 1000)
                elif self.tarif.article.charges_soumises is False:
                    selling_price = self.tarif.tarif * (int(self.tarif.mise_a_disposition.coef_vente_non_soumis) / 1000)
                else:
                    selling_price = self.tarif.tarif
                cost = self.tarif.tarif
                qte = self.quantite
            else:
                # En cas de tarif parent, alors il faut prendre le tarif parent et le multiplier par le coeficient
                if self.tarif.article.charges_soumises is True:
                    selling_price = self.tarif.tarif_pere.tarif * self.tarif.coef * (int(self.tarif.mise_a_disposition.coef_vente_soumis) / 1000)
                elif self.tarif.article.charges_soumises is False:
                    selling_price = self.tarif.tarif_pere.tarif * self.tarif.coef * (int(self.tarif.mise_a_disposition.coef_vente_non_soumis) / 1000)
                else:
                    selling_price = self.tarif.tarif_pere.tarif * self.tarif.coef
                cost = self.tarif.tarif_pere.tarif * self.tarif.coef
                qte = self.quantite

        return {
            "Project": self.tarif.mise_a_disposition.code_erp,
            "Resource": self.tarif.mise_a_disposition.salarie.code_erp,
            "ActivityDate": self.date_realisation.strftime("%Y-%m-%d"),
            "ThirdParty": self.tarif.mise_a_disposition.adherent.code_erp,
            "ItemType": self.tarif.article.type_article,
            "Item": self.tarif.article.libelle,
            "ItemCode": self.tarif.article.code_erp,
            "Unit": self.tarif.article.unite,
            "Quantity": qte,
            # Tarif du GE
            "CostPrice": cost,
            # Tarif du tarif GE * coef_vente_soumis, ou coef_vente_soumis de l'affaire (mad)
            "SellingPrice": round(selling_price, 2), 
            # Obligatoire, sinon ca bug dans Cegid !
            "ExpensesSheetId": 0,
            "ResourceExpensePayId": 0,
        }

"""
Les tables suivantes existent dans les pécifiques Cegid, et doivent servir a saisir les activités.
Elles peuvent je pense être remplacéers par quelque chose de plus utilisable.
"""

class InfosSupMoisSalarie(models.Model):
    """
        Equivalent de la table ZCREDITTEMPS de Cegid V9
        
        Contient les informations liées au salarié pour le mois et l'année donnée
    """
    salarie = models.ForeignKey(Salarie, on_delete=models.CASCADE, related_name="infos_sup_list", db_index=True)
    mois = models.IntegerField("Mois", db_index=True)
    annee = models.IntegerField("Année", db_index=True)
    # Nombre d'heures travaillées sur le mois pour le salarié, quelque soit a MAD
    heures_travaillees = models.FloatField("Heures Travaillées", db_index=True, default=0)
    # Nombre d'heures théoriques que le salarié doit réaliser dans le mois. Initialisé en fonction du calendrier et doit être modifiable
    heures_theoriques = models.FloatField("heures Théoriques", db_index=True)
    difference_heures = models.FloatField("Différence théorique - travaillé", db_index=True, default=0)
    paie_envoyee = models.BooleanField("Paie Envoyée ?", db_index=True, default=False) 
    # Memo, modifiable et récupérable d'un mois sur l'autre
    memo = models.TextField("Memo", default="", blank=True)
    # ???
    # id_detail = models.IntegerField("")

    @property
    def heures_travaillees(self):
        return self.salarie.get_heures_travail_mois(self.annee, self.mois)


class InfosSupMoisMad(models.Model):
    """
        Equivalent de la taille ZDETAILCREDITTEMPS de Cegid

        Contient les informations liées a la mise a disposition pour le mois en cours
    """
    mise_a_disposition = models.ForeignKey(MiseADisposition, on_delete=models.CASCADE, related_name="infos_sup_list", db_index=True)
    mois = models.IntegerField("Mois", default=0, db_index=True)
    annee = models.IntegerField("Année", default=0, db_index=True)
    # Heures travaillées chez l'adhérent ce mois
    heures_travaillees = models.FloatField("Heures Travaillées")
    # Heures théoriques chez l'adherent ce mois. Initialisé comment ?
    heures_theoriques = models.FloatField("heures mensuelles")
    # Est ce que la saisie est complète ? None : Non démarré, False : En cours, True : Terminée
    saisie_complete = models.BooleanField("Saise Comlète ?", null=True, default=None, db_index=True)
    # Memo, modifiable et récupérable d'un mois sur l'autre
    memo = models.TextField("Memo", default="", blank=True)



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