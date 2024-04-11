from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class YlesandehindamisedController(BaseResourceController):
    "Ülesannete kaupa hindamine"
    _permission = 'thindamine'
    _MODEL = model.Valitudylesanne
    _INDEX_TEMPLATE = 'avalik/thindamine/ylesandehindamised.mako'
    _DEFAULT_SORT = 'testiylesanne.alatest_seq, testiylesanne.seq' # vaikimisi sortimine
    _no_paginate = True
    _get_is_readonly = False
    _actions = 'index'

    def _query(self):
        c = self.c
        q = (model.Session.query(model.Testiylesanne.tahis,
                                 model.Ylesanne.nimi,
                                 model.Ylesanne.id,
                                 model.Valitudylesanne.id)
             .filter(model.Testiylesanne.testiosa_id == c.testiosa.id)
             .join(model.Testiylesanne.valitudylesanded)
             .join(model.Valitudylesanne.ylesanne)
             .filter(model.Testiylesanne.liik == const.TY_LIIK_Y)
             .filter(model.Ylesanne.arvutihinnatav==False)
             )
        return q
    
    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        if c.hindaja:
            q1 = (model.Session.query(model.Labiviijaylesanne.testiylesanne_id)
                  .filter_by(labiviija_id=c.hindaja.id))
            tyy_id = [ty_id for ty_id, in q1.all()]
            if tyy_id:
                # võib ainult osasid ylesandeid hinnata
                q = q.filter(model.Testiylesanne.id.in_(tyy_id))
        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item
        self._get_tab_urls()
        return q

    def _get_tab_urls(self):
        # funktsioon, mis genereerib lingi ylesandele
        from .toohindamine import get_tab_urls
        get_tab_urls(self, self.c)

    def _prepare_header(self):
        header = [('testiylesanne.alatest_seq,testiylesanne.seq,valitudylesanne.seq', _("Jrk")),
                  ('ylesanne.nimi', _("Ülesanne")),
                  (None, _("Hindamisjuhend")),
                  (None, _("Hindamata ülesannete arv")),
                  (None, _("Hindamine pooleli")),
                  (None, _("Hinnatud ülesannete arv")),
                  (None, ''),
                  ]
        return header

    def _prepare_item(self, rcd, is_html=False):
        c = self.c
        ty_tahis, y_nimi, y_id, vy_id = rcd

        q = (model.Session.query(sa.func.count(model.Ylesandevastus.id))
             .join((model.Sooritus, model.Sooritus.id==model.Ylesandevastus.sooritus_id))
             .filter(model.Ylesandevastus.valitudylesanne_id==vy_id)
             .filter(model.Sooritus.testiruum_id==c.testiruum.id)
             .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Ylesandevastus.mittekasitsi==False)
             .filter(model.Ylesandevastus.loplik==True)
             )
        q1 = (q.filter(model.Ylesandevastus.pallid==None)
              .filter(~ model.Ylesandevastus.ylesandehinded.any())
              )
        hindamata_arv = q1.scalar()

        q2 = (q.filter(model.Ylesandevastus.pallid==None)
              .filter(model.Ylesandevastus.ylesandehinded.any())
              )
        pooleli_arv = q2.scalar()

        q3 = (q.filter(model.Ylesandevastus.pallid!=None)
              )
        hinnatud_arv = q3.scalar()
        #model.log_query(q3)

        on_pooleli = False
        if not hindamata_arv and not pooleli_arv:
            # uusi töid hinnata ei saa
            on_pooleli = None
            if c.hindaja and hinnatud_arv:
                q = (model.Session.query(model.Ylesandehinne.id)
                     .filter(model.Ylesandehinne.valitudylesanne_id==vy_id)
                     .join(model.Ylesandehinne.hindamine)
                     .filter(model.Hindamine.labiviija_id==c.hindaja.id)
                     .filter(model.Hindamine.staatus!=const.H_STAATUS_LYKATUD)
                     .join(model.Hindamine.hindamisolek)
                     .join((model.Sooritus, model.Sooritus.id==model.Hindamisolek.sooritus_id))
                     .filter(model.Sooritus.hindamine_staatus!=const.H_STAATUS_HINNATUD)
                     )
                if q.count():
                    # juba hinnatud töid saab veel hinnata
                    on_pooleli = True
        elif c.hindaja:
            # kas olen juba hindamist alustanud
            q = (model.Session.query(model.Ylesandehinne.id)
                 .filter(model.Ylesandehinne.valitudylesanne_id==vy_id)
                 .join(model.Ylesandehinne.hindamine)
                 .filter(model.Hindamine.labiviija_id==c.hindaja.id)
                 .filter(model.Hindamine.staatus!=const.H_STAATUS_LYKATUD)
                 )
            on_pooleli = q.first() is not None
        else:
            on_pooleli = False

        item = [ty_tahis,
                y_nimi,
                '',
                hindamata_arv,
                pooleli_arv,
                hinnatud_arv,
                ]
        if is_html:
            vy = model.Valitudylesanne.get(vy_id)
            tab_data = c.f_r_tabs_data(vy, vy.ylesanne, True)
            y_url = tab_data[0][1]
            return item, on_pooleli, vy_id, y_url
        else:
            return item
    
    def __before__(self):
        c = self.c
        c.testiruum_id = self.request.matchdict.get('testiruum_id')
        c.testiruum = model.Testiruum.get(c.testiruum_id)
        c.nimekiri = c.testiruum.nimekiri
        c.testiosa = c.testiruum.testikoht.testiosa
        c.test = c.testiosa.test
        c.test_id = self.request.matchdict.get('test_id')
        c.hindaja = c.testiruum.get_labiviija(const.GRUPP_HINDAJA_K, c.user.id)
        
    def _perm_params(self):
        nimekiri = self.c.testiruum.nimekiri
        if not nimekiri:
            return False
        return {'obj':nimekiri}
