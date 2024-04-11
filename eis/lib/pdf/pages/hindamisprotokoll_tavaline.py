"Hindamisprotokoll"

import logging
import eis.model as model
from eis.model import const
from eis.model.usersession import _
import eis.lib.helpers as h
from .pdfutils import *
from .stylesheet import *

log = logging.getLogger(__name__)

def generate(story, toimumisaeg, testikoht, lang, tpr, hpr, skogum, hkogum, komplekt):
    testiosa = toimumisaeg.testiosa
    test = testiosa.test
    testiliik = test.testiliik_kood
    
    if testiliik == const.TESTILIIK_TASE:
        generate_pais_te(story, testiosa, testikoht, lang, tpr, hpr, skogum, hkogum, komplekt)
    else:
        generate_pais_r(story, test, testikoht, lang, tpr, hpr, skogum, hkogum, komplekt)

    generate_hkogum(story, toimumisaeg, testiosa, tpr, skogum, hkogum, komplekt, hpr.liik)

    if testiliik == const.TESTILIIK_TASE:
        generate_hindajad_te(story, toimumisaeg, testiosa, hkogum, hpr.liik)
    else:
        generate_hindajad_r(story, toimumisaeg, testiosa, hkogum, hpr.liik)    

    story.append(PageBreak())

def generate_pais_te(story, testiosa, testikoht, lang, tpr, hpr, skogum, hkogum, komplekt):

    testiruum = tpr.testiruum
    koht = testikoht.koht
            
    data = [['',
             Paragraph(_('Eesti keele {s}-taseme eksam').format(s=testiosa.test.keeletase_nimi), LBC),
             Paragraph(_('protokoll') + ': %s' % hpr.testiprotokoll.tahised, MBR)],
            ['',
             Paragraph(testiosa.nimi, LC),
             ''],
            ]
    if hkogum:
        data.append(['', Paragraph(hkogum.nimi, NC), ''])
        if hkogum.erinevad_komplektid:
            data.append(['', Paragraph('%s %s' % (_("Ülesandekomplekt"), komplekt.tahis), NC), ''])

    story.append(Table(data, colWidths=(34*mm, 70*mm, 60*mm)))

    data = [[Paragraph(h.str_from_datetime(testiruum.algus), MI),
             Paragraph(_('Koht') + ': %s' % (koht.nimi), MI),
             ]]
    story.append(Table(data, colWidths=(55*mm, 100*mm)))
    story.append(Spacer(3*mm,3*mm))

def generate_pais_r(story, test, testikoht, lang, tpr, hpr, skogum, hkogum, komplekt):
    lang_nimi = lang and const.LANG_NIMI.get(lang) or ''
    
    story.append(Paragraph(_('Protokolli kood') + ': <font size="14"><b>%s</b></font>' % hpr.testiprotokoll.tahised, NR))
    story.append(Paragraph(_('Sisestuskogum') + ': <b>%s</b>' % skogum.tahis, NR))
    story.append(Paragraph(_('Hindamisprotokoll'), LC))
    if hkogum:
        story.append(Paragraph('<u>%s</u>' % hkogum.nimi, NC))
        if hkogum.erinevad_komplektid:
            if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM and test.aine_kood == const.AINE_ET:
                story.append(Paragraph('<u>%s %s</u>' % (_("Variant"), komplekt.tahis), NC))
            else:
                story.append(Paragraph('<u>%s %s</u>' % (_("Ülesandekomplekt"), komplekt.tahis), NC))

    data = [[[Paragraph('<u>%s</u>' % test.nimi, NB),
              Paragraph('(%s)' % _("eksam"), S)],
             [Paragraph('<u>%s</u>' % tpr.testiruum.algus.strftime('%d.%m.%Y'), NBR),
              Paragraph('(%s)' % _("kuupäev"), SR)]],
            [[Paragraph('<u>%s</u>' % lang_nimi, NB),
              Paragraph('(%s)' % _("eksami sooritamise keel"), S)],
             ''],
            ]
    story.append(Table(data, colWidths=(125*mm, 30*mm)))

