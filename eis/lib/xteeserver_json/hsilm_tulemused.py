"""Testitulemuste väljastamine Haridussilmale statistikaks ES-3913.
Teenus väljastab sisendis antud aasta ja testiliigi sooritajate tulemused
(tehtud, hinnatud, tulemused kinnitatud, koondtulemused avaldatud),
mille põhjal Haridussilm saab koostada statistika.
"""

from datetime import date, datetime
import eis.model as model
import eiscore.const as const
from eis.model_log import Logi_adapter
from eis.lib.xteeserver_json.xroadserverjson import serve_json, jsondate, BadParameter
import logging
log = logging.getLogger(__name__)

def tulemused(request):
    "JSON teenuse osutamine"
    return serve_json(request, 'hsilm/tulemused', _args, _query)
    
def _args(request):
    "Teenuse osutamine"
    params = request.params
    try:
        name = 'aasta'
        aasta = int(params['aasta'])

        name = 'testiliik'
        testiliik = params['testiliik']
        assert testiliik in (const.TESTILIIK_TASEMETOO,
                             const.TESTILIIK_RIIGIEKSAM,
                             const.TESTILIIK_RV,
                             const.TESTILIIK_POHIKOOL), f'vale testiliik {testiliik}'

        name = 'alates'
        alates = params.get('alates')
        if alates:
            alates = datetime.fromisoformat(alates)

        name = 'min_sooritaja_id'
        min_sooritaja_id = params.get('min_sooritaja_id')
        if min_sooritaja_id:
            min_sooritaja_id = int(min_sooritaja_id)

        name = 'max_arv'
        max_arv = params.get('max_arv')
        if max_arv:
            max_arv = int(max_arv)
    except Exception as ex:
        log.error(ex)
        raise BadParameter(name, str(ex))
        
    return aasta, testiliik, alates, min_sooritaja_id, max_arv

def _query(args):
    "Teenuse sisuline töö"
    aeg = datetime.now()
    aasta, testiliik, alates, min_sooritaja_id, max_arv = args
    testisooritused = []
    q = (model.Session.query(model.Test.nimi,
                             model.Test.id,
                             model.Test.aine_kood,
                             model.Test.max_pallid,
                             model.Sooritaja,
                             model.Koht.kool_id,
                             model.Koolinimi.nimi,
                             model.Kasutaja.id,
                             model.Kasutaja.isikukood,
                             model.Kasutaja.synnikpv,
                             model.Kasutaja.sugu,
                             model.Testimiskord.alatestitulemused_avaldet,
                             model.Testimiskord.ylesandetulemused_avaldet,
                             model.Testimiskord.tahis,
                             model.Testimiskord.valim_testimiskord_id,
                             model.Testimiskord.sisaldab_valimit,
                             model.Testimiskord.stat_valim)
         .join((model.Sooritaja,
                model.Sooritaja.test_id==model.Test.id))
         .join((model.Testimiskord,
                model.Testimiskord.id==model.Sooritaja.testimiskord_id))
         .outerjoin((model.Koht,
                     model.Koht.id==model.Sooritaja.kool_koht_id))
         .outerjoin((model.Koolinimi,
                     model.Koolinimi.id==model.Sooritaja.koolinimi_id))
         .join(model.Sooritaja.kasutaja)
         .filter(model.Test.id==model.Testimiskord.test_id)
         .filter(model.Test.testiliik_kood==testiliik)
         .filter(model.Testimiskord.aasta==aasta)
         .filter(model.Testimiskord.koondtulemus_avaldet==True)
         .filter(model.Testimiskord.tulemus_kinnitatud==True)
         .filter(model.Testimiskord.statistika_ekk_kpv!=None)
         .filter(model.Sooritaja.staatus>=const.S_STAATUS_TEHTUD)
         .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)
         )
    if alates:
        q = q.filter(model.Sooritaja.tulemus_aeg>=alates)
    if min_sooritaja_id:
        q = q.filter(model.Sooritaja.id >= min_sooritaja_id)
    q = q.order_by(model.Sooritaja.id)

    cnt = 0
    items = []
    jargmine_id = None
    for r in q.all():
        (t_nimi, t_id, aine, max_p, sooritaja, kool_id, k_nimi, k_id, ik, synnikpv, sugu, a_avaldet, y_avaldet,
         tk_tahis, v_tk_id, sisaldab_valimit, stat_valim) = r
        cnt += 1
        if max_arv and cnt > max_arv:
            # mas kirjete arv on täis
            jargmine_id = sooritaja.id
            break
        
        sooritused = list(sooritaja.sooritused)

        # viimase testiosa kuupäev
        lopp = None
        for tos in sooritaja.sooritused:
            kpv = tos.algus or tos.kavaaeg
            if kpv and (not lopp or lopp < kpv):
                lopp = kpv
        kpv = lopp and lopp.date().isoformat() or None
        synnikpv = synnikpv and synnikpv.isoformat() or None
        tulemus_aeg = sooritaja.tulemus_aeg and sooritaja.tulemus_aeg.isoformat() or None
        # valimis - kogu testimiskord on valim või sisaldab valimit ja sooritaja on valimis
        valimis = v_tk_id or sisaldab_valimit and sooritaja.valimis or False
        item = {'test_nimi': t_nimi,
                'test_id': t_id,
                'aine': aine,
                'max_pallid': max_p,
                'tk_id': sooritaja.testimiskord_id,
                'algne_tk_id': v_tk_id,
                'stat_valim': stat_valim,
                'valimis': valimis,
                'kool_id': kool_id,
                'klass': sooritaja.klass,
                'oppekava': sooritaja.oppekava_kood,
                'oppevorm': sooritaja.oppevorm_kood,
                'oppekeel': sooritaja.oppekeel,
                'maakond_kood': sooritaja.kool_aadress_kood1,
                'kov_kood': sooritaja.kool_aadress_kood2,
                'tulemus_aeg': tulemus_aeg,
                'sooritaja_id': sooritaja.id,
                'staatus': sooritaja.staatus,
                'kasutaja_id': k_id,
                'synnikpv': synnikpv,
                'sugu': sugu,
                'lang': sooritaja.lang,
                'kuupaev': kpv,
                }
        if sooritaja.kursus_kood:
            item['kursus'] = sooritaja.kursus_kood
        if ik:
            item['isikukood'] = ik
        if sooritaja.pallid is not None:
            item['pallid'] = sooritaja.pallid
            item['tulemus_protsent'] = sooritaja.tulemus_protsent
        if sooritaja.keeletase_kood:
            item['keeletase'] = sooritaja.keeletase_kood
                
        # tagasiside tunnused
        if testiliik == const.TESTILIIK_TASEMETOO:
            # tagasiside tunnused
            item['tunnused'] = _get_npvastused(sooritaja.id)

        osaoskused = []
        if testiliik in (const.TESTILIIK_TASEMETOO,
                         const.TESTILIIK_POHIKOOL):
            for tos in sooritused:
                tos_a = []
                for atos in tos.alatestisooritused:
                    tos_a.append(_get_osaoskus(tos, atos, testiliik, a_avaldet, y_avaldet))
                if not tos_a:
                    # alatestideta testiosa
                    tos_a.append(_get_osaoskus(tos, None, testiliik, a_avaldet, y_avaldet))
                osaoskused.extend(tos_a)
                
        if testiliik == const.TESTILIIK_POHIKOOL or len(osaoskused) > 1:
            item['osaoskused'] = osaoskused
        items.append(item)
        
    res = {'tulemused': items,
           'aeg': aeg.isoformat(),
           }
    if jargmine_id:
        res['jargmine_sooritaja_id'] = jargmine_id
    return res

