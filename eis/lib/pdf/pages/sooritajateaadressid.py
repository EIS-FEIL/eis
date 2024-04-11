# -*- coding: utf-8 -*- 
"Sooritajate aadressid"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h

def generate(story, ta, items):

    testimiskord = ta.testimiskord
    story.append(Paragraph(testimiskord.test.nimi, NBC))
    story.append(Paragraph('Testimiskorra %s sooritajate aadressid soovitud piirkondade kaupa' % testimiskord.tahised, NBC))
    data = prev_p_nimi = None
    for rcd in items:
       p_nimi, k_ik, k_synnikpv, eesnimi, perenimi, tais_aadress, normimata, koht_nimi, markus, sk_nimi, s_tahised = rcd
       if not p_nimi:
           p_nimi = 'Piirkonnata'

       if prev_p_nimi != p_nimi:
           if data:
               story.append(_tbl(data))
           story.append(Paragraph(p_nimi, NB))
           header = [Paragraph('Isikukood',NB),
                     Paragraph('Nimi', NB),
                     Paragraph('Aadress', NB),
                     Paragraph('Õppeasutus', NB),
                     Paragraph('Märkused', NB),
                    ]
           data = [header]
           prev_p_nimi = p_nimi
           
       row = [Paragraph(k_ik or h.str_from_date(k_synnikpv), S),
              Paragraph('%s %s' % (eesnimi, perenimi), S),
              Paragraph('%s %s' % (tais_aadress or '', normimata or ''), S),
              Paragraph(koht_nimi or '', S),
              Paragraph(markus or '', S),
              ]
       data.append(row)
   
    if data:
        story.append(_tbl(data))

def _tbl(data):
    TS = [('GRID',(0,0),(-1,-1), 0.5, colors.black),
          ('LINEABOVE', (0,0), (-1,0), 1, colors.black),
          ('LINEBELOW',(0,-1),(-1,0),1, colors.black),
          ('FONTNAME', (0,-1),(-1,0),'Times-Bold'),
          ]
    data, col_widths, vaba = calc_table_width(data, max_width=275*mm, nice_width=260*mm)
    # kui jääb vaba ruumi
    if vaba > 0:
        def setwidth(col_widths, n, w, vaba):
            f = w - col_widths[n]
            if f > 0:
                d = min(f, vaba)
                vaba -= d
                col_widths[n] += d
            return vaba
        vaba = setwidth(col_widths, 1, 120, vaba)
        vaba = setwidth(col_widths, 2, 240, vaba)        
        vaba = setwidth(col_widths, 3, 150, vaba)
        col_widths[2] += vaba*.5
        col_widths[4] += vaba*.5 
        
    return Table(data, 
                 colWidths=col_widths,
                 style=TS,
                 repeatRows=1)

