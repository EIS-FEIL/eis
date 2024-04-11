# -*- coding: utf-8 -*- 
# $Id: vaidelist.py 781 2016-06-29 06:42:00Z ahti $
"Vaiete loetelu väljatrükk"

from eis.lib.pdf.pages.pdfutils import *
from eis.lib.pdf.pages.stylesheet import *
import eis.lib.helpers as h

def generate(story, header, items):
    # from eis.lib.pdf.pdfdoc import *
    # fn_path = '/srv/eis/etc/'
    # pdfmetrics.registerFont(TTFont('Times-Roman', fn_path + 'times.ttf'))
    # pdfmetrics.registerFont(TTFont('Times-Bold', fn_path + 'timesbd.ttf'))
    # pdfmetrics.registerFont(TTFont('Times-Italic', fn_path + 'timesi.ttf'))
    # addMapping('Times-Roman', 0, 0, 'Times-Roman') #normal
    # addMapping('Times-Roman', 0, 1, 'Times-Italic') #italic
    # addMapping('Times-Roman', 1, 0, 'Times-Bold') #bold
    # story.append(Paragraph('õÕ proov', N))
    # story.append(Paragraph('<b>õÕ proov</b>', N))
    # story.append(Paragraph('õÕ proov', NB))
    # buf = u"Маршрут: из Мемфиса в Новый Орлеан"
    # story.append(Paragraph(buf, N))
    # story.append(Paragraph('<b>%s</b>' % buf, N))
    # story.append(Paragraph(buf, NB))

    story.append(Paragraph('Vaided', H1))
    story.append(Spacer(3*mm, 3*mm))

    try:
        # proovime, kas kõik veerud, sh ettepaneku veerg, mahuvad laiusesse ära
        tbl = _gen_table(header, items, True)
    except:
        # kui ei mahu, siis kuvame ettepaneku alati eraldi real
        tbl = _gen_table(header, items, False)

    story.append(tbl)
    story.append(PageBreak())
        
def _gen_table(header, items, col_ettepanek):
    # koostame tabeli päised
    headerrow = [Paragraph(isinstance(s, tuple) and s[1] or s, SI) for s in header]
    hdr_ettepanek = headerrow[-1]
    if not col_ettepanek:
        # ettepanek pole eraldi veerus
        headerrow = headerrow[:-1]
    data = [headerrow]

    MAX_CELLSIZE = 600
    MAX_LINES = 50
    textrows = []
    rowind = 0
    # koostame tabeli sisu
    for item in items:
        row = []

        ettepanek = item[-1]
        if not col_ettepanek:
            # kui ettepaneku veerg ei mahu yldse laiuses ära, siis kuvatakse see eraldi real
            item = item[:-1]
        elif len(ettepanek) > MAX_CELLSIZE or ettepanek.count('<br/>') > MAX_LINES:
            # kui viimases veerus olev ettepanek on liiga pikk, et mahtuda leheküljele,
            # siis kuvatakse see eraldi real, ettepaneku veerus olev lahter jääb tühjaks
            item[-1] = ''
        else:
            # ettepanek kuvatakse oma veerus
            ettepanek = ''

        for s in item:
            if s is None:
                s = ''
            elif isinstance(s, list):
                s = '<br/>'.join(s)
            else:
                s = str(s)
            row.append(Paragraph(s, S))
        rowind += 1
        data.append(row)
        if ettepanek:
            # eraldi rida pika ettepaneku jaoks
            row = [hdr_ettepanek, Paragraph(ettepanek,S)]
            rowind += 1
            data.append(row)
            textrows.append(rowind)

    data, col_widths, vaba = calc_table_width(data, max_width=275*mm, min_extra=4,
                                              raise_table_too_wide=col_ettepanek)

    # kui jääb vaba ruumi
    if vaba > 0:
        if len(col_widths) > 13:
            col_widths[13] += vaba/3
            vaba -= vaba/3
        if len(col_widths) > 12:
            col_widths[12] += vaba/2
            vaba -= vaba/2
        col_widths[0] += vaba


    # joonistame tabeli
    ts = [('GRID', (0,0), (-1,-1), 0.5, colors.black),
          ('VALIGN', (0,0), (-1,-1), 'TOP'),
          ('LEFTPADDING', (0,0), (-1,-1), 2),
          ('RIGHTPADDING', (0,0), (-1,-1), 2),
          ]
    for rowind in textrows:
        ts.append(('SPAN', (1, rowind), (-1, rowind)))

    tbl = Table(data,
                colWidths=col_widths,
                style=TableStyle(ts),
                hAlign='LEFT',
                repeatRows=1)
    return tbl

