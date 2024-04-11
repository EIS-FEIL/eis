# -*- coding: utf-8 -*- 
# $Id: mootmisvead.py 428 2016-03-10 07:58:59Z ahti $
"Mõõtmisvea piiresse jäävate tulemuste loetelu"

from eis.lib.pdf.pages.pdfutils import *
from eis.lib.pdf.pages.stylesheet import *
import eis.lib.helpers as h
import eis.model.usersession as usersession

def generate(story, header, items, testimiskord, staatus_jrk):

    story.append(Paragraph('Mõõtmisvea piiridesse jäävad tulemused - %s' % testimiskord.tahised, H1))
    story.append(Spacer(3*mm, 3*mm))
    
    # koostame tabeli päised
    row = [Paragraph(s[1], SI) for s in header]
    data = [row]
    style = []
    
    # koostame tabeli sisu
    for n_row, item in enumerate(items):
        row = []
        n = 1

        while n < len(item):
            r = item[n]
            n += 1
            if n not in staatus_jrk:
                # tulemuse väli, mida tuleb kuvada
                if r is None:
                    r = ''
                elif isinstance(r, float):
                    # pallid, kuvame koos järgmisel väljal olevate protsentidega
                    r = '%sp (%s%%)' % (h.fstr(r), h.fstr(item[n]))
                    n += 1
                else:
                    r = str(r)
                row.append(Paragraph(r, S))

            elif r != const.S_STAATUS_TEHTUD:
                # oleku väli ja olek ei ole tehtud -
                # järgnevate tulemuste väljade asemel tuleb kuvada olek
                ignore = staatus_jrk[n] 
                colspan = (ignore - len([k for k in range(n+1, n+ignore+1) if k in staatus_jrk]))/2
                n_cell = len(row)
                style.append(('SPAN', (n_cell,n_row+1),(n_cell+colspan-1,n_row+1)))
                
                n += ignore                
                s = usersession.get_opt().S_STAATUS.get(r)
                row.append(Paragraph(s, S))
                # lisame ignoreeritavad väljad (mis ühendatakse oleku väljaga)
                for i in range(colspan-1):
                    row.append(Paragraph('',S))

        data.append(row)

    data, col_widths, vaba, style = calc_table_width(data, max_width=275*mm, style=style)

    # kui jääb vaba ruumi
    if vaba > 0:
        cnt = len(col_widths)
        for n in range(cnt):
            col_widths[n] += vaba/cnt

    # joonistame tabeli
    style += [('GRID', (0,0), (-1,-1), 0.5, colors.black),
              ('VALIGN', (0,0), (-1,-1), 'TOP'),
              ]

    tbl = Table(data,
                colWidths=col_widths,
                style=TableStyle(style),
                hAlign='LEFT',
                repeatRows=1)
    story.append(tbl)

    story.append(PageBreak())

