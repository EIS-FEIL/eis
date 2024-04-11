"Riigieksami või põhikooli lõpueksami läbiviijatele saadetav kiri töötasude kohta"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const, usersession, Klrida, Kasutaja
_ = usersession._
import eis.lib.helpers as h
import eis.lib.utils as utils
from .labiviijaakt_vaatleja import vaatleja_tbl, get_labiviijad

def generate(story, items, grupid_id, testiliik, taiendavinfo):
    k_eesnimi, k_perenimi, k_isikukood, labiviijad = get_labiviijad(items)
    
    story.append(Paragraph(_('Haridus- ja Noorteamet'), LBC))
    story.append(Paragraph(_('Lõõtsa 4, 11415 Tallinn'), LBC))
    story.append(Spacer(1,5*mm))

    story.append(Table([[Paragraph(_('Lp {s}').format(s='%s %s' % (k_eesnimi, k_perenimi)), M),
                         Paragraph(h.str_from_date(date.today()), M)]],
                       colWidths=(140*mm,40*mm),
                       style=TableStyle([('VALIGN', (0,0),(-1,-1), 'TOP'),
                                         ('LEFTPADDING', (0,0),(-1,-1), 0),
                                         ]),
                       hAlign='LEFT'
                       ))    
    story.append(Spacer(1,7*mm))
    eksamitel = txt_eksamitel(testiliik)

    story.append(Paragraph(_('Edastame Teile koondväljavõtte Teie poolt {ttype} välisvaatlejana teostatud tööde ja väljamaksmisele kuuluvate töötasude kohta.').format(ttype=eksamitel), M))
    
    story.append(Spacer(1,3*mm))

    tbl, tasu, cnt = vaatleja_tbl(labiviijad)
    story.append(tbl)

    story.append(Spacer(1, 3*mm))
    if taiendavinfo:
        story.append(Paragraph(taiendavinfo, M))
        story.append(Spacer(1, 3*mm))
    
    if cnt == 1:
        msg = _('Kokku vastu võetud {n} vaatlemiskord, töötasu arvestatud {m} eurot ({s}).')
    else:
        msg = _('Kokku vastu võetud {n} vaatlemiskorda, töötasu arvestatud {m} eurot ({s}).')
    story.append(Paragraph(msg.format(n=cnt,
                                      m=('%.2f' % (tasu)).replace('.',',').replace(',00', ''),
                                      s=utils.eurodsonades(tasu).replace(' ja 00 senti', '')),
                           M))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(_('NB! Juhul, kui esitatud andmetes on ebatäpsusi, palume sellest teatada e-posti aadressil vaatleja@harno.ee.'), M))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(_('Haridus- ja Noorteamet') + '<br/>' + _('Testide korraldamise keskus'), M))
    story.append(PageBreak())

def txt_eksamitel(testiliigid):
    map_liik = {const.TESTILIIK_POHIKOOL: _('põhikooli lõpueksamitel'),
                const.TESTILIIK_RIIGIEKSAM: _('riigieksamitel'),
                const.TESTILIIK_RV: _('rahvusvahelise võõrkeeleeksamitel'),
                }
    li = [map_liik.get(liik) for liik in testiliigid]
    eksamitel = _('eksami')
    if None not in li:
        # komadega ühendamine, lõpus "ja"
        eksamitel = utils.joinand(li)
    return eksamitel
