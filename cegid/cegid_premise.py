from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import BigInteger, CHAR, Column, DECIMAL, Index, Integer, SmallInteger, String, Table, ForeignKey, PrimaryKeyConstraint, Numeric, DateTime
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.ext.declarative import declarative_base
from django.conf import settings
from datetime import date

engine = create_engine(settings.CEGID_PREMISE_CONNEXION)

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class ChoixExt(Base):
    """
        Table des listes de choix personnalisées
        Sera éclaté dans d'autres tables
        types :
            - LF1 : Services
            - LF2 : Postes
            - ...
    """
    __tablename__ = 'CHOIXEXT'

    type_choix = Column('YX_TYPE', CHAR(3, 'French_CI_AS'))
    code = Column('YX_CODE', String(17, 'French_CI_AS'))
    libelle = Column('YX_LIBELLE', String(105, 'French_CI_AS'))
    __table_args__ = (
        PrimaryKeyConstraint(code, type_choix),
    )


    def __str__(self):
        return self.libelle

class ChoixCod(Base):
    """
        Deuxieme table de liste de choix
        CC_TYPE=FN1 : Familles articles
    """
    __tablename__ = 'CHOIXCOD'

    type_choix = Column('CC_TYPE', CHAR(3, 'French_CI_AS'))
    code = Column('CC_CODE', CHAR(3, 'French_CI_AS'))
    libelle = Column('CC_LIBELLE', String(105, 'French_CI_AS'))
    abrege = Column('CC_ABREGE', String(17, 'French_CI_AS'))
    commentaire = Column('CC_LIBRE', String(70, 'French_CI_AS'))

    __table_args__ = (
        PrimaryKeyConstraint(type_choix, code),
    )

    @staticmethod
    def get_famille_article():
        return session.query(ChoixCod).filter(ChoixCod.type_choix == "FN1")


class Salarie(Base):
    """
        Table SALARIES
    """

    __tablename__ = 'SALARIES'

    code = Column('PSA_SALARIE', String(17, 'French_CI_AS'), unique=True)
    nom = Column('PSA_LIBELLE', String(35, 'French_CI_AS'), index=True)
    prenom = Column('PSA_PRENOM', String(35, 'French_CI_AS'))

    _date_entree = Column('PSA_DATEENTREE', DateTime)
    _date_sortie = Column('PSA_DATESORTIE', DateTime)

    __table_args__ = (
        PrimaryKeyConstraint(code),
    )

    affaire_list = relationship(
        "Affaire", 
        back_populates="salarie",
        lazy='dynamic',
    )

    @property
    def date_entree(self):
        # la date d'entrée
        return self._date_entree.date()

    @property
    def date_sortie(self):
        # la date de sortie
        try:
            if self._date_sortie.date() == date(1900,1,1):
                return None
            else:
                return self._date_sortie.date()
        except TypeError:
            print(f"sortie : {self._date_sortie.date()} : {type(self._date_sortie.date())}")
            print(f"1900 : {type(datetime.date(1900,1,1))}")
            raise TypeError



    def __str__(self):
        return "{} {}".format(self.prenom, self.nom)


class Tiers(Base):
    """
        Table des Tiers. Contient les clients et les fournisseurs
    """

    __tablename__ = "TIERS"

    auxiliaire = Column('T_AUXILIAIRE', String(17, 'French_CI_AS'), unique=True)
    nature_auxiliaire = Column('T_NATUREAUXI', CHAR(3, 'French_CI_AS'))
    code = Column('T_TIERS', String(17, 'French_CI_AS'), index=True)
    libelle = Column('T_LIBELLE', String(35, 'French_CI_AS'), index=True)

    affaire_list = relationship(
        "Affaire", 
        back_populates="adherent",
        lazy='dynamic',
    )

    __table_args__ = (
        PrimaryKeyConstraint(code),
    )



    def __str__(self):
        return "{}".format(self.libelle)