def generate_hkogum(story, toimumisaeg, testiosa, tpr, skogum, hkogum, komplekt, liik):
    "Ühele hindamiskogumile vastava tabeli koostamine"

    header1 = [] # päise esimene rida
    header2 = [] # päise teine rida
    is_header2 = False
    header2_style = [] # kui on teine rida, siis selle mõju tabeli stiilile
    col = 0

    test = testiosa.test
    testiliik = test.testiliik_kood
    
    # päise moodustamine
    if testiosa.vastvorm_kood == const.VASTVORM_SP:
        # suulise osa korral on ees nime veerg
        header1.append(Paragraph(_('Nimi'), NC))
        header2.append('')
        header2_style.append(('SPAN', (col,0),(col,1))) # esimesel ja teisel real on yhine lahter
        col += 1

        if testiliik == const.TESTILIIK_TASE:
            # suulisel tasemeeksamil on isikukood ka
            header1.append(Paragraph(_('Isikukood'), NC))
            header2.append('')

    header1.append(Paragraph(_('Eksamitöö kood'), NC))
    header2.append('')
    header2_style.append(('SPAN', (col,0),(col,1))) # esimesel ja teisel real on yhine lahter
    col += 1

    is_komplektid = len(toimumisaeg.komplektid) > 1
    if is_komplektid:
        if testiliik == const.TESTILIIK_RIIGIEKSAM and test.aine_kood == const.AINE_ET:
            t = Paragraph(_('Variant'), NC)
        else:
            t = Paragraph(_('Komplekt'), NC)
        header1.append(t)
        header2.append('')
        header2_style.append(('SPAN', (col,0),(col,1))) # esimesel ja teisel real on yhine lahter
        col += 1

    kogum_aspektid = {}
    for ty in hkogum.testiylesanded: 
        vy = ty.get_valitudylesanne(komplekt)
        ylesanne = vy.ylesanne
        y_aspektid = [ha for ha in ylesanne.hindamisaspektid if ha.aspekt]
        kogum_aspektid[ty.id] = y_aspektid
        
        t = Paragraph('%s %s<br/>max %sp' % \
                          (_("Ülesanne"), ty.seq, h.fstr(ylesanne.max_pallid)), NC)
        header1.append(t)        

        if len(y_aspektid) == 0:
            header2.append('')
            header2_style.append(('SPAN', (col,0),(col,1))) # yks lahter yle kahe rea
            col += 1
        else:
            is_header2 = True
            col1 = col # selle ylesande esimese aspekti veerg
            for n, a in enumerate(y_aspektid):
                if n > 0:
                    header1.append('')
                t = Paragraph('%s<br/>%sp' % \
                                  (a.aspekt.nimi, h.fstr(a.max_pallid)), 
                              NC)
                header2.append(t)
                col += 1
            header2_style.append(('SPAN', (col1,0), (col-1,0))) # yks ylesande nimega lahter yle kõigi aspektide

    if testiosa.vastvorm_kood == const.VASTVORM_SP:
        # suulise testi korral ei ole ülesandeid, on ainult aspektid
        header = [header2[n] or header1[n] for n in range(len(header1))]
        data = [header]
        is_header2 = False
    else:
        # kirjaliku testi korral on esimeses päisereas ülesanded
        data = [header1]
        if is_header2:
            # kui mõnel ülesandel on aspekte, siis on teine päiserida aspektide nimedega
            data.append(header2)

    # tabeli sisu moodustamine
    # leiame protokollil olevad sooritajad
    q = (model.SessionR.query(model.Sooritus, model.Sooritaja)
         .join(model.Sooritus.sooritaja)
         .filter(model.Sooritus.testiprotokoll_id==tpr.id)
         .filter(model.Sooritaja.staatus>const.S_STAATUS_REGAMATA)
         .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)        
         )
    if liik == const.HINDAJA3:
        # kolmanda hindamise protokollile ei kanta neid sooritajaid,
        # kellele pole kolmandat hindamist vaja teha
        q = q.join(model.Sooritus.hindamisolekud).\
            filter(model.Hindamisolek.hindamiskogum_id==hkogum.id).\
            filter(model.Hindamisolek.hindamised.any(model.Hindamine.liik==liik))
        
    if toimumisaeg.nimi_jrk:
        q = q.order_by(model.Sooritaja.perenimi, model.Sooritaja.eesnimi)
    else:
        q = q.order_by(model.Sooritus.tahis)        

    nimi_width = 0
    for rcd in q.all():
        tos, sooritaja = rcd
        row = []
        if testiosa.vastvorm_kood == const.VASTVORM_SP:
            # mõõdame igaks juhuks, kui palju võtaks ruumi nimi ühel real
            t = Paragraph(sooritaja.nimi.replace(' ','_'), N)
            nimi_width = max(nimi_width, t.minWidth())

            # tegelikult võib nimi olla kahel real
            t = Paragraph(sooritaja.nimi or '', N)
            row.append(t)

            if testiliik == const.TESTILIIK_TASE:
                k = sooritaja.kasutaja
                t = Paragraph(k.isikukood or h.str_from_date(k.synnikpv), N)
                row.append(t)

        row.append(Paragraph(tos.tahised or '', N))

        if is_komplektid:
            if hkogum.erinevad_komplektid:
                s = komplekt.tahis
            else:
                s = ''
            t = Paragraph(s, N)
            row.append(t)

        for ty in hkogum.testiylesanded:
            ty_aspektid = kogum_aspektid.get(ty.id)
            for rcd in range(len(ty_aspektid) or 1):
                row.append('')
                
        data.append(row)

    TS = [('GRID',(0,0),(-1,-1), 1, colors.black),
          ('LEFTPADDING', (0,0), (-1,-1), 2),
          ('RIGHTPADDING', (0,0), (-1,-1), 2),          
          ]
    if is_header2:
        TS.extend(header2_style)
    
    # lisame veergudele pisut laiust
    data, col_widths, vaba, TS = calc_table_width(data, max_width=190*mm, nice_width=150*mm, style=TS, min_extra=5)

    # kui jääb vaba ruumi
    if vaba > 0:
        if nimi_width > 0:
            nimi_width += 10
            d = min(nimi_width - col_widths[0], vaba)
            col_widths[0] += d
            vaba -= d
            col1 = 1
        else:
            col1 = 0
        col_cnt = len(col_widths) - col1
        d = vaba / col_cnt
        for n in range(col1, len(col_widths)):
            col_widths[n] += vaba/col_cnt

    story.append(Table(data, style=TS, colWidths=col_widths, repeatRows=is_header2 and 2 or 1))


