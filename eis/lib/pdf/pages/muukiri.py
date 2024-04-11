# -*- coding: utf-8 -*- 
"Muu kiri"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h

def generate(story, kasutaja, taiendavinfo):

    story.append(Paragraph('Haridus- ja Noorteamet', NBC))
    story.append(Paragraph('Lõõtsa 4, 11415 Tallinn, tel 7350 500', NBC))
    story.append(Spacer(3*mm,3*mm))
    story.append(Paragraph('TEADE', NC))

    #aadress: vahemikus 4-6 cm ülalt, vähemalt 2 cm vasakust äärest
    li = [kasutaja.nimi] 
    if kasutaja.aadress:
        li.extend(kasutaja.aadress.li_print_aadress(kasutaja))
    aadress = '<br/>'.join(li)

    story.append(Table([[Paragraph(aadress, N), 
                         Paragraph(h.str_from_date(date.today()), N)]],
                       colWidths=(130*mm,30*mm),
                       style=TableStyle([('VALIGN', (0,0),(-1,-1), 'TOP'),
                                         ]) 
                       ))    

    story.append(Spacer(5*mm, 5*mm))

    story.append(Paragraph('Lp %s' % kasutaja.nimi, N))
    story.append(Spacer(5*mm,5*mm))

    story.append(Paragraph(taiendavinfo, N))        
    
    story.append(Spacer(5*mm,5*mm))
    story.append(Paragraph('Haridus- ja Noorteamet', N))
    story.append(Paragraph('Lõõtsa 4, 11415 Tallinn', N))
    story.append(Paragraph('Tel: 7350 500', N))
    story.append(Paragraph('https://www.harno.ee', N))

    story.append(PageBreak())
