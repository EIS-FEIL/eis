"Läbiviijate aktid"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const, usersession
_ = usersession._
import eis.lib.helpers as h
import eis.lib.utils as utils

def generate(story, items, grupid_id, testiliik, taiendavinfo):
    # teisendame grouperi tulemuse listiks
    items = [item for item in items]

    # võtame viimasest kirjest isiku andmed
    # ja kõigist kirjetest läbiviijad
    for r in items:
        k_eesnimi = r[2]
        k_perenimi = r[3]
        k_isikukood = r[4]
        break

    # sordime tähiste järgi
    items = sorted(items, key=lambda item: '%s %s' % (item[7], item[8]))
  
    story.append(Paragraph(_('TÖÖDE VASTUVÕTMISE AKT'), NBC))    
    story.append(Spacer(1,2*mm))
    story.append(Paragraph(h.str_from_date(date.today()), NR))
    story.append(Spacer(1,3*mm))    

    story.append(Paragraph(_('Käesolev tööde vastuvõtmise akt on koostatud selle kohta, et Haridus- ja Noorteameti esindaja on vastavalt teenuse osutamise lepingule võtnud vastu teenusepakkuja {s} (isikukood: {ik}) poolt teostatud tööd sisestajana, mille lepingujärgne teostamine nähtub Eksamite Infosüsteemis järgnevalt:').format(s='<b>%s %s</b>' % (k_eesnimi, k_perenimi), ik=k_isikukood), N))

    tbl, tasu, cnt = sisestaja_tbl(items, kuva_sk_nimi=True)
    story.append(tbl)

    story.append(Spacer(1, 3*mm))

    if taiendavinfo:
        story.append(Paragraph(taiendavinfo, N))
        story.append(Spacer(1, 3*mm))
    
    story.append(Paragraph(_('Kokku arvestatud {m} eurot ({s}).').format(
        m = ('%.2f' % (tasu)).replace('.',','),
        s = utils.eurodsonades(tasu)),
                           N))
    story.append(Spacer(1, 3*mm))
    user_nimi = usersession.get_user().fullname
    story.append(Paragraph(_('Tööd võttis vastu') + '<br/>%s' % user_nimi, N)),
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(_('(allkirjastatud digitaalselt)'), N))
    story.append(PageBreak())

def sisestaja_tbl(items, kuva_sk_nimi=False):    
    header = [Paragraph(_('Eksam'), NB),
              Paragraph(_('Toimumisaja tähis'), NB),
              Paragraph(_('Sisestuskogum'), NB),
              Paragraph(_('Sisestuste arv'), NB),
              Paragraph(_('Kogumi maksumus'), NB),
              Paragraph(_('Summa'), NB),
              ]
    data = [header]
    tasu = cnt = 0
    for r in items:
        test_nimi = r[7]
        ta_tahised = r[8]
        sk_tahis = r[11]
        sk_nimi = r[12]
        sk_tasu = r[13]
        kogus = r[16]
        s_tasu = kogus * (sk_tasu or 0)

        row = [Paragraph(test_nimi, N),
               Paragraph(ta_tahised, N),
               Paragraph(kuva_sk_nimi and sk_nimi or sk_tahis, N),
               Paragraph(str(kogus), N),
               Paragraph(h.mstr(sk_tasu or 0, digits=3, nbsp=True), N),
               Paragraph(h.mstr(s_tasu, nbsp=True), N),
               ]
        data.append(row)
        tasu += s_tasu
        cnt += 1

    data, col_widths, vaba = calc_table_width(data, max_width=190*mm, nice_width=160*mm, extra=10*mm)
    # kui jääb vaba ruumi
    if vaba > 0:
        col_widths[0] += vaba/2
        col_widths[2] += vaba/2

    TS = [('VALIGN', (0,0), (-1,-1), 'TOP'),]
    tbl = Table(data, 
                colWidths=col_widths,
                style=TS,
                repeatRows=1)
    return tbl, tasu, cnt
