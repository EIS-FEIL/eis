# -*- coding: utf-8 -*-
"Profiilileht"

from eis.lib.baseresource import *
import eis.handlers.ekk.testid.profiilileht as profiilileht

class ProfiililehtController(profiilileht.ProfiililehtController):
    _permission = 'sooritamine'

    def _has_permission(self):
        c = self.c
        return c.sooritaja.kasutaja_id == c.user.id

    def _perm_params(self):
        pass
