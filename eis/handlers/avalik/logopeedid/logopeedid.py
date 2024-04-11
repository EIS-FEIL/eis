from eis.lib.baseresource import *
import eis.handlers.avalik.koolipsyhholoogid.koolipsyhholoogid as koolipsyhholoogid
log = logging.getLogger(__name__)
_ = i18n._

class LogopeedidController(koolipsyhholoogid.KoolipsyhholoogidController):
    "Koolituste laadimine"
    _INDEX_TEMPLATE = '/avalik/logopeedid/logopeedid.mako' 
    _EDIT_TEMPLATE = '/avalik/logopeedid/logopeed.mako'
    _LIST_TEMPLATE = '/avalik/logopeedid/logopeedid_list.mako'
            
    _permission = 'lglitsentsid'
    LGROUP = const.GRUPP_A_LOGOPEED

    def _err_no_group(self):
        return _("Isikul ei ole logopeedi litsentsi")
