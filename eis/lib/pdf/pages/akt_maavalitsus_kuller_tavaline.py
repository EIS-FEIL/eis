# -*- coding: utf-8 -*- 
# $Id: akt_maavalitsus_kuller_tavaline.py 9 2015-06-30 06:34:46Z ahti $
"Tagastuskottide maavalitsuselt kullerile üleandmise akt"

from . import akt

def generate(story, toimumisaeg, prk_nimi, items):
    return akt.generate(story, toimumisaeg, prk_nimi, items, akt.const.SUUND_TAGASI, True)
