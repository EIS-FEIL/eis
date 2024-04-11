import random
import json
from eis.lib.baseresource import *
_ = i18n._
from eis.handlers.ekk.testid.komplektotsiylesanded import filter_ylesanne, check_ylesanne
from eis.lib.block import BlockController
log = logging.getLogger(__name__)

class ValitudylesandedController(BaseResourceController):

    _permission = 'ekk-testid'
    _INDEX_TEMPLATE = 'ekk/testid/valitudylesanded.mako'
    _LIST_TEMPLATE = 'ekk/testid/valitudylesanded_list.mako'
    _ITEM_FORM = forms.ekk.testid.YlesandedForm 
    _DEFAULT_SORT = 'alatest.seq,testiplokk.seq,testiylesanne.seq,valitudylesanne.seq' # vaikimisi sortimine
    _no_paginate = True
    _get_is_readonly = False

    def _query(self):
        if self.request.params.get('vali'):
            self._vali_ylesanded()

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q1):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c

        if not c.testiosa_id:
            return

        q = (model.Valitudylesanne.query
             .join(model.Valitudylesanne.komplekt)
             .join(model.Komplekt.komplektivalik)
             .filter(model.Komplektivalik.testiosa_id==c.testiosa_id))
             
        c.testiosa = model.Testiosa.get(c.testiosa_id)
        if not c.testiosa:
            return
        
        if c.komplektivalik_id:
            c.komplektivalik = model.Komplektivalik.get(c.komplektivalik_id)
            q = q.filter(model.Komplekt.komplektivalik_id==c.komplektivalik_id)
        elif not c.testiosa.on_alatestid:
            # alatestideta testiosal on yksainus komplektivalik
            c.komplektivalik = c.testiosa.get_komplektivalik()
        elif c.kursus:
            q = q.filter(model.Komplektivalik.kursus_kood==c.kursus)
            
        if c.komplekt_id:
            c.komplekt = model.Komplekt.get(c.komplekt_id)
            q = q.filter(model.Valitudylesanne.komplekt_id==c.komplekt_id)

            if not c.komplektivalik and c.komplekt:
                c.komplektivalik = c.komplekt.komplektivalik
                c.komplektivalik_id = c.komplektivalik.id

        if c.komplektivalik:
            c.kursus = c.komplektivalik.kursus_kood
                
        if c.testiplokk_id or c.alatest_id:
            q = q.join(model.Valitudylesanne.testiylesanne)
            if c.testiplokk_id:
                c.testiplokk = model.Testiplokk.get(c.testiplokk_id)
                q = q.filter(model.Testiylesanne.testiplokk_id==c.testiplokk_id)

            if c.alatest_id:
                c.alatest = model.Alatest.get(c.alatest_id)
                q = q.filter(model.Testiylesanne.alatest_id==c.alatest_id)
        return q

    def _order_join(self, q, tablename):
        if tablename == 'ylesanne':
            q = q.join(model.Valitudylesanne.ylesanne)
        elif tablename == 'testiylesanne' or tablename == 'alatest' or tablename == 'testiplokk':
            if not self.c.testiplokk_id and not self.c.alatest_id and not self.c.joined_testiylesanne:
                q = q.join(model.Valitudylesanne.testiylesanne)
                self.c.joined_testiylesanne = True
            if tablename == 'testiplokk' and not self.c.joined_testiplokk:
                q = q.outerjoin(model.Testiylesanne.testiplokk)
                self.c.joined_testiplokk = True
            if tablename == 'alatest' and not self.c.joined_alatest:
                q = q.outerjoin(model.Testiylesanne.alatest)
                self.c.joined_alatest = True
                
        return q

    def _show_kontroll(self, id):
        # kui peale update_kontroll pyyab kasutaja GET URL teha
        return self._redirect('index', getargs=True, sub=None)

    def _vali_ylesanded(self):
        cnt_found = 0
        cnt_notfound = 0
        for ty in self.c.testiosa.testiylesanded:
            for vy in ty.valitudylesanded:
                if not self.c.komplekt_id or int(self.c.komplekt_id) == vy.komplekt_id:
                    if not vy.ylesanne_id:
                        ylesanne = vy.ylesanne = _search_valik(self, ty,vy)
                        if not ylesanne:
                            cnt_notfound += 1
                        else:
                            #ylesanne.lukku(const.LUKUSTUS_SISU)
                            if ylesanne.max_pallid is None:
                                ylesanne.max_pallid = ylesanne.calc_max_pallid()
                            if ty.max_pallid is None:
                                if not self.c.testiosa.lotv:
                                    # testiylesande pallid määratakse esimese valitud ülesande pallidega
                                    ty.max_pallid = ylesanne.max_pallid or 0
                                self.c.test.arvuta_pallid()                          
                            vy.update_koefitsient(ty)

                            cnt_found += 1
                            vy.flush()

        model.Session.commit()
        error = False
        msg = ''
        if cnt_found:
            msg += _("Valitud {n} ülesannet. ").format(n=cnt_found)
        if cnt_notfound:
            msg += _("Ei saanud valida {n} ülesannet, kuna sobivaid ülesandeid ei leitud").format(n=cnt_notfound)
            error = True
        if not cnt_found and not cnt_notfound:
            msg = _("Pole kuhugi valida")
        if error:
            self.error(msg)
        else:
            self.success(msg)

    def _update_kinnita(self, id):
        self.c.komplekt_id = id
        self.c.komplekt = model.Komplekt.get(self.c.komplekt_id)

        if self.c.test.staatus == const.T_STAATUS_KOOSTAMISEL:
            self.error(_("Komplekti ei saa kinnitada, sest testi struktuur pole veel kinnitatud"))
        else:
            rc = True
            li = []
            for vy in self.c.komplekt.valitudylesanded:
                ylesanne = vy.ylesanne
                if ylesanne is not None:
                    if not set(self.c.komplekt.keeled).issubset(set(vy.ylesanne.keeled)):
                        li.append(str(vy.ylesanne_id))
                elif not self.c.testiosa.lotv:
                    rc = False
                    self.error(_("Komplekti ei saa kinnitada, kuna kõik ülesanded pole valitud"))
                    break

            if len(li) == 1:
                self.error(_("Ülesanne {s} pole komplekti keeles").format(s=', '.join(li)))
                rc = False
            elif len(li) > 1:
                self.error(_("Ülesanded {s} pole komplekti keeles").format(s=', '.join(li)))
                rc = False
                
            if rc and self.c.komplekt.staatus == const.K_STAATUS_KINNITATUD:
                self.error(_("Komplekt on juba kinnitatud"))
                rc = False

            if rc:
                old_staatus_nimi = self.c.komplekt.staatus_nimi
                self.c.komplekt.staatus = const.K_STAATUS_KINNITATUD

                self.c.test.logi(_("Komplekti {s1} ({s2}) olek").format(s1=self.c.komplekt.tahis, s2=self.c.komplekt.id),
                            old_staatus_nimi,
                            self.c.komplekt.staatus_nimi,
                            const.LOG_LEVEL_GRANT)

                model.Session.commit()
                self.success(_("Komplekt on kinnitatud"))

        self.c.nosub = True
        return self._redirect('index', komplekt_id=id)

    def _update_arhiiv(self, id):
        self.c.komplekt_id = id
        self.c.komplekt = model.Komplekt.get(self.c.komplekt_id)

        if self.c.komplekt.staatus == const.K_STAATUS_ARHIIV:
            self.error(_("Komplekt on juba arhiveeritud"))
        else:
            old_staatus_nimi = self.c.komplekt.staatus_nimi
            self.c.komplekt.staatus = const.K_STAATUS_ARHIIV
            self.c.test.logi(_("Komplekti {s1} ({s2}) olek").format(s1=self.c.komplekt.tahis, s2=self.c.komplekt.id),
                        old_staatus_nimi,
                        self.c.komplekt.staatus_nimi,
                        const.LOG_LEVEL_GRANT)
            model.Session.commit()
            self.success(_("Komplekt on arhiveeritud"))

        self.c.nosub = True
        return self._redirect('index', komplekt_id=id)

    def _update_koosta(self, id):
        self.c.komplekt_id = id
        self.c.komplekt = model.Komplekt.get(self.c.komplekt_id)

        if self.c.komplekt.staatus == const.K_STAATUS_KOOSTAMISEL:
            self.error(_("Komplekt on juba koostamise olekus"))
        else:
            old_staatus_nimi = self.c.komplekt.staatus_nimi
            if self.c.komplekt.lukus and self.c.komplekt.lukus > const.LUKUS_KINNITATUD:
                self.c.komplekt.staatus = const.K_STAATUS_KINNITATUD
                buf = _("Komplekt on kinnitatud olekus")
            else:
                self.c.komplekt.staatus = const.K_STAATUS_KOOSTAMISEL
                buf = _("Komplekt on viidud koostamise olekusse")
            if self.c.komplekt.staatus == const.K_STAATUS_ARHIIV:
                buf = _("Komplekt on arhiivist välja võetud")

            self.c.test.logi(_("Komplekti {s1} ({s2}) olek").format(s1=self.c.komplekt.tahis, s2=self.c.komplekt.id),
                        old_staatus_nimi,
                        self.c.komplekt.staatus_nimi,
                        const.LOG_LEVEL_GRANT)
            model.Session.commit()
            self.success(buf)

        self.c.nosub = True
        return self._redirect('index', komplekt_id=id)

    def _update_kopeeri(self, id):
        self.c.komplekt_id = id
        self.c.komplekt = model.Komplekt.get(self.c.komplekt_id)
        koopia = self.c.komplekt.copy()
        model.Session.commit()
        self.success(_("Komplekt on kopeeritud"))
        return HTTPFound(location=self.url('test_valitudylesanded', test_id=self.c.test.id, komplekt_id=koopia.id))

    def _update_kontroll(self, id):
        """Kontrolli ja arvuta
        """
        self.c.komplekt_id = self.request.params.get('komplekt_id')
        self.c.komplekt = model.Komplekt.get(self.c.komplekt_id)

        # kontrollime, et iga ylesande jaoks on vy olemas
        kv = self.c.komplekt.komplektivalik
        kv.give_valitudylesanded()
        
        self.c.test.arvuta_pallid()
        rc = True
        # testi struktuuri kontroll
        if len(self.c.test.testiosad) == 0:
            self.error(_("Testil pole ühtki testiosa."))
            rc = False
        else:
            for testiosa in self.c.test.testiosad:
                if len(testiosa.testiylesanded) == 0:
                    self.error(_("Testiosas {s} pole ühtki testiülesannet.").format(s=testiosa.tahis or ''))
                    rc = False
                elif len(testiosa.komplektivalikud) == 0:
                    self.error(_("Testiosas {s} pole ühtki ülesandekomplekti.").format(s=testiosa.tahis or ''))
                    rc = False
                else:
                    li = [str(r.seq) for r in testiosa.alatestid if \
                          (not r.komplektivalik or not len(r.komplektivalik.komplektid))]
                    if len(li):
                        self.error(_("Alatestid {s} on ilma komplektideta.").format(s=', '.join(li)))
                        rc = False

        # komplekti kontroll
        if self.c.komplekt:
            self.c.komplektivalik = self.c.komplekt.komplektivalik
            on_lotv = self.c.komplektivalik.testiosa.lotv
            for vy in self.c.komplekt.valitudylesanded:
                ylesanne = vy.ylesanne
                ty = vy.testiylesanne
                if not ylesanne:
                    self.error(_("Ülesanne {s} on komplekti valimata.").format(s=ty.tahis))
                    rc = False
                else:
                    if not on_lotv and ty.max_pallid is None:
                        ty.max_pallid = ylesanne.max_pallid or 0
                    vy.update_koefitsient(ty)

        self.c.test.arvuta_pallid()                          
        model.Session.commit()

        # ühisosa pallide kontroll
        err = self.c.test.calc_yhisosa()
        if err:
            self.error(err)
        model.Session.commit()
        
        self.c.kontroll = True
        self.c.check_ylesanne = check_ylesanne
        self.c.b_check_ylesanne = BlockController.check_ylesanne
        if rc:
            self.success(_("Ülesandekomplekt on kontrollitud."))
        self.c.nosub = True

        q = self._query()
        q = self._search(q)                
        q = self._order(q)
        self.c.items = self._paginate(q)            
        return self._showlist()
    
    def delete(self):
        """Kustutame valitud ülesande
        """
        id = self.request.matchdict.get('id')
        item = model.Valitudylesanne.get(id)
        item.ylesanne_id = None
        model.Session.commit()
        self.success(_("Valitud ülesanne on eemaldatud"))
        return HTTPFound(location=self.url('test_valitudylesanded', test_id=self.c.test.id, testiosa_id=self.c.testiosa.id, komplekt_id=self.c.komplekt_id))

    def _download(self, id, format=None):
        """Näita faili"""
        data = kratt_export(self.c.test)
        filedata = json.dumps(data, ensure_ascii=False)
        return Response(filedata, content_type='application/json; charset=UTF-8')
    
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)

        self.c.testiosa_id = self.request.params.get('testiosa_id')
        if not self.c.testiosa_id and len(self.c.test.testiosad):
            self.c.testiosa_id = self.c.test.testiosad[0].id
        self.c.komplektivalik_id = self.request.params.get('komplektivalik_id')
        self.c.komplekt_id = self.request.params.get('komplekt_id')

        if self.c.komplekt_id:
            self.c.komplekt = model.Komplekt.get(self.c.komplekt_id)
            self.c.komplektivalik = self.c.komplekt.komplektivalik
            self.c.komplektivalik_id = self.c.komplektivalik.id
            self.c.testiosa = self.c.komplektivalik.testiosa
            self.c.testiosa_id = self.c.testiosa.id
        elif self.c.testiosa_id:
            self.c.testiosa = model.Testiosa.get(self.c.testiosa_id)
        if self.c.testiosa:
            assert self.c.test == self.c.testiosa.test, _("Vale test")
        elif len(self.c.test.testiosad):
            self.c.testiosa = self.c.test.testiosad[0]
            self.c.testiosa_id = self.c.testiosa.id

        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}

