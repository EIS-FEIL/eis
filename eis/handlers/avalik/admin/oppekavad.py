# -*- coding: utf-8 -*- 
# $Id: oppekavad.py 544 2016-04-01 09:07:15Z ahti $

from eis.lib.baseresource import *
_ = i18n._
import eis.handlers.admin.oppekavad as oppekavad
log = logging.getLogger(__name__)

class OppekavadController(oppekavad.OppekavadController):
    _permission = 'avalikadmin'

    def _perm_params(self):
        pass

    def __before__(self):
        self.c.koht = model.Koht.get(self.request.matchdict.get('koht_id'))
        assert self.c.user.koht_id == self.c.koht.id, _("Vale koht")
        self.c.can_edit = self.c.koht.haldusoigus
        if not self.c.can_edit:
            self.c.is_edit = False
