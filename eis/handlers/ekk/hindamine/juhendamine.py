from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class JuhendamineController(BaseResourceController):
    """Labiviijate juhendamine
    """
    _permission = 'juhendamine'
    _MODEL = model.Valitudylesanne
    _INDEX_TEMPLATE = 'ekk/hindamine/juhendamine.mako'
    _EDIT_TEMPLATE = 'ekk/hindamine/juhendamine.mako'
    _DEFAULT_SORT = 'testiylesanne.alatest_seq, testiylesanne.seq' # vaikimisi sortimine
    _no_paginate = True

    def _query(self):
        VastatudHK = sa.orm.aliased(model.Hindamiskysimus)
        q = (model.Session.query(model.Testiylesanne.tahis, 
                                 model.Testiylesanne.alatest_seq,
                                 model.Testiylesanne.seq,
                                 model.Ylesanne.nimi, 
                                 model.Valitudylesanne.id,
                                 model.Valitudylesanne.ylesanne_id,
                                 model.Komplekt.tahis,
                                 sa.func.count(model.Hindamiskysimus.id),
                                 sa.func.count(VastatudHK.id))
             .join(model.Valitudylesanne.testiylesanne)
             .filter(model.Testiylesanne.testiosa_id==self.c.testiosa.id)
             .join(model.Valitudylesanne.ylesanne)
             .join(model.Valitudylesanne.komplekt)
             .outerjoin((model.Hindamiskysimus,
                        sa.and_(model.Hindamiskysimus.ylesanne_id==model.Valitudylesanne.ylesanne_id,
                                model.Hindamiskysimus.vastus==None)))
             .outerjoin((VastatudHK,
                        sa.and_(VastatudHK.ylesanne_id==model.Valitudylesanne.ylesanne_id,
                                VastatudHK.vastus!=None)))
             )
        return q
             
    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        if self.c.komplekt_id:
            q = q.filter(model.Valitudylesanne.komplekt_id==int(self.c.komplekt_id))
            k = model.Komplekt.get(self.c.komplekt_id)
            if k:
                self.c.komplektivalik_id = k.komplektivalik_id
                self.c.komplektivalik = k.komplektivalik
        elif not self.c.testiosa.on_alatestid:
            self.c.komplektivalik = self.c.testiosa.get_komplektivalik()
            self.c.komplektivalik_id = self.c.komplektivalik and self.c.komplektivalik.id or None
        elif self.c.komplektivalik_id:
            q = q.filter(model.Komplekt.komplektivalik_id==self.c.komplektivalik_id)
            self.c.komplektivalik = model.Komplektivalik.get(self.c.komplektivalik_id)
            
        q = q.group_by(model.Testiylesanne.tahis,
                       model.Testiylesanne.alatest_seq,
                       model.Testiylesanne.seq,
                       model.Ylesanne.nimi,
                       model.Valitudylesanne.id,
                       model.Valitudylesanne.ylesanne_id,
                       model.Komplekt.tahis)
        if self.c.vastamata:
            q = q.having(sa.func.count(model.Hindamiskysimus.id)>0)

        if self.c.csv:
            return self._index_csv(q)
        return q
    
    def _edit(self, item):
        self._index_d() # koostame vy indexi jaoks listi
        self.c.ylesanne = item.ylesanne

    def _edit_vastus(self, id):
        self.c.item = model.Valitudylesanne.get(id)
        hindamiskysimus_id = self.request.params.get('hindamiskysimus_id')
        if hindamiskysimus_id:
            # vastamine
            self.c.hindamiskysimus = model.Hindamiskysimus.get(hindamiskysimus_id)
        else:
            # uue küsimuse lisamine
            self.c.hindamiskysimus = self.c.new_item()
        return self.render_to_response('/ekk/hindamine/hindamiskysimus.mako')

    def _update_vastus(self, id):
        item = model.Valitudylesanne.get(id)
        hindamiskysimus_id = self.request.params.get('hindamiskysimus_id')
        if hindamiskysimus_id:
            # vastamine
            hindamiskysimus = model.Hindamiskysimus.get(hindamiskysimus_id)
        else:
            hindamiskysimus = model.Hindamiskysimus(ylesanne_id=item.ylesanne_id,
                                                    kysija_kasutaja_id=self.c.user.id,
                                                    kysimus=self.request.params.get('kysimus'))
        hindamiskysimus.vastus = self.request.params.get('vastus') or None
        hindamiskysimus.vastaja_kasutaja_id = self.c.user.id
        hindamiskysimus.vastamisaeg = datetime.now()
        model.Session.commit()
        return self._redirect(action='edit', id=id, alatest_id=self.c.alatest_id, komplekt_id=self.c.komplekt_id)

    def _prepare_header(self):
        header = [_("Ülesanne"),
                  _("Küsimus"),
                  _("Komplekt"),
                  _("Vastamata küsimusi"),
                  _("Vastatud küsimusi"),
                  ]
        return header

    def _prepare_item(self, rcd, n):
        ty_tahis, alatest_seq, ty_seq, y_nimi, vy_id, y_id, k_tahis, vastamata, vastatud = rcd
        item = [ty_tahis or '',
                y_nimi,
                k_tahis,
                vastamata or '',
                vastatud or '']
        return item

    def __before__(self):
        c = self.c
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        c.testiosa = c.toimumisaeg.testiosa
        c.alatest_id = self.request.params.get('alatest_id')
        c.komplekt_id = self.request.params.get('komplekt_id')
        c.test = c.testiosa.test

    def _perm_params(self):
        return {'obj':self.c.test}
        
