"Läbiviijate aktid"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const, usersession
_ = usersession._
import eis.lib.helpers as h
import eis.lib.utils as utils

def generate(story, items, grupid_id, testiliik, taiendavinfo):

    k_eesnimi, k_perenimi, k_isikukood, labiviijad = get_labiviijad(items)
    
    story.append(Paragraph(_('TÖÖDE VASTUVÕTMISE AKT'), NBC))    
    story.append(Spacer(1,2*mm))
    story.append(Paragraph(h.str_from_date(date.today()), NR))
    story.append(Spacer(1,3*mm))    

    story.append(Paragraph(_('Tööde vastuvõtmise akt on koostatud selle kohta, et Haridus- ja Noorteameti esindaja on vastavalt teenuse osutamise lepingule võtnud vastu teenusepakkuja {s} (isikukood: {ik}) poolt teostatud tööd välisvaatlejana, mille lepingujärgne teostamine nähtub eksamite toimumise protokollidelt.').format(s='%s %s' % (k_eesnimi, k_perenimi), ik=k_isikukood), N))

    tbl, tasu, cnt = vaatleja_tbl(labiviijad)

    story.append(tbl)
    story.append(Spacer(1, 3*mm))
    if cnt == 1:
        msg = _('Kokku vastu võetud {n} vaatlemiskord, töötasu arvestatud {m} eurot ({s}).')
    else:
        msg = _('Kokku vastu võetud {n} vaatlemiskorda, töötasu arvestatud {m} eurot ({s}).')
    story.append(Paragraph(msg.format(n=cnt,
                                      m=('%.2f' % (tasu)).replace('.',',').replace(',00', ''),
                                      s=utils.eurodsonades(tasu).replace(' ja 00 senti', '')),
                           N))
    story.append(Spacer(1, 3*mm))

    if taiendavinfo:
        story.append(Paragraph(taiendavinfo, N))
        story.append(Spacer(1, 3*mm))
    
    user_nimi = usersession.get_user().fullname
    story.append(Paragraph(_('Tööd võttis vastu') + '<br/>%s' % user_nimi, N)),
    story.append(Paragraph(_('(allkirjastatud digitaalselt)'), N))    
    story.append(PageBreak())
    
def get_labiviijad(items):
    # võtame viimasest kirjest isiku andmed
    # ja kõigist kirjetest läbiviijad
    labiviijad = []
    n_labiviija = 11
    for r in items:
        k_eesnimi = r[2]
        k_perenimi = r[3]
        k_isikukood = r[4]
        labiviijad.append(r[n_labiviija])
    
    # sordime läbiviijad alguse järgi
    items = sorted(labiviijad, key=lambda lv: lv.testiruum.algus and lv.testiruum.algus.date() or const.MAX_DATE)
    return k_eesnimi, k_perenimi, k_isikukood, items

def vaatleja_tbl(labiviijad):
    header = [Paragraph(_('Kood'), NB),
              Paragraph(_('Kuupäev'), NB),
              Paragraph(_('Eksam'), NB),
              Paragraph(_('Lisaaeg'), NB),
              Paragraph(_('Vaatlemiskoht'), NB),
              Paragraph(_('Summa'), NB),
              ]
    data = [header]
    tasu = cnt = 0
    for lv in labiviijad:
        lv_tasu = lv.get_tasu() or 0
        row = [Paragraph(lv.toimumisaeg.tahised, N),
               Paragraph(h.str_from_date(lv.testiruum.algus) or '', N),
               Paragraph(lv.toimumisaeg.testimiskord.test.nimi, N),
               Paragraph(lv.yleaja and _('Jah') or _('Ei'), N),
               Paragraph(lv.testikoht.koht.nimi, N),
               Paragraph(h.mstr(lv_tasu, nbsp=True), N),
               ]
        data.append(row)
        tasu += lv_tasu
        cnt += 1

    data, col_widths, vaba = calc_table_width(data, max_width=190*mm, nice_width=160*mm, extra=10*mm)
    # kui jääb vaba ruumi
    if vaba > 0:
        col_widths[2] += vaba/2
        col_widths[4] += vaba/2

    TS = [('VALIGN', (0,0), (-1,-1), 'TOP'),]
    tbl = Table(data, 
                colWidths=col_widths,
                style=TS,
                repeatRows=1)
    return tbl, tasu, cnt
