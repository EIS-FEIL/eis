from eis.lib.baseresource import *
_ = i18n._

from .isikud import IsikudController

log = logging.getLogger(__name__)

class HulgiisikudController(IsikudController):
    """Testidega seotud isikud
    """
    _permission = 'ekk-testid'
    _INDEX_TEMPLATE = 'ekk/testid/hulgi.isik.mako'
    _LIST_TEMPLATE = 'ekk/testid/hulgi.isik.mako'

    def __before__(self):
        """Väärtustame self.c.testid_id
        """
        self.c.testid_id = self.request.matchdict.get('testid_id')
        self.c.testid = [model.Test.get(t_id) for t_id in self.c.testid_id.split('-')]
        BaseResourceController.__before__(self)

    def _has_permission(self):
        rc = self.c.user.has_permission('testhulgi', const.BT_UPDATE)
        if rc:
            return True

        # vajaliku õiguse nimi
        permission = self._get_permission()
        # kas toimub muutmine või vaatamine?
        perm_bit = const.BT_UPDATE
        for test in self.c.testid:
            rc = self.c.user.has_permission(permission, perm_bit, obj=test)
            if not rc:
                # ei lubatud ligipääsu
                self._miss_perm = _("Test {id}").format(id=test.id)
                break
            
        return rc
