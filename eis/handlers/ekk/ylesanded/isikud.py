from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class IsikudController(BaseResourceController):
    """Ülesandega seotud isikud
    """
    _MODEL = model.Ylesandeisik
    _INDEX_TEMPLATE = 'ekk/ylesanded/koostamine.isik.mako'
    _LIST_TEMPLATE = 'ekk/ylesanded/koostamine.isik.mako'
    _EDIT_TEMPLATE = 'ekk/ylesanded/koostamine.isik.edit.mako'
    _ITEM_FORM = forms.ekk.ylesanded.KoostamineIsikForm 
    _permission = 'ylesanderoll'
    
    def _index_d(self):
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
                        return Response(self.form.render(self._INDEX_TEMPLATE, extra_info=self.response_dict))

            q = self._order(q)
            self.c.items = self._paginate(q)
        return self.response_dict

    def _query(self):
        return model.Kasutaja.query

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        isikukood = self.request.params.get('isikukood')
        eesnimi = self.request.params.get('eesnimi')
        perenimi = self.request.params.get('perenimi')
        if isikukood:
            q = q.filter(eis.forms.validators.IsikukoodP(isikukood)
                         .filter(model.Kasutaja))
        elif not self.c.user.has_permission('ylesanderoll', const.BT_CREATE, gtyyp=const.USER_TYPE_EKK):
            # avalik kasutaja saab otsida ainult isikukoodi järgi
            raise ValidationError(self, errors={'isikukood': _("Palun sisestada isikukood")})
        if eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(eesnimi))
        if perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(perenimi))
        return q

    def _create(self):            
        """Isiku lisamine ülesandega seotuks
        """
        ylesanne = self.c.ylesanne
        kasutajagrupp_id = self.form.data['kasutajagrupp_id']
        kehtib_kuni = self.form.data['kehtib_kuni']
        kasutajagrupp = model.Kasutajagrupp.get(kasutajagrupp_id)
        kk_id = self.request.params.getall('oigus')
        not_added = []
        added = False
        for k_id in kk_id:
            kasutaja = model.Kasutaja.get(k_id)
            if kasutaja:
                if ylesanne._on_ylesandeisik(kasutaja.id, kasutajagrupp_id):
                    not_added.append(kasutaja.nimi)
                else:
                    added = True
                    isik = model.Ylesandeisik(kasutaja=kasutaja,
                                              kasutajagrupp_id=kasutajagrupp_id,
                                              kehtib_alates=date.today(),
                                              kehtib_kuni=kehtib_kuni or const.MAX_DATE)
                    ylesanne.ylesandeisikud.append(isik)
                    ylesanne.set_cache_valid()
                    ylesanne.logi(_("Isiku lisamine"),
                                  None,
                                  '%s %s\n%s\n%s' % (kasutajagrupp.nimi,
                                                     self.h.str_from_date(kehtib_kuni) or '',
                                                     kasutaja.nimi,
                                                     kasutaja.isikukood),
                                  const.LOG_LEVEL_GRANT)

            
        if not_added:
            buf = _("Kasutaja {s} on selles rollis juba ülesandega seotud").format(s=', '.join(not_added))
            self.error(buf)
        if added:
            if kasutajagrupp_id == const.GRUPP_Y_TOIMETAJA:
                versioon = model.Ylesandeversioon.add(ylesanne)                

    def _update(self, item):            
        """Isiku lisamine ülesandega seotuks
        """
        kasutajagrupp_id = self.form.data['kasutajagrupp_id']
        kehtib_kuni = self.form.data['kehtib_kuni']
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
        self.c.ylesanne.logi(_("Õiguste muutmine"), buf1, buf2, const.LOG_LEVEL_GRANT)
        item.kasutajagrupp_id = kasutajagrupp_id
        item.kehtib_kuni = kehtib_kuni or const.MAX_DATE

    def _after_update(self, id):
        self.success()
        return HTTPFound(location=self.url('ylesanded_edit_koostamine', id=self.c.ylesanne.id))

    def _delete(self, item):
        isik = item
        if isik and isik.ylesanne_id == self.c.ylesanne.id:
            self.c.ylesanne.logi(_("Isiku eemaldamine"),
                                 '%s\n%s\n%s' % (isik.kasutajagrupp.nimi,
                                                 isik.kasutaja.nimi,
                                                 isik.kasutaja.isikukood),
                                 None,
                                 const.LOG_LEVEL_GRANT)
            self.c.ylesanne.set_cache_valid()
            isik.delete()
            model.Session.commit()
            self.success(_("Andmed on kustutatud"))

    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self.url('ylesanded_edit_koostamine', id=self.c.ylesanne.id))
 
    def __before__(self):
        """Väärtustame self.c.ylesanne_id
        """
        self.c.ylesanne_id = self.request.matchdict.get('ylesanne_id')
        self.c.ylesanne = model.Ylesanne.get(self.c.ylesanne_id)
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.ylesanne}
