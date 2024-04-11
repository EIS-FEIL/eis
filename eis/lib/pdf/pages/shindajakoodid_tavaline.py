"Suulise osa hindajate ja intervjueerijate koodid"

from datetime import date
import eis.model as model
from eis.model import const
from eis.model.usersession import _
import eis.lib.helpers as h

from .pdfutils import *
from .stylesheet import *

def generate(story, toimumisaeg, testikoht, testipakett):
    testiosa = toimumisaeg.testiosa
    test = testiosa.test
    koht_nimi = testikoht.koht.nimi
    testiruum = testipakett and testipakett.testiruum
    if testiruum:
        ruum = testiruum.ruum
        # on_ruumiprotokoll
        if ruum and ruum.tahis:
            koht_nimi = '%s, %s %s' % (koht_nimi, _("ruum"), testiruum.ruum.tahis)

    story.append(Paragraph(_('Toimumisaja tähis') + ': <font size="14"><b>%s</b></font>' % toimumisaeg.tahised, NR))
    story.append(Paragraph(_('Suulise osa hindajate ja intervjueerijate koodid'), LBC))

    story.append(Paragraph('<u>%s</u>' % koht_nimi, MBC))

    data = [[[Paragraph('<u>%s, %s</u>' % (test.nimi, testiosa.nimi), NB),
              Paragraph('(%s)' % _("eksam"), S)],
             ],
            ]
    if testipakett and testipakett.lang:
        lang_nimi = testipakett.lang_nimi
        data.append([[Paragraph('<u>%s</u>' % lang_nimi, NB),
                      Paragraph('(%s)' % _("eksami sooritamise keel"), S)],
                     ])

    story.append(Table(data, colWidths=(155*mm,), hAlign='LEFT'))
    story.append(Spacer(5*mm, 5*mm))
    
    header = [Paragraph(_('Nimi'), M),
              Paragraph(_('Kood'), M),
              ]
    # intervjueerijad kuvame ainult juhul, kui neil on olemas hindaja kood
    # ilma koodita ei tohi siin kedagi kuvada
    data = [header]
    grupid_id = (const.GRUPP_HINDAJA_S, const.GRUPP_HINDAJA_S2, const.GRUPP_INTERVJUU)
    q = (model.Session.query(model.Kasutaja.nimi, model.Ainelabiviija.tahis)
         .distinct()
         .join(model.Kasutaja.labiviijad)
         .filter(model.Labiviija.kasutajagrupp_id.in_(grupid_id))
         .filter(model.Labiviija.testikoht_id==testikoht.id)
         .join(model.Kasutaja.profiil)
         .join(model.Profiil.ainelabiviijad)
         .filter(model.Ainelabiviija.aine_kood==test.aine_kood)
         .filter(model.Ainelabiviija.tahis!=None))
                                                     
    if testiruum:
        q = q.filter(model.Labiviija.testiruum_id==testiruum.id)
        
    for nimi, tahis in q.order_by(model.Kasutaja.nimi).all():
        row = [Paragraph(nimi, M),
               Paragraph(str(tahis or ''), M),
               ]
        data.append(row)

    TS = TableStyle([('GRID',(0,0),(-1,-1), 0.5, colors.black),
                     ])

    data, col_widths, vaba = calc_table_width(data, max_width=190*mm, nice_width=110*mm)
    # kui jääb vaba ruumi
    if vaba > 0:
        col_widths[0] += vaba

    story.append(Table(data, 
                       colWidths=col_widths,
                       repeatRows=1,
                       hAlign='LEFT',
                       style=TS))

    story.append(Spacer(5*mm, 5*mm))
    
    story.append(Paragraph(_('Palume see kood kanda suulise osa hindamisprotokolli.'), M))
    story.append(Paragraph(_('Juhul, kui mõni hindaja või intervjueerija puudub nimekirjast, siis kirjutada hindamisprotokollile koodi asemel loetavalt hindaja või intervjueerija initsiaalid.'), M))

    story.append(PageBreak())
    
