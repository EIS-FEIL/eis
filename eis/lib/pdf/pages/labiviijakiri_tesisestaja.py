"Riigikeele tasemeeksamite läbiviijatele saadetav kiri töötasude kohta"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const, usersession, Klrida, Kasutaja
_ = usersession._
import eis.lib.helpers as h
import eis.lib.utils as utils
from .labiviijaakt_sisestaja import sisestaja_tbl

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

    story.append(Paragraph(_('Haridus- ja Noorteamet'), LBC))
    story.append(Paragraph(_('Lõõtsa 4, 11415 Tallinn'), LBC))
    story.append(Spacer(1,15*mm))

    li = [_('Lp {s}').format(s='%s %s' % (k_eesnimi, k_perenimi))] 
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
    story.append(Paragraph(_('Lugupeetud {s}, edastame Teile andmed vastavalt käsunduslepingule Teie poolt eesti keele tasemeeksamitel teostatud tööde ja väljamaksmisele kuuluvate töötasude kohta.').format(s='%s %s' % (k_eesnimi, k_perenimi)), M))
    story.append(Spacer(1,3*mm))

    tbl, tasu, cnt = sisestaja_tbl(items)
    story.append(tbl)        

    story.append(Spacer(1, 3*mm))
    if taiendavinfo:
        story.append(Paragraph(taiendavinfo, M))
        story.append(Spacer(1, 3*mm))

    buf = _('Kokku arvestatud {m} eurot ({s}).').format(m=h.mstr(tasu, nbsp=True), s=utils.eurodsendidsonades(tasu))
    story.append(Paragraph(buf, M))
    story.append(Spacer(1, 10*mm))

    story.append(Paragraph(_('NB! Juhul, kui esitatud andmetes on ebatäpsusi, palume sellest teatada telefonil 735 0562.'), M))

    story.append(PageBreak())
