"Sarnased valevastused (spikerdamise aruanne)"

from eis.lib.pdf.pages.pdfutils import *
from eis.lib.pdf.pages.stylesheet import *
import eis.lib.helpers as h

def generate(story, toimumisaeg, items, max_index, alatest_index):

    story.append(Paragraph('Sarnased vastused', H1))
    story.append(Paragraph('%s, %s' % (toimumisaeg.testiosa.test.nimi, toimumisaeg.tahised), NB))
    story.append(Spacer(3*mm, 3*mm))

    for (koht_nimi, ruum_tahis, li_sarnased) in items:
        buf = koht_nimi
        if ruum_tahis:
            buf += ', ruum %s' % ruum_tahis
        story.append(Paragraph(buf, N))
        
        # koostame tabeli päised
        row = [Paragraph('Isikukood', SI),
               Paragraph('Töökood', SI),
               ]
        row += [Paragraph('', SI)] * (max_index)
        row.extend([Paragraph('Tulemus', SI),
                    Paragraph('ÕV', SI),
                    Paragraph('H-H', SI),
                    Paragraph('SVV', SI),
                    Paragraph('MSV', SI),
                    ])
        data = [row]

        style = [('VALIGN', (0,0), (-1,-1), 'TOP'),]

        def row_j(ik, tahised, data):
            "Sooritaja andmete rida"
            row = [Paragraph(ik, S),
                   Paragraph(tahised, S),
                   ]
            for n in range(max_index):
                value = ''
                if n in alatest_index:
                    value = '*'
                elif n in data:
                    value = ' '.join(data.get(n))
                row.append(Paragraph(value or '', S))
            return row
        
        # koostame tabeli sisu
        for n_rcd, rcd in enumerate(li_sarnased):
            li1, li2, hh, svv, msv = rcd
            [ik1, tahised1, pallid1, data1, oige1] = li1
            [ik2, tahised2, pallid2, data2, oige2] = li2            

            row = row_j(ik1, tahised1, data1)
            row.extend([Paragraph(h.fstr(pallid1) or '', S),
                        Paragraph(str(oige1), S),
                        Paragraph(h.fstr(hh) or '', S),
                        Paragraph(str(svv), S),
                        Paragraph(str(msv), S),
                        ])
            data.append(row)

            row = row_j(ik2, tahised2, data2)
            row.extend([Paragraph(h.fstr(pallid2) or '', S),
                        Paragraph(str(oige2), S),
                        ])
            data.append(row)

            n = n_rcd * 2 + 1
            style.append(('LINEABOVE', (0,n),(-1,n), 0.5, colors.black))
            
        data, col_widths, vaba = calc_table_width(data, max_width=275*mm, min_extra=2)
        # kui lõpp ei mahu lehele, siis lõigatakse lõpust veerud maha
        # leiame tegelikult mahtunud vastuste arvu
        real_max_index = len(col_widths) - 7 

        # kui jääb vaba ruumi
        if vaba > 0:
            # mitte-vastuste laiustele paneme tavalise min_extra=10
            d = 10
            for n in list(range(2)) + list(range(2+max_index, len(col_widths))):
                if vaba <= d:
                    break
                col_widths[n] += d
                vaba -= d
            # vastuste laiustele paneme ka, kui mahub
            if vaba > 0:
                d = min(10, vaba / real_max_index)
                for n in range(2, 2+real_max_index):
                    col_widths[n] += d
                    vaba -= d
            # kui ikka midagi yle jääb
            if vaba > 0:
                vaba = min(vaba, 20*mm)
                col_widths[0] += vaba/2
                col_widths[1] += vaba/2

        # lahter, mis yhendatakse järgmistega -
        # kirjutame praegu peale laiuste arvutamist,
        # kuna laiuste arvutamine ei saa aru, et see yhendatakse järgmistega
        data[0][2] = Paragraph('Vastused', SI)

        style.append(('SPAN', (2,0),(2+real_max_index-1,0)))
        
        # joonistame tabeli
        tbl = Table(data,
                    colWidths=col_widths,
                    style=TableStyle(style),
                    hAlign='LEFT',
                    repeatRows=1)
        story.append(tbl)


    buf = """
Vastuste real punkt näitab õiget vastust
<br/>
Vastuste real täht näitab vale vastust
<br/>
ÕV - õiged vastused
<br/>
H-H näitab sarnaste valevastuste ja mittesarnaste valevastuste suhet
<br/>
SVV - sarnased valevastused
<br/>
MSV - mittesarnased valevastused
"""
    story.append(Paragraph(buf, N))
                 

    story.append(PageBreak())

