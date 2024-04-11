from datetime import datetime, date
import logging
import eis.model as model
import eis.model_log as model_log
import eiscore.const as const
from eis.recordwrapper import RecordWrapper
from eiscore.examwrapper import MemYlesandevastus, MemKV, MemKS
from eis.lib.apiclient import APIClient

log = logging.getLogger(__name__)

class ExamClient(APIClient):
    apikey = 'eisexam'
    
    def __init__(self, handler, host):
        self.handler = handler
        request = handler.request
        self.host = host

        userid = handler.c.user.isikukood
        if userid == const.USER_NOT_AUTHENTICATED:
            # Value for header must be of type str or bytes
            userid = str(userid)
        self.userid = userid

    def _get_headers(self):
        c = self.handler.c
        headers = {'eis-user': self.userid,
                   'eis-locale': self.handler.request.locale_name,
                   }
        return headers
        
    def create_tempvastus(self, ylesanne_id):
        data = {'ylesanne_id': ylesanne_id,
                }
        url = f'/tempvastus'
        res = self.apicall(url, data, 201)
        return res['ylesandevastus_id']
    
    def create_tempsooritaja(self, test_id, testiosa_id, komplekt_id, komplektivalik_id, kasutaja_id):
        data = {'kasutaja_id': kasutaja_id,
                'komplekt_id': komplekt_id,
                'komplektivalik_id': komplektivalik_id,
                }
        url = f'/tempsooritaja/{test_id}/{testiosa_id}'
        res = self.apicall(url, data, 201)
        return res['sooritus_id']

    def create_sooritaja(self, sooritus, sooritaja, erikomplektid):
        def _create_sooritus(tor):
            r = tor.pack_row()
            li2 = []
            for atos in tor.alatestisooritused:
                ek_lisaaeg = erikomplektid.get(atos.alatest_id)
                if ek_lisaaeg and ek_lisaaeg > (atos.lisaaeg or 0):
                    atos.lisaaeg = ek_lisaaaeg
                    
                li2.append({'id': atos.id,
                            'sooritus_id': tor.id,
                            'alatest_id': atos.alatest_id,
                            'staatus': atos.staatus,
                            'lisaaeg': atos.lisaaeg})
            r['alatestisooritused'] = li2

            li3 = []
            q = (model.Session.query(model.Soorituskomplekt)
                 .filter_by(sooritus_id=tor.id))
            for sk in q.all():
                li3.append({'id': sk.id,
                           'sooritus_id': sk.sooritus_id,
                           'komplektivalik_id': sk.komplektivalik_id,
                           'komplekt_id': sk.komplekt_id,
                           })
            r['soorituskomplektid'] = li3

            li4 = []
            q = (model.Session.query(model.Ylesandevastus)
                 .filter_by(sooritus_id=tor.id))
            for yv in q.all():
                yvr = {'id': yv.id,
                      'sooritus_id': yv.sooritus_id,
                      'valitudylesanne_id': yv.valitudylesanne_id,
                      'testiylesanne_id': yv.testiylesanne_id,
                      'loplik': yv.loplik,
                      'staatus': yv.staatus,
                      'max_pallid': yv.max_pallid,
                      'muudetav': yv.muudetav,
                      'kehtiv': yv.kehtiv,
                      'vastuseta': yv.vastuseta,
                      }
                yvr['kysimusevastused'] = []
                for kv in yv.kysimusevastused:
                    kvr = kv.pack_row()
                    kvr['kvsisud'] = [ks.pack_row(False) for ks in kv.kvsisud]
                    yvr['kysimusevastused'].append(kvr)
                li4.append(yvr)
            r['ylesandevastused'] = li4
            return r
        
        data = {'id': sooritaja.id,
                'test_id': sooritaja.test_id,
                'testimiskord_id': sooritaja.testimiskord_id,
                'staatus': sooritaja.staatus,
                'kasutaja_id': sooritaja.kasutaja_id,
                'lang': sooritaja.lang,
                'regviis_kood': sooritaja.regviis_kood,
                'valimis': sooritaja.valimis,
                'sooritus': _create_sooritus(sooritus),
                }
        url = f'/sooritajad'
        return self.apicall(url, data, 201)

    def delete_test(self, test_id, testimiskord_id=0):
        url = f'/test/{test_id}/testimiskord/{testimiskord_id}/delete'
        res = self.apicall(url, None, post=True)
        return res['rc']
    
    def delete_sooritaja(self, sooritaja_id):
        url = f'/sooritaja/{sooritaja_id}/delete'
        res = self.apicall(url, None, post=True)
        return res['rc']
    
    def teisaldatud_sooritus(self, sooritus_id):
        url = f'/sooritus/{sooritus_id}/teisaldatud'
        res = self.apicall(url, None, post=True)
        return res['rc']
    
    def delete_ylesandevastus(self, sooritus_id, ylesandevastus_id):
        "Jagatud töös ülesandevastuse kustutamine"
        url = f'/sooritus/{sooritus_id}/ylesandevastus/{ylesandevastus_id}/delete'
        res = self.apicall(url, None, post=True)
        return res['rc']
    
    def set_sooritus_p(self, tos):
        "Peale hindamist punktide salvestamine klastris"
        li = []
        for yv in tos.ylesandevastused:
            li_kv = []
            for kv in yv.kysimusevastused:
                li_ks = []
                for ks in kv.kvsisud:
                    r2 = {'id': ks.id,
                          'toorpunktid': ks.toorpunktid,
                          }
                    li_ks.append(r2)
                r1 = {'id': kv.id,
                      'pallid': kv.pallid,
                      'toorpunktid': kv.toorpunktid,
                      'vastuseta': kv.vastuseta,
                      'kvsisud': li_ks,
                      }
                li_kv.append(r1)
            r = {'id': yv.id,
                 'vastuseta': yv.vastuseta,
                 'mittekasitsi': yv.mittekasitsi,
                 'pallid': yv.pallid,
                 'toorpunktid': yv.toorpunktid,
                 'kysimusevastused': li_kv,
                 'loendurid': yv.loendurid,
                 }
            li.append(r)
        data = {'sooritus':
                {'id': tos.id,
                 'ylesandevastused': li
                 }
                }
        sooritus_id = tos.id
        url = f'/sooritus/{sooritus_id}/pallid'
        res = self.apicall(url, data, 200)
        return res['rc'] == 'ok'
   
    def get_sooritus(self, sooritus_id, hiljem):
        "Soorituskirjete tõmbamine keskserverisse peale testi sooritamist"
        url = f'/sooritus/{sooritus_id}'
        res = self.apicall(url, {'hiljem': hiljem}, 200, post=False)
        error = res.get('error')
        if error:
            return error, None
        return None, res['sooritus']
                    
    def refresh_sooritused(self, testikoht_id, testiruum_id):
        url = f'/sooritused/{testikoht_id}/{testiruum_id}'
        res = self.apicall(url, None, 200)
        for r in res.get('sooritused'):
            sooritus_id = r.get('id')
            tos = model.Sooritus.get(sooritus_id)
            if tos:
                tos.update(**r)

    def add_seblog(self, sooritus_id, remote_addr, namespace):
        "SEB konfi väljastamine sooritajale"
        url = f'/sooritus/{sooritus_id}/seblog'
        data = {'remote_addr': remote_addr,
                'namespace': namespace }
        res = self.apicall(url, data)
        return res

    def get_seblog(self, sooritus_id, sooritaja_id, url_key):
        "SEB konfi väljastamine sooritajale"
        url = f'/sooritus/{sooritus_id}/seblog'
        data = {'sooritaja_id': sooritaja_id,
                'url_key': url_key}
        res = self.apicall(url, data, post=False)
        return res

    def set_staatus(self, testiruum_id, sooritused_id, staatus, stpohjus, testiosa, alatestid, kirjalik, jatk_voimalik):
        "Soorituse olek muudetakse klastris ja seejärel värskendatakse keskserveris"
        url = f'/sooritused/testiruum/{testiruum_id}/staatus'
        data = {'sooritused_id': sooritused_id,
                'staatus': staatus,
                'stpohjus': stpohjus,
                'yhesuunaline': testiosa.yhesuunaline,
                'alatestid': alatestid,
                'kirjalik': kirjalik,
                'jatk_voimalik': jatk_voimalik,
                }
        res = self.apicall(url, data)
        return res.get('sooritused')

    def set_lisaaeg(self, sooritus_id, lisaaeg, atsid):
        url = f'/sooritus/{sooritus_id}/lisaaeg'
        data = {'lisaaeg': lisaaeg,
                'alatestisooritused': atsid,
                }
        res = self.apicall(url, data)
        r = res.get('sooritus')
        if r:
            sooritus_id = r.get('id')
            tos = model.Sooritus.get(sooritus_id)
            if tos:
                tos.update(**r)

    def set_lang(self, sooritus_id, lang):
        url = f'/sooritus/{sooritus_id}/lang'
        data = {'lang': lang,
                }
        res = self.apicall(url, data)
        return res.get('rc')

    def give_komplekt(self, sooritus_id, kv_id, valitav, komplektid_id):
        "Leitakse sooritaja komplekti ID, vajadusel määratakse"
        if not kv_id:
            raise Exception('kv_id puudub')
        url = f'/sooritus/{sooritus_id}/kv/{kv_id}'
        data = {'valitav': valitav,
                'komplektid_id': komplektid_id}
        res = self.apicall(url, data)
        return res['komplekt_id']

    def testiylesanded(self, sooritus_id, alatest_id, testiylesanded, yl_segamini, read_only):
        "Leitakse kuvatavad ülesanded õiges järjekorras"
        url = f'/sooritus/{sooritus_id}/testiylesanded'
        data = {'alatest_id': alatest_id,
                'testiylesanded': testiylesanded,
                'yl_segamini': yl_segamini,
                'read_only': read_only}
        res = self.apicall(url, data)
        error = res.get('error')        
        if error:
            return error, None, None, None, []
        else:
            li_yv = RecordWrapper.create_from_dict(res['ylesandevastused'])        
            return None, res['segatud_id'], res['viimane_ty_id'], res['viimane_vy_id'], li_yv

    def edit(self, sooritus_id, data):
        url = f'/sooritus/{sooritus_id}/edit'
        return self.apicall(url, data)
        
    def update(self, sooritus_id, data):
        url = f'/sooritus/{sooritus_id}'
        return self.apicall(url, data)

    def alatest_staatus(self, sooritus_id, alatest_id):
        "Alatesti sooritamise staatus"
        url = f'/sooritus/{sooritus_id}/alatest/{alatest_id}/staatus'
        res = self.apicall(url, None)
        return res['staatus']
    
    def showtask(self, sooritus_id, ty_id, kv_id):
        kv_id = kv_id or 0
        url = f'/sooritus/{sooritus_id}/ty/{ty_id}/kv/{kv_id}'
        return self.apicall(url, None)
        
    def edittask(self, sooritus_id, ty_id, vy_id, kv_id, vyy, alatest_id):
        url = f'/sooritus/{sooritus_id}/ty/{ty_id}/edittask'
        data = {'kv_id': kv_id,
                'vyy': vyy,
                'vy_id': vy_id,
                'alatest_id': alatest_id}
        return self.apicall(url, data)

    # get_tempvastus
    def edittask_temp(self, yv_id):
        "Testita lahendamine"
        url = f'/tempvastus/{yv_id}'
        return self.apicall(url, None)

    def edit_toovastus(self, sooritus_id, ty_id, vy_id):
        "Luuakse jagatud töö ylesandevastus või leitakse olemasolev muudetav kirje"
        data = {'sooritus_id': sooritus_id,
                'testiylesanne_id': ty_id,
                'valitudylesanne_id': vy_id,
                }
        url = f'/toovastus'
        res = self.apicall(url, data, 201)
        return res
    
    def get_toovastus(self, yv_id):
        "Jagatud töö ülesande lahendamine"
        url = f'/toovastus/{yv_id}'
        return self.apicall(url, None)

    def pooleli_toovastused(self, sooritus_id):
        "Leiame ülesanded, mida sooritaja on alustanud"
        url = f'/toovastused/{sooritus_id}/pooleli'
        res = self.apicall(url, None)
        return res['testiylesanded_id']

    def updatetask(self, sooritus_id, ty_id, vy_id, data):
        url = f'/sooritus/{sooritus_id}/ty/{ty_id}/vy/{vy_id}/updatetask'
        #url = f'/updatetask'
        res = self.apicall(url, data)
        clsmap = {'ylesandevastus': MemYlesandevastus,
                  'kysimusevastused': MemKV,
                  'kvsisud': MemKS,
                  }
        error = res.get('error')
        return RecordWrapper.create_from_dict(res, clsmap), error
    
    def update_ks(self, ks):
        url = f'/update_ks/{ks.id}'
        data = {'kvsisu': ks}
        return self.apicall(url, data)
    
    def diagnose(self, sooritus_id, vy_id, normipunktid, grupid, task_map):
        "Tehtud gruppide ülesandevastused d-testis"
        url = f'/sooritus/{sooritus_id}/diagnose/{vy_id}'
        params = {'normipunktid': normipunktid,
                  'grupid': grupid,
                  'task_map': task_map or None}
        res = self.apicall(url, params)
        rec = RecordWrapper.create_from_dict(res)
        return rec.npvastused
    
    def max_pooleli(self, toimumisaeg_id, valimis):
        "Viimane aeg, millal toimumisajal sooritati mõnd praegu pooleliolevat sooritust"
        if valimis is None:
            valimis = 'N'
        elif valimis:
            valimis = 'T'
        else:
            valimis = 'F'
        url = f'/max_pooleli/{toimumisaeg_id}/{valimis}'
        res = self.apicall(url, None)
        rec = RecordWrapper.create_from_dict(res)
        return rec.aeg
    
    def _decode_response(self, response):
        # teisendame kellaaja iso tekstist tagasi datetime-ks
        class Decoder:
            def decode(self, value):
                if isinstance(value, dict):
                    res = {}
                    for k, v in value.items():
                        if isinstance(v, str):
                            v = self._decode_str(k, v)
                        else:
                            v = self.decode(v)
                        res[k] = v
                    return res
                elif isinstance(value, list):
                    return [self.decode(v) for v in value]
                else:
                    return value

            def _decode_str(self, k, v):
                if k in ('algus','kavaaeg', 'seansi_algus', 'viimane_algus', 'lopp', 'aeg'):
                    try:
                        v = datetime.fromisoformat(v)
                    except ValueError:
                        pass
                return v

        return Decoder().decode(response.json())
