# -*- coding: utf-8 -*- 
# $Id: tkotikleebis_ts_tavaline.py 9 2015-06-30 06:34:46Z ahti $
"Tagastamise turvakoti kleebis kuupäevadega (taseme- ja seaduse tundmise eksamid)"

from eis.model import const

from .pdfutils import *
from .stylesheet import *

def generate(story, toimumisaeg, testikoht, testipakett, turvakott, n):

    test = toimumisaeg.testimiskord.test   
    testiruum = testipakett.testiruum
    
    story.append(Paragraph('<b>Haridus- ja Noorteamet</b>', NC))
    story.append(Paragraph('<b>Lõõtsa 4, 11414 Tallinn</b>', NC))

    buf = test.nimi
    if testiruum.algus:
        buf += ' / %s' % testiruum.algus.strftime('%d.%m.%Y')
    story.append(Paragraph(buf, NC))

    if testikoht.koht.piirkond:
        story.append(Paragraph(testikoht.koht.piirkond.get_nimi_ylematega(), NC))

    koht_nimi = testikoht.koht.nimi
    if testiruum.ruum and testiruum.ruum.tahis:
        koht_nimi += ', ruum %s' % testiruum.ruum.tahis
    story.append(Paragraph('<b>%s</b>' % koht_nimi, NC))

    for lv in testiruum.labiviijad:
        if lv.kasutajagrupp_id == const.GRUPP_INTERVJUU or \
               lv.kasutajagrupp_id == const.GRUPP_KOMISJON_ESIMEES:
            if lv.kasutaja:
                story.append(Paragraph('Läbiviija: %s' % lv.kasutaja.nimi, NC))

    # 1. nimekiri 1. grupp 19 töö(d)
    
    story.append(Paragraph('........ tööd ...................................', NC))
    story.append(Paragraph('                              allkiri            ', NC))

    story.append(PageBreak())

