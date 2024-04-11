# -*- coding: utf-8 -*- 
# $Id: konsnimekiri_tavaline.py 9 2015-06-30 06:34:46Z ahti $
"Konsultatsioonil osalejate nimekiri"

from datetime import date
from eis.model import const

from .pdfutils import *
from .stylesheet import *

def generate(story, toimumisaeg, testikoht, items):

    testiosa = toimumisaeg.testiosa
    test = testiosa.test
    koht_nimi = testikoht.koht.nimi

    if test.testiliik_kood == const.TESTILIIK_TASE:
        buf = 'Eesti keele %s-taseme eksami konsultatsiooni nimekiri' % (test.keeletase_nimi)
    elif test.testiliik_kood == const.TESTILIIK_SEADUS:
        buf = 'Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksami konsultatsiooni nimekiri'
    else:
        buf = 'Konsultatsiooni nimekiri'
    story.append(Paragraph(buf, LBC))

    alates = testikoht.alates
    data = [[Paragraph(alates and alates.strftime('%d.%m.%Y %H.%M') or '', LB),
             Paragraph(testikoht.koht.nimi, LBR)]]
    story.append(Table(data, colWidths=(50*mm,113*mm)))

    story.append(Spacer(4*mm, 4*mm))

    # sooritajate loetelu tabel
    header = [Paragraph('Nr', M),
              Paragraph('Eesnimi', M),
              Paragraph('Perekonnanimi', M),
              ]

    data = [header]
    for n, r in enumerate(items):
        eesnimi, perenimi, isikukood, synnikpv = r
        row = [Paragraph(str(n+1), M),
               Paragraph(eesnimi, M),
               Paragraph(perenimi, M),
               ]
        data.append(row)

    TS = TableStyle([('LINEBELOW',(0,0),(-1,0), 1, colors.black),
                     ('LINEBELOW',(0,1),(-1,-1), 0.5, colors.grey)])

    data, col_widths, vaba = calc_table_width(data, max_width=190*mm, nice_width=160*mm)
    # kui jääb vaba ruumi
    if vaba > 0:
        col_widths[1] += vaba/2
        col_widths[2] += vaba/2

    story.append(Table(data, 
                       colWidths=col_widths,
                       repeatRows=1,
                       style=TS))

    story.append(PageBreak())
    
