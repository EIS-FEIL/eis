from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class KorraldajadController(BaseResourceController):
    """Testiga seotud isikud
    """
    _permission = 'ekk-testid'
    _MODEL = model.Testiisik
    _INDEX_TEMPLATE = 'ekk/testid/korraldaja.mako'
    _get_is_readonly = False
    
    def _index_d(self):
        self.c.test_id = self.c.test.id
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
                    # isikut ei ole EISis, otsime RRist
                    kasutaja = xtee.set_rr_pohiandmed(self, None, usp.isikukood_ee)
                    if kasutaja:
                        model.Session.commit()
        if self.c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(self.c.eesnimi))
        if self.c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(self.c.perenimi))
        if not self.c.isikukood and not self.c.eesnimi and not self.c.perenimi:
            self.error(_("Puuduvad otsingutingimused"))
            return None
        return q

    def _index_file(self):
        return self.render_to_response('ekk/testid/korraldaja.file.mako')

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)
        self.c.komplekt_id = self.request.params.get('komplekt_id')
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}

