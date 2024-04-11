from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class TestinimekirjadController(BaseResourceController):
    "EKK toe ligipääs avaliku vaate testinimekirjadele"
    _MODEL = model.Nimekiri
    _SEARCH_FORM = forms.avalik.testid.TestinimekirjadForm
    _INDEX_TEMPLATE = 'avalik/testinimekirjad/testinimekirjad.mako'
    _LIST_TEMPLATE = 'avalik/testinimekirjad/testinimekirjad_list.mako'
    _DEFAULT_SORT = '-nimekiri.id'
    _actions = 'index'
    _permission = 'avtugi'

    def _query(self):
        q = (model.Session.query(model.Testiruum.id,
                                 model.Nimekiri.id,
                                 model.Nimekiri.nimi,
                                 model.Nimekiri.test_id,
                                 model.Nimekiri.alates,
                                 model.Nimekiri.kuni,
                                 model.Test.nimi,
                                 model.Kasutaja.nimi,
                                 model.Koht.nimi)
             .join(model.Testiruum.nimekiri)
             .join(model.Nimekiri.esitaja_kasutaja)
             .outerjoin(model.Nimekiri.esitaja_koht)
             .join(model.Nimekiri.test)
             .filter(model.Nimekiri.testimiskord_id==None)
             .filter(model.Test.testiliik_kood!=const.TESTILIIK_KOOLIPSYH)
             )
        return q

    def _search_default(self, q):
        return
    
    def _search(self, q):
        c = self.c
        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item

        if c.isikukood:
            q = q.filter(eis.forms.validators.IsikukoodP(c.isikukood)
                         .filter(model.Kasutaja))
        if c.nimi:
            q = q.filter(model.Kasutaja.nimi.ilike(c.nimi))
        if c.test_id:
            q = q.filter(model.Test.id==c.test_id)
        if c.aine:
            q = q.filter(model.Test.aine_kood==c.aine)
        return q

    def _prepare_header(self):
        "Loetelu päis"
        li = [('kasutaja.nimi', _("Läbiviija")),
              ('test.id', _("Testi ID")),
              ('test.nimi', _("Testi nimi")),
              ('nimekiri.nimi', _("Nimekiri")),
              ('nimekiri.alates', _("Aeg")),
              ('koht.nimi', _("Kool")),
              ]
        return li

    def _prepare_item(self, rcd, n=None):
        "Loetelu rida"
        testiruum_id, nk_id, nk_nimi, test_id, alates, kuni, test_nimi, k_nimi, koht_nimi = rcd
        aeg = ''
        if alates:
            aeg += self.h.str_from_date(alates)
        if kuni:
            aeg += ' - ' + self.h.str_from_date(kuni)
        item = [k_nimi,
                test_id,
                test_nimi,
                nk_nimi,
                aeg,
                koht_nimi]
        url = self.url('test_nimekiri', test_id=test_id, testiruum_id=testiruum_id, id=nk_id)
        return item, url
    
