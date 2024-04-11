# -*- coding: utf-8 -*- 
# $Id: testikohamarkused.py 9 2015-06-30 06:34:46Z ahti $
"Testikohtade märkuste ülevaade korraldajale"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h

def generate(story, ta, items):

    story.append(Paragraph('Toimumisaja %s märkuste ülevaade' % ta.tahised, NBC))
    story.append(Spacer(10*mm,10*mm))

    for k_nimi, markus in items:
        story.append(Paragraph(k_nimi, NB))
        story.append(Paragraph(markus, N))
        story.append(Spacer(3*mm, 3*mm))
