"Seaduse tundmise eksami sisestajate akt"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const, usersession, Klrida
_ = usersession._
import eis.lib.helpers as h
import eis.lib.utils as utils
from .labiviijaakt_sisestaja import sisestaja_tbl
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

    story.append(Paragraph(_('TÖÖ VASTUVÕTMISE AKT'), LBC))
    story.append(Spacer(1,15*mm))
    story.append(Paragraph(_('Käesolev tööde vastuvõtmise akt on koostatud selle kohta, et Käsundiandja esindaja on vastavalt käsunduslepingule võtnud vastu käsundisaaja {s} (isikukood {ik}) poolt Eesti Vabariigi põhiseaduse ja kodakondsuse tundmise seaduse eksamitel teostatud tööd alljärgnevalt:').format(s='%s %s' % (k_eesnimi, k_perenimi), ik=k_isikukood), M))
    story.append(Spacer(1,3*mm))

    tbl, tasu, cnt = sisestaja_tbl(items)
    story.append(tbl)

    story.append(Spacer(1, 3*mm))

    if taiendavinfo:
        story.append(Paragraph(taiendavinfo, M))
        story.append(Spacer(1, 3*mm))

    buf = _('Kokku arvestatud {m} eurot ({s}).').format(m=h.mstr(tasu), s=utils.eurodsendidsonades(tasu))
    story.append(Paragraph(buf, M))
    story.append(Spacer(1, 10*mm))

    vastuvotja_tbl(story, _('Sulvi Bötker / Keele- ja kodakondsuseksamite peaspetsialist'))

