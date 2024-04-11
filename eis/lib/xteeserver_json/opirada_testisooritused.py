"Testitulemuste väljastamine personaalsete õpiradade analüüsimiseks ES-3132"

import eis.model as model
import eiscore.const as const
from eis.model_log import Logi_adapter
from .xroadserverjson import serve_json, jsondate
import logging
log = logging.getLogger(__name__)

def testisooritused(request):
    "JSON teenuse osutamine"
    return serve_json(request, 'opirada/testisooritused', _args, _query)
    
def _args(request):
    "Teenuse osutamine"
    params = request.params
    try:
        test_id = int(params['test_id'])
        isikukoodid = params.getall('isikukood')
        assert len(isikukoodid) > 0, 'isikukoodid puuduvad'
    except Exception as ex:
        log.error('params='+str(params))
        log.error(str(ex))
        raise
    return test_id, isikukoodid

def _query(args):
    "Teenuse sisuline töö"
    test_id, isikukoodid = args
    testisooritused = []
    q = (model.Session.query(model.Sooritaja,
                             model.Kasutaja.isikukood)
         .filter(model.Sooritaja.test_id==test_id)
         .join(model.Sooritaja.kasutaja)
         .filter(model.Kasutaja.isikukood.in_(isikukoodid))
         .filter(model.Sooritaja.staatus>=const.S_STAATUS_REGATUD)
         .order_by(model.Sooritaja.id)
         )
    for sooritaja, isikukood in q.all():
        testiosasooritused = []
        for tos in sooritaja.sooritused:
            ylesandevastused = []
            for yv in tos.ylesandevastused:
                item3 = {'valitudylesanne_id': yv.valitudylesanne_id,
                         'testiylesanne_id': yv.testiylesanne_id,
                         'toorpunktid': yv.toorpunktid,
                         'pallid': yv.pallid,
                         'pallid_arvuti': yv.pallid_arvuti,
                         'pallid_kasitsi': yv.pallid_kasitsi,
                         'max_pallid': yv.max_pallid,
                         }
                ylesandevastused.append(item3)
            item2 = {'sooritus_id': tos.id,
                     'testiosa_id': tos.testiosa_id,
                     'staatus': tos.staatus,
                     'hindamine_staatus': tos.hindamine_staatus,
                     'algus': jsondate(tos.algus),
                     'lopp': jsondate(tos.lopp),
                     'ajakulu': tos.ajakulu,
                     'pallid': tos.pallid,
                     'pallid_arvuti': tos.pallid_arvuti,
                     'pallid_kasitsi': tos.pallid_kasitsi,
                     'max_pallid': tos.max_pallid,
                     'ylesandesooritused': ylesandevastused,
                     }
            testiosasooritused.append(item2)
        item = {'sooritaja_id': sooritaja.id,
                'isikukood': isikukood,
                'staatus': sooritaja.staatus,
                'hindamine_staatus': sooritaja.hindamine_staatus,                
                'pallid': sooritaja.pallid,
                'testiosasooritused': testiosasooritused,
                }
        testisooritused.append(item)
    return {'testisooritused': testisooritused}
