from eis.lib.baseresource import *
_ = i18n._
import eis.handlers.ekk.ylesanded.sisuplokk as sisuplokk
log = logging.getLogger(__name__)

class SisuplokkController(sisuplokk.SisuplokkController):
    """Ülesande sisu"""

    _permission = 'avylesanded'
    _EDIT_TEMPLATE = 'avalik/ylesanded/sisuplokk.mako'
