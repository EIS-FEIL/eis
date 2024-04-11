# -*- coding: utf-8 -*- 
# $Id: soorituskohad.py 9 2015-06-30 06:34:46Z ahti $
"Soorituskohtade päring"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h

def generate(story, items, keeled, sooritajad, vaatlejad, ruumid):

    story.append(Paragraph('Soorituskohad', NBC))
    story.append(Spacer(5*mm,5*mm))
    
    header = ['']
    colWidths = [0]
    langsize = 17*mm
    if ruumid:
        header.append(Paragraph('Kuupäev', N))
        header.append(Paragraph('Ruumide arv', N))
        colWidths += [20*mm, 24*mm]
    if sooritajad:
        for lang in keeled:
            header.append(Paragraph(const.LANG_NIMI.get(lang), N))
        header.append(Paragraph('Kokku', N))
        colWidths += [langsize] * (len(keeled) + 1)
    if vaatlejad:
        header.append(Paragraph('Vaatlejaid', N))
        colWidths += [langsize]
        
    colspan = len(header)
    colWidths[0] = 180*mm - sum(colWidths)

    for ta_data in items:
        ta_nimi = ta_data[0]
        story.append(Paragraph(ta_nimi, NB))

        data = [header]

        for prk_data in ta_data[1:-1]:
            prk_nimi = prk_data[0]
            data.append([Paragraph(prk_nimi, NB)])
            for k_data in prk_data[1:-1]:
                # soorituskoha rida
                row = [Paragraph(' &nbsp; %s' % k_data[0], N)]
                if ruumid:
                    row.append(Paragraph(h.str_from_date(k_data[1]), N))
                    row.append(Paragraph(str(k_data[2]), N))
                if sooritajad:
                    for lang in keeled:
                        row.append(Paragraph(str(k_data[3].get(lang) or 0), N))
                    row.append(Paragraph(str(k_data[4]), N))
                if vaatlejad:
                    row.append(Paragraph(str(k_data[5]), N))
                data.append(row)

                if k_data[6]:
                    # suunatud koolid
                    for s_data in k_data[6]:
                        row = [Paragraph(s_data[0], SR)]
                        if ruumid:
                            row.append(Paragraph('', S))
                            row.append(Paragraph('', S))                            
                        for lang in keeled:
                            row.append(Paragraph(str(s_data[1].get(lang) or 0), S))
                        row.append(Paragraph(str(s_data[2]), S))
                        data.append(row)

            # soorituspiirkond kokku
            if sooritajad:
                k_data = prk_data[-1]
                row = [Paragraph('Soorituspiirkonnas kokku', NB)]
                if ruumid:
                    row.append(Paragraph('', S))
                    row.append(Paragraph('', S))
                for lang in keeled:
                    row.append(Paragraph(str(k_data[1].get(lang) or 0), NB))
                row.append(Paragraph(str(k_data[2]), NB))
                if vaatlejad:
                    row.append(Paragraph(str(k_data[3]), NB))
                data.append(row)

        # toimumisaeg kokku
        if sooritajad:
            k_data = ta_data[-1]
            row = [Paragraph('Toimumisajal kokku', NB)]
            if ruumid:
                row.append(Paragraph('', S))
                row.append(Paragraph('', S))
            for lang in keeled:
                row.append(Paragraph(str(k_data[1].get(lang) or 0), NB))
            row.append(Paragraph(str(k_data[2]), NB))
            if vaatlejad:
                row.append(Paragraph(str(k_data[3]), NB))
            data.append(row)

        TS = TableStyle([('VALIGN', (0,0),(-1,-1), 'TOP'),
                         ('GRID', (0,0),(-1,-1), 0.5, colors.black),
                         ('BACKGROUND', (0,0),(-1,0), colors.lightgrey),
                         ])
        if colWidths[0] < 10:
            data, col_widths, vaba, TS = \
                  calc_table_width(data, max_width=190*mm, nice_width=150*mm, style=TS)
            col_widths[0] += vaba
        story.append(Table(data,
                           colWidths=colWidths,
                           style=TS,
                           repeatRows=1
                           ))    
        story.append(Spacer(5*mm, 5*mm))

    story.append(PageBreak())