def _search_valik(handler, ty, vy):
    """Ülesannete automaatne valimine kõigisse ülesandete testiülesannetesse
    antud komplektis.
    """
    q = model.Ylesanne.query
    test = ty.testiosa.test
    aine_kood = test.aine_kood
    q = filter_ylesanne(handler,
                        q,
                        test,
                        vy.komplekt,
                        aine=aine_kood,
                        valdkond=ty.teema_kood,
                        teema=ty.alateema_kood,
                        keeletase=ty.keeletase_kood,
                        mote=ty.mote_kood,
                        aste=ty.aste_kood,
                        max_pallid=ty.max_pallid,
                        tyyp=ty.tyyp,
                        kasutusmaar=ty.kasutusmaar,
                        arvutihinnatav=ty.arvutihinnatav,
                        salastamata=True)
    cnt = q.count()
    if cnt == 0:
        # Ei leia ülesandeid
        # buf = {'komplekt_id':vy.komplekt.id,
        #        'aine':aine_kood,
        #        'valdkond':ty.teema_kood,
        #        'teema':ty.alateema_kood,
        #        'keeletase':ty.keeletase_kood,
        #        'mote':ty.mote_kood,
        #        'aste':ty.aste_kood,
        #        'max_pallid':ty.max_pallid,
        #        'raskus':ty.raskus,
        #        'eristusindeks':ty.eristusindeks,
        #        'tyyp':ty.tyyp,
        #        'kasutusmaar':ty.kasutusmaar,
        #        'arvutihinnatav':ty.arvutihinnatav}
        # log.info('%s\n%s' % (q, buf))

        return None

    # võtame juhusliku ylesande
    n = int(random.random()*cnt)
    return q[n]

