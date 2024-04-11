from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class AmetnikuylesandedController(BaseResourceController):

    _INDEX_TEMPLATE = '/admin/ametnik.ylesanded.mako'
    _LIST_TEMPLATE = '/admin/ametnik.ylesanded_list.mako'
    _permission = 'ametnikud'
    _actions = 'index'
    _MODEL = model.Ylesanne
    _actions = 'index'
    _DEFAULT_SORT = '-ylesanne.id'

    def _query(self):
        today = date.today()
        q = (model.Session.query(model.Ylesanne.id,
                                 model.Ylesanne.nimi)
             .filter(model.Ylesanne.ylesandeisikud.any(
                    sa.and_(model.Ylesandeisik.kasutaja_id==self.c.kasutaja_id,
                            model.Ylesandeisik.kehtib_alates<=today,
                            model.Ylesandeisik.kehtib_kuni>=today)
                    ))
             )

        def is_muutja(y_id):
            q1 = (model.Session.query(model.Ylesandeisik.id)
                  .filter(model.Ylesandeisik.ylesanne_id==y_id)
                  .filter(model.Ylesandeisik.kasutajagrupp_id!=const.GRUPP_Y_VAATAJA)
                  .filter(model.Ylesandeisik.kasutaja_id==self.c.kasutaja_id)
                  .filter(model.Ylesandeisik.kehtib_alates<=today)
                  .filter(model.Ylesandeisik.kehtib_kuni>=today)
                  )
            return q1.count() > 0
        self.c.is_muutja = is_muutja
        
        return q
    
    def __before__(self):
        self.c.kasutaja_id = int(self.request.matchdict['kasutaja_id'])
        self.c.kasutaja = model.Kasutaja.get(self.c.kasutaja_id)
