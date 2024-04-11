"Riigieksami või põhikooli lõpueksami läbiviijatele saadetav kiri töötasude kohta"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const, usersession, Klrida, Kasutaja
import eis.lib.helpers as h
import eis.lib.utils as utils
from .labiviijaakt_riigieksam import labiviija_tbl

def generate(story, items, grupid_id, testiliik, taiendavinfo):
    # teisendame grouperi tulemuse listiks
    items = [item for item in items]

    # võtame viimasest kirjest isiku andmed
    # ja kõigist kirjetest läbiviijad
    for r in items:
        k_id = r[0]
        k_eesnimi = r[2]
        k_perenimi = r[3]
        k_isikukood = r[4]
        break

    story.append(Paragraph('Haridus- ja Noorteamet', LBC))
    story.append(Paragraph('Lõõtsa 4, 11415 Tallinn', LBC))
    story.append(Spacer(1,15*mm))

    li = ['Lp %s %s' % (k_eesnimi, k_perenimi)] 
    kasutaja = Kasutaja.get(k_id)
    if kasutaja.aadress:
        li.extend(kasutaja.aadress.li_print_aadress(kasutaja))
    aadress = '<br/>'.join(li)

    story.append(Table([[Paragraph(aadress, N), ]],
                       colWidths=(130*mm,),
                       style=TableStyle([('VALIGN', (0,0),(-1,-1), 'TOP'),
                                         ]) 
                       ))    
    story.append(Spacer(1,3*mm))
    eksamitel = txt_eksamitel(testiliik)
    story.append(Paragraph('Lugupeetud %s %s, edastame Teile andmed vastavalt käsunduslepingule Teie poolt %s teostatud tööde ja väljamaksmisele kuuluvate töötasude kohta.' % (k_eesnimi, k_perenimi, eksamitel), M))
    story.append(Spacer(1,3*mm))

    tbl, tasu, cnt = labiviija_tbl(items, False)
    story.append(tbl)

    story.append(Spacer(1, 3*mm))
    if taiendavinfo:
        story.append(Paragraph(taiendavinfo, M))
        story.append(Spacer(1, 3*mm))
    
    eurod = int(tasu)
    sendid = int((tasu - eurod)*100)
    buf = 'Kokku arvestatud %s eurot (%s eurot ja %s senti).' % \
          (h.mstr(tasu), utils.arvsonades(eurod), utils.arvsonades(sendid))
    story.append(Paragraph(buf, M))
    story.append(Spacer(1, 10*mm))

    story.append(Paragraph('NB! Juhul, kui esitatud andmetes on ebatäpsusi, palume sellest teatada e-posti aadressil harno@harno.ee.', M))

    story.append(PageBreak())

def txt_eksamitel(testiliigid):
    map_liik = {const.TESTILIIK_POHIKOOL: 'põhikooli lõpueksamitel',
                const.TESTILIIK_RIIGIEKSAM: 'riigieksamitel',
                const.TESTILIIK_RV: 'rahvusvahelise võõrkeeleeksamitel',
                }
    li = [map_liik.get(liik) for liik in testiliigid]
    eksamitel = 'eksami'
    if None not in li:
        # komadega ühendamine, lõpus "ja"
        eksamitel = utils.joinand(li)
    return eksamitel
