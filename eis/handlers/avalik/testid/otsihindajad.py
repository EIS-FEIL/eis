# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.handlers.admin.ehisopetajad import opt_koolipedagoogid
log = logging.getLogger(__name__)
_ = i18n._
class OtsihindajadController(BaseResourceController):
    """Korraldajad
    """
    _permission = 'testid'
    _MODEL = model.Labiviija
    _INDEX_TEMPLATE = 'avalik/testid/nimekiri.otsihindajad.mako'
    _actions = 'index,create,delete'

    def _query(self):
        c = self.c
        c.opt_opetaja = opt_koolipedagoogid(self, c.user.koht_id)        
        c.testiosa = c.testiruum.testikoht.testiosa
        
        return model.Kasutaja.query

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c

        c.pedagoog_id = c.opetaja_id
        if c.pedagoog_id:
            grupp_id = const.GRUPP_HINDAJA_K
            liik = const.HINDAJA1
            pedagoog = model.Pedagoog.get(c.pedagoog_id)
            if pedagoog:
                kasutaja = model.Kasutaja.get_by_ik(pedagoog.isikukood)
                if kasutaja:
                    c.hindaja = self._get_hindaja(kasutaja.id, grupp_id, liik)
                    if c.hindaja:
                        c.planeeritud_toode_arv = c.hindaja.planeeritud_toode_arv
                        c.tyy_id = [ly.testiylesanne_id for ly in c.hindaja.labiviijaylesanded]
        return None

    def _get_kasutaja(self, pedagoog_id, grupp_id, liik):
        c = self.c
        pedagoog = model.Pedagoog.get(pedagoog_id)
        kasutaja = model.Kasutaja.get_by_ik(pedagoog.isikukood)
        if not kasutaja:
            kasutaja = model.Kasutaja.add_kasutaja(pedagoog.isikukood,
                                                   pedagoog.eesnimi,
                                                   pedagoog.perenimi)
            model.Session.flush()
        kasutaja_id = kasutaja.id
        
        q = (model.Session.query(model.Labiviija)
             .filter_by(testiruum_id=c.testiruum.id)
             .filter_by(kasutajagrupp_id=grupp_id)
             .filter_by(liik=liik)
             .filter_by(kasutaja_id=kasutaja_id)
             )
        return q.first()

    def _get_hindaja(self, kasutaja_id, grupp_id, liik):
        c = self.c
        q = (model.Session.query(model.Labiviija)
             .filter_by(testiruum_id=c.testiruum.id)
             .filter_by(kasutajagrupp_id=grupp_id)
             .filter_by(liik=liik)
             .filter_by(kasutaja_id=kasutaja_id)
             )
        return q.first()

    def _create(self):            
        """Isiku lisamine ülesandega seotuks
        """
        c = self.c
        testiosa_id = c.testiruum.testikoht.testiosa_id
        grupp_id = const.GRUPP_HINDAJA_K
        liik = const.HINDAJA1
        pedagoog_id = self.request.params.get('pedagoog_id')
        pedagoog = pedagoog_id and model.Pedagoog.get(pedagoog_id)
        if pedagoog:
            kasutaja = model.Kasutaja.get_by_ik(pedagoog.isikukood)
            if not kasutaja:
                kasutaja = model.Kasutaja.add_kasutaja(pedagoog.isikukood,
                                                       pedagoog.eesnimi,
                                                       pedagoog.perenimi)
                model.Session.flush()
            hindaja = self._get_hindaja(kasutaja.id, grupp_id, liik)
            if not hindaja:
                hindaja = model.Labiviija(kasutaja=kasutaja,
                                          testikoht_id=c.testiruum.testikoht_id,
                                          testiruum_id=c.testiruum.id,
                                          liik=liik,
                                          kasutajagrupp_id=grupp_id,
                                          toode_arv=0,
                                          hinnatud_toode_arv=0,
                                          tasu_toode_arv=0)                            

                msg = _("Hindaja on lisatud")
            else:
                msg = _("Hindaja on muudetud")
                
            # planeeritud tööde arv
            try:
                toode_arv = int(self.request.params.get('planeeritud_toode_arv'))
            except:
                toode_arv = None
            hindaja.planeeritud_toode_arv = toode_arv
            
            # ylesanded, mida võib hinnata
            tyy_id = list(map(int, self.request.params.getall('ty_id')))

            # leiame arvutihinnatavad testiylesanded
            q = (model.Session.query(model.Testiylesanne.id)
                 .filter(model.Testiylesanne.arvutihinnatav==False)
                 .filter(model.Testiylesanne.testiosa_id==testiosa_id)
                 )
            all_tyy_id = [ty_id for ty_id, in q.all()]

            if not tyy_id or len(tyy_id) == len(all_tyy_id):
                # kõik ylesanded on lubatud
                if hindaja.id:
                    for ly in list(hindaja.labiviijaylesanded):
                        ly.delete()
            else:
                ly_tyy_id = []
                for ly in list(hindaja.labiviijaylesanded):
                    ty_id = ly.testiylesanne_id
                    if ty_id not in tyy_id:
                        # eemaldame ylesanded, mida enam pole
                        ly.delete()
                    else:
                        # jätame meele, mis on
                        ly_tyy_id.append(ty_id)
                for ty_id in tyy_id:
                    if ty_id not in ly_tyy_id:
                        ly = model.Labiviijaylesanne(testiylesanne_id=ty_id)
                        hindaja.labiviijaylesanded.append(ly)
            model.Session.commit()
            self.success(msg)

        return HTTPFound(location=self.h.url('test_nimekirjad', test_id=c.test.id, testiruum_id=c.testiruum.id))

    def _after_delete(self, parent_id=None):
        c = self.c
        return HTTPFound(location=self.h.url('test_nimekirjad', test_id=c.test.id, testiruum_id=c.testiruum.id))

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)
        self.c.test_id = self.c.test.id
        testiruum_id = self.request.matchdict.get('testiruum_id')
        self.c.testiruum = model.Testiruum.get(testiruum_id)
        nimekiri_id = self.request.matchdict.get('nimekiri_id')
        self.c.nimekiri = model.Nimekiri.get(nimekiri_id)
        assert self.c.testiruum.nimekiri_id == self.c.nimekiri.id, 'vale nimekiri'
        assert self.c.nimekiri.test_id == self.c.test.id, 'vale test'
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.nimekiri}

        
