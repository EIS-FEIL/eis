"""
Teenus väljastab sisendis antud õppeaasta eksamite tulemuste vaiete loetelu.

Teenusel on versioonid 1 ja 2, mis erinevad väljundis kasutatud õppeainete klassifikaatori poolest. Versioonis 2 on kasutusel EISi õppeainete klassifikaator.  
Versioonis 1 on õppeainete kood ja nimetus kodeeritud samuti kui teenuse saisEksamid versioonis 1.
"""
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *
from eis import model
from eis.model import const
import eis.lib.helpers as h
#from eis.lib.xtee.xroad import fstr, test_me
from .saisEksamid import sais_aine, sais_keel

def serve(paring, header=None, attachments=[], context=None):
    error = None
    s_aasta = paring.find('aasta').text
    try:
        aasta = int(s_aasta)
    except:
        error = 'Palun esitada aastaarv'

    # teenuse v1 väljastab ainete koodid ja nimetused iidses SAISi liidese klassifikaatoris
    # teenuse v2 kasutab EISi oma klassifikaatorit
    version = header.service.serviceVersion
    use_sais_aine = version == 'v1'

    if not error:
        model.Paring_logi.log(header)
        jada = _search(aasta, use_sais_aine)

        if not len(jada):
            error = 'Vaideid ei leitud'
        else:
            #if handler and handler.is_rpc:
            #    jada = rpc_array(jada)

            buf = 'Aasta: %d' % aasta
            res = E.response(E.teade(buf),
                         jada)

    if error:
        res = E.response(E.teade(error))

    return res, []

def _search(aasta, use_sais_aine):
    q = model.Session.query(model.Sooritaja, model.Test, model.Vaie).\
        join(model.Vaie.sooritaja).\
        join(model.Sooritaja.test).\
        join(model.Sooritaja.testimiskord).\
        filter(model.Vaie.staatus != const.V_STAATUS_ESITAMATA).\
        filter(model.Testimiskord.aasta==aasta).\
        filter(model.Test.testiliik_kood==const.TESTILIIK_RIIGIEKSAM)

    # jätame välja need vaided, mille tulemus jääb alla mõne teise aasta sooritusele
    sa = model.sa
    Sooritaja2 = sa.orm.aliased(model.Sooritaja)
    Test2 = sa.orm.aliased(model.Test)
    Testimiskord2 = sa.orm.aliased(model.Testimiskord)
    q = q.filter(~ sa.exists().where(sa.and_(Sooritaja2.kasutaja_id==model.Sooritaja.kasutaja_id,
                                             Sooritaja2.test_id==Test2.id,
                                             Test2.testiliik_kood==const.TESTILIIK_RIIGIEKSAM,
                                             Test2.aine_kood==model.Test.aine_kood,
                                             Sooritaja2.lang==model.Sooritaja.lang,
                                             Testimiskord2.id==Sooritaja2.testimiskord_id,
                                             Testimiskord2.tulemus_kinnitatud==True,
                                             Testimiskord2.koondtulemus_avaldet==True,
                                             sa.or_(Sooritaja2.kursus_kood==model.Sooritaja.kursus_kood,
                                                    sa.and_(Sooritaja2.kursus_kood==None, model.Sooritaja.kursus_kood==None)),
                                             sa.or_(Sooritaja2.pallid>model.Sooritaja.pallid,
                                                    sa.and_(Sooritaja2.pallid==model.Sooritaja.pallid,
                                                            Sooritaja2.id>model.Sooritaja.id))
                                             )
                                     ))
    q = q.order_by(model.Vaie.id)

    li = E.sais_apellatsioonid_jada()
    for rcd in q.all():
        sooritaja, test, vaie = rcd
        tkord = sooritaja.testimiskord
        if len(sooritaja.sooritused):
            kpv = sooritaja.sooritused[0].algus
        else:
            kpv = None
        kasutaja = sooritaja.kasutaja

        if use_sais_aine:
            aine_kood, aine_nimi = sais_aine(test.aine_kood, kpv)
        else:
            aine_kood = test.aine_kood
            aine_nimi = test.aine_nimi
        keele_nimetus = sais_keel(sooritaja.lang)

        item = E.item()
        item.append(E.isikukood(kasutaja.isikukood))
        item.append(E.nimetus(aine_nimi))
        item.append(E.kood(aine_kood))

        if sooritaja.kursus_kood:
            item.append(E.kursus(sooritaja.kursus_kood))
        if sooritaja.keeletase_kood:
            item.append(E.keeletase(sooritaja.keeletase_kood))

        item.append(E.kuupaev(kpv and kpv.strftime('%d.%m.%Y') or ''))
        item.append(E.tulemus(h.fstr(sooritaja.pallid) or ''))
        item.append(E.keele_kood(sooritaja.lang or ''))
        item.append(E.keele_nimetus(keele_nimetus or ''))
        li.append(item)
    return li

if __name__ == '__main__':
    from eis.scripts.scriptuser import *

    # kasuta kujul: python saisEksamid.py -admin TEGIJAKOOD AASTA [-v4 true]
    aasta = noname_args[0]
    paring = E.request(E.aasta(aasta))
    test_me(serve, 'saisApellatsioonid.v1', paring, named_args)
    test_me(serve, 'saisApellatsioonid.v2', paring, named_args)    
