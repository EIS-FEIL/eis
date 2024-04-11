from eis.lib.baseresource import *
import eis.handlers.avalik.eksamistatistika.riikliktagasiside as riikliktagasiside
_ = i18n._
log = logging.getLogger(__name__)

class RiikliktagasisideController(riikliktagasiside.RiikliktagasisideController):
    """Eksamite tulemuste statistika
    """
    _permission = 'aruanded-tulemused'
    _authorize = True
    _ITEM_TEMPLATE = 'ekk/statistika/eksamistatistika.riikliktagasiside.mako'
    # kas testimiskorrad peavad olema avalikus vaates avaldatud
    avalik = False
