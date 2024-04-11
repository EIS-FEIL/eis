from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
_ = i18n._
log = logging.getLogger(__name__)

class JagamisedController(BaseResourceController):

    _permission = 'tookogumikud'

    _MODEL = model.Nimekiri
    _INDEX_TEMPLATE = 'avalik/tookogumikud/tookogumik.mako'
    _EDIT_TEMPLATE = 'avalik/tookogumikud/tookogumik.mako' 
    _LIST_TEMPLATE = 'avalik/tookogumikud/tookogumik.jagamised_list.mako'
    #_DEFAULT_SORT = 'tookogumik.id' # vaikimisi sortimine
    _ignore_default_params = ['csv','xls','max_limit']
    _actions = 'index' # võimalikud tegevused

    def __init__(self, request, parent_handler=None):
        if parent_handler:
            # tegelik kontroller on juba olemas
            self.request = request
            c = self.c = parent_handler.c
            self.response_dict = parent_handler.response_dict
        else:
            BaseResourceController.__init__(self, request)

    def _query(self):
        c = self.c
        Testiruum1 = (model.SessionR.query(sa.func.min(model.Testiruum.id).label('id'))
                      .filter(model.Testiruum.nimekiri_id==model.Nimekiri.id)
                      .subquery()
                      .lateral())
        Sooritajad = (model.SessionR.query(sa.func.count(model.Sooritaja.id).label('cnt'))
                      .filter(model.Sooritaja.nimekiri_id==model.Nimekiri.id)
                      .subquery()
                      .lateral())
        Tehtud = (model.SessionR.query(sa.func.count(model.Sooritaja.id).label('cnt'))
                  .filter(model.Sooritaja.nimekiri_id==model.Nimekiri.id)
                  .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
                  .subquery()
                  .lateral())                                                
        # jagamiste loetelud
        q = (model.SessionR.query(model.Nimekiri,
                                 model.Test,
                                 Testiruum1.columns.id,
                                 Sooritajad.columns.cnt,
                                 Tehtud.columns.cnt)
             .filter(model.Nimekiri.esitaja_kasutaja_id==self.c.user.id)
             .filter(model.Nimekiri.esitaja_koht_id==self.c.user.koht_id)
             .filter(sa.or_(model.Nimekiri.testimiskord_id==None,
                            model.Nimekiri.testimiskord.has(
                                model.Testimiskord.tahis=='EELTEST')))
             .join(model.Nimekiri.test)
             .outerjoin((Testiruum1, sa.sql.expression.literal_column('1')==1))
             .join((Sooritajad, sa.sql.expression.literal_column('1')==1))
             .outerjoin((Tehtud, sa.sql.expression.literal_column('1')==1))
             )
        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        c.max_limit = True
        c.jagamised_lahendamisel = self._search_lahendamisel(q)
        c.jagamised_moodunud = self._search_moodunud(q)
        
    def _index_lahendamisel(self):
        c = self.c
        c.max_limit = bool(self.request.params.get('max_limit'))
        c.jagamised = self._search_lahendamisel(self._query())
        c.jcls = 'lahendamisel'
        return self.render_to_response(self._LIST_TEMPLATE)

    def _index_moodunud(self):
        c = self.c
        c.max_limit = bool(self.request.params.get('max_limit'))        
        c.jagamised = self._search_moodunud(self._query())
        c.jcls = 'moodunud'
        return self.render_to_response(self._LIST_TEMPLATE)

    def _search_lahendamisel(self, q):
        c = self.c
        c.MAX_PAGE = 10
        q1 = (q.filter(sa.or_(model.Nimekiri.kuni == None,
                              model.Nimekiri.kuni >= date.today()))
              .filter(sa.or_(model.Test.avalik_kuni==None,
                             model.Test.avalik_kuni > date.today()))
              .order_by(sa.desc(model.Nimekiri.id))
              )
        if c.max_limit:
            q1 = q1.limit(c.MAX_PAGE)
        return q1.all()
    
    def _search_moodunud(self, q):
        c = self.c
        c.MAX_PAGE = 10
        q1 = (q.filter(sa.or_(model.Nimekiri.kuni < date.today(),
                              model.Test.avalik_kuni < date.today()))
              .order_by(sa.desc(model.Nimekiri.id))
              )
        if c.max_limit:
            q1 = q1.limit(c.MAX_PAGE)
        return q1.all()
          
    def _perm_params(self):
        if not self.c.user.has_permission('tookogumikud', const.BT_INDEX):
            self.error(_('Töökogumikele on ligipääs ainult õpetajatel'))
            return False
        return {'obj':self.c.item}

    def _get_perm_bit(self):
        action = self.c.action
        if action == 'delete':
            tkv_id = self.request.params.get('tkv_id')
            if tkv_id:
                self.c.tkv = model.Tkvaataja.get(tkv_id)
                if self.c.tkv and self.c.tkv.kasutaja_id == self.c.user.id:
                    # on mulle jagamine ja soovin seda jagamist kustutada
                    # selleks piisab, kui mul on töökogumiku vaatamise õigus
                    return const.BT_SHOW
        return super(JagamisedController, self)._get_perm_bit()
    
    def __before__(self):
        id = self.request.matchdict.get('id')
        if id:
            self.c.item = model.Tookogumik.get(id)
        super(JagamisedController, self).__before__()

def get_jagamised(handler):
    ctrl = JagamisedController(handler.request, handler)
    q = ctrl._query()
    ctrl._search(q)
