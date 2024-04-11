"Suulise hindamise protokoll hindajate ja intervjueerijate veeruga"

import logging
import eis.model as model
from eis.model import const
from eis.model.usersession import _
import eis.lib.helpers as h
from .pdfutils import *
from .stylesheet import *

from .hindamisprotokoll_tavaline import generate_pais_te, generate_pais_r

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
    generate_hindajad_r(story, toimumisaeg, testiosa, hkogum, hpr.liik)    

    story.append(PageBreak())

def generate_hkogum(story, toimumisaeg, testiosa, tpr, skogum, hkogum, komplekt, liik):
    "Ühele hindamiskogumile vastava tabeli koostamine"

    header1 = [] # päise esimene rida
    header2 = [] # päise teine rida
    is_header2 = False
    header2_style = [] # kui on teine rida, siis selle mõju tabeli stiilile
    col = 0

    testiliik = testiosa.test.testiliik_kood
    
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

    header1.append(Paragraph(_('Eksaminandi kood'), NC))
    header2.append('')
    header2_style.append(('SPAN', (col,0),(col,1))) # esimesel ja teisel real on yhine lahter
    col += 1

    is_komplektid = len(toimumisaeg.komplektid) > 1
    if is_komplektid:
        header1.append(Paragraph(_('Teema tähis'), NC))
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

    header1.append(Paragraph('H*', NC))
    header1.append(Paragraph('I*', NC))
    header2.append('')
    header2.append('')
    header2_style.append(('SPAN', (-1,0),(-1,1))) # esimesel ja teisel real on yhine lahter
    header2_style.append(('SPAN', (-2,0),(-2,1))) # esimesel ja teisel real on yhine lahter

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
                
        row.append('')
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
    log.info(col_widths)
    # rohkem ruumi H ja I veergudele
    min_hi = 35
    lisadaH = max(0, min_hi - col_widths[-2])
    lisadaI = max(0, min_hi - col_widths[-1])
    if vaba >= lisadaH + lisadaI:
        vaba -= lisadaH + lisadaI
    else:
        sum_width = sum(col_widths)
        vaba += max(0, 190*mm - sum_width)
        lisadaH = min(lisadaH, vaba/2)
        lisadaI = min(lisadaI, vaba/2)
        vaba = 0
    col_widths[-2] += lisadaH
    col_widths[-1] += lisadaI
        
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


def generate_hindajad_r(story, toimumisaeg, testiosa, hkogum, liik):

    story.append(Spacer(100*mm,5*mm))
    TS = TableStyle([('ALIGN', (0,0),(0,-1), 'RIGHT'),
                     ('LINEBELOW',(0,-1),(-1,-1),0.5, colors.black)])
    data1 = [[Paragraph(_('Hindaja:'), NR), Paragraph('.......................................', DOT)],
             [Paragraph(_('Allkiri:'), NR), Paragraph('.......................................', DOT)],
             ]
    table1 = Table(data1, style=TS, colWidths=(35*mm, 40*mm), hAlign='LEFT')

    data2 = [[Paragraph(_('Intervjueerija:'), NR), Paragraph('.......................................', DOT)],
             [Paragraph(_('Allkiri:'), NR), Paragraph('.......................................', DOT)],
             ]
    table2 = Table(data2, style=TS, colWidths=(35*mm, 40*mm), hAlign='LEFT')

    data = [[table1, table2]]
    story.append(Table(data))

    story.append(Paragraph(_('* Veergu H kirjutada hindaja kood (selle puudumisel loetavalt hindaja initsiaalid).<br/>Veergu I kirjutada intervjueerija kood (selle puudumisel loetavalt intervjueerija initsiaalid).'), S)) 

    story.append(Spacer(100*mm,5*mm))
    if hkogum.kahekordne_hindamine or hkogum.kahekordne_hindamine_valim:
        data = [[Paragraph('_____ ' + _("KOOLIHINDAJA"), NB)],
                [Paragraph('_____ ' + _("VÄLISHINDAJA"), NB)]]
        TS = TableStyle([('VALIGN', (0,0),(-1,-1), 'BOTTOM'),
                         ('BOX', (0,0), (-1,-1), .5, colors.black)])
        col_widths = (45*mm,)
        story.append(Table(data, style=TS, colWidths=col_widths, hAlign='RIGHT'))
