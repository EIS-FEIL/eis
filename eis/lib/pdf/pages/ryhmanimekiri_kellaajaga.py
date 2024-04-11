"Eksaminandide nimekiri rühmade kaupa, kellaaegadega"

from datetime import date
from eis.model import const
import eis.model as model
from eis.model.usersession import _
import eis.lib.helpers as h
from .pdfutils import *
from .stylesheet import *
from datetime import datetime

def generate(fullstory, toimumisaeg, testikoht, lang, tpr):

    testiosa = toimumisaeg.testiosa
    test = testiosa.test
    koht_nimi = testikoht.koht.nimi

    story = []

    s_time = datetime.now().strftime('%d.%m.%Y %H.%M')
    story.append(Table([[Paragraph(_('Väljatrükk') + ': %s' % s_time, S),
                         Paragraph(_('Toimumisaja tähis') + ': <font size="14"><b>%s</b></font>' % toimumisaeg.tahised, NR)]]))

    story.append(Paragraph(_('Eksaminandide nimekiri'), LC))
    story.append(Paragraph('<u>%s</u>' % koht_nimi, LBC))

    grupp_nimi = _('Grupi number') + ' %s' % tpr.tahis
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
    if lang:
        lang_nimi = const.LANG_NIMI.get(lang)
        data.append([[Paragraph('<u>%s</u>' % lang_nimi, NB),
                      Paragraph('(%s)' % _("eksami sooritamise keel"), S)],
                     '',
                     ''])
    story.append(Table(data, colWidths=(70*mm,80*mm, 23*mm)))

    # leitakse selle protokollirühma sooritajate nimekiri
    qi = (model.SessionR.query(model.Sooritaja.eesnimi, model.Sooritaja.perenimi, model.Sooritus.kavaaeg)
          .filter(model.Sooritaja.staatus>const.S_STAATUS_REGAMATA)
          .join(model.Sooritaja.sooritused)
          .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)        
          .filter(model.Sooritus.testiprotokoll_id==tpr.id)
          .order_by(model.Sooritus.kavaaeg,model.Sooritaja.perenimi,model.Sooritaja.eesnimi)
          )
    items = qi.all()

    # sooritajate loetelu tabel
    header = [Paragraph(_('Nr'), N),
              Paragraph(_('Eesnimi'), N),
              Paragraph(_('Perekonnanimi'), N),
              Paragraph(_('Kell'), N),              
              ]

    data = [header]
    for n, r in enumerate(items):
        eesnimi, perenimi, kavaaeg = r
        s_kavaaeg = h.str_est_time_from_datetime(kavaaeg)
        row = [Paragraph(str(n+1), N),
               Paragraph(eesnimi, N),
               Paragraph(perenimi, N),
               Paragraph(s_kavaaeg, N),
               ]
        data.append(row)

    TS = TableStyle([('LINEBELOW',(0,0),(-1,0), 1, colors.black),
                     ('LINEBELOW',(0,1),(-1,-1), 0.5, colors.grey)])

    data, col_widths, vaba = calc_table_width(data, max_width=190*mm, nice_width=160*mm)
    # kui jääb vaba ruumi
    if vaba > 0:
        col_widths[1] += vaba/2
        col_widths[2] += vaba/2

    story.append(Table(data, 
                       colWidths=col_widths,
                       repeatRows=1,
                       style=TS))

    story.append(Spacer(100*mm, 5*mm))

    # story hoitakse üleni ühel lehel
    fullstory.append(KeepTogether(story))

