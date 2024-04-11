from eis.lib.baseresource import *

log = logging.getLogger(__name__)
_ = i18n._
class IsikudController(BaseResourceController):
    """Korraldajad
    """
    _permission = 'testid'
    _MODEL = model.Testiisik
    _INDEX_TEMPLATE = 'avalik/testid/isik.mako'
    _actions = 'index' # võimalikud tegevused
    
    def _index_d(self):
        self.c.test_id = self.c.test.id
        self.c.grupp_id = self.request.params.get('grupp_id')
        if 'isikukood' in self.request.params:
            # kasutaja on vajutanud nupule Otsi
            # (akna avamisel automaatselt ei otsita)
            q = self._query()
            if not self.form:
                if self.request.params:
                    self.form = Form(self.request, schema=self._SEARCH_FORM)
                    if not self.form.validate():
                        return Response(self.form.render(self._INDEX_TEMPLATE, extra_info=self.response_dict))

                    self._copy_search_params(self.form.data)
                    q = self._search(q)

            if q:
                q = self._order(q)
                if q.count() == 0 and self.c.isikukood:
                    usp = eis.forms.validators.IsikukoodP(self.c.isikukood)
                    if usp.isikukood_ee and self.request.is_ext():
                        log.debug('otsime RRist')
                        error, data = xtee.rr_pohiandmed(self, usp.isikukood_ee)
                        if error:
                            self.error(error)
                        if data:
                            self.c.items = [NewItem(eesnimi=data['eesnimi'], 
                                                    perenimi=data['perenimi'], 
                                                    isikukood=usp.isikukood_ee)]
                else:
                    self.c.items = self._paginate(q)

        return self.response_dict

    def _query(self):
        return model.Kasutaja.query

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.isikukood:
            q = q.filter(eis.forms.validators.IsikukoodP(c.isikukood)
                         .filter(model.Kasutaja))            
        if c.eesnimi:
            like_expr = c.eesnimi
            q = q.filter(model.Kasutaja.eesnimi.ilike(like_expr))
        if c.perenimi:
            like_expr = c.perenimi
            q = q.filter(model.Kasutaja.perenimi.ilike(like_expr))

        if not c.isikukood and not c.perenimi:
            self.error(_('Isikukood või perekonnanimi on vaja ette anda'))
            return None
        return q

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        self.c.test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(self.c.test_id)
        self.c.testiruum_id = self.request.matchdict.get('testiruum_id')
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}

        
