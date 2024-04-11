from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class ToohindamisedController(BaseResourceController):
    "Tööde kaupa hindamine"
    _permission = 'thindamine'
    _MODEL = model.Sooritus
    _INDEX_TEMPLATE = 'avalik/thindamine/toohindamised.mako'
    _DEFAULT_SORT = 'sooritaja.perenimi,sooritaja.eesnimi'
    _no_paginate = True
    _get_is_readonly = False
    _actions = 'index'

    def _query(self):
        q = model.SessionR.query(model.Sooritus, 
                                model.Sooritaja.eesnimi,
                                model.Sooritaja.perenimi,
                                model.Hindamisolek.mittekasitsi,
                                model.Hindamine.id)
        q = (q.filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
             .join(model.Sooritus.sooritaja)
             .outerjoin((model.Hindamisolek,
                         sa.and_(model.Hindamisolek.sooritus_id==model.Sooritus.id,
                                 model.Hindamisolek.hindamiskogum_id==None)))
             .outerjoin((model.Hindamine,
                         sa.and_(model.Hindamine.hindamisolek_id==model.Hindamisolek.id,
                                 model.Hindamine.hindaja_kasutaja_id==self.c.user.id)))
             )       
        return q
    
    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        q = self._filter(q)
        self._query_sooritused()
        return q

    def _filter(self, q):
        q = q.filter(model.Sooritus.testiruum_id==self.c.testiruum.id)
        return q

    def _query_sooritused(self):
        c = self.c
        # päritakse sooritajate nimekiri

        # päritakse tulemuste tabel
        q = model.SessionR.query(model.Sooritus.id,
                                model.Testiylesanne.alatest_seq,
                                model.Testiylesanne.seq,
                                model.Ylesandevastus.valitudylesanne_id,
                                model.Ylesandevastus.pallid,
                                model.Ylesandehinne.pallid,
                                model.Ylesandehinne.probleem_varv)
        q = self._filter(q)

        q = (q.filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
             .join((model.Ylesandevastus,
                    model.Ylesandevastus.sooritus_id==model.Sooritus.id))
             .filter(model.Ylesandevastus.kehtiv==True)
             .join((model.Testiylesanne,
                    model.Testiylesanne.id==model.Ylesandevastus.testiylesanne_id))
             .filter(model.Testiylesanne.arvutihinnatav==False)
             .outerjoin((model.Ylesandehinne,
                         sa.and_(model.Ylesandehinne.ylesandevastus_id==model.Ylesandevastus.id,
                                 model.Ylesandehinne.hindamine.has(
                                     model.Hindamine.hindaja_kasutaja_id==c.user.id)
                         )))
             )
        if c.test.on_jagatudtoo:        
            q = q.filter(model.Ylesandevastus.muudetav==False)

        res = {}
        for rcd in q.all():
            sooritus_id, alatest_seq, ty_seq, vy_id, y_pallid, yh_pallid, probleem_varv = rcd
            if sooritus_id not in res:
                res[sooritus_id] = {}
            if y_pallid is None and not probleem_varv:
                y_pallid = yh_pallid
            res[sooritus_id][(alatest_seq, ty_seq)] = (y_pallid, probleem_varv)

        self.c.res = res
 
    def __before__(self):
        c = self.c
        c.testiruum_id = self.request.matchdict.get('testiruum_id')
        c.testiruum = model.Testiruum.get(c.testiruum_id)
        c.nimekiri = c.testiruum.nimekiri
        c.testiosa = c.testiruum.testikoht.testiosa
        c.test = c.testiosa.test
        c.test_id = self.request.matchdict.get('test_id')
        c.hindaja = c.testiruum.get_labiviija(const.GRUPP_HINDAJA_K, c.user.id)

        c.cannot_edit = False
        if c.hindaja:
            # töökaupa ei või hinnata, kui ei ole lubatud kõiki ylesandeid hinnata
            li = []
            for ly in c.hindaja.labiviijaylesanded:
                li.append(ly.testiylesanne_id)
                c.cannot_edit = True
            c.lubatud_ty_id = li

    def _perm_params(self):
        c = self.c
        nimekiri = c.testiruum.nimekiri
        if not nimekiri:
            return False
        return {'obj':nimekiri}
