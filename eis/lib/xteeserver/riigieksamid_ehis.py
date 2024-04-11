"""
Väljastatakse parameetriks antud isikukoodidega isikute riigieksamisoorituste andmed.

Sisendiks antakse komaga eraldatud stringi kujul isikukoodide loetelu.
Väljundi parameeter ret64 sisaldab base64-kodeeritud ZIP-pakitud tekstifaili, milles on riigieksamitulemuste andmed.
Väljastatakse need riigieksamisooritused, mille tulemused on kinnitatud ja avaldatud. Kui sooritaja on samas aines teinud mitu riigieksamit, siis väljastatakse neist ainult kõige parema tulemusega soorituse andmed.
Tekstifailis on iga testisooritaja kohta üks rida kujul:
isikukood,ainekood,pallid,taidetud

kus taidetud väärtus on 1 (õpilasel on täidetud lõpetamise tingimused) või 0 (õpilasel pole täidetud lõpetamise tingimused).

"""
import zipfile
import tempfile
import io
import os
from lxml import etree
import base64
from eis.lib.pyxadapterlib.xutils import *
from eis import model
from eis.model import const, sa
import eis.lib.helpers as h

import logging
log = logging.getLogger(__name__)

def serve(paring, header, attachments=[], context=None):
    isikukoodid = paring.find('isikukoodid').text or ''
    ik = isikukoodid.split(',')
    if not len(ik):
        error = 'Sisendparameetrid puuduvad'
        res = E.response(E.teade(error),
                         E.kood('1'))
    else:
        model.Paring_logi.log(header)
        data = _search(ik)
        encoded = _encode(data)
        res = E.response(E.ret64(encoded),
                         E.kood('0'),
                         E.teade(''))
    return res, []

def _search(ik):
    q = model.Session.query(model.Sooritaja.pallid,
                            model.Test.aine_kood,
                            model.Kasutaja.lopetanud,
                            model.Kasutaja.lopetanud_kasitsi)
    q = q.join(model.Sooritaja.test).\
        filter(model.Test.testiliik_kood==const.TESTILIIK_RIIGIEKSAM).\
        filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD).\
        filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD).\
        join(model.Sooritaja.testimiskord).\
        filter(model.Testimiskord.tulemus_kinnitatud==True).\
        filter(model.Testimiskord.koondtulemus_avaldet==True).\
        filter(model.Sooritaja.pallid!=None).\
        join(model.Sooritaja.kasutaja).\
        order_by(model.Test.aine_kood,sa.desc(model.Sooritaja.pallid))

    data = ''
    for isikukood in ik:
        prev_aine = None
        for rcd in q.filter(model.Kasutaja.isikukood==isikukood).all():
            pallid, aine_kood, lopetanud, lopetanud_kasitsi = rcd
            if aine_kood == prev_aine:
                # igast ainest väljastame ainult kõige parema tulemuse
                continue
            prev_aine = aine_kood
            lopetanud = (lopetanud or lopetanud_kasitsi) and '1' or '0'
            data += '%s,%s,%s,%s\n' % (isikukood, ehis_aine(aine_kood), h.rstr(pallid), lopetanud)
    return data 

def _encode(data):
    tf = tempfile.NamedTemporaryFile(delete=False)
    zf = zipfile.ZipFile(tf, "w", zipfile.ZIP_DEFLATED, False)
    zf.writestr('data.txt', data)
    zf.close()
    tf.close()

    f = open(tf.name, 'rb')
    zipped_data = f.read()
    f.close()
    
    os.unlink(tf.name)

    b64_data = base64.b64encode(zipped_data).decode('ascii')
    return b64_data

def ehis_aine(kood):
    """Aine klassifikaatori teisendamine
    EH-168 (ee ja vv)
    """
    ained = {'ee': 'E',
             'vv': 'W',
             }
    return ained.get(kood) or kood

if __name__ == '__main__':
    from eis.scripts.scriptuser import *

    # kasuta kujul: python riigieksamid_ehis.py -admin TEGIJAKOOD IK1,IK2,...,IKN 
    ikd = noname_args[0]
    ik = ikd.split(',')
    data = _search(ik)
    print(data)
    

