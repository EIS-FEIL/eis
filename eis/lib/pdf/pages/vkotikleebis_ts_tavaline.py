# -*- coding: utf-8 -*- 
# $Id: vkotikleebis_ts_tavaline.py 9 2015-06-30 06:34:46Z ahti $
"Väljastamise turvakoti kleebis kuupäevadega (taseme- ja seaduse tundmise eksamid)"

from eis.model import const

from .pdfutils import *
from .stylesheet import *

def generate(story, toimumisaeg, testikoht, testipakett, turvakott, n):

    test = toimumisaeg.testimiskord.test   
    testiruum = testipakett.testiruum

    if testikoht.koht.piirkond:
        story.append(Paragraph('<b>%s</b>' % testikoht.koht.piirkond.get_nimi_ylematega(), NC))
    koht_nimi = testikoht.koht.nimi
    if testiruum and testiruum.ruum and testiruum.ruum.tahis:
        koht_nimi = '%s, ruum %s' % (koht_nimi, testiruum.ruum.tahis)
    story.append(Paragraph(koht_nimi, NC))

    tais_aadress = testikoht.koht.tais_aadress
    if tais_aadress:
        story.append(Paragraph(tais_aadress, NC))

    buf = test.nimi
    if testiruum.algus:
        buf += ' / %s' % testiruum.algus.strftime('%d.%m.%Y')
    story.append(Paragraph(buf, NC))

    for lv in testiruum.labiviijad:
        if lv.kasutajagrupp_id == const.GRUPP_INTERVJUU or \
               lv.kasutajagrupp_id == const.GRUPP_KOMISJON_ESIMEES:
            if lv.kasutaja:
                story.append(Paragraph('Läbiviija: %s' % lv.kasutaja.nimi, NC))

    # 1. nimekiri 1. grupp 19 töö(d)
    
    story.append(PageBreak())

