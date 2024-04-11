from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class RvtunnistusedController(BaseResourceController):
    "Rahvusvaheliste eksamite tunnistused"
    _authorize = False
    _MODEL = model.Rvsooritaja
    _EDIT_TEMPLATE = 'avalik/tunnistused/rvtunnistus.mako'

    def _edit(self, item):
        kasutaja = item.tunnistus.kasutaja
        if kasutaja.id != self.c.user.id:
            self.error(_('Lubatud on vaadata ainult enda tunnistusi'))
            raise HTTPFound(self.url('tunnistused'))
            
