# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
from eis.handlers.admin import kohakasutajad
log = logging.getLogger(__name__)

class KohakasutajadController(kohakasutajad.KohakasutajadController):
    _permission = 'avalikadmin'
    _INDEX_TEMPLATE = 'avalik/admin/koht.kasutajad.mako'
    def _perm_params(self):
        pass

    def _has_permission(self):
        c = self.c
        if c.user.koht_id != c.koht.id:
            return False
        return BaseController._has_permission(self)
        
    def __before__(self):
        c = self.c
        c.koht = model.Koht.get(self.request.matchdict.get('koht_id'))
        c.can_roll = c.koht.haldusoigus and \
                     c.user.has_permission('kasutajad', const.BT_UPDATE, koht_id=c.koht.id)
        c.can_edit = c.koht.haldusoigus and \
                     c.user.has_permission('avalikadmin', const.BT_UPDATE, koht_id=c.koht.id)        
        if not c.can_edit:
            c.is_edit = False
