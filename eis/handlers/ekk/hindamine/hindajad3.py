from eis.lib.baseresource import *
_ = i18n._
from . import hindajad

log = logging.getLogger(__name__)

class Hindajad3Controller(hindajad.HindajadController):

    _permission = 'hindajamaaramine'
    _INDEX_TEMPLATE = 'ekk/hindamine/maaramine.hindajad3.mako'
    _LIST_TEMPLATE = 'ekk/hindamine/maaramine.hindajad_list.mako'

    def _query(self):
        testiosa = self.c.toimumisaeg.testiosa
        self.c.hindamiskogumid_opt = [(r.id, r.tahis) for r in testiosa.hindamiskogumid \
                                          if r.staatus]
        self.c.hindajad_opt = self._get_hindajad_opt()

        self.Kasutaja1 = None
        self.Kasutaja2 = None        
        self.Labiviija1 = sa.orm.aliased(model.Labiviija) # hindaja_1
        f_hindaja1 = sa.and_(self.Labiviija1.hindamiskogum_id==model.Hindamiskogum.id,
                             self.Labiviija1.liik==const.HINDAJA3,
                             self.Labiviija1.toimumisaeg_id==self.c.toimumisaeg.id)

        q = model.SessionR.query(model.Hindamiskogum, self.Labiviija1).\
            join((self.Labiviija1, f_hindaja1))

        return q

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        self._calc_kolmasprotsent()

        if self.c.hindamiskogum_id:
            hindamiskogum_id = int(self.c.hindamiskogum_id)
            q = q.filter(model.Hindamiskogum.id==hindamiskogum_id)
            self.c.hindamiskogum = model.Hindamiskogum.get(hindamiskogum_id)
        else:
            hindamiskogum_id = None
            
        self._get_arvud(hindamiskogum_id)
        
        if self.c.hindaja_id:
            hindaja_id = int(self.c.hindaja_id)
            #if self.c.kaks_hindajat:
            q = q.filter(self.Labiviija1.kasutaja_id==hindaja_id)

        if self.c.lang:
            q = q.filter(self.Labiviija1.lang==self.c.lang)
        if self.c.piirkond_id:
            q = q.filter(sa.exists()
                         .where(model.Kasutajapiirkond.piirkond_id==self.c.piirkond_id)
                         .where(model.Kasutajapiirkond.kasutaja_id==self.Labiviija1.kasutaja_id))

        if self.c.csv:
            return self._index_csv(q)
        return q

    def _calc_kolmasprotsent(self):
        # arvutame, mitu protsenti hinnatud töödest on III hindamist vajanud
        q3 = (model.SessionR.query(sa.func.count(model.Sooritus.id))
              .filter_by(toimumisaeg_id=self.c.toimumisaeg.id)
              .filter_by(staatus=const.S_STAATUS_TEHTUD)
              .join(model.Sooritus.hindamisolekud)
              .join(model.Hindamisolek.hindamised)
              .filter(model.Hindamine.sisestus==1)
              .filter(model.Hindamine.liik==const.HINDAJA1)
              .filter(model.Hindamine.staatus==const.H_STAATUS_HINNATUD)
              )
        if self.c.hindamiskogum_id:
            q3 = q3.filter(model.Hindamisolek.hindamiskogum_id==self.c.hindamiskogum_id)
        if self.c.lang:
            q3 = (q3.join(model.Sooritus.sooritaja)
                  .filter(model.Sooritaja.lang==self.c.lang))
        if self.c.piirkond_id:
            q3 = (q3.join(model.Sooritus.testikoht)
                  .join(model.Testikoht.koht)
                  .filter(model.Koht.piirkond_id==self.c.piirkond_id))

        self.c.esmanekokku = total = q3.scalar()
        if total:
            q3 = q3.filter(model.Hindamisolek.hindamistase>=const.HINDAJA3)
            kolmas = q3.scalar()
            self.c.kolmasprotsent = self.h.fstr(kolmas * 100. / total)
            log.debug('kolmas %s/%s = %s%%' % (kolmas, total, self.c.kolmasprotsent))
        else:
            self.c.kolmasprotsent = None

    def _get_hindajad_opt(self):
        qh = model.SessionR.query(model.Kasutaja.id, model.Kasutaja.nimi).\
            filter(model.Kasutaja.labiviijad.any(\
                sa.and_(model.Labiviija.toimumisaeg_id==self.c.toimumisaeg.id,
                        model.Labiviija.liik==const.HINDAJA3))).\
            order_by(model.Kasutaja.nimi)
        return [(k[0],k[1]) for k in qh.all()] 

    def __before__(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        self.c.testiosa = self.c.toimumisaeg.testiosa
        self.c.testimiskord = self.c.toimumisaeg.testimiskord
        self.c.test = self.c.testimiskord.test
        self.c.on_hindaja3 = True
