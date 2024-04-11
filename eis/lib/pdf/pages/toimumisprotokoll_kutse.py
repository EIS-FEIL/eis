"Kutseeksami toimumise protokoll"

from datetime import date
import re
from .pdfutils import *
from .stylesheet import *
import eis.model as model
from eis.model.usersession import _

def generate(story, testikoht1, toimumisprotokoll):
    testimiskord = toimumisprotokoll.testimiskord
    koht = toimumisprotokoll.koht
    testikoht = toimumisprotokoll.testikoht
    testiosa = testikoht.testiosa
    test = testiosa.test
    testikohad = list(toimumisprotokoll.testikohad)
    toimumisaeg = testikoht.toimumisaeg
    if toimumisaeg:
        story.append(Paragraph(_('Toimumisaja tähis') + ': <b>%s</b>' % toimumisaeg.tahised, NR))
    story.append(Spacer(5*mm, 5*mm))
    buf = _('Protokoll eksami toimumise kohta')
    story.append(Paragraph(buf, NBC))

    pais(story, toimumisprotokoll, test, testikohad, koht)
    story.append(Spacer(3*mm, 3*mm))

    story.append(labiviijad(toimumisprotokoll, testikohad))
    story.append(Spacer(2*mm, 2*mm))
    osalejad(story, toimumisprotokoll, testikohad)
    story.append(PageBreak())

def labiviijad(toimumisprotokoll, testikohad):
    if not toimumisprotokoll.testimiskord_id and toimumisprotokoll.testiruum_id:
        # nimekirjapõhine protokoll
        f_lv = model.sa.and_(
            model.Labiviija.testiruum_id==toimumisprotokoll.testiruum_id,
            model.Labiviija.kasutajagrupp_id==const.GRUPP_T_ADMIN)
    else:
        testikohad_id = [r.id for r in testikohad]
        f_lv = model.sa.and_(
            model.Labiviija.testikoht_id.in_(testikohad_id),
            model.Labiviija.kasutajagrupp_id==const.GRUPP_T_ADMIN)
    
    q = (model.SessionR.query(model.Kasutaja.nimi)
         .filter(model.Kasutaja.labiviijad.any(f_lv))
         .order_by(model.Kasutaja.nimi)
         )
    nimed = [nimi for nimi, in q.all()]
    if len(nimed) == 1:
        buf = _('Eksami läbiviija: ')
    else:
        buf = _('Eksami läbiviijad: ')
    buf += ', '.join(nimed)
    return Paragraph(buf, N)

