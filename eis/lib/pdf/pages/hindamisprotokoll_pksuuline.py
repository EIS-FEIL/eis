"Suulise osa hindamisprotokoll põhikoolile"

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
    
    generate_pais(story, test, testikoht, lang, tpr, hpr, skogum, hkogum, komplekt)
    generate_hkogum(story, toimumisaeg, testiosa, tpr, skogum, hkogum, komplekt, hpr.liik)
    generate_hindajad(story, toimumisaeg, testiosa, hkogum, hpr.liik)    

    story.append(PageBreak())

def generate_pais(story, test, testikoht, lang, tpr, hpr, skogum, hkogum, komplekt):
    
    story.append(Paragraph(testikoht.koht.nimi, NR))
    story.append(Paragraph(_('Hindamisprotokoll'), LC))
    if hkogum:
        story.append(Paragraph('<u>%s</u>' % hkogum.nimi, NC))
        if hkogum.erinevad_komplektid:
            story.append(Paragraph('<u>%s %s</u>' % (_("Ülesandekomplekt"), komplekt.tahis), NC))

    data = [[[Paragraph('<u>%s</u>' % test.nimi, NB),
              Paragraph('(%s)' % _("eksam"), S)],
             [Paragraph('<u>%s</u>' % tpr.testiruum.algus.strftime('%d.%m.%Y'), NBR),
              Paragraph('(%s)' % _("kuupäev"), SR)]],
            ]
    if lang:
        lang_nimi = const.LANG_NIMI.get(lang)
        data.append([[Paragraph('<u>%s</u>' % lang_nimi, NB),
                      Paragraph('(%s)' % _("eksami sooritamise keel"), S)],
                     ''])

    story.append(Table(data, colWidths=(125*mm, 30*mm)))

def generate_hkogum(story, toimumisaeg, testiosa, tpr, skogum, hkogum, komplekt, liik):
    "Ühele hindamiskogumile vastava tabeli koostamine"

    header1 = [] # päise esimene rida
    col = 0

    testiliik = testiosa.test.testiliik_kood
    
    # päise moodustamine

    # suulise osa korral on ees nime veerg
    header1.append(Paragraph(_('Nimi'), NC))
    col += 1

    header1.append(Paragraph(_('Isikukood'), NC))
    col += 1

    is_komplektid = len(toimumisaeg.komplektid) > 1
    if is_komplektid:
        header1.append(Paragraph(_('Teema'), NC))
        col += 1

    kogum_aspektid = {}
    for ty in hkogum.testiylesanded: 
        vy = ty.get_valitudylesanne(komplekt)
        ylesanne = vy.ylesanne
        y_aspektid = [ha for ha in ylesanne.hindamisaspektid if ha.aspekt]
        kogum_aspektid[ty.id] = y_aspektid
        
        for n, a in enumerate(y_aspektid):
            t = Paragraph('%s<br/>%sp' % \
                          (a.aspekt.nimi, h.fstr(a.max_pallid)), 
                          NC)
            header1.append(t)
            col += 1

        header1.append(Paragraph(_('Punkte kokku'), NC))
        col += 1

    data = [header1]

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

        # mõõdame igaks juhuks, kui palju võtaks ruumi nimi ühel real
        t = Paragraph(sooritaja.nimi.replace(' ','_'), N)
        nimi_width = max(nimi_width, t.minWidth())

        # tegelikult võib nimi olla kahel real
        t = Paragraph(sooritaja.nimi or '', N)
        row.append(t)

        k = sooritaja.kasutaja
        t = Paragraph(k.isikukood or h.str_from_date(k.synnikpv), N)
        row.append(t)

        if is_komplektid:
            if hkogum.erinevad_komplektid:
                s = komplekt.tahis
            else:
                s = ''
            t = Paragraph(s, N)
            row.append(t)

        for ty in hkogum.testiylesanded:
            ty_aspektid = kogum_aspektid.get(ty.id)
            for rcd in range(len(ty_aspektid)):
                row.append('')
            row.append('')
            
        data.append(row)

    TS = [('GRID',(0,0),(-1,-1), 1, colors.black),
          ('LEFTPADDING', (0,0), (-1,-1), 2),
          ('RIGHTPADDING', (0,0), (-1,-1), 2),
          ]
    
    # lisame veergudele pisut laiust
    data, col_widths, vaba, TS = calc_table_width(data, max_width=190*mm, nice_width=170*mm, style=TS, min_extra=5)

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
        col_cnt = len(col_widths) - col1 - 1
        d = vaba / col_cnt
        for n in range(col1, len(col_widths)):
            if n != 1: # isikukoodi välja laiemaks ei tee
                col_widths[n] += vaba/col_cnt 

    story.append(Table(data, style=TS, colWidths=col_widths, repeatRows=1))

def generate_hindajad(story, toimumisaeg, testiosa, hkogum, liik):

    story.append(Spacer(100*mm,5*mm))
    TS = TableStyle([('ALIGN', (0,0),(0,-1), 'RIGHT'),
                     ])
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
