"Läbiviijate aktid"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const, usersession
_ = usersession._
import eis.lib.helpers as h

def generate(story, items):

    # võtame viimasest kirjest isiku andmed
    # ja kõigist kirjetest läbiviijad
    labiviijad = []
    for r in items:
        k_eesnimi = r[2]
        k_perenimi = r[3]
        k_isikukood = r[4]
        labiviijad.append(r[5])

    # sordime läbiviijad alguse järgi
    f_kpv = lambda lv: lv.testiruum and lv.testiruum.algus and lv.testiruum.algus.date() or \
                       lv.testikoht and lv.testikoht.alates and lv.testikoht.alates.date() or \
                       None
    items = sorted(labiviijad, key=f_kpv)

    # samal kuupäeval samas soorituskohas arvestatakse yhtainust kirjet
    labiviijad = []
    keys = []
    for lv in items:
        kpv = f_kpv(lv)
        koht_id = lv.testikoht.koht_id
        key = (kpv, koht_id)
        if key not in keys:
            keys.append(key)
            labiviijad.append(lv)
    
    story.append(Paragraph(_('Käsunduslepingu nr 8.2-19.3/______'), NBC))
    story.append(Paragraph(_('TEENUSE VASTUVÕTMISE AKT'), NBC))
    story.append(Spacer(10*mm,15*mm))
    story.append(Paragraph('%s, %s' % (_("Tallinnas"), h.str_from_date(date.today())), N))
    story.append(Spacer(10*mm,10*mm))    

    story.append(Paragraph(_('Käesolev teenuse vastuvõtmise akt on koostatud selle kohta, et käsundiandja esindaja on vastavalt käsunduslepingule võtnud vastu käsundisaaja {s} (isikukood: {ik}) poolt teostatud tööd konsultandina alljärgnevalt:').format(s='<b>%s %s</b>' % (k_eesnimi, k_perenimi), ik=k_isikukood), N))
    
    header = [Paragraph(_('Kood'), NB),
              Paragraph(_('Kuupäev'), NB),
              Paragraph(_('Konsultatsioon'), NB),
              Paragraph(_('Koht'), NB),
              Paragraph(_('Summa'), NB),
              ]
    data = [header]
    tasu = cnt = 0
    for lv in labiviijad:
        lv_tasu = lv.get_tasu() or 0
        if lv.toimumisaeg.on_ruumiprotokoll:
            kpv = lv.testiruum.algus
        else:
            kpv = lv.testikoht.alates
        row = [Paragraph(lv.toimumisaeg.tahised, N),
               Paragraph(h.str_from_date(kpv) or '', N),
               Paragraph(lv.toimumisaeg.testimiskord.test.nimi, N),
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
    story.append(Table(data, 
                       colWidths=col_widths,
                       style=TS,
                       repeatRows=1))

    story.append(Spacer(10*mm, 10*mm))
    story.append(Paragraph(_('Kokku vastu võetud {n} osalemiskorda, väljamaksmisele kuulub {m}.').format(n=cnt, m=h.mstr(tasu)), N))
    story.append(Spacer(10*mm, 15*mm))
    user_nimi = usersession.get_user().fullname    
    story.append(Paragraph(user_nimi, N))
    
    story.append(PageBreak())
