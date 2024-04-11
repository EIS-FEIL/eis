"Riigikeele tasemeeksamite suuliste II-III hindajate ja kirjalike hindajate akt"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const, usersession, Klrida
_ = usersession._
import eis.lib.helpers as h
import eis.lib.utils as utils
from .labiviijaakt_tasemeeksam import vastuvotja_tbl

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

    story.append(Paragraph(_('TÖÖDE VASTUVÕTMISE AKT'), LBC))
    story.append(Spacer(1,15*mm))
    story.append(Paragraph(_('Käesolev tööde vastuvõtmise akt on koostatud selle kohta, et Haridus- ja Noorteameti esindaja on vastavalt teenuse osutamise lepingule võtnud vastu teenusepakkuja {s} (isikukood: {ik}) poolt teostatud tööd, mille lepingujärgne teostamine nähtub lepingu juurde vormistatud protokollist alljärgnevalt:').format(s='<b>%s %s</b>' % (k_eesnimi, k_perenimi), ik=k_isikukood), M))
    story.append(Spacer(1,3*mm))

    tbl, tasu, cnt = hindaja_tbl(items, True)
    story.append(tbl)        

    story.append(Spacer(1, 3*mm))

    if taiendavinfo:
        story.append(Paragraph(taiendavinfo, M))
        story.append(Spacer(1, 3*mm))

    buf = _('Kokku arvestatud {m} eurot ({s}).').format(m=h.mstr(tasu, nbsp=True), s=utils.eurodsendidsonades(tasu))
    story.append(Paragraph(buf, M))
    story.append(Spacer(1, 10*mm))

    vastuvotja_tbl(story, _('Pilvi Alp / Testide keskuse peaspetsialist'))

def hindaja_tbl(items, tasemega):                  
    tasu = cnt = 0
    header = [Paragraph(_('Kuupäev'), NB),
              ]
    if tasemega:
        header.append(Paragraph(_('Tase'), NB))
    header += [Paragraph(_('Tööliik'), NB),
               Paragraph(_('Hindamiskogum'), NB),
               Paragraph(_('Liik'), NB),
               Paragraph(_('Tööde arv'), NB),
               Paragraph(_('Maksumus'), NB),
               Paragraph(_('Summa'), NB),
               ]
    data = [header]

    n_alates = 9
    n_labiviija = 11

    for r in items:
        alates = r[n_alates]
        lv = r[n_labiviija]
        hkogum = lv.hindamiskogum
        if hkogum:
            # kirjalik hindaja on seotud yhe hindamiskogumiga
            hk_tasu = hkogum.tasu or 0
            hkogum_tahis = hkogum.tahis
        else:
            # suuline hindaja hindab kõiki hindamiskogumeid (peaks olema ainult 1 hindamiskogum)
            hkogumid = [hk for hk in lv.toimumisaeg.testiosa.hindamiskogumid if hk.staatus]
            hk_tasu = sum([hk.tasu or 0 for hk in hkogumid])
            hkogum_tahis = ', '.join([hk.tahis for hk in hkogumid])
        lv_tasu = lv.get_tasu() or 0
            
        row = [Paragraph(h.str_from_date(alates), N),
               ]
        if tasemega:
            row.append(Paragraph(lv.toimumisaeg.testiosa.test.keeletase_nimi, N))

        row += [Paragraph(lv.kasutajagrupp.nimi, N),
                Paragraph(hkogum_tahis, N),
                Paragraph(lv.liik_nimi, N),
                Paragraph(str(lv.tasu_toode_arv or 0), N),
                Paragraph(h.mstr(hk_tasu, nbsp=True), N),
                Paragraph(h.mstr(lv_tasu, nbsp=True), N),
                ]
        data.append(row)
        tasu += lv_tasu
        cnt += 1

    data, col_widths, vaba = calc_table_width(data, max_width=190*mm, nice_width=160*mm)
    # kui jääb vaba ruumi
    if vaba > 0:
        col_widths[-6] += vaba*.7
        col_widths[-4] += vaba*.3

    TS = [('LINEBELOW', (0,0), (-1,0), 0.5, colors.black), 
          ('VALIGN', (0,0), (-1,-1), 'TOP'),
          ]
    tbl = Table(data, 
                colWidths=col_widths,
                style=TS,
                repeatRows=1)
    return tbl, tasu, cnt
