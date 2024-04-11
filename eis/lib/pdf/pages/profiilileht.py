# -*- coding: utf-8 -*- 
"Õpipädevuse testi soorituse profiilileht"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h

def generate(story, handler, sooritus, header, items):
    sooritaja = sooritus.sooritaja
    lang = sooritaja.lang
    #lang = const.LANG_RU
    test = sooritaja.test
    kasutaja = sooritaja.kasutaja
    #aastad, kuud = kasutaja.get_vanus(sooritaja.algus)
    testija = sooritaja.esitaja_kasutaja and sooritaja.esitaja_kasutaja.nimi or ''
    
    story.append(Paragraph(test.tran(lang).nimi or '', NC))

    koolinimi = sooritaja.koolinimi
    ajakulu = sum([s.ajakulu or 0 for s in sooritaja.sooritused]) / 60
    if lang == const.LANG_RU:
        row1 = [Paragraph('Имя ученика', NB),
                Paragraph('%s %s' % (sooritaja.eesnimi, sooritaja.perenimi), NB)]
        row2 = [Paragraph('Школа', NB),
                Paragraph(koolinimi and koolinimi.nimi or '', NB),
                Paragraph('Класс', NB),
                Paragraph('%s%s' % (sooritaja.klass or '', sooritaja.paralleel or ''), NB)]
        row3 = [Paragraph('Дата тестирования', NB),
                Paragraph(sooritaja.millal, NB),
                Paragraph('Время, затраченное на выполнение теста', NB),
                Paragraph('%d мин.' % ajakulu, NB)]
    else:
        row1 = [Paragraph('Õpilase nimi', NB),
                Paragraph('%s %s' % (sooritaja.eesnimi, sooritaja.perenimi), NB)]
        row2 = [Paragraph('Kool', NB),
                Paragraph(koolinimi and koolinimi.nimi or '', NB),
                Paragraph('Klass', NB),
                Paragraph('%s%s' % (sooritaja.klass or '', sooritaja.paralleel or ''), NB)]
        row3 = [Paragraph('Testi tegemise kuupäev', NB),
                Paragraph(sooritaja.millal, NB),
                Paragraph('Testi tegemisele kulunud aeg', NB),
                Paragraph('%d min' % ajakulu, NB)]
        

    TS = [('VALIGN', (0,0), (-1,-1), 'TOP'),
          ('GRID', (0,0), (-1,-1), 0.5, colors.black),
          ]
    data1, col_widths, vaba = calc_table_width([row1], max_width=134*mm, min_extra=5*mm,
                                               nice_widths=(25*mm, None))
    if vaba:
        col_widths[1] += vaba
    tbl1 = Table(data1, colWidths=col_widths, style=TS, hAlign='LEFT', spaceBefore=0, spaceAfter=0)

    data2, col_widths, vaba = calc_table_width([row2], max_width=93*mm, min_extra=5*mm)
    if vaba:
        col_widths[1] += vaba
    tbl2 = Table(data2, colWidths=col_widths, style=TS, hAlign='LEFT')

    data3, col_widths, vaba = calc_table_width([row3], max_width=93*mm, min_extra=5*mm)
    if vaba:
        col_widths[0] += vaba/2
        col_widths[2] += vaba/2

    tbl3 = Table(data3, colWidths=col_widths, style=TS, hAlign='LEFT')
    tbl4 = [tbl2, tbl3]

    if lang == const.LANG_RU:
        data = [[tbl1,
                 Paragraph('', N),
                 Paragraph('', N),
                 Paragraph('Группа', NC),
                 Paragraph('', N),
                 Paragraph('', N)],
                [tbl4,
                 Paragraph('Тест мин.-макс.', NC),
                 Paragraph('Резуль-<br/>тат', NC),
                 Paragraph('Низ-<br/>кий резуль-<br/>тат', NC),
                 Paragraph('Сред-<br/>ний резуль-<br/>тат', NC),
                 Paragraph('Высо-<br/>кий резуль-<br/>тат', NC)]
                ]
    else:
        data = [[tbl1,
                 Paragraph('', N),
                 Paragraph('', N),
                 Paragraph('Sooritusrühm', NC),
                 Paragraph('', N),
                 Paragraph('', N)],
                [tbl4,
                 Paragraph('Testi min-max', NC),
                 Paragraph('Tulemus', NC),
                 Paragraph('Madal', NC),
                 Paragraph('Kesk-<br/>mine', NC),
                 Paragraph('Kõrge', NC)]
                ]

    header_cnt = len(data)
    grouprows = []
    gridrows = [0,1]
    g_colors = ('#d5e5f2', '#88aecf', '#479ce6') # madal, keskmine, kõrge
    ts_colors = []
    NBGrupp = ParagraphStyle(name='NormalBoldG',
                             parent=NB,
                             #textColor='#479ce6')
                             textColor='#2a6ea8')
    
    for n_item, item in enumerate(items):
        if len(item) == 1:
            # alatestide grupi nimetus
            grouprows.append(n_item+header_cnt)
            gridrows.append(n_item+header_cnt)            
        elif len(item) == 6:
            # sooritusrühm on antud
            gridrows.append(n_item+header_cnt)
        #row = [Paragraph(value, N) for value in item]
        if len(item) == 1:
            row = [Paragraph(item[0], NBGrupp)]
            for x in range(1, 6):
                row.append(Paragraph('', N))                
        else:
            row = []
            # sooritusryhma veerud + normipunkt
            normipunkt = item.pop()
            pooratud_varv = normipunkt.pooratud_varv
            varv2_mk = normipunkt.varv2_mk
            on_sooritusryhm = False
            n_row = n_item + header_cnt
            for n_cell, value in enumerate(item):
                if n_cell in (3,4,5):
                    # sooritusryhma veerud
                    if value:
                        on_sooritusryhm = True
                        pos = (n_cell, n_row)
                        if n_cell == 4 or item[4]:
                            color = g_colors[1] # kui vähemalt üks sooritusrühmadest on keskmine, siis vaikimisi kasutame keskmist värvi 
                            if varv2_mk and (n_cell == 5 or item[5]):
                                color = g_colors[not pooratud_varv and 2 or 0]
                            elif varv2_mk and (n_cell == 3 or item[3]):
                                color = g_colors[pooratud_varv and 2 or 0]                                
                        elif n_cell == 3:
                            color = g_colors[pooratud_varv and 2 or 0] # ainult madal sooritusrühm
                        elif n_cell == 5:
                            color = g_colors[not pooratud_varv and 2 or 0] # ainult kõrge sooritusrühm
                        ts_colors.append(('BACKGROUND', pos, pos, color))
                    row.append(Paragraph('', NC))
                else:
                    row.append(Paragraph(value, n_cell==0 and N or NC))
            if on_sooritusryhm:
                ts_colors.append(('GRID', (3, n_row), (5, n_row), 0.5, colors.black))

        data.append(row)

    # värvide legend
    if lang == const.LANG_RU:
        rowf = [Paragraph('Значение результата:', NC),
                Paragraph('', NC),
                Paragraph('Может нуждаться в помощи', N),
                Paragraph('', NC),
                Paragraph('Средний', N),
                Paragraph('', NC),
                Paragraph('Выше среднего', N)]
    else:
        rowf = [Paragraph('Tulemuse tähendus:', NC),
                Paragraph('', NC),
                Paragraph('Võib vajada abi', N),
                Paragraph('', NC),
                Paragraph('Keskmine', N),
                Paragraph('', NC),
                Paragraph('Üle keskmise', N)]
    TS.extend([('BACKGROUND', (1,0), (1,0), g_colors[0]),
               ('BACKGROUND', (3,0), (3,0), g_colors[1]),
               ('BACKGROUND', (5,0), (5,0), g_colors[2])])
    col_widths = (36*mm,18*mm,31*mm,18*mm,31*mm,18*mm,30*mm)        
    #col_widths = (36*mm,18*mm,30*mm,18*mm,30*mm,18*mm,30*mm)        
    tblf = Table([rowf], colWidths=col_widths, style=TS, hAlign='LEFT', spaceBefore=0, spaceAfter=0)
    p = Paragraph('', N)
    data.append([tblf, p, p, p, p, p])
    ts_legend = [('SPAN', (0,-1), (-1,-1)),
                 ('LEFTPADDING',(0,-1),(-1,-1), 0),
                 ('RIGHTPADDING',(0,-1),(-1,-1), 0),          
                 ('TOPPADDING',(0,-1),(-1,-1), 0),
                 ('BOTTOMPADDING',(0,-1),(-1,-1), 0),
                 ('LEADING', (0,-1),(-1,-1), 0),
                 ]

    # suure tabeli stiil
    TS = [('VALIGN', (0,0), (-1,-1), 'TOP'),
          ('GRID', (0,0), (2,-1), 0.5, colors.black),
          ('SPAN', (0,0), (2,0)), # nimi
          # nimi
          ('LEFTPADDING',(0,0),(2,0), 0),
          ('RIGHTPADDING',(0,0),(2,0), 0),          
          ('TOPPADDING',(0,0),(2,0), 0),
          ('BOTTOMPADDING',(0,0),(2,0), 0),
          ('LEADING', (0,0),(2,0), 0),

          ('SPAN', (3,0), (5,0)), # sooritusrühm

          # kool
          ('LEFTPADDING',(0,1),(0,1), 0),
          ('RIGHTPADDING',(0,1),(0,1), 0),          
          ('TOPPADDING',(0,1),(0,1), 0),
          ('BOTTOMPADDING',(0,1),(0,1), 0),
          ('LEADING', (0,1),(0,1), 0),
          ] + ts_colors + ts_legend
    for n_row in gridrows:
        TS.append(('GRID', (3, n_row), (5, n_row), .5, colors.black))

    for group_begin in reversed(grouprows):
        # grupi nimi üle kõigi lahtrite
        TS.append(('SPAN', (0, group_begin), (-1, group_begin)))
    col_widths = (93*mm, 21*mm, 20*mm, 16*mm, 16*mm, 16*mm)
    #col_widths = (93*mm, 21*mm, 21*mm, 15*mm, 15*mm, 15*mm)

    table = Table(data, colWidths=col_widths, style=TS, repeatRows=2, hAlign='LEFT')
    story.append(table)

