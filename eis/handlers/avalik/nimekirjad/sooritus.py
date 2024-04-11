# -*- coding: utf-8 -*- 
# $Id: sooritus.py 889 2016-09-29 13:36:33Z ahti $

from eis.lib.base import *
_ = i18n._
from eis.handlers.avalik.sooritamine import sooritus

log = logging.getLogger(__name__)

class SooritusController(sooritus.SooritusController):
    """Testiosa soorituse vaatamine
    """
    _EDIT_TEMPLATE = 'avalik/nimekirjad/kontroll.sooritus.mako'

    def __before__(self):
        id = self.request.matchdict.get('id')
        self.c.item = model.Sooritus.get(id)
        sooritus.SooritusController.__before__(self)
        
    def _has_permission(self):
        if self.c.item:
            sooritaja = self.c.item.sooritaja
            if sooritaja.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
                return sooritaja.esitaja_kasutaja_id == self.c.user.id
            else:
                opilane = sooritaja.kasutaja.opilane
                return opilane and opilane.koht_id == self.c.user.koht_id
