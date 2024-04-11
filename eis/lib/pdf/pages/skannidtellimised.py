# -*- coding: utf-8 -*- 
"Skannide tellimiste väljatrükk"

from eis.lib.pdf.pages.pdfutils import *
from eis.lib.pdf.pages.stylesheet import *
import eis.lib.helpers as h

def generate(story, header, items):
    story.append(Paragraph('Skannitud eksamitööd', H1))
    story.append(Spacer(3*mm, 3*mm))
    
    # koostame tabeli päised
    row = [Paragraph(isinstance(s, tuple) and s[1] or s, SI) for s in header]
    data = [row]
    
    # koostame tabeli sisu
    for item in items:
        row = []
        for s in item:
            if s is None:
                s = ''
            elif isinstance(s, list):
                s = '<br/>'.join(s)
            else:
                s = str(s)
            row.append(Paragraph(s, S))
        data.append(row)

    data, col_widths, vaba = calc_table_width(data, max_width=275*mm, min_extra=4)

    # kui jääb vaba ruumi
    if vaba > 0:
        col_widths[0] += vaba/3
        col_widths[6] += vaba/3
        col_widths[7] += vaba/3

    # joonistame tabeli
    ts = [('GRID', (0,0), (-1,-1), 0.5, colors.black),
          ('VALIGN', (0,0), (-1,-1), 'TOP'),
          ('LEFTPADDING', (0,0), (-1,-1), 2),
          ('RIGHTPADDING', (0,0), (-1,-1), 2),
          ]

    tbl = Table(data,
                colWidths=col_widths,
                style=TableStyle(ts),
                hAlign='LEFT',
                repeatRows=1)
    story.append(tbl)

    story.append(PageBreak())

