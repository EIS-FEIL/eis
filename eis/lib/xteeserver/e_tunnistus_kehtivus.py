"""
Tunnistuse kehtivuse kontrollimine ja tunnistuse .asice/.ddoc/.bdoc faili allalaadimine.
Kui 10 minuti jooksul esitatakse 3 korda sisendandmeid, millele tunnistusi ei vasta, siis blokeeritakse teenuse kasutamine 24 tunniks.
"""
from eis.lib.pyxadapterlib.xutils import *
from eis import model
import eiscore.const as const
from eis.lib.pyxadapterlib import attachment
import eis.lib.helpers as h

def serve(paring, header, attachments=[], context=None):
    error = None
    out_attachments = []

    isikukood = paring.find('isikukood').text
    tunnistus_nr = paring.find('tunnistus_nr').text

    if not isikukood or not tunnistus_nr:
        error = 'Palun esitada mõlemad sisendparameetrid'
    elif not len(isikukood) == 11:
        error = 'Vigane isikukood'

    if not error:
        error = model.Paring_blokeering.check(header)

    if not error:
        model.Paring_logi.log(header, isikukood)
        res, out_attachments, error = _search(header, isikukood, tunnistus_nr)
                       
    if error:
        res = E.response(E.teade(error))

    return res, out_attachments

def _search(header, isikukood, tunnistus_nr):
    error = None
    attachments = []

    q = (model.Tunnistus.query
         .filter(model.Tunnistus.tunnistusenr==tunnistus_nr)
         .join(model.Tunnistus.kasutaja)
         .filter(model.Kasutaja.isikukood==isikukood)
         .filter(model.Tunnistus.staatus.in_((const.N_STAATUS_KEHTETU,
                                              const.N_STAATUS_AVALDATUD)))
         )
    tunnistus = q.first()
    if not tunnistus:
        error = 'Valed sisendandmed. ' + \
            model.Paring_blokeering.increment(header)

        return None, None, error

    if tunnistus.staatus == const.N_STAATUS_KEHTETU:
        error = 'E-tunnistus numbriga %s on kehtetuks määratud.' % tunnistus_nr
        return None, None, error

    eksam_jada = _get_eksam_jada(tunnistus)
    if len(eksam_jada) == 0:
        error = 'Eksamite andmeid ei leitud'
        return None, None, error

    model.Paring_tunnistus.log(header, tunnistus.id)    

    res = E.response(E.nimi('%s %s' % (tunnistus.eesnimi, tunnistus.perenimi)),
                 E.tunnistus_nr(tunnistus.tunnistusenr),
                 E.kehtiv(tunnistus.staatus and '1' or '0'),
                 eksam_jada)
    data_dok = tunnistus.filedata
    filename = tunnistus.filename
    if data_dok:
        att = attachment.Attachment(data_dok, use_gzip=False)
        att.filename = filename
        content_id = att.gen_content_id()
        attachments = [att]
        res.append(E.tunnistus('', href='cid:%s' % content_id, filename=filename))

    return res, attachments, None

def _get_eksam_jada(tunnistus):
    q = model.Session.query(model.Sooritaja, model.Test).\
        join(model.Sooritaja.test).\
        join(model.Sooritaja.testitunnistused).\
        filter(model.Testitunnistus.tunnistus_id==tunnistus.id).\
        order_by(model.Sooritaja.id)
    jada = E.eksam_jada()
    for rcd in q.all():
        sooritaja, test = rcd
        if len(sooritaja.sooritused):
            sooritus1 = sooritaja.sooritused[0]
            kpv = sooritus1.algus
        else:
            kpv = None        

        staatus = _conv_staatus(sooritaja)

        item = E.item(E.nimetus(test.aine_nimi),
                      E.aeg(kpv and kpv.strftime('%d.%m.%Y') or ''),
                      E.staatus(staatus)
                      )
        if sooritaja.hindamine_staatus == const.H_STAATUS_HINNATUD:
            item.append(E.tulemus(h.fstr(sooritaja.pallid)))
        item.append(E.id(str(test.id)))
        jada.append(item)
    return jada

def _conv_staatus(sooritaja):
    # staatus:
    # 1 - Tulemus teada
    # 2 - Puudus eksamilt
    # 3 - Tulemus tühistatud
    # 4 - Tulemus ei ole teada
    if sooritaja.staatus == const.S_STAATUS_EEMALDATUD:
        staatus = '3' # tulemus tühistatud
    elif sooritaja.staatus != const.S_STAATUS_TEHTUD:
        staatus = '2' # puudus eksamilt
    else:
        if sooritaja.hindamine_staatus == const.H_STAATUS_HINNATUD:
            staatus = '1' # tulemus teada
        else:
            staatus = '4' # tulemus ei ole teada
    return staatus

