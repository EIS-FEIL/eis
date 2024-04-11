from cgi import FieldStorage
from eis.lib.xtee import set_rr_pohiandmed
from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class IsikudController(BaseResourceController):
    """Testiga seotud isikud
    """
    _permission = 'testiroll'
    _MODEL = model.Testiisik
    _INDEX_TEMPLATE = 'ekk/testid/koostamine.isik.mako'
    _LIST_TEMPLATE = 'ekk/testid/koostamine.isik.mako'
    _EDIT_TEMPLATE = 'ekk/testid/koostamine.isik.edit.mako'
    _ITEM_FORM = forms.ekk.testid.KoostamineIsikForm
    _SEARCH_FORM = forms.ekk.testid.KoostamineIsikudForm
    
    def _index_d(self):
        c = self.c
        if 'isikukood' in self.request.params:
            # kasutaja on vajutanud nupule Otsi
            # (akna avamisel automaatselt ei otsita)
            q = self._query()
            if not self.form:
                if self.request.params:
                    self.form = Form(self.request, schema=self._SEARCH_FORM, method='GET')
                    if self.form.validate():
                        self._copy_search_params(self.form.data)
                        try:
                            q = self._search(q)
                        except ValidationError as ex:
                            self.form.errors = ex.errors
                    if self.form.errors:
                        return Response(self.form.render(self._INDEX_TEMPLATE, self.response_dict))

            q = self._order(q)
            c.items = self._paginate(q)
        return self.response_dict

    def _query(self):
        return model.Kasutaja.query

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.isikukood:
            usp = validators.IsikukoodP(c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))
            if not q.count() and usp.isikukood_ee and self.request.is_ext():
                if set_rr_pohiandmed(self, None, usp.isikukood_ee):
                    model.Session.commit()
        elif not self.c.user.has_permission('testiroll', const.BT_CREATE, gtyyp=const.USER_TYPE_EKK):
            # avalik kasutaja saab otsida ainult isikukoodi järgi
            raise ValidationError(self, errors={'isikukood': _("Palun sisestada isikukood")})
        if c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(c.eesnimi))
        if c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(c.perenimi))

        now = datetime.now()
        today = date.today()
        if c.test:
            testityyp = c.test.testityyp
        else:
            testityyp = c.testid[0].testityyp
        if c.ametnik and testityyp == const.TESTITYYP_AVALIK:
            # peab olema avaliku testi koostaja roll
            q = q.filter(
                model.Kasutaja.kasutajarollid.any(
                    sa.and_(model.Kasutajaroll.kasutajagrupp_id==const.GRUPP_OMATEST,
                            model.Kasutajaroll.kehtib_kuni>=today)
                    ))
        elif c.ametnik:
            # peab olema mõni EKK vaate grupp
            q = q.filter(
                model.Kasutaja.kasutajarollid.any(
                    sa.and_(
                        model.Kasutajaroll.kasutajagrupp.has(
                            model.Kasutajagrupp.tyyp==const.USER_TYPE_EKK),
                        model.Kasutajaroll.kehtib_kuni>=today)
                    ))
        else:
            # peab olema õpetaja
            q = q.filter(sa.or_(
                model.Kasutaja.pedagoogid.any(
                    sa.or_(model.Pedagoog.kehtib_kuni==None,
                           model.Pedagoog.kehtib_kuni>=today)),
                sa.exists().where(sa.and_(
                    model.Kasutajaroll.kasutaja_id==model.Kasutaja.id,
                    model.Kasutajaroll.kehtib_alates<=now,
                    model.Kasutajaroll.kehtib_kuni>=now,
                    model.Kasutajaroll.kasutajagrupp_id==model.Kasutajagrupp_oigus.kasutajagrupp_id,
                    model.Kasutajagrupp_oigus.nimi=='tookogumikud'))
                ))
        c.mitteametnik = not c.ametnik
        return q
    
    def _create(self):            
        """Isiku lisamine testiga seotuks
        """
        kasutajagrupp_id = self.form.data['kasutajagrupp_id']
        kehtib_kuni = self.form.data['kehtib_kuni']
        kk_id = self.request.params.getall('oigus')
        self._add_roles(kk_id, kasutajagrupp_id, kehtib_kuni)
        
    def _add_roles(self, kk_id, kasutajagrupp_id, kehtib_kuni, check_pedag=False):
        test = self.c.test
        kasutajagrupp = model.Kasutajagrupp.get(kasutajagrupp_id)
        not_added = []
        not_pedag = []
        added = False
        for k_id in kk_id:
            kasutaja = model.Kasutaja.get(k_id)
            if kasutaja:
                isik = test._on_testiisik(kasutaja.id, kasutajagrupp_id)
                if isik:
                    not_added.append(kasutaja.nimi)
                elif check_pedag and not kasutaja.on_kehtiv_tookogumikud:
                    not_pedag.append(ik)
                else:
                    added = True
                    isik = model.Testiisik(kasutaja=kasutaja,
                                           kasutajagrupp_id=kasutajagrupp_id,
                                           kehtib_alates=date.today(),
                                           kehtib_kuni=kehtib_kuni or const.MAX_DATE)
                    test.testiisikud.append(isik)
                    test.logi(_("Isiku lisamine"),
                              None,
                              '%s %s\n%s\n%s' % (kasutajagrupp.nimi,
                                                 self.h.str_from_date(kehtib_kuni) or '',
                                                 kasutaja.nimi,
                                                 kasutaja.isikukood),
                              const.LOG_LEVEL_GRANT)
        if not added:
            buf = _("Kasutajarolli ei antud")
            self.error(buf)
        if not_pedag:
            buf = _("Kasutaja {s} ei ole pedagoog").format(s=', '.join(not_pedag))
            self.error(buf)
        if not_added:
            buf = _("Kasutaja {s} on selles rollis juba testiga seotud").format(s=', '.join(not_added))
            self.error(buf)
        return added
    
    def _update(self, item):            
        """Isiku lisamine testiga seotuks
        """
        kasutajagrupp_id = self.form.data['kasutajagrupp_id']
        kehtib_kuni = self.form.data['kehtib_kuni']
        test = self.c.test
        old_g = item.kasutajagrupp
        new_g = model.Kasutajagrupp.get(kasutajagrupp_id)
        kasutaja = item.kasutaja
        buf1 = '%s %s\n%s\n%s' % (old_g.nimi,
                                  self.h.str_from_date(item.kehtib_kuni_ui) or '',
                                  kasutaja.nimi,
                                  kasutaja.isikukood)
        buf2 = '%s %s\n%s\n%s' % (new_g.nimi,
                                  self.h.str_from_date(kehtib_kuni) or '',
                                  kasutaja.nimi,
                                  kasutaja.isikukood)
        test.logi(_("Õiguste muutmine"), buf1, buf2, const.LOG_LEVEL_GRANT)
        item.kasutajagrupp_id = kasutajagrupp_id
        item.kehtib_kuni = kehtib_kuni or const.MAX_DATE

    def _after_update(self, id):
        return HTTPFound(location=self.url('test_edit_koostamine', id=self.c.test.id))

    def _index_fail(self):
        """Isikute lisamine failist.
        """
        return self.render_to_response('/ekk/testid/koostamine.isikfail.mako')

    def _create_fail(self):
        """Isikute lisamine failist.
        """
        self.form = Form(self.request, schema=forms.ekk.testid.KoostamineIsikFailForm)
        if self.form.validate():
            try:
                self._create_fail_ex()
            except ValidationError as e:
                self.form.errors = e.errors
        if self.form.errors:
            for key, value in self.form.errors.items():
                self.error(value)
            model.Session.rollback()

        return self._after_update(None)

    def _create_fail_ex(self):
        """Isikute lisamine failist
        """
        kehtib_kuni = self.form.data['kehtib_kuni']
        value = self.request.params.get('fail')
        if not isinstance(value, FieldStorage):
            raise ValidationError(self, {'fail': 'Palun sisestada fail'})

        # value on FieldStorage objekt
        value = value.value
        isikukoodid = []
        for ind, line in enumerate(value.splitlines()):
            line = utils.guess_decode(line).strip()
            if line:
                isikukoodid.append(line)
        if isikukoodid:
            if self._add_roles(isikukoodid, const.GRUPP_T_KORRALDAJA, kehtib_kuni, True):
                model.Session.commit()
                self.success()
        
    def _delete(self, item):
        isik = item
        test = self.c.test
        if isik and isik.test_id == test.id:
            test.logi(_("Isiku eemaldamine"),
                      '%s\n%s\n%s' % (isik.kasutajagrupp.nimi,
                                      isik.kasutaja.nimi,
                                      isik.kasutaja.isikukood),
                      None,
                      const.LOG_LEVEL_GRANT)
            isik.delete()
            model.Session.commit()
            self.success(_("Andmed on kustutatud"))

    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self.url('test_edit_koostamine', id=self.c.test.id))
        
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)
        self.c.test_id = self.c.test.id
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}

