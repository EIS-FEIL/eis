"Läbiviijate aruanded"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h

def generate(story, header, items, title):

    story.append(Paragraph(title, NBC))
    story.append(Spacer(10*mm,10*mm))

    data = []
    row = [Paragraph(s, SI) for s in header]
    data.append(row)    

    for item in items:
        row = [Paragraph(s, S) for s in item]
        data.append(row)

    TS = [('GRID',(0,0),(-1,-1), 0.5, colors.black),
          ('LINEABOVE', (0,0), (-1,0), 1, colors.black),
          ('LINEBELOW',(0,-1),(-1,0),1, colors.black),
          ('FONTNAME', (0,-1),(-1,0),'Times-Bold'),
          ]

    data, col_widths, vaba = calc_table_width(data, max_width=275*mm, nice_width=260*mm)
    # kui jääb vaba ruumi
    if vaba > 0:
        col_widths[1] += vaba/5 # eesnimi
        col_widths[2] += vaba/5 # perekonnanimi
        col_widths[3] += vaba/5 # testi nimi
        col_widths[5] += vaba/5 # koha nimi
        col_widths[6] += vaba/5 # testi nimi

    story.append(Table(data, 
                       colWidths=col_widths,
                       style=TS,
                       repeatRows=1))

