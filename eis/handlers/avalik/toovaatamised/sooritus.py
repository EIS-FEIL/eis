from eis.lib.base import *
_ = i18n._
from eis.handlers.avalik.sooritamine import sooritus

import logging
log = logging.getLogger(__name__)

class SooritusController(sooritus.SooritusController):
    """Töövaataja vaatab lahendaja lahendust.
    """
    _permission = 'toovaatamine'
    _EDIT_TEMPLATE = 'avalik/toovaatamised/toovaatamine.sooritus.mako'
    _actionstask = 'showtask,correct'
    
    def new(self):
        raise Exception(_("Vale tegevus"))

    def _show(self, item):
        if item.staatus != const.S_STAATUS_TEHTUD:
            self.error(_("Testi pole sooritatud"))
        self.c.sooritus = item
        self.c.sooritaja = item.sooritaja
        self.c.read_only = True
        sooritus.SooritusController._show(self, item)

    def showtask(self):
        c = self.c
        c.read_only = True
        c.ty = ty = self._checkty()
        komplekt = c.sooritus.get_komplekt(ty.alatest_id)
        c.ylesandevastus = c.sooritus.getq_ylesandevastus(ty.id, komplekt.id)
        if c.ylesandevastus:
            vy = c.ylesandevastus.valitudylesanne
        else:
            # ylesannet pole lahendatud
            vy = komplekt.getq_valitudylesanne(None, testiylesanne_id=ty.id)
        c.vy = vy
        c.ylesanne = vy.ylesanne
        c.lang = c.sooritus.sooritaja.lang
        return self._gentask(yv=c.ylesandevastus, pcorrect=True, showres=True)

    def __before__(self):
        c = self.c
        sooritus_id = self.request.matchdict.get('id')
        c.sooritus = model.Sooritus.get(sooritus_id)
        c.alatest_id = self.request.matchdict.get('alatest_id') or ''
        if c.alatest_id:
            c.alatest = model.Alatest.get(c.alatest_id)
            c.testiosa = c.alatest.testiosa
        else:
            c.testiosa = model.Testiosa.get(self.request.matchdict.get('testiosa_id'))
        c.test = c.testiosa.test
        c.test_id = c.testiosa.test_id
        c.testiosa_id = c.testiosa.id

    def _has_permission(self):
        return BaseController._has_permission(self)

    def _perm_params(self):
        id = self.c.sooritus.sooritaja_id
        if id:
            return {'sooritaja_id': id}
