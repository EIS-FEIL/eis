from eis.lib.baseresource import *
from eis.handlers.avalik.klabiviimine.labiviimised import set_sooritus_staatus
_ = i18n._

log = logging.getLogger(__name__)

class VastajadController(BaseResourceController):

    _MODEL = model.Sooritus
    _INDEX_TEMPLATE = 'avalik/svastamine/vastajad.mako'
    _LIST_TEMPLATE = 'avalik/svastamine/vastajad_list.mako'
    _DEFAULT_SORT = 'sooritaja.eesnimi,sooritaja.perenimi'
    _no_paginate = True
    
    def _query(self):
        q = (model.SessionR.query(model.Sooritus, model.Sooritaja, model.Kasutaja)
             .filter(model.Sooritus.testiruum_id==self.c.testiruum.id)
             .join(model.Sooritus.sooritaja)
             .join(model.Sooritaja.kasutaja)
             .filter(model.Sooritus.staatus>=const.S_STAATUS_REGATUD)
             )
        return q
       
    def _search(self, q):
        return q

    def _create(self):
        # staatuse muutmine
        c = self.c
        staatus = self.request.params.get('staatus')
        for sooritus_id in self.request.params.getall('sooritus_id'):
            tos = model.Sooritus.get(sooritus_id)
            if tos and tos.testiruum_id == c.testiruum.id:
                set_sooritus_staatus(self, tos, staatus, False)
        model.Session.commit()
        return self._redirect('index')
                    
    def __before__(self):
        c = self.c
        c.testiruum = model.Testiruum.get(self.request.matchdict.get('testiruum_id'))
        c.toimumisaeg = c.testiruum.testikoht.toimumisaeg
        c.testiosa = c.toimumisaeg.testiosa
        c.test = c.testiosa.test
        # leitakse kasutaja roll selles testiruumis
        q = (model.Labiviija.query
             .filter(model.Labiviija.toimumisaeg_id==c.toimumisaeg.id)
             .filter(model.Labiviija.testiruum_id==c.testiruum.id)
             .filter(model.Labiviija.kasutaja_id==c.user.id)
             .filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_INTERVJUU)
             )
        c.labiviija = q.first()

    def _has_permission(self):
        dt = date.today()
        return self.c.labiviija is not None and \
               self.c.testiruum.algus.date() == dt

