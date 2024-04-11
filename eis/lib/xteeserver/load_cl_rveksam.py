# -*- coding: utf-8 -*- 
"""
Abiteenus EISis kasutatava rahvusvaheliselt tunnustatud eksamite klassifikaatori allalaadimiseks.

Klassifikaatori rida väljastatakse elemendina <item>. Elemendi väärtuseks on eksami nimetus. Elemendil on atribuudud:
-	aine – õppeaine kood
-	keeletase – eksami tase (võib puududa)
-	max_tulemus – maksimaalne võimalik arvuline tulemus (punktid või protsendid, võib puududa)
-	value – klassifikaatori kood.
Kui sama klassifikaatoririda on kasutusel mitmes rahvusvahelises eksamis, mille õppeaine, keeleoskuse tase või maksimaalne tulemus on erinevad, siis väljastab teenus iga võimaliku kombinatsiooni eraldi real (st klassifikaatori kood ei ole tulemuste seas unikaalne).
"""
from eis.lib.pyxadapterlib.xutils import *
import eis.model as model
import eiscore.const as const
from eis.lib.xtee.xroad import test_me, fstr
import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):
    error = teade = None
    res = E.response(_get_cl(E.cl_rveksam(), 'RVEKSAM'))
    return res, []
    
def _get_cl(node, klassifikaator_kood):
    q = (model.Klrida.query
         .filter_by(klassifikaator_kood=klassifikaator_kood)
         .order_by(model.Klrida.jrk, model.Klrida.nimi)
         )
    for r in q.all():
        qe = (model.Session.query(model.Rveksam.aine_kood,
                                  model.Rveksam.keeletase_kood,
                                  model.Rveksam.kuni)
              .distinct()
              .filter_by(rveksam_kood=r.kood)
              )
        for aine, tase, kuni in qe.all():
            kw = {'value': r.kood}
            kw['aine'] = aine
            if tase:
                kw['keeletase'] = tase
            if kuni:
                kw['max_tulemus'] = fstr(kuni)
            item = E.item(r.nimi, **kw)
            node.append(item)
    return node

if __name__ == '__main__':
    from eis.scripts.scriptuser import *
    paring = E.request()
    test_me(serve, 'load_cl_rveksam.v1', paring, named_args)
