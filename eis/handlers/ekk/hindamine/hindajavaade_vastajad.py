from eis.lib.baseresource import *
_ = i18n._
from eis.handlers.avalik.khindamine.vastajad import VastajadController
from .hindajavaade_hkhindamine import get_tab_urls

log = logging.getLogger(__name__)

class HindajavaadeVastajadController(VastajadController):
    """Hindamiskogumi soorituste näitamine
    """
    _permission = 'hindajamaaramine'    
    _INDEX_TEMPLATE = 'ekk/hindamine/hindajavaade_vastajad.mako'

    def _redirect_hinda(self, sooritus_id):
        "Algab hindamine"
        c = self.c
        partial = self.request.params.get('partial') or None                
        if c.testiosa.vastvorm_kood == const.VASTVORM_SH:
            url = self.url('hindamine_hindajavaade_shindamised', 
                           toimumisaeg_id=c.toimumisaeg.id,
                           hindaja_id=c.hindaja.id, 
                           sooritus_id=sooritus_id)
        else:
            url = self.url('hindamine_hindajavaade_hkhindamised', 
                           toimumisaeg_id=c.toimumisaeg.id, 
                           hindaja_id=c.hindaja.id, 
                           sooritus_id=sooritus_id,
                           partial=partial)
        return HTTPFound(location=url)

    def _create_kinnita(self):
        """Kasutaja linnutas pooleli hindamisega tööd ja soovib nende hindamise kinnitada
        """
        self.notice(_("Eelvaates hindamisi ei kinnitata"))
        return self._redirect('index')

    def _get_tab_urls(self):
        # funktsioon, mis genereerib lingi ylesandele
        get_tab_urls(self, self.c)

    def _has_permission(self):
        return BaseResourceController._has_permission(self)

    def _perm_params(self):
        return {'obj':self.c.test}
    
