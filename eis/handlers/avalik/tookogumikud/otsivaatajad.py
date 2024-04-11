# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.lib.basegrid import *
_ = i18n._

log = logging.getLogger(__name__)

class OtsivaatajadController(BaseResourceController):
    """Ülesandega seotud isikud
    """
    _permission = 'tookogumikud'
    _MODEL = model.Tkvaataja
    _INDEX_TEMPLATE = 'avalik/tookogumikud/otsivaataja.mako'
    _LIST_TEMPLATE = 'avalik/tookogumikud/otsivaataja.mako'
    _ITEM_FORM = forms.avalik.tookogumikud.OtsivaatajaForm 
    _ignore_default_params = ['op']
    _DEFAULT_SORT = 'kasutaja.eesnimi,kasutaja.perenimi'

    def _query(self):
        q = (model.SessionR.query(model.Kasutaja, model.Tkvaataja)
             .outerjoin((model.Tkvaataja,
                         sa.and_(model.Tkvaataja.kasutaja_id==model.Kasutaja.id,
                                 model.Tkvaataja.tookogumik_id==self.c.tookogumik.id))
                        )
             .filter(sa.or_(model.Kasutaja.on_labiviija==True,
                            model.Tkvaataja.id!=None))
             )
        # otsime uusi isikuid, kes on läbiviijaid,
        # või juba jagatud kasutajaid, sõltumata sellest, kas on läbiviija
        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        
        if c.jagatud:
            # kuvame isikud, kellele on juba jagatud
            q = q.filter(model.Tkvaataja.id!=None)

        if not c.jagatud:
            if not c.eesnimi or not c.perenimi:
                if c.op == 'otsi':
                    self.error(_('Uutele isikutele jagamiseks palun sisestada nii ees- kui ka perekonnanimi'))
                return
            c.eesnimi = c.eesnimi.replace('_', '').replace('%', '')
            c.perenimi = c.perenimi.replace('_', '').replace('%', '')
        if c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(c.eesnimi))
        if c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(c.perenimi))
        return q

    def _create(self):
        kasutaja_id = int(self.request.params.get('op'))
        item = model.Tkvaataja(tookogumik_id=self.c.tookogumik.id,
                               kasutaja_id=kasutaja_id)
        return item

    def _after_create(self, id):
        return Response(_('Jagamine lisatud'))

    def _after_delete(self, parent_id=None):
        return Response(_('Jagamine eemaldatud'))

    def _perm_params(self):
        if not self.c.tookogumik:
            return False
        return {'obj':self.c.tookogumik}

    def __before__(self):
        """Väärtustame self.c.ylesanne_id
        """
        tk_id = self.request.matchdict.get('tookogumik_id')
        if tk_id:
            self.c.tookogumik = model.Tookogumik.get(tk_id)
        BaseResourceController.__before__(self)
