# -*- coding: utf-8 -*- 
# $Id: sooritus.py 890 2016-09-29 13:46:02Z ahti $

from eis.lib.base import *
_ = i18n._
from eis.handlers.avalik.sooritamine import sooritus

import logging
log = logging.getLogger(__name__)

class SooritusController(sooritus.SooritusController):
    """Õpetaja vaatab lahendaja lahendust.
    """
    _permission = 'nimekirjad'
    _EDIT_TEMPLATE = 'avalik/klabiviimine/sooritus.mako'
    def new(self):
        raise Exception(_("Vale tegevus"))

    def _show(self, item):
        self.c.hindaja = True
        self.c.show_tulemus = True
        if item.staatus != const.S_STAATUS_TEHTUD:
            self.error(_("Testi pole sooritatud"))
        return sooritus.SooritusController._show(self, item)

    def _perm_params(self):
        self.c.sooritus = model.Sooritus.get(self.request.matchdict.get('id'))
        return {'obj':self.c.sooritus.sooritaja.nimekiri}
