# -*- coding: utf-8 -*- 
# $Id: vkotikleebis_r_tavaline.py 9 2015-06-30 06:34:46Z ahti $
"Väljastuse turvakoti kleebis kuupäevadega"

from .tkotikleebis_r_tavaline import gen_kleebis

def generate(story, toimumisaeg, testikoht, testipakett, turvakott, n):
    gen_kleebis(story, toimumisaeg, testikoht, testipakett, turvakott, True, n)
