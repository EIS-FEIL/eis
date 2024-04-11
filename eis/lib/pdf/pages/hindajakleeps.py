# -*- coding: utf-8 -*- 
# $Id: hindajakleeps.py 9 2015-06-30 06:34:46Z ahti $
"Tagastusümbriku hindajate kleebised"

from eis.model import const
from .pdfutils import *
from .stylesheet import *

def generate(story, toimumisaeg, hkogum, hindaja1, hindaja2):

    test = toimumisaeg.testimiskord.test

    story.append(Paragraph('%s %s' % (test.nimi, toimumisaeg.tahised), MCI))
    lang = hindaja1 and hindaja1.lang or hindaja2.lang
    story.append(Paragraph('Keel: %s' % const.LANG_NIMI.get(lang).lower(), MCI))
    if hindaja1:
        story.append(Paragraph('1. hindaja %s, kood %s' % (hindaja1.kasutaja.nimi, hindaja1.tahis), MCI))
    if hindaja2:
        story.append(Paragraph('2. hindaja %s, kood %s' % (hindaja2.kasutaja.nimi, hindaja2.tahis), MCI))        
    story.append(Paragraph(hkogum.nimi, MCI))
    story.append(PageBreak())
