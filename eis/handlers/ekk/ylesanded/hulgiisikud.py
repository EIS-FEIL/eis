# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.lib.basegrid import *
_ = i18n._

from .isikud import IsikudController

log = logging.getLogger(__name__)

class HulgiisikudController(IsikudController):
    """Ülesannetega seotud isikud
    """
    _permission = 'ylesanded'
    _INDEX_TEMPLATE = 'ekk/ylesanded/hulgi.isik.mako'
    _LIST_TEMPLATE = 'ekk/ylesanded/hulgi.isik.mako'

    def __before__(self):
        """Väärtustame self.c.ylesanne_id
        """
        self.c.ylesanded_id = self.request.matchdict.get('ylesanded_id')
        self.c.ylesanded = [model.Ylesanne.get(yl_id) for yl_id in self.c.ylesanded_id.split('-')]
        BaseResourceController.__before__(self)

    def _has_permission(self):
        rc = self.c.user.has_permission('ylhulgi', const.BT_UPDATE)
        if rc:
            return True

        # vajaliku õiguse nimi
        permission = self._get_permission()
        # kas toimub muutmine või vaatamine?
        perm_bit = const.BT_UPDATE
        for ylesanne in self.c.ylesanded:
            rc = self.c.user.has_permission(permission, perm_bit, obj=ylesanne)
            if not rc:
                # ei lubatud ligipääsu
                self._miss_perm = _("Ülesanne {id}").format(id=ylesanne.id)
                break
            
        return rc
