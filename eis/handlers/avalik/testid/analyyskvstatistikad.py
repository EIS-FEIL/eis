from eis.lib.baseresource import *
from .testiosavalik import Testiosavalik
from eis.handlers.ekk.hindamine.analyyskvstatistikad import AnalyyskvstatistikadController as akvsController
_ = i18n._

log = logging.getLogger(__name__)

class AnalyyskvstatistikadController(akvsController, Testiosavalik):
    "Kysimuste vastuste statistika kuvamine"
    _permission = 'testid,ekk-testid'

    def _show_filter(self, q):
        c = self.c
        q = q.filter(model.Sooritaja.nimekiri_id==c.nimekiri.id)
        return q

    def _perm_params(self):
        c = self.c
        if c.test.opetajale_peidus:
            return False
        return {'obj': c.nimekiri or c.test}        
    
    def _can_edit_hm(self, user, test, kysimus):
        c = self.c
        perm = 'avylesanded'
        return user.has_permission(perm, const.BT_UPDATE, obj=c.ylesanne)
    
    def __before__(self):
        c = self.c
        Testiosavalik.set_test_testiosa(self)

        kst_id = self.request.matchdict.get('kst_id')
        c.kst = model.Kysimusestatistika.get(kst_id)
        c.kvst_order = self.request.params.get('kvst_order')

    def _can_edit_hm(self, user, test, kysimus):
        # avalikus vaates saab muuta omatehtud ylesandeid
        perm = 'avylesanded'
        ylesanne = kysimus.sisuplokk.ylesanne            
        return user.has_permission(perm, const.BT_UPDATE, obj=ylesanne)            
