"Hindaja akt"

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

    # grupeerime aine järgi
    ained = {}
    a_testiliigid = {}
    for r in items:
        aine_kood = r[5]
        tliik = r[6]
        if not aine_kood in ained:
            ained[aine_kood] = [r]
            a_testiliigid[aine_kood] = set(tliik)
        else:
            ained[aine_kood].append(r)
            a_testiliigid[aine_kood].add(tliik)

    story.append(Paragraph(_('TÖÖ VASTUVÕTMISE AKT'), NBC))
    story.append(Spacer(1,15*mm))
    story.append(Paragraph('%s, %s' % (_("Tallinnas"), h.str_from_date(date.today())), N))
    story.append(Spacer(1,10*mm))    

    story.append(Paragraph(_('Käesolev töövõtulepingu vastuvõtmise akt on koostatud selle kohta, et tellija esindaja on vastavalt töövõtulepingule võtnud vastu töövõtja {s} (isikukood: {ik}) poolt töövõtulepingu punktis 1 teostatud tööd.').format(s='<b>%s %s</b>' % (k_eesnimi, k_perenimi), ik=k_isikukood), N))

    tasu = cnt = 0
        
    for aine_kood in ained:
        # sordime tähiste järgi
        items = sorted(ained[aine_kood], key=lambda item: '%s %s' % (item[9], item[10]))    
        aine_nimi = Klrida.get_str('AINE', aine_kood).lower()
        testiliigi = txt_eksami(a_testiliigid[aine_kood])
        story.append(Spacer(1,3*mm))
        story.append(Paragraph(_('Õppeaine {s} {typ} tööde hindamine').format(s=aine_nimi, typ=testiliigi), N))
        story.append(Spacer(1,2*mm))

        tbl, tbl_tasu, tbl_cnt = hindaja_tbl(items)
        story.append(tbl)
        tasu += tbl_tasu
        cnt += tbl_cnt

    story.append(Spacer(1, 3*mm))
    if taiendavinfo:
        story.append(Paragraph(taiendavinfo, N))
        story.append(Spacer(1, 3*mm))

    eurod = int(tasu)
    sendid = int(round((tasu - eurod)*100))
    story.append(Paragraph(_('Vastavalt lepingus kokkulepitule arvestatakse töötaja tasuks {n1}€ {n2} senti.').format(n1=eurod, n2=sendid), N))
    story.append(Spacer(1, 10*mm))

    vastuvotja_tbl(story, 
                   usersession.get_user().fullname + '<br/>' + _("Tellija esindaja"))

def txt_eksami(testiliigid):
    map_liik = {const.TESTILIIK_POHIKOOL: _('põhikooli lõpueksami'),
                const.TESTILIIK_RIIGIEKSAM: _('riigieksami'),
                const.TESTILIIK_RV: _('rahvusvahelise võõrkeeleeksami'),
                }
    li = [map_liik.get(liik) for liik in testiliigid]
    eksamitel = _('eksami')
    if None not in li:
        # komadega ühendamine, lõpus "ja"
        eksamitel = utils.joinand(li)
    return eksamitel
    
def vastuvotja_tbl(story, vastuvotja):    
    kpv = date.today()
    story.append(Paragraph(_('Tööd võttis vastu'), N))
    story.append(Paragraph(vastuvotja, N))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(_('(allkirjastatud digitaalselt)'), N))
    story.append(Paragraph('%s, %s' % (_("Tallinn"), kpv.strftime('%d.%m.%Y')), N))
    story.append(PageBreak())


def hindaja_tbl(items):                  
    tasu = cnt = 0
    header = [Paragraph(_('Hindamiskogum'), NB),
              Paragraph(_('Tööde arv'), NB),
              Paragraph(_('Maksumus'), NB),
              Paragraph(_('Summa'), NB),
              ]
    data = [header]

    n_labiviija = 11

    for r in items:
        lv = r[n_labiviija]
        hkogum = lv.hindamiskogum
        if hkogum:
            # kirjalik hindaja on seotud yhe hindamiskogumiga
            hk_tasu = hkogum.tasu or 0
            hkogum_tahis = hkogum.tahis
        else:
            # suuline hindaja ja vaidehindaja hindab kõiki hindamiskogumeid
            hkogumid = [hk for hk in lv.toimumisaeg.testiosa.hindamiskogumid if hk.staatus]
            hk_tasu = sum([hk.tasu or 0 for hk in hkogumid])
            hkogum_tahis = ', '.join([hk.tahis for hk in hkogumid])
        lv_tasu = lv.get_tasu() or 0
            
        row = [Paragraph(hkogum_tahis, N),
               Paragraph(str(lv.tasu_toode_arv or 0), N),
               Paragraph(h.mstr(hk_tasu, nbsp=True), N),
               Paragraph(h.mstr(lv_tasu, nbsp=True), N),
               ]
        data.append(row)
        tasu += lv_tasu
        cnt += 1

    data, col_widths, vaba = calc_table_width(data, max_width=190*mm, nice_width=160*mm, extra=10*mm)
    # kui jääb vaba ruumi
    if vaba > 0:
        col_widths[0] += vaba*.7
        col_widths[1] += vaba*.3

    TS = [('VALIGN', (0,0), (-1,-1), 'TOP'),]
    tbl = Table(data, 
                colWidths=col_widths,
                style=TS,
                repeatRows=1)
    return tbl, tasu, cnt
