"""Rahvusvaheliste keeleeksamite tunnistuste esitajate arv ES-3913
Teenus väljastab sisendis antud aasta rahvusvahelise eksamit tunnistuse esitanute arvud
võõrkeele ja saadud keeletaseme lõikes.
"""

import eis.model as model
import eiscore.const as const
from eis.model_log import Logi_adapter
from eis.lib.xteeserver_json.xroadserverjson import serve_json, jsondate, BadParameter

def rvtunnistused(request):
    "JSON teenuse osutamine"
    return serve_json(request, 'hsilm/rvtunnistused', _args, _query)
    
def _args(request):
    "Teenuse osutamine"
    params = request.params
    aasta = int(params['aasta'])
    return aasta

def _query(args):
    "Teenuse sisuline töö"
    aasta = args

    # ained: I, P, S, V
    voorkeeled = (const.AINE_EN, const.AINE_FR, const.AINE_DE, const.AINE_RU)
    q = (model.Session.query(model.Rveksam.aine_kood,
                             model.Rvsooritaja.keeletase_kood,
                             model.sa.func.count(model.Rvsooritaja.id))
         .filter(model.Rvsooritaja.sooritaja_id==None)
         .join(model.Rvsooritaja.rveksam)
         .join(model.Rvsooritaja.tunnistus)
         .filter(model.Rveksam.aine_kood.in_(voorkeeled))
         .filter(model.Tunnistus.oppeaasta==aasta)
         .group_by(model.Rveksam.aine_kood,
                   model.Rvsooritaja.keeletase_kood)
         .order_by(model.Rveksam.aine_kood,
                   model.Rvsooritaja.keeletase_kood)
         )
    items = []
    for aine, keeletase, cnt in q.all():
        item = {'aine': aine,
                'keeletase': keeletase,
                'arv': cnt,
                }
        items.append(item)
        
    res = {'tunnistused': items}
    return res

if __name__ == '__main__':
    from eis.scripts.scriptuser import *
    aasta = int(named_args.get('aasta'))
    dt = datetime.now()
    print(_query(aasta))
    diff = datetime.now() - dt
    print(diff.total_seconds())
