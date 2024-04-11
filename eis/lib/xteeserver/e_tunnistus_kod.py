# -*- coding: utf-8 -*- 
"""
Tunnistuse allalaadimine. Mõeldud kasutamiseks riigiportaalist komplekspäringu koosseisus.
"""
from eis.lib.pyxadapterlib.xutils import *
from eis import model
from eis.model import const
from eis.lib.pyxadapterlib import attachment
from eis.lib.xtee.xroad import get_ee_user_id

def serve(paring, header=None, attachments=[], context=None):
    error = None
    data_dok = None
    out_attachments = []
    tunnistus_id = paring.find('tunnistus_id').text
    if not tunnistus_id:
        error = 'Sisend puudub'
    else:
        try:
            tunnistus_id = int(tunnistus_id)
        except:
            tunnistus_id = None
            error = 'Vigane sisend'
        else:
            ik = get_ee_user_id(header)            
            k = model.Kasutaja.get_by_ik(ik)
            if not k:
                error = 'Pole andmeid isiku kohta'
            else:
                tunnistus = model.Tunnistus.get(tunnistus_id)
                if not tunnistus:
                    error = 'Antud ID-ga tunnistust ei leitud'
                elif tunnistus.kasutaja_id != k.id:
                    error = 'Tunnistuse vaatamise õigus puudub'
                elif tunnistus.staatus != const.N_STAATUS_AVALDATUD:
                    error = 'Tunnistus pole avaldatud'
                else:
                    data_dok = tunnistus.filedata
                    filename = tunnistus.filename
                    if not data_dok:
                        error = 'Tunnistus on olemas, kuid seda ei saa alla laadida'

    if error:
        res = E.response(E.teade(error))
    else:
        model.Paring_tunnistus.log(header, tunnistus.id)

        att = attachment.Attachment(data_dok, use_gzip=False)
        att.filename = filename
        content_id = att.gen_content_id()
        out_attachments = [att]
        kpv = tunnistus.valjastamisaeg and tunnistus.valjastamisaeg.strftime('%Y-%m-%d') or ''
        res = E.response(E.tunnistusenr(tunnistus.tunnistusenr),
                         E.valjastamisaeg(kpv),
                         E.kehtiv(tunnistus.staatus and '1' or '0'),
                         E.tunnistus('', href='cid:%s' % content_id, filename=filename))

    return res, out_attachments
