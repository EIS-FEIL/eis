# -*- coding: utf-8 -*-
"Profiilileht"

from eis.lib.baseresource import *
import eis.handlers.ekk.testid.profiilileht as profiilileht

class ProfiililehtController(profiilileht.ProfiililehtController):
    _permission = 'aruanded-testisooritused'
    #_EDIT_TEMPLATE = 'ekk/otsingud/profiilileht.mako'

    def _has_permission(self):
        if self.c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH and not self.is_devel:
            return False
        return BaseController._has_permission(self)

    def _perm_params(self):
        pass
