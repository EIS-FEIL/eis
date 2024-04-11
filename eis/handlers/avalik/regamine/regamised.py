from eis.lib.baseresource import *
from eis.lib.pangalink import Pangalink
import eis.lib.regpiirang as regpiirang
import eis.handlers.ekk.otsingud.kohateated as kt
from eis.handlers.avalik.regamine.avaldus.testid import save_reg
log = logging.getLogger(__name__)
_ = i18n._
class RegamisedController(BaseResourceController):
    """Sooritaja vaatab oma registreeringuid
    """
    _permission = 'sooritamine'
    _MODEL = model.Sooritaja
    _INDEX_TEMPLATE = 'avalik/regamine/otsing.mako'
    _LIST_TEMPLATE = 'avalik/regamine/otsing_list.mako'
    _DEFAULT_SORT = '-sooritaja.id'
    _actions = 'index'

    def _query(self):
        d = date.today()
        q = (model.Sooritaja.query
             .filter(model.Sooritaja.staatus<const.S_STAATUS_POOLELI)
             .filter(model.Sooritaja.kasutaja_id==self.c.user.id)
             .join(model.Sooritaja.testimiskord)
             .filter(model.Testimiskord.osalemise_naitamine==True)
             .join(model.Testimiskord.test)
             .filter(model.Test.avaldamistase==const.AVALIK_EKSAM)
             .filter(sa.or_(model.Testimiskord.sooritajad_peidus_kuni==None,
                            model.Testimiskord.sooritajad_peidus_kuni<datetime.now()))
             .filter(model.Sooritaja.regviis_kood!=const.REGVIIS_EELVAADE)
             .filter(sa.or_(
                 # tühistatud ja pooleli regamisi kuvame ainult juhul, kui regamine on veel avatud
                 # või test pole alanud
                 sa.and_(model.Testimiskord.reg_sooritaja==True,
                         model.Testimiskord.reg_sooritaja_alates<=d,
                         model.Testimiskord.reg_sooritaja_kuni>=d),
                 model.Sooritaja.staatus == const.S_STAATUS_REGATUD,
                 model.Testimiskord.alates>d
                 ))
            )
        return q

    def _search(self, q):
        return q
        
    def _has_permission(self):
        rc = super()._has_permission()
        if rc:
            # kontrollida, et sooritaja kirje on kasutaja oma
            id = self.request.matchdict.get('id')
            if id:
                item = model.Sooritaja.get(id)
                if not item or item.kasutaja_id != self.c.user.id:
                    rc = False
        return rc
