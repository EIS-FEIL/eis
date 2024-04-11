from eis.lib.baseresource import *
from .suulisedhindamised import SuulisedhindamisedController

log = logging.getLogger(__name__)

class KirjalikudhindamisedController(SuulisedhindamisedController):
    """Kirjalike testide hinnete sisestamine paberil toodud hindamisprotokollilt
    """
    _permission = 'sisestamine'
    _INDEX_TEMPLATE = 'ekk/sisestamine/kirjalikud.hindamised.mako'

    def _back_to_index(self):
        return HTTPFound(location=self.url('sisestamine_kirjalikud', sessioon_id=self.c.toimumisaeg.testimiskord.testsessioon_id, toimumisaeg_id=self.c.toimumisaeg.id))
