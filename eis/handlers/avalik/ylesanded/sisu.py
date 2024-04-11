from eis.lib.baseresource import *
_ = i18n._
import eis.handlers.ekk.ylesanded.sisu as sisu

log = logging.getLogger(__name__)

class SisuController(sisu.SisuController):
    """Ülesande sisu"""

    _permission = 'avylesanded'
    _EDIT_TEMPLATE = 'avalik/ylesanded/sisu.mako'

    def _edit(self, item):
        # kui on lukus, siis kontrollime, kas lukku on vaja
        if item.lukus and not item.get_lukustusvajadus():
            item.lukus = None
            model.Session.commit()
        return super()._edit(item)
    
    @property
    def _ITEM_FORM(self):
        return forms.avalik.ylesanded.SisuForm

    def _get_permission(self):
        # ylesanded-markused roll pole avalikus vaates kasutusel
        return BaseResourceController._get_permission(self)
