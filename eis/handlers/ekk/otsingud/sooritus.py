from eis.lib.base import *
_ = i18n._
from eis.handlers.avalik.sooritamine import sooritus

import logging
log = logging.getLogger(__name__)

class SooritusController(sooritus.SooritusController):
    """Eksamikeskuse ametnik vaatab lahendaja lahendust.
    """
    _permission = 'aruanded-testisooritused'
    _EDIT_TEMPLATE = 'ekk/otsingud/tulemus.sooritus.mako'
    _actionstask = 'showtask,correct'
    
    def new(self):
        raise Exception(_("Vale tegevus"))

    def _show(self, item):
        if self.c.sooritus.staatus != const.S_STAATUS_TEHTUD:
            self.error(_("Testi pole sooritatud"))
        self.c.read_only = True
        sooritus.SooritusController._show(self, item)

    def __before__(self):
        c = self.c
        super().__before__()
        c.sooritus_id = self.request.matchdict.get('id')
        c.sooritus = model.Sooritus.get(c.sooritus_id)
        c.alatest_id = self.request.matchdict.get('alatest_id') or ''
        if c.alatest_id:
            c.alatest = model.Alatest.get(c.alatest_id)
            c.alatest_id = c.alatest.id # int
            c.testiosa = c.alatest.testiosa
        else:
            c.testiosa = model.Testiosa.get(self.request.matchdict.get('testiosa_id'))
        c.test = c.testiosa.test
        c.test_id = c.testiosa.test_id
        c.testiosa_id = c.testiosa.id
        c.sooritaja = c.sooritus.sooritaja
        c.exapi_host = model.Klaster.get_host(c.sooritaja.klaster_id)
        
    def _has_permission(self):
        if self.c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH and not self.is_devel and not self.c.user.on_admin:
            return False
        return BaseController._has_permission(self)
