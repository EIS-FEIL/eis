from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class AmetnikutestidController(BaseResourceController):

    _INDEX_TEMPLATE = '/admin/ametnik.testid.mako'
    _LIST_TEMPLATE = '/admin/ametnik.testid_list.mako'
    _permission = 'ametnikud'
    _actions = 'index'
    _MODEL = model.Test
    _actions = 'index'
    _DEFAULT_SORT = '-test.id'

    def _query(self):
        today = date.today()
        q = (model.Session.query(model.Test.id,
                                 model.Test.nimi)
             #.filter(model.Test.testityyp==const.TESTITYYP_EKK)
             .filter(model.Test.testiisikud.any(
                    sa.and_(model.Testiisik.kasutaja_id==self.c.kasutaja_id,
                            model.Testiisik.kehtib_alates<=today,
                            model.Testiisik.kehtib_kuni>=today)
                    ))
             )

        def is_muutja(t_id):
            q1 = (model.Session.query(model.Testiisik.id)
                  .filter(model.Testiisik.test_id==t_id)
                  .filter(model.Testiisik.kasutajagrupp_id!=const.GRUPP_T_VAATAJA)
                  .filter(model.Testiisik.kasutaja_id==self.c.kasutaja_id)
                  .filter(model.Testiisik.kehtib_alates<=today)
                  .filter(model.Testiisik.kehtib_kuni>=today)
                  )
            return q1.count() > 0
        self.c.is_muutja = is_muutja
        
        return q
    
    def __before__(self):
        self.c.kasutaja_id = int(self.request.matchdict['kasutaja_id'])
        self.c.kasutaja = model.Kasutaja.get(self.c.kasutaja_id)
