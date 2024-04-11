from eis.lib.baseresource import *
import eis.handlers.avalik.eksamistatistika.eksamistatistika as eksamistatistika
_ = i18n._
log = logging.getLogger(__name__)

class EksamistatistikaController(eksamistatistika.EksamistatistikaController):
    """Eksamite tulemuste statistika
    """
    _permission = 'aruanded-tulemused'
    _authorize = True
    _INDEX_TEMPLATE = 'ekk/statistika/eksamistatistika.otsing.mako'
    _ITEM_TEMPLATE = 'ekk/statistika/eksamistatistika.riikliktagasiside.html'
    # kas testimiskorrad peavad olema avalikus vaates avaldatud
    avalik = False
