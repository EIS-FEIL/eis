"Eksaminandide tähestikuline nimekiri"

from datetime import date
from eis.model import const
from eis.model.usersession import _
from .pdfutils import *
from .stylesheet import *

def generate(story, toimumisaeg, testikoht, lang, items):

    testiosa = toimumisaeg.testiosa
    test = testiosa.test
    koht_nimi = testikoht.koht.nimi
    kuva_grupp = not test.on_tseis

    story.append(Paragraph(_('Toimumisaja tähis') + ': <font size="14"><b>%s</b></font>' % toimumisaeg.tahised, NR))
    story.append(Paragraph(_('Eksaminandide tähestikuline nimekiri'), LC))
    story.append(Paragraph('<u>%s</u>' % koht_nimi, LBC))

    data = [[[Paragraph('<u>%s, %s</u>' % (test.nimi, testiosa.nimi), NB),
              Paragraph('(%s)' % _("eksam"), S)],
             [Paragraph('<u>%s</u>' % (testikoht.millal or ''), NBR),
              Paragraph('(%s)' % _("kuupäev"), SR)]],
            ]
    if lang:
        lang_nimi = const.LANG_NIMI.get(lang)
        data.append([[Paragraph('<u>%s</u>' % lang_nimi, NB),
                      Paragraph('(%s)' % _("eksami sooritamise keel"), S)],
                     ''])

    story.append(Table(data, colWidths=(125*mm, 30*mm)))

    
    # sooritajate loetelu tabel
    header = [Paragraph(_('Nr'), N),
              Paragraph(_('Eesnimi'), N),
              Paragraph(_('Perekonnanimi'), N),
              Paragraph(_('Ruum'), N),
              ]
    if kuva_grupp:
        header.append(Paragraph(_('Grupi number'), N))

    data = [header]
    for n, r in enumerate(items):
        eesnimi, perenimi, ruum_tahis, tpr_tahis = r
        row = [Paragraph(str(n+1), N),
               Paragraph(eesnimi, N),
               Paragraph(perenimi, N),
               Paragraph(ruum_tahis or '', N),
               ]
        if kuva_grupp:
            row.append(Paragraph(tpr_tahis, N))
        data.append(row)

    TS = TableStyle([('LINEBELOW',(0,0),(-1,0), 1, colors.black),
                     ('LINEBELOW',(0,1),(-1,-1), 0.5, colors.grey)])

    data, col_widths, vaba = calc_table_width(data, max_width=190*mm, nice_width=160*mm)
    # kui jääb vaba ruumi
    if vaba > 0:
        # ruumile juurde ruumi, et ei läheks mitmele reale
        d = min(20*mm - col_widths[2], vaba)
        if d > 0:
            col_widths[2] += d
            vaba -= d
        col_widths[1] += vaba/2
        col_widths[2] += vaba/2

    story.append(Table(data, 
                       colWidths=col_widths,
                       repeatRows=1,
                       style=TS))

    story.append(PageBreak())
    
