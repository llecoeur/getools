import os
import sys
sys.path.append('..')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "getools.settings")
import django
django.setup()
from datetime import datetime
import urllib.parse
import pyodbc 
from django.conf import settings
from cegid.cegid_premise import session, Salarie, Tiers, Affaire, Remuneration, Article, TarifGe


if __name__ == "__main__":
    """
    salarie_list = session.query(Salarie).all()
    for salarie in salarie_list:
        print(salarie)
    """

    """
    adherent_list = session.query(Tiers).filter(Tiers.nature_auxiliaire == 'CLI')
    for adherent in adherent_list:
        print(adherent)
    """
    """
    affaire_list = session.query(Affaire).filter(Affaire.code_1 == 'MAD')
    for affaire in affaire_list:
        print("{} {}".format(affaire.salarie, affaire.adherent))
    """
    """
    rub_list = session.query(Remuneration).all()
    for rub in rub_list:
        print(rub)
    """
    """
    art_list = session.query(Article).all()
    for art in art_list:
        print("{} - {}".format(art, art.rubrique_paie))
    """
    tarif_list = session.query(TarifGe).all()
    for tarif in tarif_list:
        print(f"{tarif.code}")