# -*- coding: utf-8 -*- 
# $Id: konsprotokoll_tavaline.py 9 2015-06-30 06:34:46Z ahti $
"Konsultatsiooni läbiviimise protokoll"

from datetime import date
from eis.model import const

from .pdfutils import *
from .stylesheet import *

def generate(story, toimumisaeg, testikoht, items):

    testiosa = toimumisaeg.testiosa
    test = testiosa.test
    koht_nimi = testikoht.koht.nimi

    if test.testiliik_kood == const.TESTILIIK_TASE:
        buf = 'Eesti keele %s-taseme eksami konsultatsiooni läbiviimise protokoll' % (test.keeletase_nimi)
    elif test.testiliik_kood == const.TESTILIIK_SEADUS:
        buf = 'Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksami konsultatsiooni läbiviimise protokoll'
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
              Paragraph('Isikukood', M),
              Paragraph('Allkiri', M),
              ]

    data = [header]
    for n, r in enumerate(items):
        eesnimi, perenimi, isikukood, synnikpv = r
        row = [Paragraph(str(n+1), M),
               Paragraph(eesnimi, M),
               Paragraph(perenimi, M),
               Paragraph(isikukood or synnikpv.strftime('%d.%m.%Y'), M),
               Paragraph('', M),
               ]
        data.append(row)

    TS = TableStyle([('LINEBELOW',(0,0),(-1,0), 1, colors.black),
                     ('LINEBELOW',(0,1),(-1,-1), 0.5, colors.grey),
                     ('BOTTOMPADDING', (0,1), (-1,-1), 6),
                     ('TOPPADDING', (0,1), (-1,-1), 6),
                     ])

    data, col_widths, vaba = calc_table_width(data, max_width=190*mm, nice_width=160*mm)
    # kui jääb vaba ruumi
    if vaba > 0:
        d = 50*mm - col_widths[-1]
        if d > 0:
            d = min(vaba, d)
            vaba -= d
            col_widths[-1] += d

        col_widths[1] += vaba/2
        col_widths[2] += vaba/2

    story.append(Table(data, 
                       colWidths=col_widths,
                       repeatRows=1,
                       style=TS))

    story.append(Spacer(5*mm, 5*mm))
    story.append(Paragraph('Konsultatsioonil osales ____________ inimest.', M))
    story.append(Spacer(3*mm, 3*mm))
    story.append(Paragraph('Konsultatsiooni läbiviija %s' % ('_'*47), M))
    story.append(Paragraph('(nimi ja allkiri)', MC))
    story.append(PageBreak())
    
