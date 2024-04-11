# -*- coding: utf-8 -*- 

from eis.lib.base import *
from eis.handlers.avalik.protokollid.kinnitamine import KinnitamineController

log = logging.getLogger(__name__)

class ProtokollController(KinnitamineController):
    """Protokolli kinnitamine
    """
    _permission = 'testiadmin,omanimekirjad'
    _INDEX_TEMPLATE = 'avalik/testid/protokoll.mako'

    def index(self):
        q = (model.SessionR.query(sa.func.count(model.Sooritus.id))
             .filter(model.Sooritus.staatus.in_(
                 (const.S_STAATUS_REGATUD,
                  const.S_STAATUS_ALUSTAMATA))
                     )
             .filter(model.Sooritus.testiruum_id==self.c.testiruum.id))
        self.c.cnt_alustamata = q.scalar()
        
        q = (model.SessionR.query(sa.func.count(model.Sooritus.id))
             .filter(model.Sooritus.staatus==const.S_STAATUS_POOLELI)
             .filter(model.Sooritus.testiruum_id==self.c.testiruum.id))
        self.c.cnt_pooleli = q.scalar()

        return self.render_to_response(self._INDEX_TEMPLATE)
    
    def create(self):
        c = self.c

        # loome vajadusel protokolli kirje
        testikoht = c.testiruum.testikoht
        if not c.toimumisprotokoll:
            c.toimumisprotokoll = model.Toimumisprotokoll(
                koht_id=testikoht.koht_id,
                testikoht_id=testikoht.id,
                testiruum_id=c.testiruum.id)

        # märgime kõik määratud läbiviijad osalejaks
        q = (model.Session.query(model.Labiviija)
             .filter(model.Labiviija.testiruum_id==c.testiruum.id)
             .filter(model.Labiviija.staatus==const.L_STAATUS_MAARATUD))
        for lv in q.all():
            lv.staatus = const.L_STAATUS_OSALENUD

        model.Session.flush()
        return KinnitamineController.create(self)

    def _after_create(self, id):
        return self._redirect('index')

    def _download(self, id, format):
        """Näita faili"""
        c = self.c
        c.toimumisprotokoll = model.Toimumisprotokoll.get(id)
        if not c.toimumisprotokoll or \
           c.toimumisprotokoll.testiruum_id != c.testiruum.id:
            raise NotFound(_("Dokumenti ei leitud"))
        return super()._download(id, format)
    
    def _perm_params(self):
        return {'obj': self.c.testiruum}

    def _has_permission(self):
        return BaseController._has_permission(self)

    def __before__(self):
        c = self.c
        c.testiruum_id = self.request.matchdict.get('testiruum_id')
        c.testiruum = model.Testiruum.get(c.testiruum_id)
        c.nimekiri = c.testiruum.nimekiri
        c.test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(c.test_id)
        c.testikohad = [c.testiruum.testikoht]
        for prot in c.testiruum.toimumisprotokollid:
            c.toimumisprotokoll = prot
            break
        
