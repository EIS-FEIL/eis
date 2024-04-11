"Üleandmisprotokoll kahe vihikuga"

from datetime import date

from .pdfutils import *
from .stylesheet import *
import eis.model as model
from eis.model.usersession import _
from .yleandmisprotokoll_tavaline import pealdis, allkirjad

def generate(story, toimumisaeg, testikoht, testipakett, tpr):
    testiosa = toimumisaeg.testiosa
    test = testiosa.test

    story.append(Paragraph(_('Protokolli kood') + ': <font size="12"><b>%s</b></font>' % tpr.tahised, NR))
    story.append(Spacer(100*mm, 6*mm))

    pealdis(story, toimumisaeg, testikoht, testipakett, tpr, True)
    
    # sooritajate loetelu tabel
    header = [Paragraph(_('Nr'), NC),
              Paragraph(_('Nimi'), NC),
              Paragraph(_('Isikukood'), NC),
              Paragraph(_('Eksamitöö kood'), NC),
              ]
    if test.on_tseis:
        header.append(Paragraph(_('Esitatud dok.nr'), NC))
        header.append(Paragraph(_('I vihik allkiri'), NC))
        header.append(Paragraph(_('II vihik allkiri'), NC))
    else:
        header.append(Paragraph(_('I vihik'), NC))
        header.append(Paragraph(_('II vihik'), NC))    

    data = [header]
    nimi_width = 50*mm
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

        kasutaja = tos.sooritaja.kasutaja
        sooritaja = tos.sooritaja
        
        t = Paragraph('%s_%s' % (sooritaja.eesnimi, sooritaja.perenimi), N)
        nimi_width = max(nimi_width, t.minWidth())

        row = [Paragraph(str(n), N),
               Paragraph(sooritaja.nimi, N),
               Paragraph(kasutaja.isikukood or kasutaja.synnikpv.strftime('%d.%m.%Y'), N),
               Paragraph('%s %s' % (testikoht.tahis, tos.tahis), N),
               ]
        if test.on_tseis:
            row.append('') # dok nr
        row.append(Table([['']], rowHeights=(7*mm,))) # allkirja koht, teeme rea kõrgemaks
        row.append('') # II vihiku allkirja koht
        data.append(row)

    TS = TableStyle([('GRID',(0,0),(-1,-1), 0.5, colors.black),
                     ('LEFTPADDING',(0,0),(-1,-1), 3),
                     ('RIGHTPADDING',(0,0),(-1,-1), 3),])
    colWidths = [7*mm, nimi_width, 23*mm, 18*mm]
    allkirjade_arv = 3
    allkiri_width = 75*mm/allkirjade_arv
    for i in range(allkirjade_arv):
        colWidths.append(allkiri_width)

    story.append(Table(data, 
                       colWidths=colWidths,
                       style=TS))

    story.append(Spacer(100*mm, 10*mm))

    allkirjad(story, test, testiosa, toimumisaeg)

    story.append(PageBreak())
    