def generate_hindajad_te(story, toimumisaeg, testiosa, hkogum, liik):

    if liik == const.HINDAJA1:
        liik_nimi = _('esimene hindamine')
    elif liik == const.HINDAJA2:
        liik_nimi = _('teine hindamine')
    elif liik == const.HINDAJA3:
        liik_nimi = _('kolmas hindamine')
    else:
        liik_nimi = str(liik)

    TS = TableStyle([('VALIGN', (0,0),(0,0), 'BOTTOM'),
                     ('VALIGN', (-1,-1),(-1,-1), 'MIDDLE'),
                     ('GRID', (-1,-1),(-1,-1), 0.5, colors.black),
                     ])
    data = [[Paragraph(_('Hindamine'), N)],
            [Paragraph(liik_nimi, DOT)],
            ]
    t_liik = Table(data, style=TS, colWidths=(20*mm), rowHeights=(4*mm,15*mm), hAlign='RIGHT')

    if testiosa.vastvorm_kood == const.VASTVORM_KP:
        # kirjaliku töö korral on üks hindaja, aga võib olla kahekordne hindamine
        story.append(Spacer(100*mm,5*mm))
        data = [[Paragraph(_('Hindaja:'), NR), Paragraph('.'*47, DOT)],
                [Paragraph(_('Allkiri:'), NR), Paragraph('.'*47, DOT)],
                ]
        story.append(Table(data, colWidths=(120*mm, 55*mm), rowHeights=(6*mm,9*mm)))          
    else:
        # suulisel tööl mitu hindajat ja võib-olla ka intervjueerija
        story.append(Spacer(100*mm,5*mm))
        TS = TableStyle([('ALIGN', (0,0),(0,-1), 'RIGHT'),
                         ])

        data1 = [[Paragraph(_('Intervjueerija:'), NR), Paragraph('.'*47, DOT)],
                 [Paragraph(_('Allkiri:'), NR), Paragraph('.'*47, DOT)],
                 ]
        table1 = Table(data1, style=TS, colWidths=(25*mm, 47*mm), rowHeights=(6*mm, 9*mm), hAlign='LEFT')

        data2 = [[Paragraph(_('Hindaja:'), NR), Paragraph('.'*47, DOT)],
                 [Paragraph(_('Allkiri:'), NR), Paragraph('.'*47, DOT)],
                 ]
        table2 = Table(data2, style=TS, colWidths=(20*mm, 47*mm), rowHeights=(6*mm, 9*mm), hAlign='LEFT')

        data = [[table1, table2]]
        story.append(Table(data, colWidths=(90*mm, 90*mm), hAlign='LEFT'))

    TS = TableStyle([('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
                     ])
    data = [[Paragraph('', N),
             Paragraph(_('Hindaja kood:'), NR),
             Table([['','','']], colWidths=(7*mm,7*mm,7*mm), rowHeights=(10*mm,),
                   style=TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.black),])),
             t_liik,
             ]]
    story.append(Table(data, style=TS, colWidths=(40*mm, 30*mm, 30*mm, 30*mm), hAlign='RIGHT'))

