"Lisatingimuste või erivajadustega isikute nimekiri"

from datetime import date
import eis.lib.helpers as h
from eis.model.usersession import _
from .pdfutils import *
from .stylesheet import *

def generate(story, toimumisaeg, erivajadustega, lisatingimustega):

    test = toimumisaeg.testiosa.test
    tase_nimi = test.keeletase_nimi

    story.append(Paragraph(_('Lisatingimuste või eritingimustega isikute nimekiri'), LB))
    story.append(Spacer(3*mm, 3*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))

    story.append(Paragraph('%s: %s' % (_("Kuupäev"), toimumisaeg.millal), NI))
    story.append(Spacer(6*mm, 6*mm))

    story.append(Paragraph(test.nimi, LB))
    story.append(Spacer(6*mm, 6*mm))

    ############### erivajadused

    story.append(Paragraph(_('Eritingimustega isikud'), LB))
    if len(erivajadustega) == 0:
        story.append(Paragraph(_('Eritingimustega isikuid ei ole'), N))
    for item in erivajadustega:
        isikukood, synniaeg, eesnimi, perenimi, sooritus, lisatingimused = item
        header = [Paragraph(_('Isikukood'), N),
                  Paragraph(_('Eesnimi'), N),
                  Paragraph(_('Perekonnanimi'), N),
                  Paragraph(_('Töö kood'), N),
                  Paragraph(_('Vabastatud'), N),
                  ]

        if sooritus.staatus == const.S_STAATUS_VABASTATUD:
            vabastatud = sooritus.testiosa.nimi
        else:
            li = [a.alatest.nimi for a in sooritus.alatestisooritused if a.staatus==const.S_STAATUS_VABASTATUD]
            vabastatud = ','.join(li)

        body = [Paragraph(isikukood or h.str_from_date(synniaeg), NB),
                Paragraph(eesnimi, NB),
                Paragraph(perenimi, NB),
                Paragraph(sooritus.tahised or '', NB),
                Paragraph(vabastatud, NB),
                ]

        if tase_nimi:
            header.insert(3, Paragraph(_('Tase'), N))
            body.insert(3, Paragraph(tase_nimi, NB))

        data = [header, body]
        data, col_widths, vaba = calc_table_width(data, max_width=175*mm)
        if vaba > 0:
            col_widths[1] += vaba/4
            col_widths[2] += vaba/4           
            col_widths[-1] += vaba/4
            col_widths[-2] += vaba/4            

        TS = TableStyle([('LINEBELOW',(0,0),(-1,0), 0.5, colors.black),
                         ])      
        story.append(Table(data, colWidths=col_widths, style=TS))

        erivajadus = sooritus.get_erivajadus(None)
        if erivajadus and erivajadus.kinnitus_markus:
            story.append(Paragraph("%s: %s" % (_('Komisjoni otsuse tekst'), erivajadus.kinnitus_markus), N))

        story.append(Spacer(3*mm, 3*mm))


    ############### lisatingimustega isikud
    story.append(Spacer(6*mm, 6*mm))
    story.append(Paragraph(_('Lisatingimustega isikud'), LB))
    if len(lisatingimustega) == 0:
        story.append(Paragraph(_('Lisatingimustega isikuid ei ole'), N))
    for item in lisatingimustega:
        isikukood, synniaeg, eesnimi, perenimi, sooritus, lisatingimused = item
        header = [Paragraph(_('Isikukood'), N),
                  Paragraph(_('Eesnimi'), N),
                  Paragraph(_('Perekonnanimi'), N),
                  Paragraph(_('Töö kood'), N),
                  ]

        body = [Paragraph(isikukood or h.str_from_date(synniaeg), NB),
                Paragraph(eesnimi, NB),
                Paragraph(perenimi, NB),
                Paragraph(sooritus.tahised or '', NB),
                ]

        if tase_nimi:
            header.insert(3, Paragraph(_('Tase'), N))
            body.insert(3, Paragraph(tase_nimi, NB))

        data = [header, body]
        data, col_widths, vaba = calc_table_width(data, max_width=175*mm)
        if vaba > 0:
            col_widths[1] += vaba/3
            col_widths[2] += vaba/3           
            col_widths[3] += vaba/3

        TS = TableStyle([('LINEBELOW',(0,0),(-1,0), 0.5, colors.black),
                         ])      
        story.append(Table(data, colWidths=col_widths, style=TS))
        story.append(Paragraph(lisatingimused, N))

        story.append(Spacer(3*mm, 3*mm))
  

    story.append(PageBreak())
    
