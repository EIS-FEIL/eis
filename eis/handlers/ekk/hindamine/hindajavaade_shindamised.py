from simplejson import dumps
from eis.lib.baseresource import *
_ = i18n._
from eis.handlers.avalik.shindamine.hindamised import HindamisedController

log = logging.getLogger(__name__)

class HindajavaadeShindamisedController(HindamisedController):
    """Hindaja eelvaade
    """
    _permission = 'hindajamaaramine'    
    _INDEX_TEMPLATE = 'ekk/hindamine/hindajavaade_shindamised.mako'
    _get_is_readonly = True
    
    def _redirect_to_index(self, is_json):
        c = self.c
        if c.labiviija and c.labiviija.testiruum_id:
            # hindaja soorituste loetellu (eelvaatest välja, sest kooli eelvaadet pole tehtud)
            url = self.url('hindamine_sooritused', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.labiviija.id)
        elif c.labiviija:
            # hindaja tööde loetellu
            url = self.url('hindamine_hindajavaade_vastajad',
                           toimumisaeg_id=c.toimumisaeg.id,
                           hindaja_id=c.labiviija.id)
        elif c.action == 'index':
            # EKK hindaja eelvaade ilma hindajata
            url = self.url('hindamine_hindajad', toimumisaeg_id=c.toimumisaeg.id)
        else:
            # eelvaade ilma hindajata
            url = self.url_current('index', hindaja_id=0)
        return HTTPFound(location=url)

    def _create(self):
        # ylesande hindamise salvestamine
        c = self.c
        self.warning(_("Hindaja eelvaates muudatusi ei salvestata"))
        return self._redirect_to_index(False)

    def _index_start(self):
        d = self._index_d()
        if isinstance(d, dict):
            return self._showlist()
        else:
            return d
    
    def __before__(self):
        c = self.c
        c.sooritus_id = self.request.matchdict.get('sooritus_id')
        if c.sooritus_id != '0':
            c.sooritus = model.Sooritus.get(c.sooritus_id)

        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        c.testiosa = c.toimumisaeg.testiosa
        c.test = c.testiosa.test
        
        c.hindaja_id = self.request.matchdict.get('hindaja_id')
        if c.hindaja_id.startswith('hk'):
            c.hindamiskogum_id = int(c.hindaja_id[2:])
            c.hindamiskogum = model.Hindamiskogum.get(c.hindamiskogum_id)
        else:
            c.hindaja_id = int(c.hindaja_id)
            c.labiviija = model.Labiviija.get(c.hindaja_id)
            c.hindamiskogum_id = c.labiviija.hindamiskogum_id
            c.hindamiskogum = c.labiviija.hindamiskogum
            
    def _has_permission(self):
        return BaseResourceController._has_permission(self)

    def _perm_params(self):
        return {'obj':self.c.test}
    
