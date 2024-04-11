# -*- coding: utf-8 -*-
from collections import OrderedDict
from eis.tests.functional import *

ylesanne_id = None

class YlesanneTests(FunctionalTestBase):
        
    def test_01_create(self):
        "Ülesande loomine"
        global ylesanne_id
        self._login()

        res = self.testapp.get('/ekk/ylesanded/new', status=200)        
        form = res.form
        form['f_nimi'] = 'Testülesanne'
        form['f_aine_kood'] = 'B'
        res = form.submit()
        res = res.follow()
        ylesanne_id = int(res.request.url.split('/')[-2])
        print('Loodud ylesanne %d' % ylesanne_id)

        #rq = response.pyquery
        #rq.remove_namespaces()
        #assert(0 == len(rq('div.saved')))
        
    def test_02_sp19(self):
        "Avatud vastusega küsimus"
        self._login()
        res = self.testapp.get('/ekk/ylesanded/%d/sisu/sisuplokid/new?tyyp=19' % ylesanne_id, status=200)        

        form = res.form
        # ei saa teha submit, kuna originaalvormil puudub hindamismaatriksi rida
        params = self._get_params(form)
        params['f_nimi'] = 'Kui palju on 2 x 3?'
        params['am1.baastyyp'] = 'integer'
        params['am1.arvutihinnatav'] = '1'
        _set_hm(params, 0, kood1='6')     
        res = self.testapp.post(form.action, params, status=302)
        res = res.follow()
        self.assertTrue(_success(res))
                      
    def test_03_sp16(self):
        "Lühivastusega küsimus"
        self._login()
        res = self.testapp.get('/ekk/ylesanded/%d/sisu/sisuplokid/new?tyyp=16' % ylesanne_id, status=200)        

        form = res.form
        params = self._get_params(form)
        params['f_nimi'] = 'Kui palju on 2 + 3?'
        params['am1.baastyyp'] = 'integer'
        params['am1.arvutihinnatav'] = '1'
        _set_hm(params, 0, kood1='5')
        
        res = self.testapp.post(form.action, params, status=302)
        res = res.follow()
        self.assertTrue(_success(res))

    def test_04_sp12(self):
        "Valikvastusega küsimus"
        self._login()
        res = self.testapp.get('/ekk/ylesanded/%d/sisu/sisuplokid/new?tyyp=12' % ylesanne_id, status=200)        

        form = res.form
        params = self._get_params(form)
        params['f_nimi'] = 'Vali'
        params['v-0.kood'] = 'A'
        params['v-0.nimi_rtf'] = ''
        params['v-0.nimi'] = 'esimene'
        params['v-1.kood'] = 'B'
        params['v-1.nimi_rtf'] = ''
        params['v-1.nimi'] = 'teine'
        params['v-2.kood'] = 'C'
        params['v-2.nimi_rtf'] = ''
        params['v-2.nimi'] = 'kolmas'
        _set_hm(params, 0, kood1='A')
        
        res = self.testapp.post(form.action, params, status=302)
        res = res.follow()
        self.assertTrue(_success(res))

    def test_05_sp17(self):
        "Faili laadimine"
        self._login()
        res = self.testapp.get('/ekk/ylesanded/%d/sisu/sisuplokid/new?tyyp=17' % ylesanne_id, status=200)        

        form = res.form
        form['f_nimi'] = 'Laadi fail'
        form['am1.max_pallid'] = '4'
        res = form.submit()
        res = res.follow()
        self.assertTrue(_success(res))
                      
    def test_06_sp15(self):
        "Järjestamine"
        self._login()
        res = self.testapp.get('/ekk/ylesanded/%d/sisu/sisuplokid/new?tyyp=15' % ylesanne_id, status=200)        

        form = res.form
        params = self._get_params(form)
        params['f_nimi'] = 'Sordi'
        params['v-0.kood'] = 'A'
        params['v-0.nimi_rtf'] = ''
        params['v-0.nimi'] = 'kolmas'
        params['v-1.kood'] = 'B'
        params['v-1.nimi_rtf'] = ''
        params['v-1.nimi'] = 'viies'
        params['v-2.kood'] = 'C'
        params['v-2.nimi_rtf'] = ''
        params['v-2.nimi'] = 'teine'
        _set_hm(params, 0, kood1='C')
        _set_hm(params, 1, kood1='A')
        _set_hm(params, 2, kood1='B')
        
        res = self.testapp.post(form.action, params, status=302)
        res = res.follow()
        self.assertTrue(_success(res))

    def test_07_sp11(self):
        "Liugur"
        self._login()
        res = self.testapp.get('/ekk/ylesanded/%d/sisu/sisuplokid/new?tyyp=11' % ylesanne_id, status=200)        

        form = res.form
        params = self._get_params(form)
        params['f_nimi'] = 'Liiguta'
        params['sl.min_vaartus'] = '15'
        params['sl.max_vaartus'] = '25'        
        params['sl.samm'] = '2'
        params['sl.yhik'] = 'm'
        params['sl.samm_nimi'] = '1'
        params['sl.asend_paremal'] = '1'
        _set_hm(params, 0, kood1='15', kood2='20')
        
        res = self.testapp.post(form.action, params, status=302)
        res = res.follow()
        self.assertTrue(_success(res))

    def test_08_sp20(self):
        "Avatud vastusega lünk"
        self._login()
        res = self.testapp.get('/ekk/ylesanded/%d/sisu/sisuplokid/new?tyyp=20' % ylesanne_id, status=200)        
        form = res.form
        form['f_nimi'] = 'Sisesta'
        form['f_sisu'] = 'At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga.'
        res = form.submit()
        res = res.follow()
        form = res.form
        sp_id = int(res.request.url.split('/')[-2])

        # dialoogiaken
        res_d = self.testapp.get('/ekk/ylesanded/%d/sisuplokid/%d/kysimused/A/edit?data=&tyyp=16' % (ylesanne_id, sp_id), status=200)
        form_d = res_d.form
        params_d = self._get_params(form_d)
        _set_hm(params_d, 0, kood1='iusto')
        res_d = self.testapp.post(form_d.action, params_d, status=200)
        self.assertTrue("dialog('close')" in res_d.body)

        form['f_sisu'] = '<div style="position:relative;">At vero eos et accusamus et <input baastyyp="string" max_pallid="" min_pallid="0" type="text" vaikimisi_pallid="0" value="A" />&nbsp;iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga.</div>'
        res = form.submit()
        res = res.follow()
        self.assertTrue(_success(res))

    def test_09_sp14(self):
        "Tekstiosa valik"
        self._login()
        res = self.testapp.get('/ekk/ylesanded/%d/sisu/sisuplokid/new?tyyp=14' % ylesanne_id, status=200)        
        form = res.form
        form['f_nimi'] = 'Märgi õiged tekstiosad'
        form['f_sisu'] = 'At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum <span class="hottext" group="R" name="3" uitype="underline">(R:3)deleniti</span> atque <span class="hottext" group="R" name="2" uitype="underline">(R:2)corrupti</span> quos dolores et quas molestias excepturi sint <span class="hottext" group="B" name="1" uitype="checkbox">(B:1)occaecati</span> cupiditate non provident, <span class="hottext" group="B" name="2" uitype="checkbox">(B:2)similique</span> sunt in culpa qui officia deserunt mollitia animi, id est <span class="hottext" group="P" name="1" uitype="checkbox">(P:1)laborum</span> et <span class="hottext" group="P" name="2" uitype="checkbox">(P:2)dolorum</span> fuga.<br />'
        res = form.submit()
        res = res.follow()
        form = res.form
        params = self._get_params(form)
        _set_hm(params, 0, am='am-0', kood1='2')
        _set_hm(params, 0, am='am-1', kood1='1')
        _set_hm(params, 0, am='am-2', kood1='1')                        
        res = self.testapp.post(form.action, params, status=302, content_type=self.CTYPE)
        #res = self.testapp.post(form.action, params, status=302)
        res = res.follow()
        self.assertTrue(_success(res))

    def test_10_sp5(self):
        "Sobitamine 3 hulgaga"
        self._login()
        res = self.testapp.get('/ekk/ylesanded/%d/sisu/sisuplokid/new?tyyp=5' % ylesanne_id, status=200)        
        form = res.form
        form['f_nimi'] = 'Sobita'
        params = self._get_params(form)

        def _set_v(params, v_ind, ind, kood='', nimi=''):
            prefix = 'v%d-%d.' % (v_ind, ind)
            params[prefix + 'kood'] = kood
            params[prefix + 'nimi_rtf'] = ''
            params[prefix + 'nimi'] = nimi
            params[prefix + 'min_vastus'] = ''
            params[prefix + 'max_vastus'] = ''
            params[prefix + 'id'] = ''

        params['l.max_vastus'] = '4'
        params['l2.max_vastus'] = '2'
        params['l3.max_vastus'] = '2'

        _set_v(params, 1, 0, kood='A', nimi='esimene')
        _set_v(params, 1, 1, kood='B', nimi='teine')
        _set_v(params, 1, 2, kood='C', nimi='kolmas')        

        _set_v(params, 2, 0, kood='1', nimi='nr 3')
        _set_v(params, 2, 1, kood='2', nimi='nr 1')
        _set_v(params, 2, 2, kood='3', nimi='nr 2')        

        _set_v(params, 3, 0, kood='a', nimi='aaa')
        _set_v(params, 3, 1, kood='b', nimi='bbb')
        _set_v(params, 3, 2, kood='c', nimi='ccc')        

        #res = self.testapp.post(form.action, params, status=302)
        #res = res.follow()
        #params = self._get_params(form)

        _set_hm(params, 0, am='am1', kood1='A', kood2='1')
        _set_hm(params, 1, am='am1', kood1='1', kood2='a')
        _set_hm(params, 2, am='am1', kood1='A', kood2='a')

        params['am1.kysimus_id'] = ''
        params['am1.kood'] = 'K10_1'
        params['am1.min_pallid'] = '0'
        params['am1.max_pallid'] = '1'
        params['am1.vaikimisi_pallid'] = ''
        params['am1.arvutihinnatav'] = '1'

        res = self.testapp.post(form.action, params, status=302)
        #print res.body
        res = res.follow()
        self.assertTrue(_success(res))

    def test_10_sp23(self):
        "Sobitamine 2 hulgaga"
        self._login()
        #ylesanne_id=565
        res = self.testapp.get('/ekk/ylesanded/%d/sisu/sisuplokid/new?tyyp=23' % ylesanne_id, status=200)        
        form = res.form
        form['f_nimi'] = 'Sobita'
        params = self._get_params(form)

        def _set_v(params, v_ind, ind, kood='', nimi=''):
            prefix = 'v%d-%d.' % (v_ind, ind)
            params[prefix + 'kood'] = kood
            params[prefix + 'nimi_rtf'] = ''
            params[prefix + 'nimi'] = nimi
            params[prefix + 'min_vastus'] = ''
            params[prefix + 'max_vastus'] = ''
            params[prefix + 'id'] = ''

        params['l.ridu'] = '1'

        _set_v(params, 1, 0, kood='K10_A', nimi='esimene')
        _set_v(params, 1, 1, kood='K10_B', nimi='teine')
        _set_v(params, 1, 2, kood='K10_C', nimi='kolmas')        

        _set_v(params, 2, 0, kood='1', nimi='nr 3')
        _set_v(params, 2, 1, kood='2', nimi='nr 1')
        _set_v(params, 2, 2, kood='3', nimi='nr 2')        

        res = self.testapp.post(form.action, params, status=302)
        res = res.follow()

        params = self._get_params(form)
        # ei tule jadasid
        _set_hm(params, 0, am='am-0', kood1='3')
        _set_hm(params, 0, am='am-1', kood1='1')
        _set_hm(params, 0, am='am-2', kood1='2')

        params['am-0.kysimus_id'] = ''
        params['am-0.kood'] = 'K10_A'
        params['am-0.min_pallid'] = '0'
        params['am-0.max_pallid'] = '1'
        params['am-0.vaikimisi_pallid'] = ''

        params['am-1.kysimus_id'] = ''
        params['am-1.kood'] = 'K10_B'
        params['am-1.min_pallid'] = '0'
        params['am-1.max_pallid'] = '1'
        params['am-1.vaikimisi_pallid'] = ''

        params['am-2.kysimus_id'] = ''
        params['am-2.kood'] = 'K10_C'
        params['am-2.min_pallid'] = '0'
        params['am-2.max_pallid'] = '1'
        params['am-2.vaikimisi_pallid'] = ''

        res = self.testapp.post(form.action, params, status=302)
        #print res.body
        res = res.follow()
        self.assertTrue(_success(res))

    def test_11_sp18(self):
        "Seostamine"
        self._login()
        res = self.testapp.get('/ekk/ylesanded/%d/sisu/sisuplokid/new?tyyp=18' % ylesanne_id, status=200)        
        form = res.form
        form['f_nimi'] = 'Sobita'
        params = self._get_params(form)

        def _set_v(params, ind, kood='', nimi=''):
            prefix = 'v-%d.' % (ind)
            params[prefix + 'kood'] = kood
            params[prefix + 'nimi_rtf'] = ''
            params[prefix + 'nimi'] = nimi
            params[prefix + 'min_vastus'] = ''
            params[prefix + 'max_vastus'] = ''
            params[prefix + 'id'] = ''

        _set_v(params, 0, kood='A', nimi='esimene')
        _set_v(params, 1, kood='B', nimi='teine')
        _set_v(params, 2, kood='C', nimi='kolmas')
        _set_v(params, 3, kood='D', nimi='neljas')                
        _set_v(params, 4, kood='E', nimi='viies')
        
        _set_hm(params, 0, kood1='A', kood2='C')
        _set_hm(params, 1, kood1='D', kood2='E')

        res = self.testapp.post(form.action, params, status=302)
        res = res.follow()
        self.assertTrue(_success(res))

    def test_11_sp4(self):
        "Pangaga lünk"
        self._login()
        res = self.testapp.get('/ekk/ylesanded/%d/sisu/sisuplokid/new?tyyp=4' % ylesanne_id, status=200)        
        form = res.form
        params = self._get_params(form)
        params['f_nimi'] = 'Vii lünka'

        def _set_v(params, ind, kood='', nimi=''):
            prefix = 'v-%d.' % (ind)
            params[prefix + 'kood'] = kood
            params[prefix + 'nimi_rtf'] = ''
            params[prefix + 'nimi'] = nimi
            params[prefix + 'min_vastus'] = ''
            params[prefix + 'max_vastus'] = ''
            params[prefix + 'id'] = ''

        _set_v(params, 0, kood='1', nimi='esimene')
        _set_v(params, 1, kood='2', nimi='teine')
        _set_v(params, 2, kood='3', nimi='kolmas')
        
        params['am1.kysimus_id'] = ''
        params['am1.kood'] = 'K11_1'
        params['am1.min_pallid'] = '0'
        params['am1.max_pallid'] = ''
        params['am1.vaikimisi_pallid'] = ''
        params['am1.arvutihinnatav'] = '1'
        #_set_hm(params, 0, kood1='A', kood2='C')
        #_set_hm(params, 1, kood1='D', kood2='E')

        params['f_sisu'] = """<div style="position:relative;">
<p>Esimene rida&nbsp;<input hm0="1/1/0" max_pallid="" min_pallid="0" size="10" type="text" vaikimisi_pallid="0" value="A" /></p>

<p>Teine rida&nbsp;<input hm0="1/1/0" max_pallid="" min_pallid="0" size="10" type="text" vaikimisi_pallid="0" value="B" /></p>
</div>"""
        res = self.testapp.post(form.action, params, status=302)
        res = res.follow()
        self.assertTrue(_success(res))

    def test_12_sp24(self):
        "GeoGebra"
        self._login()
        res = self.testapp.get('/ekk/ylesanded/%d/sisu/sisuplokid/new?tyyp=24' % ylesanne_id, status=200)        

        form = res.form
        params = self._get_params(form)
        params['f_nimi'] = 'GeoGebra ülesanne'
        params['mo.kood'] = 'sZN7kF7J'
        # nagu impordiks koodi järgi, tegelikult genereeritakse vorm uuesti
        res = self.testapp.post(form.action, params, status=302)
        res = res.follow()
        form = res.form
        params = self._get_params(form)
        params['ggb_filedata_b64'] = "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"
        # salvestame geogebra pildi
        res = self.testapp.post(form.action, params, status=302)
        res = res.follow()
        self.assertTrue(_success(res))        

    def test_12_sp25(self):
        "Google Charts"
        self._login()
        res = self.testapp.get('/ekk/ylesanded/%d/sisu/sisuplokid/new?tyyp=25' % ylesanne_id, status=200)        

        form = res.form
        params = self._get_params(form)
        params['f_nimi'] = 'Vaata diagrammi'
        params['f_alamtyyp'] = 'BarChart'
        params['ggc.datasetcnt'] = '1'
        params['mo.laius'] = '500'
        params['mo.korgus'] = '400'
        params['ggc.header.col-0.inst-0.value'] = 'Pealkiri1'
        params['ggc.header.col-1.inst-0.value'] = 'Pealkiri2'
        params['ggc.data-0.col-0.inst-0.value'] = '1'
        params['ggc.data-0.col-1.inst-0.value'] = '10'
        params['ggc.data-1.col-0.inst-0.value'] = '1'
        params['ggc.data-1.col-1.inst-0.value'] = '15'
        params['sub'] = 'change'
        res = self.testapp.post(form.action, params, status=200)
        form = res.form
        params = self._get_params(form)
        params['f_sisuvaade'] = """var rows=[["Pealkiri1","Pealkiri2"],["1",10],["2",15]];
var options={"width":500,"height":400};"""

        res = self.testapp.post(form.action, params, status=302)
        res = res.follow()
        self.assertTrue(_success(res))        

    def test_50_test(self):
        "Testis kasutamiseks ülesannete loomine"
        global ylesanne_id

        sisuplokid = (self.test_02_sp19,
                      self.test_03_sp16,
                      self.test_04_sp12,
                      #self.test_05_sp17,
                      self.test_06_sp15,
                      self.test_07_sp11,
                      self.test_08_sp20,
                      self.test_09_sp14,
                      self.test_11_sp18)
        ylesanded_id = []
        for f_sp in sisuplokid:
            self.test_01_create()
            f_sp()
            ylesanded_id.append(ylesanne_id)
        print(('**************** Loodud ülesanded: %s' % (ylesanded_id)))

    def _get_params(self, form):
        "Koostame parameetrite dicti vormi põhjal"
        params = OrderedDict()
        #print dir(form.fields)
        #print form.fields.items()
        for key, fields in list(form.fields.items()):
            field = fields[0]
            try:
                if not field.checked:
                    #print 'continue key=%s, fields=%s' % (key, fields)
                    continue
            except:
                pass
            value = field.value
            #print 'key=%s, value=%s, fields=%s' % (key, value, fields)
            if key is None:
                continue
            params[key] = value or ''
        return params

def _set_hm(params, ind, am='am1', kood1='', kood2='', pallid='', oige='1', id=''):
    prefix = '%s.hm1-%d.' % (am, ind)
    params[prefix + 'kood1'] = kood1
    params[prefix + 'kood2'] = kood2
    params[prefix + 'pallid'] = pallid
    params[prefix + 'oige'] = oige
    params[prefix + 'id'] = id

def _success(res):
    # return "Andmed on salvestatud" in res.body
    return '<span id="flashsuccess"' in res.body
