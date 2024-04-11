from datetime import datetime, date
import logging
log = logging.getLogger(__name__)
import eis.model as model
import eis.model_log as model_log
import eiscore.const as const
from eiscore.examwrapper import MemKV, MemKS
from eis.recordwrapper import RecordWrapper, MemYlesanne, MemSisuplokk, MemSisuobjekt, MemKysimus, MemValik, MemTulemus, MemTest
from eis.lib.apiclient import APIClient

class TestClient(APIClient):
    apikey = 'eistest'

    def _get_headers(self):
        c = self.handler.c
        headers = {}
        if c.app_ekk or c.test_cachepurge:
            # ei soovi puhvrist vastust, vaid värsket
            headers['cachepurge'] = 'true'
        return headers
    
    def get_test(self, test_id, testiosa_id, alatest_id, komplekt_id, lang, ty_id=None, e_komplekt_id=None, preview=False):
        url = f'/test/{test_id}/testiosa/{testiosa_id or 0}'
        params = {}
        if e_komplekt_id:
            params['e_komplekt_id'] = e_komplekt_id
        if alatest_id:
            params['alatest_id'] = alatest_id
        if komplekt_id:
            params['komplekt_id'] = komplekt_id
        if ty_id:
            params['ty_id'] = ty_id
        elif preview:
            # preview on kasutusel siis, kui pole ty_id, komplektide hulga valimiseks
            params['preview'] = preview
        params['lang'] = lang
        
        res = self.apicall(url, params, post=False)
        clsmap = {'test': MemTest,
                  }
        return RecordWrapper.create_from_dict(res, clsmap)

    def get_valitudylesanne(self, test_id, testiosa_id, ty_id, vy_id, komplekt_id, lang):
        url = f'/test/{test_id}/testiosa/{testiosa_id}/ty/{ty_id}/vy/{vy_id or 0}'
        params = {}
        if komplekt_id:
            params['komplekt_id'] = komplekt_id
        if lang:
            params['lang'] = lang
        res = self.apicall(url, params, post=False)
        
        clsmap = {'ylesanne': MemYlesanne,
                  'sisuplokid': MemSisuplokk,
                  'sisuobjektid': MemSisuobjekt,
                  'kysimused': MemKysimus,
                  'valikud': MemValik,
                  'tulemused': MemTulemus,
                  'correct': MemKV,
                  'kvsisud': MemKS,
                  }
        item = RecordWrapper.create_from_dict(res, clsmap)
        correct_responses = {r.kood: r for r in item.correct or []}
        return item.vy, item.ylesanne, correct_responses

    def get_testiylesanded(self, test_id, testiosa_id, alatest_id, komplekt_id, hindamiskogum_id, ignore_ty_id, lang):
        url = f'/test/{test_id}/testiosa/{testiosa_id}/komplekt/{komplekt_id}/testiylesanded'
        if not komplekt_id:
            raise Exception('komplekt_id puudub')
        params = {}
        if alatest_id:
            params['alatest_id'] = alatest_id
        if hindamiskogum_id:
            params['hindamiskogum_id'] = hindamiskogum_id
        if ignore_ty_id:
            params['ignore_ty_id'] = ignore_ty_id
        if lang:
            params['lang'] = lang
        res = self.apicall(url, params, post=False)
        return RecordWrapper.create_from_dict(res['testiylesanded'])
    
    def get_next_ty_id(self, test_id, testiosa_id, ty_id):
        url = f'/test/{test_id}/testiosa/{testiosa_id}/ty/{ty_id}/next'
        res = self.apicall(url, None)
        return res['next_ty_id']

    def vy_grupid(self, test_id, testiosa_id, ty_id, vy_id):
        url = f'/test/{test_id}/testiosa/{testiosa_id}/ty/{ty_id}/vy/{vy_id}/grupid'
        res = self.apicall(url, None)
        return res['grupid']

    def kysitlus_alatest(self, test_id, testiosa_id):
        url = f'/test/{test_id}/testiosa/{testiosa_id}/kysitlus'
        res = self.apicall(url, None)
        return res['tv_alatest_id']

    def normipunktid(self, test_id, testiosa_id, grupid_id):
        url = f'/test/{test_id}/testiosa/{testiosa_id}/normipunktid'
        params = {'grupp_id': grupid_id}
        res = self.apicall(url, params)
        return res['normipunktid']
    
    def lukusta_komplekt(self, test_id, testiosa_id, komplekt_id, lukus):
        url = f'/test/{test_id}/testiosa/{testiosa_id}/komplekt/{komplekt_id}/lukusta'
        data = {'lukus': lukus}
        res = self.apicall(url, data, post=True)
        return res

    def get_sisuobjekt(self, ylesanne_id, vy_id, sisuplokk_id, filename, hotspot=False):
        url = f'/ylesanne/{ylesanne_id or 0}/sisuobjekt'
        params = {}
        if sisuplokk_id:
            params['sisuplokk_id'] = sisuplokk_id
        if not ylesanne_id and vy_id:
            params['vy_id'] = vy_id
        if filename:
            params['filename'] = filename
        if hotspot:
            params['hotspot'] = True
        res = self.apicall(url, params, post=False)
        error = res.get('error')
        sobj = res.get('sisuobjekt')
        valikud = res.get('valikud')
        return (sobj and MemSisuobjekt.create_from_dict(sobj) or None,
                RecordWrapper.create_from_dict(valikud))

    def get_kratt_datafile(self, ylesanne_id):
        url = f'/ylesanne/{ylesanne_id}/kratt_datafile'
        res = self.apicall(url, None)
        return res

    def get_tagasisidefail(self, test_id, filename):
        url = f'/test/{test_id}/tagasisidefail/{filename}'
        res = self.apicall(url, None)
        return RecordWrapper.create_from_dict(res)

    def get_shared(self, filename):
        url = f'/shared/{filename}'
        res = self.apicall(url, None)
        if res.get('id'):
            return RecordWrapper.create_from_dict(res)

    def get_abivahend(self, vahend_kood):
        url = f'/vahend/{vahend_kood}'
        res = self.apicall(url, None, post=False)
        return RecordWrapper.create_from_dict(res)
