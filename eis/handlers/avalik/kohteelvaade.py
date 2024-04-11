# -*- coding: utf-8 -*- 
"Soorituskoha admini eelvaade kasutajate juhendamise jaoks"
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class KohteelvaadeController(BaseController):
    _permission = 'kohteelvaade'
    _actions = 'show' 

    def show(self):
        id = self.request.matchdict.get('id')
        koht = model.Koht.get(id)
        if not koht:
            self.error('Kohta ei leitud')
        else:
            self.c.user.start_kohteelvaade(self.request.session, koht.id)
        raise HTTPFound(location=self.url('avaleht'))

    def _has_permission(self):
        kasutaja_id = self.c.user.id
        if kasutaja_id:
            kasutaja = model.Kasutaja.get(kasutaja_id)
            return kasutaja.has_permission(self._permission, const.BT_SHOW, koht_id=None)
        return False
