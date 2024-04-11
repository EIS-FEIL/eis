"""
Abiteenus EISis kasutatava õppeainete klassifikaatori allalaadimiseks.

Klassifikaatori rida väljastatakse elemendina <item>. Elemendi väärtus on õppeaine nimetus. Elemendil on järgmised atribuudid:
-	riigieksam – 1 või 0 vastavalt sellele, kas on riigieksami aine või mitte
-	kehtetu – 1, kui õppeaine ei ole enam kasutusel
-	value – õppeaine klassifikaatori kood

"""
from eis.lib.pyxadapterlib.xutils import *
import eis.model as model
import eiscore.const as const
from eis.lib.xtee.xroad import test_me
import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):
    error = teade = None
    if not header.client:
        # vana X-tee
        version = header.service.rsplit('.', 1)[-1]
    else:
        version = header.service.serviceVersion
    kuva_riigieksam = version == 'v2'
    res = E.response(_get_cl(E.cl_aine(), 'AINE', kuva_riigieksam))
    return res, []
    
def _get_cl(node, klassifikaator_kood, kuva_riigieksam):
    q = (model.Session.query(model.Test.aine_kood)
         .distinct()
         .filter(model.Test.testiliik_kood==const.TESTILIIK_RIIGIEKSAM)
         .filter(model.Test.staatus >= const.T_STAATUS_KINNITATUD)
         )
    riigieksami_ained = [r[0] for r in q.all()]
    q = (model.Klrida.query
         .filter_by(klassifikaator_kood=klassifikaator_kood)
         .order_by(model.Klrida.jrk, model.Klrida.nimi)
         )
    for r in q.all():
        kw = {'value': r.kood}
        if kuva_riigieksam:
            riigieksam = r.kood in riigieksami_ained and '1' or '0'
            kw['riigieksam'] = riigieksam
            if not r.kehtib:
                kw['kehtetu'] = '1'
        item = E.item(r.nimi, **kw)
        node.append(item)
    return node

if __name__ == '__main__':
    from eis.scripts.scriptuser import *
    paring = E.request()
    test_me(serve, 'load_cl_aine.v1', paring, named_args)
    test_me(serve, 'load_cl_aine.v2', paring, named_args)    
