from eis.lib.baseresource import *
from .koostamine import set_test_staatus, set_test_secret
_ = i18n._

log = logging.getLogger(__name__)

class HulgiController(BaseResourceController):

    _permission = 'ekk-testid'

    _EDIT_TEMPLATE = 'ekk/testid/hulgi.mako' 
    _ITEM_FORM = forms.ekk.testid.HulgiForm

    def _new_d(self):
        self._edit()
        return self.response_dict

    def edit(self):
        self.c.sub = self._get_sub()
        if self.c.sub:
            id = self.request.matchdict.get('id')
            template = eval('self._edit_t_%s' % self.c.sub)(id)
            return self.render_to_response(template)
        d = self._edit_d()
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _edit_d(self):
        id = self.request.matchdict.get('id')
        self._edit()
        return self.response_dict

    def _edit(self, item=None):
        q = (model.Session.query(model.Testiisik, model.Kasutaja.nimi)
             .filter(model.Testiisik.test_id.in_(self.c.t_id))
             .join(model.Testiisik.kasutaja)
             .order_by(model.Kasutaja.nimi,model.Kasutaja.id,
                       model.Testiisik.kasutajagrupp_id))
        data = list()
        prev_kasutaja_id = prev_grupp_id = None
        for yisik, nimi in q.all():
            if prev_kasutaja_id != yisik.kasutaja_id or prev_grupp_id != yisik.kasutajagrupp_id:
                prev_row = [yisik.kasutaja_id, yisik.kasutajagrupp_id, nimi, [yisik]]
                data.append(prev_row)
                prev_kasutaja_id = yisik.kasutaja_id
                prev_grupp_id = yisik.kasutajagrupp_id
            else:
                prev_row[3].append(yisik)
                
        self.c.testiisikud = data

    def _edit_t_aine(self, id):
        self.c.sub = 'aine'
        return 'ekk/testid/hulgi.aine.mako'

    def _edit_t_kvaliteet(self, id):
        return 'ekk/testid/hulgi.kvaliteet.mako'

    def _edit_t_tolge(self, id):
        q = (model.Session.query(model.Test.skeeled)
             .filter(model.Test.id.in_(self.c.t_id)))
        # leiame keeled, mis on kõigis testides olemas ja mida ei saa enam lisada
        keeled = None
        for skeeled, in q.all():
            li = (skeeled or '').split()
            if keeled is None:
                keeled = li
            else:
                keeled = [r for r in keeled if r in li]
        self.c.keeled = keeled
        return 'ekk/testid/hulgi.tolge.mako'

    def _edit_t_olek(self, id):
        return 'ekk/testid/hulgi.olek.mako'

    def _edit_t_autor(self, id):
        return 'ekk/testid/hulgi.autor.mako'

    def _edit_t_aste(self, id):
        return 'ekk/testid/hulgi.aste.mako'

    def _edit_t_testiliik(self, id):
        return 'ekk/testid/hulgi.testiliik.mako'

    def _edit_t_secret(self, id):
        """Salasta
        """
        self.c.sub = 'secret'
        return 'ekk/testid/hulgi.sala.mako'

    def _edit_t_nosecret(self, id):
        """Salasta
        """
        self.c.sub = 'nosecret'
        return 'ekk/testid/hulgi.sala.mako'

    def _delete_isik(self, id):
        kasutaja_id = self.request.params.get('kasutaja_id')
        grupp_id = self.request.params.get('grupp_id')
        q = (model.Testiisik.query
             .filter(model.Testiisik.test_id.in_(self.c.t_id))
             .filter(model.Testiisik.kasutajagrupp_id==grupp_id)
             .filter(model.Testiisik.kasutaja_id==kasutaja_id))
        cnt = 0
        for isik in q.all():
            test = isik.test
            if self.c.user.has_permission('testiroll', const.BT_UPDATE, test):
                test.logi(_("Isiku eemaldamine"),
                          '%s\n%s\n%s' % (isik.kasutajagrupp.nimi,
                                          isik.kasutaja.nimi,
                                          isik.kasutaja.isikukood),
                          None,
                          const.LOG_LEVEL_GRANT)
                isik.delete()
                #test.set_cache_valid()
                cnt += 1
        if cnt:
            model.Session.commit()
            self.success(_("Isik on eemaldatud {n} testist").format(n=cnt))
        return self._redirect('edit', id)

    def update(self):
        id = self.request.matchdict.get('id')
        self.c.sub = self._get_sub()
        err = False
        self.form = Form(self.request, schema=self._ITEM_FORM)
        if self.form.validate():
            try:
                return eval('self._update_%s' % self.c.sub)(id)
            except ValidationError as e:
                self.form.errors = e.errors
                err = True
        if self.form.errors or err:
            model.Session.rollback()
            return self._error_update()

    def _error_update(self):
        id = self.request.matchdict.get('id')
        sub = self._get_sub()
        template = eval('self._edit_t_%s' % sub)(id)
        html = self.form.render(template, extra_info=self.response_dict)
        return Response(html)

    def _update_aine(self, id):
        aine_kood = self.request.params.get('aine_kood')
        muu_aine = []
        for test in self.c.testid:
            if test.aine_kood != aine_kood:
                test.aine_kood = aine_kood
                # kas testis on ylesandeid, mis ei ole antud aines?
                q = (model.Session.query(sa.func.count(model.Ylesanne.id))
                     .join(model.Ylesanne.valitudylesanded)
                     .filter(model.Valitudylesanne.test_id==test.id)
                     .filter(~ model.Ylesanne.ylesandeained.any(
                         model.Ylesandeaine.aine_kood==aine_kood))
                     )
                if q.scalar() > 0:
                    muu_aine.append(str(test.id))

        model.Session.commit()
        self.success()
        if muu_aine:
            s_muu = ', '.join(muu_aine)
            self.notice(_("Testides {idlist} leidus ülesandeid, mis ei ole valitud aines").format(idlist=s_muu))
        return self._redirect('edit', id)

    def _update_olek(self, id):
        staatus = self.request.params.get('staatus')
        staatus = staatus and int(staatus) or None
        avaldamistase = self.request.params.get('avaldamistase')
        avaldamistase = avaldamistase and int(avaldamistase) or None
        markus = self.request.params.get('markus')
        cnt = 0
        if not staatus and not avaldamistase:
            self.error('Olekut ei muudetud')
        else:
            for test in self.c.testid:
                if test.staatus != staatus or test.avaldamistase != avaldamistase:        
                    rc, msg = set_test_staatus(self, test, staatus, avaldamistase, markus, 0, 0)
                    if rc:
                        cnt += 1
                    else:
                        self.error(msg)
                        cnt = 0
                        break
            if cnt:
                model.Session.commit()
            if not self.has_errors():
                self.success(_("Muudeti {n} testi olek").format(n=cnt))
        return self._redirect('edit', id)

    def _update_autor(self, id):
        autor = self.request.params.get('autor')[:128]
        cnt = 0
        for test in self.c.testid:
            if test.autor != autor:
                test.autor = autor
                cnt += 1
        if cnt:
            model.Session.commit()
        if cnt:
            self.success(_("{n} testi muudetud").format(n=cnt))
        return self._redirect('edit', id)

    def _update_secret(self, id):
        """Salastamine
        """
        markus = self.request.params.get('markus')
        if self.request.params.get('secret1'):
            salastatud = const.SALASTATUD_SOORITATAV
        else:
            salastatud = const.SALASTATUD_LOOGILINE
        cnt = 0
        for test in self.c.testid:
            if test.salastatud != salastatud:
                rc, err = set_test_secret(self, test, salastatud, markus)
                if rc:
                    cnt += 1
                else:
                    self.error(err)
                    break
        if not self.has_errors():
            if cnt:
                model.Session.commit()
            self.notice(_("{n} testi on salastatud").format(n=cnt))
        return self._redirect('edit', id)

    def _update_nosecret(self, id):
        cnt = 0
        salastatud = const.SALASTATUD_POLE
        markus = self.request.params.get('markus')
        for test in self.c.testid:
            if test.salastatud in (const.SALASTATUD_LOOGILINE, const.SALASTATUD_SOORITATAV):
                rc, err = set_test_secret(self, test, salastatud, markus)
                if rc:
                    cnt += 1
                else:
                    self.error(err)
                    break
        if not self.has_errors():
            if cnt:
                model.Session.commit()
            self.success(_("{n} testi pole enam salastatud").format(n=cnt))
        return self._redirect('edit', id)

    def _update_aste(self, id):
        kooliastmed = self.request.params.getall('v_aste_kood')
        mask = 0
        for kood in kooliastmed:
            mask += self.c.opt.aste_bit(kood) or 0
            
        cnt = 0
        for test in self.c.testid:
            if mask != test.aste_mask:
                test.aste_mask = mask
        model.Session.commit()
        self.success()
        return self._redirect('edit', id)

    def _update_testiliik(self, id):
        cnt = 0
        testiliik = self.request.params.get('testiliik_kood')
        for test in self.c.testid:
            if test.testiliik_kood != testiliik:
                if test.testiliik_kood == const.TESTILIIK_KOOLIPSYH and not self.c.user.on_admin:
                    # koolipsyhi testi liiki võib muuta ainult admin
                    q = (model.Session.query(model.sa.func.count(model.Sooritaja.id))
                         .filter(model.Sooritaja.test_id==test.id)
                         .filter(model.Sooritaja.staatus>=const.S_STAATUS_POOLELI))
                    cnt = q.scalar()
                    if cnt:
                        self.error(_("Kui koolipsühholoogi testi on juba sooritatud, siis saab selle liiki muuta ainult administraator"))
                        continue

                cnt += 1
                test.testiliik_kood = testiliik
                if testiliik == const.TESTILIIK_DIAG2:
                    test.diagnoosiv = True
                    test.give_testiosa()
                    if test.avaldamistase == const.AVALIK_EKSAM:
                        # diag2 testil ei ole testimiskordade sakki ega võimalust
                        test.avaldamistase = const.AVALIK_POLE
                elif testiliik == const.TESTILIIK_KOOLIPSYH:
                    # koolispyhholoogi testis toimub alati lahendamine yhekordselt ja yhesuunaliselt
                    for testiosa in test.testiosad:
                        for alatest in testiosa.alatestid:
                            if not alatest.yhesuunaline:
                                alatest.yhesuunaline = True
                            if not alatest.on_yhekordne:
                                alatest.on_yhekordne = True
                        
        if cnt:
            model.Session.commit()
        self.success(_("{n} testi muudetud").format(n=cnt))
        return self._redirect('edit', id)

    def _update_tolge(self, id):
        keeled = self.request.params.getall('skeel')
        for test in self.c.testid:
            for lang in keeled:
                if not test.has_lang(lang):
                    if not test.lang:
                        test.lang = lang
                    test.skeeled = (test.skeeled or '') + ' ' + lang
            t_keeled = test.keeled
            for testiosa in test.testiosad:
                for kvalik in testiosa.komplektivalikud:
                    for k in kvalik.komplektid:
                        if test.diagnoosiv:
                            # komplekti keeled alati samad, mis testil, kuna diag2 testil saab olla ainult yks komplekt
                            k.skeeled = test.skeeled
                        else:
                            # kontroll, et ühelgi komplektil poleks keeli, mida testil pole
                            k_keeled = [r for r in k.keeled if r in t_keeled]
                            k.skeeled = ' '.join(k_keeled)
                
        model.Session.commit()
        self.success()
        return self._redirect('edit', id)

    def _update_kvaliteet(self, id):
        kvaliteet = self.request.params.get('kvaliteet_kood')
        for test in self.c.testid:
            if self.c.user.has_permission('ylkvaliteet', const.BT_UPDATE, test):
                test.kvaliteet_kood = kvaliteet or None
        model.Session.commit()
        self.success()
        return self._redirect('edit', id)

    def _update_isik(self, id):            
        """Isiku lisamine ülesandega seotuks
        """
        kasutajagrupp_id = int(self.request.params.get('kasutajagrupp_id'))
        kasutajagrupp = model.Kasutajagrupp.get(kasutajagrupp_id)
        kehtib_kuni = self.form.data['kehtib_kuni']
        isikukoodid = self.request.params.getall('oigus')
        not_added = []
        added = False
        for ik in isikukoodid:
            kasutaja = model.Kasutaja.get_by_ik(ik)
            if kasutaja:
                for test in self.c.testid:
                    if self.c.user.has_permission('testiroll', const.BT_UPDATE, test):
                        if test._on_testiisik(kasutaja.id, kasutajagrupp_id):
                            not_added.append(kasutaja.nimi)
                        else:
                            added = True
                            isik = model.Testiisik(kasutaja=kasutaja,
                                                   kasutajagrupp_id=kasutajagrupp_id,
                                                   kehtib_alates=date.today(),
                                                   kehtib_kuni=kehtib_kuni or const.MAX_DATE)
                            test.testiisikud.append(isik)
                            #test.set_cache_valid()
                            test.logi(_("Isiku lisamine"),
                                      None,
                                      '%s %s\n%s\n%s' % (kasutajagrupp.nimi,
                                                         self.h.str_from_date(kehtib_kuni) or '',
                                                         kasutaja.nimi,
                                                         kasutaja.isikukood),
                                      const.LOG_LEVEL_GRANT)

            model.Session.commit()
           
        if added:
            model.Session.commit()
            self.success()
        return self._redirect('edit', id)
            
    def __before__(self):
        testid_id = self.request.matchdict.get('id')
        if testid_id:
            # edit
            self.c.testid_id = testid_id
            self.c.t_id = testid_id.split('-')
        else:
            # new
            self.c.t_id = self.request.params.getall('t_id')
            self.c.testid_id = '-'.join(self.c.t_id)
        self.c.testid = [model.Test.get(t_id) for t_id in self.c.t_id]
        self.c.can_testhulgi = self.c.user.has_permission('testhulgi', const.BT_UPDATE)

    def _has_permission(self):
        if self.c.can_testhulgi:
            return True
        
        # vajaliku õiguse nimi
        permission = self._get_permission()
        # kas toimub muutmine või vaatamine?
        perm_bit = const.BT_UPDATE
        rc = False
        for test in self.c.testid:
            rc = self.c.user.has_permission(permission, perm_bit, obj=test)
            if not rc:
                # ei lubatud ligipääsu
                self._miss_perm = _("Test {id}").format(id=test.id)
                break
            
        return rc
                              