def osalejad(story, toimumisprotokoll, testikohad):
    testikoht = toimumisprotokoll.testikoht
    testiosa = testikoht.testiosa
    test = testiosa.test
    #testimiskord = toimumisprotokoll.testimiskord
    toimumisaeg = testikoht.toimumisaeg
    
    # sooritajate loetelu tabel
    header = [Paragraph(_('Jrk nr'), NC),
              Paragraph(_('Isikukood'), NC),
              Paragraph(_('Ees- ja perekonnanimi'), NC),
              Paragraph(_('Punktide arv (max punktid)'), NC),
              Paragraph(_('Märkused'), NC),
              ]

    testiosad = test.testiosad
    mitu_testiosa = len(testiosad)
    if mitu_testiosa > 1:
        header_testiosa = [Paragraph(testiosa.tahis, NC) for testiosa in testiosad]
        header[2:2] = header_testiosa
    
    data = [header]
    nimi_width = 120

    q = (model.SessionR.query(model.Sooritaja,
                             model.Kasutaja.isikukood,
                             model.Sooritus.tahis,
                             model.Sooritus.markus)
         .join(model.Sooritaja.sooritused)
         .join(model.Sooritaja.kasutaja)
         .filter(model.Sooritaja.testimiskord_id==toimumisprotokoll.testimiskord_id)
         .filter(model.Sooritus.testikoht_id==toimumisprotokoll.testikoht_id)
         .filter(model.Sooritaja.staatus>const.S_STAATUS_REGAMATA)
         .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
         )
    if not toimumisaeg and toimumisprotokoll.testiruum_id:
        q = q.filter(model.Sooritus.testiruum_id==toimumisprotokoll.testiruum_id)
    
    if toimumisaeg:
        nimi_jrk = toimumisaeg.nimi_jrk
    else:
        nimi_jrk = True
    if nimi_jrk:
        q = q.order_by(model.Sooritaja.perenimi, model.Sooritaja.eesnimi)
    else:
        q = q.order_by(model.Sooritus.tahis)        

    n = 0
    table_style = [('GRID', (0,0), (-1,-1), 0.5, colors.black)]
    for sooritaja, ik, tahis, tos_markus in q.all():
        n += 1
        t = Paragraph('XX' + sooritaja.nimi.replace(' ','X'), N)
        nimi_width = max(nimi_width, t.minWidth())
        if sooritaja.staatus == const.S_STAATUS_TEHTUD:
            tulemus = '%s (%s)' % (model.fstr(sooritaja.pallid), model.fstr(sooritaja.max_pallid))
        elif sooritaja.staatus > const.S_STAATUS_POOLELI:
            tulemus = sooritaja.staatus_nimi
        else:
            tulemus = ''
        row = [Paragraph('%s' % n, N),
               Paragraph(ik or '', N),
               Paragraph(sooritaja.nimi, N),
               Paragraph(tulemus, N),
               Paragraph(sooritaja.markus or tos_markus or '', N),
               ]
        data.append(row)

    TS = TableStyle(table_style)
    data, col_widths, vaba, TS = calc_table_width(data, max_width=190*mm, nice_width=175*mm, style=TS)
    
    # kui jääb vaba ruumi
    if vaba > 0:
        # märkuste veeru laiuseks 52 mm
        d = min(vaba, 52*mm - col_widths[-1])
        col_widths[-1] += d
        vaba -= d

        # nime veerg nii, et nimed yhel real
        d = min(vaba, nimi_width - col_widths[2])
        col_widths[2] += d
        vaba -= d

        # muu jagamisele
        col_widths[3] += vaba/2
        col_widths[4] += vaba/2        
        
    story.append(Table(data, 
                       colWidths=col_widths,
                       style=TS))


def pais(story, toimumisprotokoll, test, testikohad, koht):
    kuupaev = toimumisprotokoll.millal or date.today().strftime('%d.%m.%Y')
    tahised = list()
    keeled = list()
    for testikoht in testikohad:
        tahis = testikoht.tahis
        if tahis and tahis not in tahised:
            tahised.append(tahis)
        q = (model.SessionR.query(model.Sooritaja.lang).distinct()
             .join(model.Sooritaja.sooritused)
             .filter(model.Sooritus.testikoht_id==testikoht.id))
        for lang, in q.all():
            if lang and lang not in keeled:
                keeled.append(lang)

    s_tahised = ', '.join(tahised)
    s_keeled = ', '.join([const.LANG_NIMI.get(lang) for lang in keeled]).capitalize()

    data = [[Paragraph('%s' % kuupaev, N),
             Paragraph('%s' % s_tahised, NR)],
            [Paragraph('(%s)' % _("kuupäev"), S),
             Paragraph('(%s)' % _("kooli kood"), SR)],
            [Paragraph('%s' % (test.nimi), N),
             Paragraph('%s' % koht.nimi, NR)],
            [Paragraph('(%s)' % _("eksam"), S),
             Paragraph('(%s)' % _("kooli nimi"), SR)],
            [Paragraph('%s' % s_keeled, N),
             Paragraph('',N)],
            [Paragraph('(%s)' % _("eksami sooritamise keel"), S),
             Paragraph('',S)],
            ]
    TS = [('ALIGN',(0,0),(0,-1), 'LEFT'),
          ('ALIGN',(1,0),(1,-1), 'RIGHT'),
          ('LEFTPADDING', (0,0),(-1,-1), 0),
          ]        
    for n in range(3):
        TS.append(('BOTTOMPADDING', (0, n*2), (-1,n*2), 0))
        TS.append(('TOPPADDING', (0, n*2+1), (-1, n*2+1), 0))
    
    story.append(Table(data, 
                       colWidths=(83*mm, 83*mm),
                       style=TS,
                       hAlign='LEFT')) 
