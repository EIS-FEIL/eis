# -*- coding: utf-8 -*- 
# $Id: vkotikleebis_r_kuupaevata.py 9 2015-06-30 06:34:46Z ahti $
"Väljastuse turvakoti kleebis ilma kuupäevata"

from .tkotikleebis_r_tavaline import gen_kleebis

def generate(story, toimumisaeg, testikoht, testipakett, turvakott, n):
    gen_kleebis(story, toimumisaeg, testikoht, testipakett, turvakott, False, n)
