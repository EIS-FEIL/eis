import json
from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
_ = i18n._
from eis.lib.block import BlockController
from eis.lib.testsaga import TestSaga
from eis.lib.examclient import ExamClient
log = logging.getLogger(__name__)

class TestidController(BaseResourceController):
    """Testide otsing ning testi üldandmed
    """
    _permission = 'ekk-testid'
    _MODEL = model.Test
    _INDEX_TEMPLATE = 'ekk/testid/otsing.mako'
    _EDIT_TEMPLATE = 'ekk/testid/yldandmed.mako' 
    _LIST_TEMPLATE = 'ekk/testid/otsing_list.mako'
    _SEARCH_FORM = forms.ekk.testid.OtsingForm 
    _ITEM_FORM = forms.ekk.testid.YldandmedForm
    _DEFAULT_SORT = '-test.id' # vaikimisi sortimine
    
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c

        # kas oma test või EKK test?
        lif = []
        if c.user.has_permission('ekk-testid', const.BT_INDEX, gtyyp=const.USER_TYPE_AV):
            # võib vaadata oma avaliku vaate teste
            today = date.today()
            fst = sa.and_(model.Test.testityyp==const.TESTITYYP_AVALIK,
                          model.Test.testiisikud.any(sa.and_(
                              model.Testiisik.kasutaja_id==c.user.id,
                              model.Testiisik.kehtib_alates<=today,
                              model.Testiisik.kehtib_kuni>=today))
                          )
            lif.append(fst)
        if c.user.has_permission('ekk-testid', const.BT_INDEX, gtyyp=const.USER_TYPE_EKK):
            # võib vaadata EKK vaate teste
            lif.append(model.Test.testityyp==const.TESTITYYP_EKK)

        if not lif:
            return
        elif len(lif) == 1:
            q = q.filter(lif[0])
        else:
            q = q.filter(sa.or_(*lif))

        # otsingutingimused
        if c.idr:
            flt = forms.validators.IDRange.filter(c.idr, model.Test.id)
            if flt is not None:
                q = q.filter(flt)            
        if c.id:
            q = q.filter_by(id=c.id)
        if c.nimi:
            like_expr = '%%%s%%' % c.nimi            
            q = q.filter(model.Test.nimi.ilike(like_expr))
        if c.staatus:
            q = q.filter_by(staatus=c.staatus)
        else:
            # EIS-323 - arhiivi olekus teste vaikimisi ei näidata
            q = q.filter(model.Test.staatus!=const.T_STAATUS_ARHIIV)
            
        if c.sessioon:
            q = q.filter(model.Test.testimiskorrad.any(model.Testimiskord.testsessioon_id==c.sessioon))
        if c.testiliik:
            q = q.filter_by(testiliik_kood=c.testiliik)
        else:
            liigid = c.user.get_testiliigid(self._permission, const.BT_INDEX)
            if None not in liigid:
                q = q.filter(sa.or_(model.Test.testiliik_kood.in_(liigid),
                                    model.Test.testiisikud.any(
                                        sa.and_(model.Testiisik.kasutaja_id==c.user.id,
                                                model.Testiisik.kehtib_kuni>=date.today()))))
        if c.periood:
            q = q.filter_by(periood_kood=c.periood)
        if c.aine:
            q = q.filter_by(aine_kood=c.aine)

        ained = c.user.get_ained(self._permission, const.BT_INDEX)
        if None not in ained:
            q = q.filter(sa.or_(model.Test.aine_kood.in_(ained),
                                model.Test.testiisikud.any(
                                    sa.and_(model.Testiisik.kasutaja_id==c.user.id,
                                            model.Testiisik.kehtib_kuni>=date.today()))))
        if c.koostaja:
            like_expr = '%%%s%%' % c.koostaja
            q = q.join((model.Kasutaja, 
                        model.Kasutaja.isikukood==model.Test.creator)).\
                filter(model.Kasutaja.nimi.ilike(like_expr))

        # silumiseks
        if c.debug:
            c.is_debug = True
        if c.vastvorm:
            q = q.filter(model.Test.testiosad.any(model.Testiosa.vastvorm_kood==c.vastvorm))
        if c.testiosa_id:
            q = q.filter(model.Test.testiosad.any(model.Testiosa.id==c.testiosa_id))
        if c.tsmall:
            q = q.filter(model.Test.tagasiside_mall==c.tsmall)
        if c.tvorm:
            if c.tvorm == '1':
                q = q.filter(model.Test.tagasisidevormid.any())
            else:
                q = q.filter(model.Test.tagasisidevormid.any(
                    model.Tagasisidevorm.sisu.like('%' + c.tvorm + '%')))
        if c.verif:
            # V, P
            q = q.filter(model.Test.testimiskorrad.any(
                model.Testimiskord.toimumisajad.any(
                    model.Toimumisaeg.verif==c.verif)))
        if c.koolkoht:
            # debug
            q = q.filter(model.Test.sooritajad.any(
                sa.and_(model.Sooritaja.testimiskord_id!=None,
                        model.Sooritaja.pallid>0,
                        model.Sooritaja.kool_koht_id!=None)))
        #model.log_query(q)
        return q

    def _query(self):
        return model.Test.query

    def _search_default(self, q):
        """Otsingu tingimuste seadmine siis, kui otsing toimub 
        kohe otsinguvormi avamisel ja kasutaja pole veel saanud 
        otsingutingimusi valida.
        """
        return None

    def _new(self, item):
        item.oige_naitamine = False
        if self.c.user.has_permission('ekk-testid', const.BT_CREATE, gtyyp=const.USER_TYPE_EKK):
            item.testityyp = const.TESTITYYP_EKK
        elif self.c.user.has_permission('ekk-testid', const.BT_CREATE, gtyyp=const.USER_TYPE_AV):
            item.testityyp = const.TESTITYYP_AVALIK

    def _create(self, **kw):
        testiliik = self.request.params.get('f_testiliik_kood')
        # testiliik peab vastama testityybile
        # kontrollime igaks juhuks ka testityybi kasutamise õigust
        if testiliik == const.TESTILIIK_AVALIK:
            testityyp = const.TESTITYYP_AVALIK
        else:
            testityyp = const.TESTITYYP_EKK
        item = BaseResourceController._create(self, testityyp=testityyp)

        # määrame testile tagasiside malli
        if item.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
            mall = const.TSMALL_PSYH
        elif item.diagnoosiv:
            mall = const.TSMALL_DIAG
        else:
            mall = const.TSMALL_VABA
        item.tagasiside_mall = mall

        item.avaldamistase = const.AVALIK_EKSAM
        item.logi('Loomine', None, None, const.LOG_LEVEL_GRANT)
        
        # testi looja saab kohe testiga seotud isikuks koostaja rollis
        if testiliik == const.TESTILIIK_AVALIK:
            item.add_testiisik(const.GRUPP_T_OMANIK)
        else:
            item.add_testiisik(const.GRUPP_T_KOOSTAJA)
        return item

    def _update(self, item, lang=None):
        oli_rveksam_id = item.rveksam_id
        oli_testiliik = item.testiliik_kood
        oli_avaldamistase = item.avaldamistase
        BaseResourceController._update(self, item, lang)

        if oli_testiliik != item.testiliik_kood:
            # koolipsyhi testi liiki võib muuta ainult admin
            if oli_testiliik == const.TESTILIIK_KOOLIPSYH and not self.c.user.on_admin:
                q = (model.Session.query(model.sa.func.count(model.Sooritaja.id))
                    .filter(model.Sooritaja.test_id==item.id)
                    .filter(model.Sooritaja.staatus>=const.S_STAATUS_POOLELI))
                cnt = q.scalar()
                if cnt:
                    errors = {'f_testiliik_kood': _("Kui koolipsühholoogi testi on juba sooritatud, siis saab selle liiki muuta ainult administraator")}
                    raise ValidationError(self, errors)
            if item.testiliik_kood != const.TESTILIIK_TKY:
                # taustakysitluse seosed on ainult taustakysitluse testiliigi korral
                for r in (item.opetaja_taustakysitlus, item.opilase_taustakysitlus):
                    if r:
                        r.delete()
                        
        if self.c.user.has_permission('ylkvaliteet', const.BT_UPDATE, item):
            kvaliteet = self.request.params.get('kvaliteet_kood')
            # kui kasutajal on õigus
            item.kvaliteet_kood = kvaliteet or None
            
        if oli_rveksam_id != item.rveksam_id:
            # kui test ei ole enam seotud selle tunnistusega, mis varem,
            # siis tuleb tühistada ka rvosaoskused
            for testiosa in item.testiosad:
                if testiosa.rvosaoskus_id:
                    testiosa.rvosaoskus_id = None
                for alatest in testiosa.alatestid:
                    if alatest.rvosaoskus_id:
                        alatest.rvosaoskus_id = None
            
        if item.testiliik_kood == const.TESTILIIK_DIAG2:
            item.diagnoosiv = True
            if item.avaldamistase == const.AVALIK_EKSAM:
                # diag2 testil ei ole testimiskordade sakki ega võimalust
                item.avaldamistase = const.AVALIK_POLE
        if item.diagnoosiv:
            item.give_testiosa()
            
        item.skeeled = ' '.join(self.form.data.get('skeel'))
        item.set_lang()
        t_keeled = item.keeled
        for testiosa in item.testiosad:
            for kvalik in testiosa.komplektivalikud:
                for k in kvalik.komplektid:
                    if item.diagnoosiv:
                        # komplekti keeled alati samad, mis testil, kuna diag2 testil saab olla ainult yks komplekt
                        k.skeeled = item.skeeled
                    else:
                        # kontroll, et ühelgi komplektil poleks keeli, mida testil pole
                        k_keeled = [r for r in k.keeled if r in t_keeled]
                        k.skeeled = ' '.join(k_keeled)

        eeltest = item.eeltest
        if not eeltest and \
               self.c.user.has_permission('korduvsooritatavus', const.BT_UPDATE, item) and \
               oli_avaldamistase in (const.AVALIK_POLE, const.AVALIK_SOORITAJAD, const.AVALIK_OPETAJAD, const.AVALIK_MAARATUD):
            item.from_form(self.form.data, 'r_')
        elif item.testiliik_kood == const.TESTILIIK_DIAG2 and oli_testiliik != const.TESTILIIK_DIAG2 and \
                 oli_avaldamistase not in (const.AVALIK_POLE, const.AVALIK_SOORITAJAD, const.AVALIK_OPETAJAD, const.AVALIK_MAARATUD):
            # kui muudeti d-testiks, siis teeme vaikimisi korduvalt sooritatavaks
            item.korduv_sooritamine = True

        # testiga hinnatavad keeleoskuse tasemed
        cnt = 0
        prev = None
        testitasemed = list()
        for n, r in enumerate(self.form.data.get('t')):
            if r['keeletase_kood']:
                cnt += 1
                testitase = item.give_testitase(cnt)
                testitasemed.append(testitase)
                
                pallid = r['pallid']
                if pallid is not None:
                    if prev is not None and prev <= pallid:
                        errors = {'t-%d.pallid' % n: _("Palun sisestada kõrgem tase enne")}
                        raise ValidationError(self, errors)
                    prev = pallid
                testitase.pallid = pallid
                testitase.keeletase_kood = r['keeletase_kood']
                testitase.aine_kood = item.aine_kood
        for r in list(item.testitasemed):
            if r not in testitasemed:
                r.delete()

        # testi eest antav hinne
        cnt = 0
        prev = None
        testihinded = list()
        for n, r in enumerate(self.form.data.get('h')):
            pallid = r['pallid']
            hinne = r['hinne']
            if pallid is not None:
                testihinne = item.give_testihinne(hinne)
                testihinded.append(testihinne)               
                if pallid is not None:
                    if prev is not None and prev <= pallid:
                        errors = {'h-%d.pallid' % n: _("Palun sisestada kõrgem hinne enne")}
                        raise ValidationError(self, errors)
                    prev = pallid
                testihinne.pallid = pallid
        for r in list(item.testihinded):
            if r not in testihinded:
                r.delete()

        # kursused ja õppeaine nimetused tunnistusel
        testikursused = self.form.data.get('testikursus')
        self._check_kursused(item, testikursused)
        BaseGridController(item.testikursused, model.Testikursus, parent_controller=self, pkey='kursus_kood').save(testikursused)
        
        if item.on_tseis or item.aine_kood == const.AINE_ET2:
            # tasemeeksamite, seaduse tundmise eksamite 
            # ja aine "eesti keel teise keelena" (põhikooli lõpueksamite ja riigieksamite)
            # korral seatakse tulemuste vahemikud ja lävi
            
            vahemikud = self.form.data.get('vahemikud')
            prev = 0
            for n, algus in enumerate(vahemikud):
                if not algus:
                    errors = {'vahemikud-%d' % n: _("Väärtus puudub")}
                    raise ValidationError(self, errors)                    
                elif algus <= prev:
                    errors = {'vahemikud-%d' % n: _("Palun pane vahemikud järjekorda!")}
                    raise ValidationError(self, errors)
                prev = algus

            item.tulemuste_vahemikud_pr = ','.join(map(str,vahemikud))

            # vaikimisi väärtused
            if not item.tulemuste_vahemikud_pr:
                item.tulemuste_vahemikud_pr = '1,50,60,76,91'

            if not item.lavi_pr:
                item.lavi_pr = 60

        # salvestame kooliastmed, kodeerides need maskiks
        kooliastmed = self.form.data.get('aste_kood')
        mask = 0
        for kood in kooliastmed:
            mask += self.c.opt.aste_bit(kood) or 0
        if mask != item.aste_mask:
            item.aste_mask = mask

        # koolispyhholoogi testis toimub alati lahendamine yhekordselt ja yhesuunaliselt
        if item.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
            for testiosa in item.testiosad:
                for alatest in testiosa.alatestid:
                    if not alatest.yhesuunaline:
                        alatest.yhesuunaline = True
                    if not alatest.on_yhekordne:
                        alatest.on_yhekordne = True
        item.arvuta_pallid(False)
        self._update_kogutestid(item)
        self._update_eristuskiri(item)
        item.sum_tahemargid_lang(item.lang)        
        
    def _update_kogutestid(self, item):
        kogud_id = list(map(int, self.request.params.getall('kogud_id') or []))
        kogud = [{'ylesandekogu_id': kogu_id} for kogu_id in kogud_id]
        ctrl = BaseGridController(item.kogutestid, model.Kogutest, None, self, pkey='ylesandekogu_id')        
        ctrl.save(kogud) 

    def _update_eristuskiri(self, item):
        ek = item.eristuskiri
        ek_sisu = self.form.data.get('ek_sisu')
        ek_filedata = self.form.data.get('ek_filedata')
        if ek_filedata == b'' and not ek_sisu:
            if ek:
                ek.delete()
        else:
            if not ek:
                ek = model.Eristuskiri(test=item)
            ek.from_form(self.form.data, 'ek_')
          
    def _update_kopeeri(self, id):            
        """Testi kopeerimine
        """
        item = model.Test.get(id)

        # salastatud ylesannetega testi võib kopeerida ainult koostaja
        # kas olen koostaja?
        dt = date.today()
        q = (model.Session.query(sa.func.count(model.Testiisik.id))
             .filter_by(test_id=item.id)
             .filter_by(kasutaja_id=self.c.user.id)
             .filter(model.Testiisik.kasutajagrupp_id.in_(
                 (const.GRUPP_T_KOOSTAJA, const.GRUPP_T_OMANIK)))
             .filter(model.Testiisik.kehtib_alates<=dt)
             .filter(model.Testiisik.kehtib_kuni>=dt)
             )
        if not q.scalar():
            # ei ole koostaja
            # kas on salastatud ylesandeid?
            q = (model.Session.query(sa.func.count(model.Ylesanne.id))
                 .filter(model.Ylesanne.salastatud!=const.SALASTATUD_POLE)
                 .join(model.Ylesanne.valitudylesanded)
                 .join(model.Valitudylesanne.testiylesanne)
                 .join(model.Testiylesanne.testiosa)
                 .filter(model.Testiosa.test_id==item.id)
                 )
            if q.scalar():
                self.error(_("Puudub õigus kopeerida salastatud ülesannetega testi"))
                return HTTPFound(location=self.url('test', id=item.id))
            
        cp = item.copy()
        cp.eeltest_id = None
        cp.staatus = const.T_STAATUS_KINNITATUD
        if item.testiliik_kood == const.TESTILIIK_DIAG2:
            cp.avaldamistase = const.AVALIK_POLE
        else:
            cp.avaldamistase = const.AVALIK_EKSAM        
        cp.avalik_alates = None
        cp.avalik_kuni = None
        model.Session.flush()

        cp.logi('Loomine koopiana', None, None, const.LOG_LEVEL_GRANT)
        # testi looja saab kohe testiga seotud isikuks koostaja rollis
        cp.add_testiisik(const.GRUPP_T_OMANIK)
        model.Session.commit()
        self.success(_("Testist on tehtud koopia"))
        return HTTPFound(location=self.url('test', id=cp.id))

    def _edit_tky(self, id):
        "Taustaküsitluse testide sidumine"
        item = self.c.item = model.Test.get(id)
        tky = item.opilase_taustakysitlus
        if tky:
            self.c.test2 = tky.opetaja_test
        else:
            tky = item.opetaja_taustakysitlus
            if tky:
                self.error(_("Test on juba õpetaja testina teise testiga seotud!"))
        return self.render_to_response('ekk/testid/yldandmed.tky.mako')

    def _update_tky(self, id):
        "Taustaküsitluse testide sidumine"
        err = None
        item = self.c.item = model.Test.get(id)        
        tky = item.opetaja_taustakysitlus
        if tky:
            err = _("Test on juba õpetaja testina teise testiga seotud!")
        else:
            tky = item.opilase_taustakysitlus
            opetaja_test_id = self.request.params.get('opetaja_test_id')
            if not opetaja_test_id:
                # test ID valimata, seost ei tee
                if tky:
                    tky.delete()
            else:
                # teeme seose
                test2 = model.Test.get(opetaja_test_id)
                if not test2:
                    err = _("Testi {id} ei leitud").format(id=opetaja_test_id)
                elif test2.testiliik_kood != const.TESTILIIK_TKY:
                    err = _("Test {id} ei ole taustaküsitlus").format(id=opetaja_test_id)
                else:
                    if not tky:
                        tky = model.Taustakysitlus(opilase_test_id=item.id)
                    tky.opetaja_test_id = test2.id
        if err:
            self.error(err)
            return self.render_to_response('ekk/testid/yldandmed.tky.mako')
        else:
            model.Session.commit()
            self.c.nosub = True
            return self.edit()
    
    def _delete(self, item):
        params = self.request.params
        if item:
            rc = True
            test_id = item.id
            eeltest = item.eeltest
            dsooritajad = params.get('dsooritajad')

            # kustutame kirjed eksamiserveritest
            q = (model.SessionR.query(sa.func.distinct(model.Sooritaja.klaster_id))
                 .filter_by(test_id=test_id)
                 .filter(model.Sooritaja.klaster_id!=None))
            for klaster_id, in q.all():
                host = model.Klaster.get_host(klaster_id)
                if host:
                    ExamClient(self, host).delete_test(test_id, 0)
            
            # sooritajate kustutamine
            q = (model.Session.query(model.sa.func.count(model.Sooritaja.id))
                 .filter_by(test_id=item.id))
            if q.scalar():
                if not eeltest:
                    if dsooritajad:
                        self.error(_("Sooritajate eemaldamine pole lubatud"))                        
                    else:
                        self.error(_("Testi ei saa kustutada, sest sellele on registreeritud sooritajaid"))
                    rc = False
                else:
                    model.delete_test_sooritajad(item.id)
                    model.Session.flush()
                    
            if dsooritajad:
                # ainult sooritajate kustutamine
                if rc:
                    item = model.Test.get(test_id)
                    # määrame komplektide lukustuse uuesti
                    TestSaga(self).test_check_lukus(item)                    
                    model.Session.commit()
                    self.success(_("Sooritajad on eemaldatud"))                                    
                return self._redirect('show', item.id)
            else:
                # kogu testi kustutamine
                model.delete_test_statistika(item.id)
                model.delete_test_testikohad(item.id)            
                model.Session.flush()

                # testimiskordade kustutamine
                for tk in item.testimiskorrad:
                    if not eeltest:
                        self.error(_("Testi ei saa kustutada, sest sellel on olemas testimiskordi"))                  
                        rc = False
                        break
                    tk.delete()
                if not rc:
                    return self._redirect('show', item.id)

                model.Session.flush()
                item = model.Test.get(test_id)
                TestSaga(self).test_check_lukus(item)                    
                item.delete()
                model.Session.commit()
                self.success(_("Andmed on kustutatud"))

    def _check_kursused(self, item, testikursused):
        kursused = set()
        lubatud_kursused = [r[0] for r in self.c.opt.klread_kood('KURSUS', item.aine_kood, ylem_required=True)]
        for n, r in enumerate(testikursused):
            kursus = r.get('kursus_kood') or None
            if kursus and kursus not in lubatud_kursused:
                kursus = r['kursus_kood'] = None
            if kursus in kursused:
                if kursus:
                    errors = {'testikursus-%d.kursus_kood' % n: _("Peab olema unikaalne")}
                else:
                    errors = {'testikursus-%d.tunnaine_kood' % n: _("Kursusteta aine korral saab ainult üks nimetus olla")}
                raise ValidationError(self, errors)
            if kursus:
                kursused.add(kursus)
            r['aine_kood'] = item.aine_kood

        on_kursused = len(kursused) > 0
        kasutusel = set()
        for ta in item.testiosad:
            on_alatestid = False
            for alatest in ta.alatestid:
                on_alatestid = True
                if on_kursused and not alatest.kursus_kood:
                    alatest.kursus_kood = list(kursused)[0]
                if alatest.kursus_kood and alatest.kursus_kood not in kursused:
                    kasutusel.add(alatest.kursus_nimi or alatest.kursus_kood)
            if not on_alatestid and on_kursused and len(ta.testiylesanded):
                buf = _("Kursuste lisamiseks palun esmalt eemaldada ilma kursuseta ülesanded")
                raise ValidationError(self, {}, buf)                
        if kasutusel:
            buf = _("Kursusi {s} ei saa eemaldada, kuna on alatestides kasutusel").format(s=','.join(kasutusel))
            raise ValidationError(self, {}, buf)
        if on_kursused:
            qnull = (model.Session.query(model.Sooritaja)
                     .filter(model.Sooritaja.test_id==item.id)
                     .filter(model.Sooritaja.kursus_kood==None))
            cnt = qnull.count()
            if cnt:
                if len(kursused) == 1:
                    # omistame selle yhe kursuse kõigile sooritajatele, kellel kursust pole
                    kursus = list(kursused)[0]
                    qnull.update({"kursus_kood": kursus})
                else:
                    buf = _("Kursusi ei saa lisada, kuna on registreeritud ilma kursuseta sooritajaid")
                    raise ValidationError(self, {}, buf)
            qcnt = model.Session.query(model.Sooritaja.kursus_kood).distinct().\
                   filter(model.Sooritaja.test_id==item.id).\
                   filter(~model.Sooritaja.kursus_kood.in_(kursused))
            regatud = [r for r in qcnt.all()]
            if regatud:
                buf = _("Kursusi {s} ei saa eemaldada, kuna neile on registreeritud sooritajaid").format(s=', '.join([r[0] for r in regatud]))
                raise ValidationError(self, {}, buf)
        if not on_kursused:
            cnt = model.Session.query(sa.func.count(model.Sooritaja.id)).\
                  filter(model.Sooritaja.test_id==item.id).\
                  filter(model.Sooritaja.kursus_kood!=None).\
                  scalar()
            if cnt:
                buf = _("Kursusi ei saa eemaldada, kuna on registreeritud kursusega sooritajaid")
                raise ValidationError(self, {}, buf)

    def _download(self, id, format=None):
        """Näita faili"""
        if format == 'raw' and self.c.user.on_admin:
            # testi eksport
            import eis.lib.raw_export as raw_export
            item = model.Test.get(id)            
            filedata = raw_export.export(item, False)
            filename = 'test%s.raw' % id
            mimetype = 'application/octet-stream'
            return utils.download(filedata, filename, mimetype)
        
        # eristuskirja allalaadimine
        ek = (model.Session.query(model.Eristuskiri)
              .filter_by(test_id=id)
              .first())
        if not ek or not ek.has_file:
            raise NotFound('Kirjet %s ei leitud' % id)
        return utils.download(ek.filedata, ek.filename, ek.mimetype)
               
    def _perm_params(self):
        test_id = self.request.matchdict.get('id')
        if test_id:
            return {'obj':model.Test.get(test_id)}

