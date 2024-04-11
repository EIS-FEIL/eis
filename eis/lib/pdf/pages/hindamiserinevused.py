# -*- coding: utf-8 -*- 
"Hindamiserinevuste aruanne"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h

def generate(story, ta, hkogum, q, query_ylesandehinded, punktides):

    story.append(Paragraph(ta.testiosa.test.nimi, NBC))
    story.append(Paragraph(ta.tahised, NBC))
    story.append(Spacer(5*mm,5*mm))

    N = ParagraphStyle(name='Normal',
                       fontName='Times-Roman',
                       fontSize=10,
                       leading=12,
                       spaceBefore=1,
                       spaceAfter=1)
    NB = ParagraphStyle(name='NormalBold',
                        parent=N,
                        fontName='Times-Bold')

    header = [Paragraph('Jrk', NB),
              Paragraph('Protokolli tähis', NB),
              Paragraph('Testitöö tähis', NB),
              Paragraph('Vahe', NB),
              Paragraph('Hindamise jrk', NB),
              Paragraph('Hindaja', NB),
              ]
    for ty in hkogum.testiylesanded:
        title = ty.alatest_seq and '%s.%s' % (ty.alatest_seq, ty.seq) or '%s' % ty.seq
        header.append(Paragraph('Ül %s' % title, NB))
    header.append(Paragraph('Kokku', NB))
    
    colspan = len(hkogum.testiylesanded) + 7
    rowsize = 180*mm

    data = [header]
    for n, rcd in enumerate(q.all()):
        tk_tahis, pr_tahis, s_tahised, holek, h1_id, h1_pallid, h1_nimi, h2_id, h2_pallid, h2_nimi = rcd
        row = [Paragraph('%s' % (n+1), N),
               Paragraph('%s-%s' % (tk_tahis, pr_tahis), N),
               Paragraph(s_tahised, N),
               ]

        def hindaja_veerud(liik, h1_nimi, h1_id, h1_pallid):
            row = []
            row.append(Paragraph(liik, N))
            row.append(Paragraph(h1_nimi, N))
            d = query_ylesandehinded(h1_id)
            punktid = 0
            for ty in hkogum.testiylesanded:
                v = d.get(ty.id)
                if v:
                    punktid += v[0]
                    if punktides:
                        tulemus = h.fstr(v[0])
                    else:
                        tulemus = '%s (%s)' % (h.fstr(v[1]), h.fstr(v[0]))
                    row.append(Paragraph(tulemus, N))
                else:
                    row.append(Paragraph('', N))
            if punktides:
                tulemus = h.fstr(punktid)
            else:
                tulemus = '%s (%s)' % (h.fstr(h1_pallid), h.fstr(punktid))
            row.append(Paragraph(tulemus, N))
            return row, punktid

        h_row1, punktid1 = hindaja_veerud('1', h1_nimi, h1_id, h1_pallid)
        h_row2, punktid2 = hindaja_veerud('2', h2_nimi, h2_id, h2_pallid)

        if punktides:
            hindamiserinevus = h.fstr(abs(punktid2-punktid1))
        else:
            hindamiserinevus = holek.hindamiserinevus
        row.append(Paragraph(h.fstr(hindamiserinevus) or '', N))

        row.extend(h_row1)
        data.append(row)

        row = [Paragraph('',N)]*4
        row.extend(h_row2)
        data.append(row)


    colWidths = [0] * colspan
    for row in data:
        for n in range(colspan):
            w = row[n].minWidth() + 8
            if w > colWidths[n]:
                colWidths[n] = w

    s = sum(colWidths)
    if s < rowsize:
        lisada = (rowsize - s) / (colspan - 5)
        for n in range(5, colspan):
            colWidths[n] += lisada

    style = [('VALIGN', (0,0),(-1,-1), 'TOP'),
             ('LINEABOVE', (0,0),(-1,0), 0.5, colors.black),
             ('LINEBELOW', (0,-1),(-1,-1), 0.5, colors.black),                          
             ('LINEBEFORE', (0,0),(-1,-1), 0.5, colors.black),
             ('LINEAFTER', (-1,0),(-1,-1), 0.5, colors.black),
             ('LEFTPADDING', (0,0), (-1,-1), 3),
             ('RIGHTPADDING', (0,0), (-1,-1), 3),
             ]
    for n in range(int(len(data)/2)):
        n_row = n*2
        style.append(('LINEBELOW', (0,n_row),(-1,n_row), 0.5, colors.black))

    story.append(Table(data,
                       colWidths=colWidths,
                       style=TableStyle(style),
                       repeatRows=1
                       ))    
    story.append(Spacer(5*mm, 5*mm))

    story.append(PageBreak())

