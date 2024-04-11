"Läbiviimisprotokoll"

from datetime import date
import eis.model as model
from eis.model.usersession import _
from .pdfutils import *
from .stylesheet import *

def generate(story, toimumisaeg, testikoht, testipakett, tpr):
    testiosa = toimumisaeg.testiosa
    test = testiosa.test

    story.append(Paragraph(_('Protokolli kood') + ': <font size="12"><b>%s</b></font>' % tpr.tahised, NR))
    story.append(Spacer(100*mm, 3*mm))

    pealdis(story, toimumisaeg, testikoht, testipakett, tpr)
    story.append(Spacer(100*mm, 3*mm))
    
    # sooritajate loetelu tabel
    header = [Paragraph(_('Nr'), NC),
              Paragraph(_('Nimi'), NC),
              Paragraph(_('Isikukood'), NC),
              Paragraph(_('Testitöö kood'), NC),
              Paragraph(_('Osales'), NC),
              Paragraph(_('Märkused / Puudumise põhjus'), NC),
              ]

    data = [header]
    nimi_width = 0
    n = 0
    q = (model.SessionR.query(model.Sooritus)
         .filter(model.Sooritus.testiprotokoll_id==tpr.id)
         .join(model.Sooritus.sooritaja)
         .filter(model.Sooritaja.staatus>const.S_STAATUS_REGAMATA)
         .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD))
    if toimumisaeg.nimi_jrk:
        q = q.order_by(model.Sooritaja.perenimi, model.Sooritaja.eesnimi)
    else:
        q = q.order_by(model.Sooritus.tahis)
    for tos in q.all():
        n += 1

        sooritaja = tos.sooritaja
        kasutaja = tos.sooritaja.kasutaja

        t = Paragraph('%s_%s' % (sooritaja.eesnimi, sooritaja.perenimi), N)
        nimi_width = max(nimi_width, t.minWidth())
        
        row = [Paragraph(str(n), N),
               Paragraph(sooritaja.nimi, N),
               Paragraph(kasutaja.isikukood or kasutaja.synnikpv.strftime('%d.%m.%Y'), N),
               Paragraph('%s %s' % (testikoht.tahis, tos.tahis), N),
               Paragraph('', N),
               Paragraph('', N),
               ]
        data.append(row)

    TS = TableStyle([('GRID',(0,0),(-1,-1), 0.5, colors.black),
                     ('LEFTPADDING',(0,0),(-1,-1), 3),
                     ('RIGHTPADDING',(0,0),(-1,-1), 3),
                     ])
    data, col_widths, vaba, TS = calc_table_width(data, max_width=190*mm, nice_width=175*mm, style=TS)

    # kui jääb vaba ruumi
    if vaba > 0:
        # testitöö koodi veeru laius
        d = min(vaba, 18*mm - col_widths[3])
        col_widths[3] += d
        vaba -= d

        # märkuste veeru laiuseks 52 mm
        d = min(vaba, 52*mm - col_widths[-1])
        col_widths[-1] += d
        vaba -= d

        # ylejäänu nime veerule
        col_widths[1] += vaba

    story.append(Table(data, 
                       colWidths=col_widths,
                       style=TS))

    story.append(Spacer(100*mm, 5*mm))

    story.append(Paragraph('%s: %s' % (_("Kooli esindaja või testi läbiviija nimi ja allkiri"), '.'*107), DOT))
    
    story.append(PageBreak())

def pealdis(story, toimumisaeg, testikoht, testipakett, tpr):
    testiosa = toimumisaeg.testiosa
    test = testiosa.test
    koht = testikoht.koht
    
    story.append(Paragraph(test.nimi, LBC))
    story.append(Paragraph(_('läbiviimise protokoll'), LBC))
    story.append(Spacer(100*mm, 2*mm))

    story.append(Paragraph(koht.nimi, LC))

    kpv = tpr.testiruum.algus
    if testipakett and testipakett.lang:
        lang_nimi = testipakett.lang_nimi.capitalize()
        keel = Paragraph('<b>%s</b><br/>(%s)' % (lang_nimi, _("testi sooritamise keel")), N)
    else:
        keel = Paragraph('', N)
    data = [[keel,
             Paragraph('<b>%s</b><br/>(%s)' % (kpv.strftime('%d.%m.%Y'), _("kuupäev")), NR),
             ]]

    story.append(Table(data, colWidths=(85*mm, 85*mm), hAlign='LEFT'))
