from eis.lib.baseresource import *
_ = i18n._
import eis.handlers.ekk.ylesanded.kysimus as kysimus
log = logging.getLogger(__name__)

class KysimusController(kysimus.KysimusController):
    """Ülesande sisu"""
    _permission = 'avylesanded'
