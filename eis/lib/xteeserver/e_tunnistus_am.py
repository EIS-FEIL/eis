"""
Tunnistuse ID järgi tunnistuse .asice/.ddoc/.bdoc faili alla laadimine
"""
from eis.lib.pyxadapterlib.xutils import *
from eis import model
from eis.model import const
from eis.lib.pyxadapterlib import attachment

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
            tunnistus = model.Tunnistus.get(tunnistus_id)
            if not tunnistus:
                error = 'Antud ID-ga tunnistust ei leitud'
            elif tunnistus.staatus != const.N_STAATUS_AVALDATUD:
                error = 'Antud ID-ga tunnistus pole avalik'                
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
        res = E.response(E.teade('Tunnistus nr %s' % tunnistus.tunnistusenr),
                         E.tunnistus('', href='cid:%s' % content_id, filename=filename))

    return res, out_attachments
