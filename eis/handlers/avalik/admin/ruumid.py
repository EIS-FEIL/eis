from eis.lib.baseresource import *
_ = i18n._
from eis.handlers.admin import ruumid
log = logging.getLogger(__name__)

class RuumidController(ruumid.RuumidController):
    _permission = 'avalikadmin'
    _INDEX_TEMPLATE = 'avalik/admin/ruumid.mako'
    _perm_koht = True
    
    def _perm_params(self):
        if self.c.user.koht_id != self.c.koht.id:
            return False

    def __before__(self):
        self.c.koht = model.Koht.get(self.request.matchdict.get('koht_id'))
        self.c.can_edit = self.c.koht.haldusoigus
        if not self.c.can_edit:
            self.c.is_edit = False

