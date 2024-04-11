from eis.lib.baseresource import *
from eis.lib.xtee import set_rr_pohiandmed
_ = i18n._

log = logging.getLogger(__name__)

class IsikudController(BaseResourceController):
    """Isikute otsimine soorituskohas õiguste andmiseks
    """
    #_MODEL = model.Testiisik
    _permission = 'kohad'
    _INDEX_TEMPLATE = 'admin/koht.kasutajavalik.mako'
    _LIST_TEMPLATE = 'admin/koht.kasutajavalik.mako'

    def _index_d(self):
        if 'isikukood' in self.request.params:
            # kasutaja on vajutanud nupule Otsi
            # (akna avamisel automaatselt ei otsita)
            q = self._query()
            if not self.form:
                if self.request.params:
                    self.form = Form(self.request, schema=self._SEARCH_FORM, method='GET')
                    if not self.form.validate():
                        return Response(self.form.render(self._INDEX_TEMPLATE, extra_info=self._index_d()))
                    self._copy_search_params()
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
        c = self.c
        self._get_opt_grupid()

        if c.isikukood:
            usp = validators.IsikukoodP(c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))
            if not q.count() and usp.isikukood_ee and self.request.is_ext():
                if set_rr_pohiandmed(self, None, usp.isikukood_ee):
                    model.Session.commit()
        if c.eesnimi:
            like_expr = c.eesnimi
            q = q.filter(model.Kasutaja.eesnimi.ilike(like_expr))
        if c.perenimi:
            like_expr = c.perenimi
            q = q.filter(model.Kasutaja.perenimi.ilike(like_expr))

        if not c.isikukood and not c.perenimi:
            self.error(_("Isikukood või perekonnanimi on vaja ette anda"))
            return None
        return q

    def _get_opt_grupid(self):
        c = self.c
        GRUPP_SEOTUD = 1000 # sellist gruppi pole olemas, on Kasutajakoht kirje
        c.opt_grupid = [(const.GRUPP_OPETAJA, _("Pedagoog"))] + \
            c.opt.get_antav_kooligrupp(c.app_ekk) +\
            [(GRUPP_SEOTUD, _("Soorituskohaga seotud isik"))]

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        self.c.koht = model.Koht.get(self.request.matchdict.get('koht_id'))
        BaseResourceController.__before__(self)

