"""
Väljastatakse loetelu testsessioonidest, mille testidel päringu sooritaja on osalenud. 
Arvestatakse ainult kodakondsusseksamite, tasemeeksamite, põhikooli lõpueksamite, riigieksamite ja rahvusvaheliste eksamite testsessioone.
Mõeldud kasutamiseks riigiportaalist ja haridusportaalist.
"""
from eis.lib.pyxadapterlib.xutils import *
from eis import model
from eis.lib.xtee.xroad import get_ee_user_id, fstr, test_me
import eiscore.const as const


def serve(paring, header=None, attachments=[], context=None):
    error = None
    ik = get_ee_user_id(header)
    model.Paring_logi.log(header, paritav=ik)
    k = model.Kasutaja.get_by_ik(ik)

    li = []

    if not k:
        error = 'Pole andmeid isiku kohta'
    else:
        testiliigid = (const.TESTILIIK_POHIKOOL,
                       const.TESTILIIK_RIIGIEKSAM,
                       const.TESTILIIK_RV,
                       const.TESTILIIK_TASE,
                       const.TESTILIIK_SEADUS)
        q = (model.Testsessioon.query
             .filter(model.Testsessioon.testiliik_kood.in_(testiliigid))
             .filter(model.Testsessioon.testimiskorrad.any(
                 model.Testimiskord.sooritajad.any(
                     model.sa.and_(model.Sooritaja.kasutaja_id==k.id,
                                   model.Sooritaja.staatus>=const.S_STAATUS_TASUMATA)
                 )))
             )
        q = q.order_by(model.Testsessioon.seq)
        for rcd in q.all():
            item = E.item(E.nimi(str(rcd.nimi)), 
                          E.oppeaasta(str(rcd.oppeaasta)),
                          E.testsessioon_id(str(rcd.id)))
            li.append(item)
        if not len(li):
            error = 'Pole andmeid isiku registreerimistest testsessioonidele'

    if error:
        res = E.response(E.teade(error))
    else:
        buf = ''
        res = E.response(E.teade(buf))
        jada = E.testsessioonid_kod_jada()
        for item in li:
            jada.append(item)
        res.append(jada)

    return res, []

if __name__ == '__main__':
    from eis.scripts.scriptuser import *

    # kasuta kujul: python testid_kod.py -admin TEGIJAKOOD
    paring = E.request()
    test_me(serve, 'testsessioonid_kod.v1', paring, named_args)
