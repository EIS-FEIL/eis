# -*- coding: utf-8 -*-
"Profiilileht, ainult testimiseks muud/pstulemused/{sooritus_id}"

from eis.lib.baseresource import *
_ = i18n._
import eis.handlers.avalik.testid.psyhtulemus as psyhtulemus

class PstulemusController(psyhtulemus.PsyhtulemusController):
    _permission = 'admin'
    _EDIT_TEMPLATE = 'ekk/muud/pstulemus.mako'

    def _show_items(self, sooritaja):
        q = model.Sooritaja.query.filter(model.Sooritaja.id==sooritaja.id)
        return [r for r in q.all()]

    def _has_permission(self):
        if not (self.is_test or self.is_devel):
            return False
        rc = BaseResourceController._has_permission(self)
        return rc
