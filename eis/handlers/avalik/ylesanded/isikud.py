from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class IsikudController(BaseResourceController):
    """Ülesandega seotud isikud
    """
    _MODEL = model.Ylesandeisik
    _INDEX_TEMPLATE = 'avalik/ylesanded/yldandmed.isik.mako'
    _LIST_TEMPLATE = 'avalik/ylesanded/yldandmed.isik.mako'
    _SEARCH_FORM = forms.avalik.ylesanded.IsikudForm 
    _permission = 'avylesanded'
    
    def _index_d(self):
        if 'isikukood' in self.request.params:
            # kasutaja on vajutanud nupule Otsi
            # (akna avamisel automaatselt ei otsita)
            q = self._query()
            if not self.form:
                if self.request.params:
                    self.form = Form(self.request, schema=self._SEARCH_FORM, method='GET')
                    if not self.form.validate():
                        return Response(self.form.render(self._INDEX_TEMPLATE, extra_info=self.response_dict))
                    self._copy_search_params(self.form.data)
                    q = self._search(q)
                if q:
                    q = self._order(q)
                    self.c.items = self._paginate(q)

        return self.response_dict

    def _query(self):
        return model.Kasutaja.query

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.isikukood:
            usp = eis.forms.validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))
            if not q.count() and usp.isikukood_ee:
                rahvastikuregister.set_rr_pohiandmed(self, None, isikukood=usp.isikukood_ee, reg=reg)
                model.Session.commit()

        if self.c.eesnimi:
            like_expr = self.c.eesnimi
            q = q.filter(model.Kasutaja.eesnimi.ilike(like_expr))
        if self.c.perenimi:
            like_expr = self.c.perenimi
            q = q.filter(model.Kasutaja.perenimi.ilike(like_expr))

        if not self.c.isikukood and not self.c.perenimi:
            self.error(_('Isikukood või perekonnanimi on vaja ette anda'))
            return None
        return q

    def _create(self):            
        """Isiku lisamine ülesandega seotuks
        """
        ylesanne = self.c.ylesanne
        kasutajagrupp_id = const.GRUPP_Y_KOOSTAJA
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
                                              kehtib_kuni=const.MAX_DATE)
                    ylesanne.ylesandeisikud.append(isik)
                    ylesanne.set_cache_valid()
                    ylesanne.logi(_("Isiku lisamine"),
                                  None,
                                  '%s\n%s\n%s' % (kasutajagrupp.nimi,
                                                  kasutaja.nimi,
                                                  kasutaja.isikukood),
                                  const.LOG_LEVEL_GRANT)

            
        if not_added:
            buf = _("Kasutaja {s} on selles rollis juba ülesandega seotud").format(s=', '.join(not_added))
            self.error(buf)


    def _after_update(self, id):
        self.success()
        return HTTPFound(location=self.url('edit_ylesanne', id=self.c.ylesanne.id))

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
        return HTTPFound(location=self.url('edit_ylesanne', id=self.c.ylesanne.id))
 
    def __before__(self):
        """Väärtustame self.c.ylesanne_id
        """
        self.c.ylesanne_id = self.request.matchdict.get('ylesanne_id')
        self.c.ylesanne = model.Ylesanne.get(self.c.ylesanne_id)
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.ylesanne}