class Affaire(Base):
    """
        Table des affaires
    """
    __tablename__ = 'AFFAIRE'

    code = Column('AFF_AFFAIRE', String(17, 'French_CI_AS'), unique=True)
    code_0 = Column('AFF_AFFAIRE0', CHAR(1, 'French_CI_AS'))
    code_1 = Column('AFF_AFFAIRE1', String(14, 'French_CI_AS'))
    code_2 = Column('AFF_AFFAIRE2', String(13, 'French_CI_AS'))
    code_3 = Column('AFF_AFFAIRE3', String(12, 'French_CI_AS'))
    _etat = Column('AFF_ETATAFFAIRE', CHAR(3, 'French_CI_AS'))

    avenant = Column('AFF_AVENANT', String(2, 'French_CI_AS'))
    duree_travail_mensuel = Column('AFF_VALLIBRE2', Numeric(19, 4))
    duree_travail_quotidien = Column('AFF_VALLIBRE3', Numeric(19, 4))
    service_code = Column('AFF_LIBREAFF1', String(6, 'French_CI_AS'))
    poste_code = Column('AFF_LIBREAFF2', String(6, 'French_CI_AS'))
    coef_vente_soumis_code = Column('AFF_LIBREAFF3', String(6, 'French_CI_AS'))
    coef_vente_non_soumis_code = Column('AFF_LIBREAFF4', String(6, 'French_CI_AS'))

    created = Column('AFF_DATECREATION', DateTime)

    duree_travail_mensuel = Column('AFF_VALLIBRE2', Numeric(19, 4))
    duree_travail_quotidien = Column('AFF_VALLIBRE3', Numeric(19, 4))

    # C'est le code de la ressource, qui est identique au code salarié. Autant prendre les infos du salarié ici
    salarie_code = Column('AFF_RESPONSABLE', String(17, 'French_CI_AS'), ForeignKey('SALARIES.PSA_SALARIE'))
    salarie = relationship(
        "Salarie", 
        back_populates="affaire_list",
    )

    adherent_code = Column('AFF_TIERS', String(17, 'French_CI_AS'), ForeignKey('TIERS.T_TIERS'))
    adherent = relationship(
        "Tiers", 
        back_populates="affaire_list",
    )

    __table_args__ = (
        PrimaryKeyConstraint(code),
    )

    def cloturee(self):
        if self._etat == "ENC":
            return False
        else:
            return True

    @property
    def coef_vente_soumis(self):
        try:
            return int(self.coef_vente_soumis_code) / 1000
        except ValueError:
            return 0

    @property
    def coef_vente_non_soumis(self):
        try:
            return int(self.coef_vente_non_soumis_code) / 1000
        except ValueError:
            return 0
        

    def __str__(self):
        return self.code

class Remuneration(Base):
    """
        Table des rubriques de paie
    """
    __tablename__ = 'REMUNERATION'

    code = Column('PRM_RUBRIQUE', String(17, 'French_CI_AS'))
    libelle = Column('PRM_LIBELLE', String(35, 'French_CI_AS'))
    abrege = Column('PRM_ABREGE', String(17, 'French_CI_AS'))

    article_list = relationship(
        "Article", 
        back_populates="rubrique_paie",
        lazy='dynamic',
    )

    __table_args__ = (
        PrimaryKeyConstraint(code),
    )

    def __str__(self):
        return "{} {}".format(self.code, self.libelle)

class Article(Base):
    """
        Table des articles
    """
    __tablename__ = 'ARTICLE'

    code_interne = Column('GA_ARTICLE', String(35, 'French_CI_AS'), unique=True)
    code = Column('GA_CODEARTICLE', String(18, 'French_CI_AS'))
    type_article = Column('GA_TYPEARTICLE', CHAR(3, 'French_CI_AS'))
    libelle = Column('GA_LIBELLE', String(70, 'French_CI_AS'), index=True)
    # rubrique_paie_code = Column('GA_LIBREART1', String(6, 'French_CI_AS'))
    rubrique_paie_code = Column('GA_LIBREART1', String(6, 'French_CI_AS'), ForeignKey('REMUNERATION.PRM_RUBRIQUE'))
    # Famille article
    famille_code = Column('GA_FAMILLENIV1', CHAR(3, 'French_CI_AS'))

    rubrique_paie = relationship(
        "Remuneration", 
        back_populates="article_list",
    )

    __table_args__ = (
        PrimaryKeyConstraint(code),
    )

    def __str__(self):
        return self.libelle


class CegidTarifGe(Base):
    """
        Table des tarifs GE, qui associe les articles aux employés et aux adhérents
    """
    __tablename__ = 'ZTARIFSGE'

    code = Column('ZGE_ID', Integer, unique=True)
    adherent_code = Column('ZGE_CLIENT', String(17, 'French_CI_AS'))
    article_code = Column('ZGE_ARTICLE', String(18, 'French_CI_AS'))
    poste = Column('ZGE_POSTE', String(17, 'French_CI_AS'))
    salarie_code = Column('ZGE_RESSOURCE', String(17, 'French_CI_AS'))
    tarif = Column('ZGE_TARIF', Numeric(19, 4))
    _exportable = Column('ZGE_EXPORTABLE', CHAR(1, 'French_CI_AS'))
    article2_code = Column('ZGE_ARTICLE2', String(17, 'French_CI_AS'))
    eltnat = Column('ZGE_ELTNAT', String(17, 'French_CI_AS'))
    _coefficient = Column('ZGE_COEFFICIENT', Numeric(19, 4))
    mode_calcul = Column('ZGE_MODECALCUL', Integer)
    _coefficient_paie = Column('ZGE_COEFFPAIE', Numeric(19, 4))
    _article_saisir = Column('ZGE_ARTICLEASAISIR', CHAR(1, 'French_CI_AS'))

    __table_args__ = (
        PrimaryKeyConstraint(code),
    )

    @property
    def exportable(self):
        if self._exportable == None:
            return False
        elif self._exportable == "X":
            return True
        else:
            return False

    @property
    def article_saisir(self):
        if self._article_saisir == None:
            return False
        elif self._article_saisir == "X":
            return True
        else:
            return False

    @property
    def coefficient_paie(self):
        if self._coefficient_paie is None:
            return 0
        else:
            return self._coefficient_paie

    @property
    def coefficient(self):
        if self._coefficient is None:
            return 0
        else:
            return self._coefficient