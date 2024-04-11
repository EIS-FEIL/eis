"Riigikeele tasemeeksamite läbiviijate akt"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const, usersession, Klrida
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

    story.append(Paragraph(_('TÖÖDE VASTUVÕTMISE AKT'), LBC))
    story.append(Spacer(1,15*mm))
    story.append(Paragraph(_('Tööde vastuvõtmise akt on koostatud selle kohta, et Haridus- ja Noorteameti esindaja on vastavalt teenuse osutamise lepingule võtnud vastu teenusepakkuja {s} (isikukood: {ik}) poolt teostatud tööd, mille lepingujärgne teostamine nähtub lepingu juurde vormistatud protokollist alljärgnevalt:').format(s='<b>%s %s</b>' % (k_eesnimi, k_perenimi), ik=k_isikukood), M))
    story.append(Spacer(1,3*mm))

    tbl, tasu, cnt = labiviija_tbl(items, True)
    story.append(tbl)

    story.append(Spacer(1, 3*mm))

    if taiendavinfo:
        story.append(Paragraph(taiendavinfo, M))
        story.append(Spacer(1, 3*mm))

    buf = _('Kokku arvestatud {m} eurot ({s}).').format(m=h.mstr(tasu), s=utils.eurodsendidsonades(tasu))
    story.append(Paragraph(buf, M))
    story.append(Spacer(1, 10*mm))

    vastuvotja_tbl(story, _('Sulvi Bötker / Keele- ja kodakondsuseksamite peaspetsialist'))
    story.append(PageBreak())
    
def labiviija_tbl(items, tasemega):        
    tasu = cnt = 0
    header = [Paragraph(_('Kuupäev'), N),
              ]
    if tasemega:
        header.append(Paragraph(_('Tase'), N))
    header += [Paragraph(_('Tööliik'), N),
               Paragraph(_('Toimumise koht'), N),
               Paragraph(_('Kogus'), N),
               Paragraph(_('Summa'), N),
               ]
    data = [header]

    n_alates = 9
    n_labiviija = 11
    n_koht = 12

    for r in items:
        alates = r[n_alates]
        lv = r[n_labiviija]
        lv_tasu = lv.get_tasu() or 0
        koht_nimi, tr_algus, tk_algus = r[n_koht:n_koht+3]
        kogus = lv.tasu_toode_arv or 1

        row = [Paragraph(h.str_from_datetime(tr_algus or tk_algus or alates) or '', N),
               ]
        if tasemega:
            keeletase_nimi = lv.toimumisaeg.testiosa.test.keeletase_nimi
            row.append(Paragraph(keeletase_nimi or '', N))
        row += [Paragraph(lv.kasutajagrupp.nimi, N),
                Paragraph(koht_nimi or '', N),
                Paragraph(str(kogus or ''), N),
                Paragraph(h.mstr(lv_tasu, nbsp=True) or '', N),
                ]
        data.append(row)
        tasu += lv_tasu
        cnt += 1

    data, col_widths, vaba = calc_table_width(data, max_width=190*mm, nice_width=160*mm, extra=10*mm)
    # kui jääb vaba ruumi
    if vaba > 0:
        if col_widths[0] < 23*mm:
            d = min(23*mm, vaba)
            col_widths[0] += d
            vaba -= d
        col_widths[2] += vaba/2
        col_widths[3] += vaba/2

    TS = [('LINEBELOW', (0,0), (-1,0), 0.5, colors.black), 
          ('VALIGN', (0,0), (-1,-1), 'TOP'),
          ]

    tbl = Table(data, 
                colWidths=col_widths,
                style=TS,
                repeatRows=1)
    return tbl, tasu, cnt

def vastuvotja_tbl(story, vastuvotja):
    kpv = date.today()
    story.append(Paragraph(_('Tööd võttis vastu'), M))
    story.append(Paragraph(vastuvotja, M))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(_('(allkirjastatud digitaalselt)'), M))
    story.append(PageBreak())
