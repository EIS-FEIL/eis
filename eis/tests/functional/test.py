import re
from collections import OrderedDict
from eis.tests.functional import *

test_id = None
testiosa_id = None

# ylesanded.py test_50 loodud ylesanded
ylesanded_id = (424,425,426,427,428,429,430,431)

class TestTests(FunctionalTestBase):
        
    def test_01_create(self):
        "Testi loomine"
        global test_id
        self._login()

        res = self.testapp.get('/ekk/testid/new', status=200)        
        form = res.form
        form['f_testiliik_kood'] = 'p'
        form['f_periood_kood'] = '2014'
        form['f_aine_kood'] = 'B'
        form['f_nimi'] = 'Testimistest'
        hinded = ((5,90),(4,80),(3,50),(2,35),(1,0))
        for ind, (hinne, pallid) in enumerate(hinded):
            form['h-%s.hinne' % ind] = hinne
            form['h-%s.pallid' % ind] = pallid
        form['f_ymardamine'] = '1'
        form['f_oige_naitamine'] = '1'
        form['f_arvutihinde_naitamine'] = '1'
        form['f_tulemus_vaade'] = '2'
        form['f_lang'] = 'et'
        res = form.submit()
        res = res.follow()
        test_id = int(res.request.url.split('/')[-2])
        print('Loodud test %d' % test_id)
        
    def test_02_testiosa(self):
        global testiosa_id
        self._login()
        # avame struktuuri vormi
        res = self.testapp.get('/ekk/testid/%d/struktuur' % test_id, status=200)        
        # avame testiosa dialoogiakna
        res = self.testapp.get('/ekk/testid/%d/testiosad/new?partial=True' % test_id, status=200)
        form = res.form
        form['f_nimi'] = 'Osa1'
        form['f_vastvorm_kood'] = 'ke'
        res = form.submit()
        # avame struktuuri vormi, kus on olemas testiosa
        res = res.follow()
        # leiame nupu "Eemalda" seest testiosa ID
        m = re.findall('"/testid/[\d]+/testiosad/([\d]+)/delete"', res.body)
        testiosa_id = int(m[-1])
        print(('testiosa %d' % testiosa_id))
        for ind1 in range(3):
            alatest_id, res = self._add_alatest(test_id, testiosa_id)
            print((' alatest %d' % alatest_id))
            for ind2 in range(2):
                ty_id, res = self._add_testiylesanne(test_id, testiosa_id, alatest_id)
                print(('  testiylesanne %d' % ty_id))
                
        # kinnitame struktuuri
        #<input type="button" value="Kinnita struktuur"  href="/testid/2644/struktuur/3750/edit?partial=True&sub=kinnita" class="get button1" id="kinnita_struktuur"/>
        m = re.search('value="Kinnita struktuur"[^>]+href="([^"]+)"', res.body)
        url = m.groups()[0]
        res = self.testapp.get(url, status=200)
        self.assertTrue('Testi struktuur on kinnitatud' in res.body)
        #self.assertTrue(_success(res))

    def test_03_komplektid(self):
        self._login()
        # avame testi ylesannete vormi
        y_ind = 0
        print('****** test_03_komplektid')
        res = self.testapp.get('/ekk/testid/%d/valitudylesanded' % test_id, status=200)        
        for ind in range(2):
            komplekt_id, res = self._add_komplekt(testiosa_id, res)
            y_ind = self._add_valitudylesanne(komplekt_id, res, y_ind)
            
    def _add_komplekt(self, testiosa_id, res):
        # avame komplekti lisamise vormi
        #<input type="button" value="Lisa komplekt"  class="button1" onclick="dialog('', 'Komplekt', '/testid/2647/testiosad/3753/komplektid/new?komplektivalik_id=3854&partial=True&361495834015', 400, null, null, 'get', null)" id="lisa_komplekt"/>
        url = _get_dlg_btn_url('Lisa komplekt', res)
        res = self.testapp.get(url, status=200)
        form = res.form

        #<input checked="checked" id="komplektivalik_id" name="komplektivalik_id" onchange="change_komplektivalik(this)" type="checkbox" value="3855" />
        #<input checked="checked" id="komplektivalik_id" name="komplektivalik_id" onchange="change_komplektivalik(this)" type="checkbox" value="3855" />
        #<input id="alatest_id" name="alatest_id" onchange="change_alatestivalik()" type="checkbox" value="3957" />

        try:
            #alatestid_id = re.findall('name="alatest_id"[^>]+value="([\d]+)"', res.body)
            #form['alatest_id'] = alatestid_id[:2]
            form.get('alatest_id', index=0).checked = True
        except AssertionError:
            # No field by the name 'alatest_id' found
            #kvalikud_id = re.findall('name="komplektivalik_id"[^>]+value="([\d]+)"', res.body)
            #form['komplektivalik_id'] = kvalikud_id[0]
            form.get('komplektivalik_id', index=0).checked = True
            
        res = form.submit()
        res = res.follow()

        # leiame komplekti id
        #<input type="button" value="Kinnita komplekt"  href="/testid/2647/valitudylesanded/274?komplektivalik_id=3855&komplekt_id=274&testiosa_id=3753&sub=kinnita" class="put button1" id="kinnita_komplekt"/>
        komplekt_id = _get_btn_url('Kinnita komplekt', res)
        return komplekt_id, res

    def _add_valitudylesanne(self, komplekt_id, res, y_ind):
        #<input type="button" value="Vali"  class="button1" onclick="dialog('', 'Ülesande valimine', '/testid/2647/komplekt/273/testiylesanne/638/ylesanded/1/edit?komplekt_id2=273&833831771264', 800, null, null, 'get', null)" id="vali"/>
        #print res.body
        urlid = _get_dlg_btn_urlid('Vali', res)
        for url in urlid:
            #print 'url=%s' % url
            res = self.testapp.get(url, status=200)
            form = res.forms['form_search_y']
            if y_ind >= len(ylesanded_id):
                y_ind = 0
            ylesanne_id = ylesanded_id[y_ind]
            form['ylesanne_id'] = ylesanne_id
            res_list = form.submit()
            #<input class="button1" id="ylesanne_id_32" name="ylesanne_id_32" type="submit" value="Vali" />
            form = res.forms['form_save']
            params = self._get_params(form)
            params['ylesanne_id_%d' % ylesanne_id] = 'Vali'
            res = self.testapp.post(form.action, params, status=302)
            y_ind += 1
        return y_ind

    def _add_alatest(self, test_id, testiosa_id):
        # avame alatesti lisamise dialoogiakna
        #<input type="button" value="Lisa alatest"  class="button1" onclick="dialog('', 'Alatest', '/testid/2644/testiosad/3750/alatestid/new?partial=True&803963583953', 600, null, null, 'get', null)" id="lisa_alatest"/>
        url = '/ekk/testid/%d/testiosad/%d/alatestid/new?partial=True' % (test_id, testiosa_id)
        res = self.testapp.get(url, status=200)
        form = res.form
        form['f_nimi'] = 'Alatest1'
        form['piiraeg'] = '10:00'
        form['hoiatusaeg'] = '5'
        form['f_on_yhekordne'] = '1'
        res = form.submit()
        res = res.follow()
        # leiame eemaldamise risti juurest alatesti ID
        # <a href="/testid/2644/testiosad/3750/alatestid/3953/delete" class="delete menu2">X</a>
        m = re.findall('"/testid/[\d]+/testiosad/[\d]+/alatestid/([\d]+)/delete"', res.body)
        alatest_id = int(m[-1])
        return alatest_id, res

    def _add_testiylesanne(self, test_id, testiosa_id, alatest_id):
        # avame testiylesande lisamise dialoogiakna
        #<input type="button" value="Lisa testiülesanne"  class="button1" onclick="dialog('', 'Ülesanne', '/testid/2644/testiosad/3750/testiylesanded/new?alatest_id=3953&partial=True&373481966267', 600, null, null, 'get', null)" id="lisa_testi_lesanne"/>
        url = '/ekk/testid/%d/testiosad/%d/testiylesanded/new?alatest_id=%d&partial=True' % (test_id, testiosa_id, alatest_id)
        res = self.testapp.get(url, status=200)
        form = res.form
        #form['f_nimi'] = '1'
        form['f_max_pallid'] = '10'
        form['f_hindamine_kood'] = 'o'
        form['f_arvutihinnatav'] = '1'
        res = form.submit()
        res = res.follow()        
        # leiame testiylesande ID
        #<a href="/testid/2644/testiosad/3750/testiylesanded/634/delete" class="delete menu2">X</a>
        m = re.findall('"/testid/[\d]+/testiosad/[\d]+/testiylesanded/([\d]+)/delete"', res.body)
        ty_id = int(m[-1])
        return ty_id, res

    
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

def _get_dlg_btn_urlid(title, res):
    m = re.findall('value=\"' + title + "\"[^>]+dialog\('[^']*', '[^']*', '([^\']+)'", res.body)
    return m

def _get_dlg_btn_url(title, res):
    return _get_dlg_btn_urlid(title, res)[-1]

def _get_btn_url(title, res):
    m = re.findall('value=\"' + title + '"[^>]+href="([^"]+)', res.body)
    return m[-1]

def _success(res):
    # return "Andmed on salvestatud" in res.body
    return '<span id="flashsuccess"' in res.body
