# -*- coding: utf-8 -*- 
# $Id: akt_ekk_kuller_tavaline.py 9 2015-06-30 06:34:46Z ahti $
"Väljastuskoti Haridus- ja Noorteametilt kullerile üleandmise akt"

from . import akt

def generate(story, toimumisaeg, prk_nimi, items):
    return akt.generate(story, toimumisaeg, prk_nimi, items, akt.const.SUUND_VALJA, True)