def generate_hindajad_r(story, toimumisaeg, testiosa, hkogum, liik):

    if liik == const.HINDAJA1:
        liik_nimi = _('esimene hindamine')
    elif liik == const.HINDAJA2:
        liik_nimi = _('teine hindamine')
    elif liik == const.HINDAJA3:
        liik_nimi = _('kolmas hindamine')
    else:
        liik_nimi = str(liik)

    TS = TableStyle([('VALIGN', (0,0),(0,0), 'BOTTOM'),
                     ('VALIGN', (-1,-1),(-1,-1), 'MIDDLE'),
                     ('GRID', (-1,-1),(-1,-1), 0.5, colors.black),
                     ])
    data = [[Paragraph(_('Hindamine'), N)],
            [Paragraph(liik_nimi, DOT)],
            ]
    t_liik = Table(data, style=TS, colWidths=(23*mm), rowHeights=(4*mm,15*mm), hAlign='RIGHT')

    if testiosa.vastvorm_kood == const.VASTVORM_KP:
        # kirjaliku töö korral on üks hindaja, aga võib olla kahekordne hindamine
        story.append(Spacer(100*mm,5*mm))
        data = [[Paragraph(_('Hindaja:'), NR), Paragraph('......................................', DOT)],
                [Paragraph(_('Allkiri:'), NR), Paragraph('......................................', DOT)],
                ]
        story.append(Table(data, colWidths=(18*mm, 50*mm)))

        test = testiosa.test
        if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM and test.aine_kood == const.AINE_ET:
            hindajakood = Paragraph('__ __ __', DOT)
        else:
            hindajakood = Paragraph('__ __', DOT)
        if liik == const.HINDAJA3:
            TS = TableStyle([('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
                             ])
            data = [[Paragraph(_('Hindaja kood:'), NR),
                     hindajakood,
                     t_liik],
                    ]
            story.append(Table(data, style=TS, colWidths=(30*mm, 20*mm, 30*mm), hAlign='RIGHT'))

        elif hkogum.kahekordne_hindamine or hkogum.kahekordne_hindamine_valim:
            TS = TableStyle([('VALIGN', (0,0),(-1,-1), 'BOTTOM'),
                             ('GRID', (-1,-1),(-1,-1), 0.5, colors.black),
                             ])

            data = [[Paragraph('', N),
                     Paragraph('', N),
                     Paragraph(_('Hindamine'), N)],
                    [Paragraph(_('Hindaja kood:'), NR),
                     hindajakood,
                     Paragraph('__ %s<br/>__ %s' % (_("esimene"), _("teine")), DOT)],
                    ]
            story.append(Table(data, style=TS, colWidths=(30*mm, 20*mm, 23*mm), hAlign='RIGHT'))
        else:
            data = [[Paragraph(_('Hindaja kood:'), NR),
                     hindajakood]
                    ]
            story.append(Table(data, colWidths=(30*mm, 20*mm), hAlign='RIGHT'))

        if testiosa.test.on_tseis:
            # lisaks hindajale kirjutab kirjalikus osas alla ka komisjoni esimees
            story.append(Spacer(5*mm,5*mm))
            data = [[Paragraph(_('Komisoni esimees:'), NR), Paragraph('................................', DOT)],
                    [Paragraph(_('Allkiri:'), NR),          Paragraph('................................', DOT)],
                    ]
            story.append(Table(data, colWidths=(32*mm, 37*mm)))
            
    else:
        # suulisel tööl mitu hindajat ja võib-olla ka intervjueerija
        story.append(Spacer(100*mm,5*mm))
        TS = TableStyle([('ALIGN', (0,0),(0,-1), 'RIGHT'),
                         ('LINEBELOW',(0,-1),(-1,-1),0.5, colors.black)])
        data1 = [[Paragraph(_('Hindaja:'), NR), Paragraph('......................................', DOT)],
                 [Paragraph(_('Eksamitöö koodid*:'), NR), Paragraph('......................................', DOT)],
                 [Paragraph(_('Allkiri:'), NR), Paragraph('......................................', DOT)],
                 ]
        table1 = Table(data1, style=TS, colWidths=(36*mm, 39*mm), hAlign='LEFT')

        if toimumisaeg.intervjueerija_maaraja:
            data2 = [[Paragraph(_('Intervjueerija:'), NR), Paragraph('......................................', DOT)],
                     [Paragraph(_('Eksamitöö koodid*:'), NR), Paragraph('......................................', DOT)],
                     [Paragraph(_('Allkiri:'), NR), Paragraph('......................................', DOT)],
                     ]
            table2 = Table(data2, style=TS, colWidths=(36*mm, 39*mm), hAlign='LEFT')
        else:
            table2 = ''

        data = []
        for n in range(3):
            row = [table1, table2]
            data.append(row)

        story.append(Table(data))

        if liik == const.HINDAJA3:
            story.append(Table([[t_liik]], colWidths=(33*mm,), hAlign='RIGHT'))
            
        elif hkogum.kahekordne_hindamine or hkogum.kahekordne_hindamine_valim:
            TS = TableStyle([('VALIGN', (0,0),(-1,-1), 'BOTTOM'),
                             ('GRID', (-1,-1),(-1,-1), 0.5, colors.black),
                             ])

            data = [[Paragraph(_('Hindamine'), N)],
                    [Paragraph('__ %s<br/>__ %s' % (_("(kooli)hindaja"), _("välishindaja")), DOT)],
                    ]
            story.append(Table(data, style=TS, colWidths=(32*mm), hAlign='RIGHT'))

        
        story.append(Paragraph(_('* Eksamitöö koodid kirjutada välja juhul, kui hindajaid ja intervjueerijaid on rohkem kui üks'), S))

