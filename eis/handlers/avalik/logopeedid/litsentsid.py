from eis.lib.baseresource import *
import eis.handlers.avalik.koolipsyhholoogid.litsentsid as litsentsid
log = logging.getLogger(__name__)
_ = i18n._

class LitsentsidController(litsentsid.LitsentsidController):
    "Koolituste laadimine"
    _INDEX_TEMPLATE = '/avalik/logopeedid/litsentsid.mako'
            
    _permission = 'lglitsentsid'
    LGROUP = const.GRUPP_A_LOGOPEED
