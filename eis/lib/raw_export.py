"EISi andmemudeli formaadis eksportimine"
from datetime import datetime
import pickle

import eis
from eis.lib.base import *
from eis.lib.qti import * 
from eis.lib.block import BlockController

log = logging.getLogger(__name__)
_debug = False

def export(item, debug=False):
    global _debug
    _debug = debug
    li = add_to_export(None, item)
    return export_dump(li)

def export_meta():
    meta = {'class':'meta',
            'seisuga':datetime.now(), 
            'version': eis.__version__,
            }
    return [meta]

def add_to_export(li, item):
    if not li:
        li = export_meta()
    li = li + item.pack(False, None)
    if isinstance(item, model.Ylesanne):
        for rcd in item.ylesandeisikud:
            li += rcd.pack_exp()
    elif isinstance(item, model.Test):
        li += pack_test(item)
    elif isinstance(item, model.Rveksam):
        li += pack_rveksam(item)

    return li

def export_klread(kl):
    # klassifikaatori ridade eksport
    li = export_meta()
    li += kl.pack(False, None)
    now = datetime.now()
    for k in kl.read:
        if k.kehtib and \
           (not k.alates or k.alates <= now) and \
           (not k.kuni or k.kuni >= now):
            extra = {}
            ylem = k.ylem
            if ylem:
                extra['_ylem_kood'] = ylem.kood
            li += k.pack(False, None, ignore_keys=['ylem_id'], extra=extra)
            for r in k.trans:
                li += r.pack(False, None)
    return export_dump(li)

def export_dump(li):
    data = pickle.dumps(li)
    return data

def pack_test(test):
    li = []
    for r in test.testikursused:
        li += r.pack(False, None)
    for r in test.testitasemed:
        li += r.pack(False, None)
    for r in test.testihinded:
        li += r.pack(False, None)
    for osa in test.testiosad:
        li += pack_testiosa(osa)
    r = test.testitagasiside
    if r:
        li += r.pack(False, None)
    for r in test.tagasisidevormid:
        li += r.pack(False, None)
        for r2 in r.alamosad:
            li += r2.pack(False, None)
    for r in test.tagasisidefailid:
        li += r.pack(False, None)
    return li

def pack_testiosa(osa):
    # ylesannete ID, mis on juba pakitud (et korduvalt testis kasutatud ylesannet ei peaks korduvalt pakkima)
    packed_y_id = []
    
    trace(' testiosa %s' % osa.id)
    li = osa.pack(False, None)
    # komplektivalikud pakkida enne alateste
    for kvalik in osa.komplektivalikud:
        li += kvalik.pack(False, None)
    for sk in osa.sisestuskogumid:
        li += sk.pack(False, None)
    for hk in osa.hindamiskogumid:
        li += hk.pack(False, None)
        for rcd2 in hk.hindamiskriteeriumid:
            li += rcd2.pack(False, None)
    for r in osa.alatestigrupid:
        li += r.pack(False, None)
    for rcd in osa.alatestid:
        li += rcd.pack(False, None)
        for rcd2 in rcd.testiplokid:
            li += rcd2.pack(False, None)
    for rcd2 in osa.testiylesanded:
        li += rcd2.pack(False, None)
        
    for kvalik in osa.komplektivalikud:
        for k in kvalik.komplektid:
            trace(' komplekt %s' % k.id)
            li += k.pack(False, None)
            for vy in k.valitudylesanded:
                ylesanne = vy.ylesanne
                if ylesanne and ylesanne.id not in packed_y_id:
                    packed_y_id.append(ylesanne.id)
                    trace(' ülesanne %s' % ylesanne.id)
                    li += ylesanne.pack(False, None)
                li += vy.pack(False, None)

    for r in osa.ylesandegrupid:
        li += r.pack(False, None)
        for r2 in r.grupiylesanded:
            li += r2.pack(False, None)
    for r in osa.nsgrupid:
        li += r.pack(False, None)
    for np in osa.normipunktid:
        li += np.pack(False, None)
        for pr in np.normiprotsentiilid:
            li += pr.pack(False, None)
        for ns in np.nptagasisided:
            li += ns.pack(False, None)
    return li

def pack_rveksam(rveksam):
    li = []
    for r in rveksam.rvosaoskused:
        li += r.pack(False, None)
        for osa in r.rvosatulemused:
            li += osa.pack(False, None)
    for r in rveksam.rveksamitulemused:
        li += r.pack(False, None)
    return li

def trace(buf):
    if _debug:
        print(buf)
