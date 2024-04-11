"Registreerunute nimekiri rühmade kaupa, eksaminandide allkirjadega"

from datetime import date
from eis.model import const
from eis.model.usersession import _
import eis.lib.helpers as helpers
from .pdfutils import *
from .stylesheet import *

def generate(fullstory, toimumisaeg, testikoht, lang, items, tpr):

    testiosa = toimumisaeg.testiosa
    test = testiosa.test
    koht_nimi = testikoht.koht.nimi

    story = []
    story.append(Paragraph(_('Toimumisaja tähis') + ': <font size="14"><b>%s</b></font>' % toimumisaeg.tahised, NR))
    story.append(Paragraph(_('Registreerunute nimekiri'), LC))
    story.append(Paragraph('<u>%s</u>' % koht_nimi, LBC))

    grupp_nimi = _('Grupp') + ' %s' % tpr.tahis
    ruum = tpr.testiruum.ruum
    if ruum and ruum.tahis:
        grupp_nimi += ', %s %s' % (_("ruum"), ruum.tahis)

    alates = tpr.testiruum.algus
    data = [[[Paragraph('<u>%s</u>' % (test.nimi), NB),
              Paragraph('(%s)' % _("eksam"), S)],
             Paragraph(grupp_nimi, NB),
             [Paragraph('<u>%s</u>' % (alates and alates.strftime('%d.%m.%Y') or ''), NBR),
              Paragraph('(%s)' % _("kuupäev"), SR)]],
            ]
    story.append(Table(data, colWidths=(70*mm,80*mm, 23*mm)))

    # sooritajate loetelu tabel
    header = [Paragraph(_('Nr'), N),
              Paragraph(_('Eesnimi'), N),
              Paragraph(_('Perekonnanimi'), N),
              Paragraph(_('Isikukood'), N),
              Paragraph(_('Allkiri'), N),
              ]

    data = [header]
    for n, r in enumerate(items):
        eesnimi, perenimi, isikukood, synnikpv = r
        row = [Paragraph(str(n+1), N),
               Paragraph(eesnimi, N),
               Paragraph(perenimi, N),
               Paragraph(isikukood or helpers.str_from_date(synnikpv), N),
               Paragraph('', N),
               ]
        data.append(row)

    TS = TableStyle([('LINEBELOW',(0,0),(-1,0), 1, colors.black),
                     ('LINEBELOW',(0,1),(-1,-1), 0.5, colors.grey),
                     ('BOTTOMPADDING', (0,1), (-1,-1), 6),
                     ('TOPPADDING', (0,1), (-1,-1), 6),
                     ])

    data, col_widths, vaba = calc_table_width(data, max_width=190*mm, nice_width=160*mm)
    # kui jääb vaba ruumi
    if vaba > 0:
        d = min(vaba, 60*mm - col_widths[-1])
        col_widths[-1] += d
        vaba -= d
        col_widths[1] += vaba/2
        col_widths[2] += vaba/2

    story.append(Table(data, 
                       colWidths=col_widths,
                       repeatRows=1,
                       style=TS))

    story.append(Spacer(100*mm, 5*mm))

    # story hoitakse üleni ühel lehel
    fullstory.append(KeepTogether(story))

