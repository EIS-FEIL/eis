"Küsimuse hindamismaatriksi täiendamine sooritajate antud vastustega"
from eis.lib.baseresource import *
from .testiosavalik import Testiosavalik
_ = i18n._
from eis.handlers.ekk.hindamine.analyysmaatriksid import AnalyysmaatriksidController as amxController
log = logging.getLogger(__name__)

class AnalyysmaatriksidController(amxController, Testiosavalik):
    _permission = 'testid,ekk-testid'

    _MODEL = model.Hindamismaatriks
   
    def _has_permission(self):
        # leitakse, kas on õigus antud tegevusele,
        # ning seatakse c.can_edit_hm - kas on muutmisõigus

        perm = self._permission
        test = self.c.test
        can_show = self.c.user.has_permission(perm, const.BT_SHOW, obj=test)
        can_edit_hm = self._can_edit_hm(self.c.user, test, self.c.kysimus)

        self.c.can_edit_hm = can_edit_hm
        if self._is_modify():
            return can_edit_hm
        else:
            return can_show

    def _perm_params(self):
        if c.test.opetajale_peidus:
            return False
        return {'obj': c.nimekiri or c.test}        
    
    def _can_edit_hm(self, user, test, kysimus):
        perm = 'avylesanded'
        return user.has_permission(perm, const.BT_UPDATE, obj=self.c.ylesanne)
    
    def __before__(self):
        c = self.c
        Testiosavalik.set_test_testiosa(self)

        kysimus_id = self.request.matchdict.get('kysimus_id')
        c.kysimus = model.Kysimus.get(kysimus_id)
        c.ylesanne = c.kysimus.sisuplokk.ylesanne
        c.maatriks = self.request.params.get('maatriks') or 1
        c.prefix = self.request.params.get('prefix')
