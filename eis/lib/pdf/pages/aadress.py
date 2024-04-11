# -*- coding: utf-8 -*- 
"Abifunktsioonid - aadressikasti genereerimine"

from .pdfutils import *
from .stylesheet import *
import eis.lib.helpers as h
from datetime import date

def aadressikast(kasutaja, on_kpv=True, font=N, on_lp=True):
    """Saaja aadressi printimine kirja ülaossa"""
    # aadress: vahemikus 4-6 cm ülalt, vähemalt 2 cm vasakust äärest
    if on_lp:
        li = ['Lp %s' % kasutaja.nimi]
    else:
        li = [kasutaja.nimi]
    if kasutaja.aadress:
        li.extend(kasutaja.aadress.li_print_aadress(kasutaja))
    aadress = '<br/>'.join(li)

    return Table([[Paragraph(aadress, font), 
                   Paragraph(on_kpv and h.str_from_date(date.today()) or '', font)]],
                 colWidths=(130*mm, 30*mm),
                 style=TableStyle([('VALIGN', (0,0),(-1,-1), 'TOP'),
                                   ('LEFTPADDING', (0,0), (-1,-1), 0),
                                   ]),
                 hAlign='LEFT',
                 )

