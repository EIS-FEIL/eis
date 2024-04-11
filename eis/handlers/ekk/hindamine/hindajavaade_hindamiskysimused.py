"Testi ülesande sisu näitamine kirjalikule hindajale"

from eis.lib.baseresource import *
_ = i18n._
from eis.handlers.avalik.khindamine.hindamiskysimused import HindamiskysimusedController
from .hindajavaade_hkhindamine import get_tab_urls

log = logging.getLogger(__name__)

class HindajavaadeHindamiskysimusedController(HindamiskysimusedController):
    _permission = 'hindajamaaramine'    
   
    def _get_tab_urls(self):
        get_tab_urls(self, self.c)
    
    def _has_permission(self):
        return BaseResourceController._has_permission(self)

    def _perm_params(self):
        test = self.c.toimumisaeg.testiosa.test
        return {'obj': test}
    
