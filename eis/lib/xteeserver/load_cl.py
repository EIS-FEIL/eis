# -*- coding: utf-8 -*- 
"""
Klassifikaatorite laadimine eesti.ee portaali kasutajaliidesesse.

Klassifikaatori rida väljastatakse elemendina <item>, mille sisuks on klassifikaatorirea kood ja nimetus eraldatuna kooloniga. Lisaks on elemendi atribuudi „value“ väärtuseks klassifikaatorirea kood ning atribuudi „label“ väärtuseks nimetus.
"""
from eis.lib.pyxadapterlib.xutils import *
import eis.model as model
import eiscore.const as const
from eis.lib.xtee.xroad import test_me
import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):
    error = teade = None
    res = E.response(_get_cl(E.cl_tookoht(), 'TVALDKOND'),
                     _get_cl(E.cl_amet(), 'AMET'),
                     _get_cl(E.cl_haridus(), 'HARIDUS'),
                     #_get_cl(E.cl_kodak(), 'KODAKOND'),
                     )

    return res, []
    
def _get_cl(node, klassifikaator_kood):
    q = model.Klrida.get_q_by_kood(klassifikaator_kood)
    for r in q.order_by(model.Klrida.jrk, model.Klrida.nimi):
        k_kood = r[1]
        k_nimi = r[2]
        item = E.item('%s: %s' % (k_kood, k_nimi),
                      label=k_nimi,
                      value=k_kood)
        node.append(item)
    return node

if __name__ == '__main__':
    from eis.scripts.scriptuser import *
    paring = E.request()
    test_me(serve, 'load_cl.v1', paring, named_args)
