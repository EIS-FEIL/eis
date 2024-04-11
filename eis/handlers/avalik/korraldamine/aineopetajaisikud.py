from eis.lib.baseresource import *
from eis.handlers.admin.ehisopetajad import opt_koolipedagoogid
_ = i18n._
from eis.handlers.admin import isikud
log = logging.getLogger(__name__)

class AineopetajaisikudController(isikud.IsikudController):
    _permission = 'avalikadmin'
    _INDEX_TEMPLATE = 'avalik/korraldamine/new.aineopetaja.mako'
    _LIST_TEMPLATE = 'avalik/korraldamine/new.aineopetaja.mako'    
    _get_is_readonly = False
    _perm_koht = True
    
    def _search(self, q):
        self.c.opt_pedagoogid = opt_koolipedagoogid(self, self.c.user.koht_id)
        if self.c.isikukood:
            q = q.filter(eis.forms.validators.IsikukoodP(self.c.isikukood)
                         .filter(model.Kasutaja))
        else:
            self.error(_("Isikukood on vaja ette anda"))
            return None
        return q
            
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        testikoht_id = self.request.matchdict.get('testikoht_id')
        self.c.testikoht = model.Testikoht.get(testikoht_id)
        self.c.koht = self.c.testikoht.koht
        BaseResourceController.__before__(self)

    def _perm_params(self):
        if self.c.testikoht.koht_id != self.c.user.koht_id:
            return False