def kratt_export(test):
    "Testi struktuur kratile"
    error = None
    
    def _export_tyy(testiylesanded):
        li = []
        for ty in testiylesanded:
            j_ty = {'jrk': ty.seq,
                    'tahis': ty.tahis,
                    }
            vy_found = False
            for vy in ty.valitudylesanded:
                if vy_found:
                    raise Exception('Valikülesandeid ei või olla')
                vy_found = True
                ylesanne = vy.ylesanne
                j_ty['ylesanne_id'] = vy.ylesanne_id
                pildid = {}
                juhised = []
                audio_piiraeg = None
                yl_piiraeg = ty.piiraeg
                for sp in ylesanne.sisuplokid:
                    if sp.tyyp == const.BLOCK_IMAGE:
                        for obj in sp.sisuobjektid:
                            pildid[obj.filename] = obj.get_url()
                    elif sp.tyyp == const.BLOCK_RUBRIC and sp.tahis == 'KRATT':
                        # and sp.staatus == const.B_STAATUS_NAHTAMATU:
                        text = sp.sisuvaade
                        juhised.append(text)
                    elif sp.tyyp == const.INTER_AUDIO:
                        audio_piiraeg = sp.piiraeg
                #j_ty['pildid'] = pildid
                j_ty['juhised'] = juhised
                j_ty['ylesande_piiraeg'] = yl_piiraeg
                j_ty['audio_piiraeg'] = audio_piiraeg
            li.append(j_ty)
        return li
    
    data = {'nimetus': test.nimi,
            }
    testiosad = []
    for testiosa in test.testiosad:
        j_osa = {'jrk': testiosa.seq,
                 'tahis': testiosa.tahis,
                 'nimetus': testiosa.nimi,
                 }
        # leiame ainsa komplekti
        komplekt_id = None
        for kv in testiosa.komplektivalikud:
            for k in kv.komplektid:
                if komplekt_id:
                    raise Exception('Testiosas ei või olla mitu komplekti')
                komplekt_id = k.id
        
        j_osa['ylesanded'] = _export_tyy(testiosa.testiylesanded)
        testiosad.append(j_osa)
    data['testiosad'] = testiosad
    return data