def _get_npvastused(sooritaja_id):
    "Tagasiside tunnuste vastused (tasemetöö korral)"
    qn = (model.Session.query(model.Normipunkt.kood,
                              model.Normipunkt.nimi,
                              model.Nptagasiside.stat_tagasiside)
          .join((model.Npvastus,
                 model.Normipunkt.id==model.Npvastus.normipunkt_id))
          .join((model.Nptagasiside,
                 model.Nptagasiside.id==model.Npvastus.nptagasiside_id))
          .join((model.Sooritus,
                 model.Sooritus.id==model.Npvastus.sooritus_id))
          .filter(model.Sooritus.sooritaja_id==sooritaja_id)
          .filter(model.Normipunkt.kood!=None)
          .filter(model.Nptagasiside.stat_tagasiside!=None)
          .order_by(model.Normipunkt.kood))
    npitems = []
    for (kood, nimi, txt) in qn.all():
        npitems.append({'kood': kood,
                        'nimi': nimi,
                        'tagasiside': txt,
                        })
    return npitems

def _get_atos_ylesandevastused(atos):
    q = (model.Session.query(model.Ylesandevastus)
         .filter(model.Ylesandevastus.sooritus_id==atos.sooritus_id)
         .join((model.Testiylesanne,
                model.Ylesandevastus.testiylesanne_id==model.Testiylesanne.id))
         .filter(model.Testiylesanne.alatest_id==atos.alatest_id)
         .order_by(model.Testiylesanne.seq))
    return [yv for yv in q.all()]

def _get_osaoskus(tos, atos, testiliik, a_avaldet, y_avaldet):
    "Alatestideta testiosa või alatesti soorituse andmed"
    item = {}
    if atos:
        item['nimi'] = atos.alatest.nimi
        if atos.pallid is not None and a_avaldet:
            item['pallid'] = atos.pallid
            item['tulemus_protsent'] = atos.tulemus_protsent
    else:
        item['nimi'] = tos.testiosa.nimi
        if tos.pallid is not None:
            item['pallid'] = tos.pallid
            item['tulemus_protsent'] = tos.tulemus_protsent

    if testiliik == const.TESTILIIK_POHIKOOL and y_avaldet:
        if atos:
            ylesandevastused = _get_atos_ylesandevastused(atos)
        else: 
            ylesandevastused = tos.ylesandevastused
        li = []
        for yv in ylesandevastused:
            ty = yv.testiylesanne
            if ty.liik == const.TY_LIIK_Y:
                yitem = {'tahis': ty.tahis,
                         'seq': ty.seq,
                         'pallid': yv.pallid,
                         'max_pallid': yv.max_pallid,
                         }
                li.append(yitem)
        item['ylesanded'] = li
    return item

if __name__ == '__main__':
    from eis.scripts.scriptuser import *
    aasta = int(named_args.get('aasta'))
    testiliik = named_args.get('testiliik')
    max_arv = named_args.get('max_arv') or None
    if max_arv:
        max_arv = int(max_arv)
    min_sooritaja_id = named_args.get('min_sooritaja_id')
    if min_sooritaja_id:
        min_sooritaja_id = int(min_sooritaja_id)
    alates = None
    args = aasta, testiliik, alates, min_sooritaja_id, max_arv
    dt = datetime.now()
    print(_query(args))
    diff = datetime.now() - dt
    print(diff.total_seconds())
