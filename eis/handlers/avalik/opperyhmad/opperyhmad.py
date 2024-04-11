from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class OpperyhmadController(BaseResourceController):

    _permission = 'klass'

    _MODEL = model.Opperyhm
    _INDEX_TEMPLATE = 'avalik/opperyhmad/opperyhmad.mako'
    _NEW_TEMPLATE = 'avalik/opperyhmad/opperyhm.new.mako'
    _EDIT_TEMPLATE = 'avalik/opperyhmad/opperyhmad.mako' 
    _DEFAULT_SORT = '-opperyhm.id' # vaikimisi sortimine

    def _query(self):
        q = (model.SessionR.query(model.Opperyhm)
             .filter(model.Opperyhm.kasutaja_id==self.c.user.id)
             .filter(model.Opperyhm.koht_id==self.c.user.koht_id)
             )
        return q

    def _index_d(self):
        self.c.item = self._edit(None)
        return self.response_dict

    def new(self):
        d = self._new_d()
        if isinstance(d, dict):
            return self.render_to_response(self._NEW_TEMPLATE)
        else:
            return d

    def _edit_nimi(self, id):
        return self.render_to_response(self._NEW_TEMPLATE)

    def _edit(self, item):
        c = self.c
        q = self._query()
        c.items = q.order_by(sa.desc(model.Opperyhm.id))        
        if not item:
            for r in c.items:
                item = r
                break
        if item:
            q = (model.Session.query(model.Opperyhmaliige.id,
                                     model.Kasutaja.isikukood,
                                     model.Kasutaja.nimi,
                                     model.Opilane.oppekeel,
                                     model.Opilane.klass,
                                     model.Opilane.paralleel)
                 .filter(model.Opperyhmaliige.opperyhm_id==item.id)
                 .join(model.Opperyhmaliige.kasutaja)
                 .outerjoin((model.Opilane,
                             sa.and_(model.Opilane.kasutaja_id==model.Kasutaja.id,
                                     model.Opilane.on_lopetanud==False)))
                 .order_by(model.Kasutaja.nimi)
                 )
            c.ryhmaliikmed = list(q.all())

            q = (model.Session.query(model.Nimekiri.id,
                                     model.Test.id,
                                     model.Test.nimi,
                                     model.Test.aine_kood,
                                     sa.func.count(sa.distinct(model.Testiylesanne.id)),
                                     sa.func.count(sa.distinct(model.Sooritaja.id)))
                 .join(model.Test.sooritajad)
                 .filter(sa.exists().where(
                     sa.and_(model.Opperyhmaliige.kasutaja_id==model.Sooritaja.kasutaja_id,
                             model.Opperyhmaliige.opperyhm_id==item.id))
                         )
                 .join(model.Sooritaja.nimekiri)
                 .filter(model.Nimekiri.esitaja_kasutaja_id==c.user.id)
                 .filter(model.Nimekiri.esitaja_koht_id==c.user.koht_id)
                 .join(model.Test.testiosad)
                 .join(model.Testiosa.testiylesanded)
                 .filter(model.Nimekiri.created>(date.today()-timedelta(days=365)))
                 .group_by(model.Test.nimi,
                           model.Test.aine_kood,
                           model.Test.id,
                           model.Nimekiri.id)
                 .order_by(sa.desc(model.Nimekiri.id))
                 )
            c.ryhmatood = q.all()
            #model.log_query(q)
        return item
    
    def _create(self, **kw):
        kw['kasutaja_id'] = self.c.user.id
        kw['koht_id'] = self.c.user.koht_id
        item = BaseResourceController._create(self, **kw)
        return item

    def _perm_params(self):
        if not self.c.user.koht_id:
            return False
        return {'obj':self.c.item}
   
    def __before__(self):
        id = self.request.matchdict.get('id')
        if id:
            self.c.item = model.Opperyhm.get(id)
        super(OpperyhmadController, self).__before__()
