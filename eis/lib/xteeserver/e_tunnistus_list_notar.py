"""
Tunnistuste loetelu päring notaritele.
Väljastatakse sisendis olnud isikukoodiga isiku kõigi tunnistuste loetelu.
"""
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *
from eis import model
from eis.model import const
import eis.lib.helpers as h

def serve(paring, header=None, attachments=[], context=None):
    error = None
    isikukood = paring.find('isikukood').text
    if not isikukood:
        error = 'Isikukood puudub'
    else:
        li, error = _search(isikukood)

        if not error and not len(li):
            error = 'Kehtivaid e-tunnistusi isikule isikukoodiga %s ei leitud' % isikukood

    if error:
        res = E.response(E.teade(error))
    else:
        model.Paring_logi.log(header)
        buf = ''
        res = E.response(E.teade(buf))
        jada = E.e_tunnistus_jada()
        for item in li:
            jada.append(item)
        res.append(jada)

    return res, []

def _search(isikukood):
    kasutaja = model.Kasutaja.get_by_ik(isikukood)
    if not kasutaja:
        return None, 'Andmebaasist ei leitud isikukoodiga %s isiku andmeid' % isikukood

    q = model.Session.query(model.Tunnistus).\
        filter(model.Tunnistus.kasutaja_id==kasutaja.id).\
        filter(model.Tunnistus.staatus==const.N_STAATUS_AVALDATUD).\
        order_by(model.Tunnistus.id)

    li = []
    for rcd in q.all():
        tunnistus = rcd
        item = E.item(E.tunnistus_id(str(tunnistus.id)), # xsd:integer
                      E.tunnistus_nr(tunnistus.tunnistusenr),
                      E.nimi('%s %s' % (tunnistus.eesnimi, tunnistus.perenimi)),
                      E.isikukood(kasutaja.isikukood),
                      E.aasta(str(tunnistus.valjastamisaeg.year)) # xsd:integer
                      )
        li.append(item)
    return li, None
