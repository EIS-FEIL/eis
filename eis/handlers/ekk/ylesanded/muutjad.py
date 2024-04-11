# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class MuutjadController(BaseResourceController):
    """Koostamise ajalugu (logi vaatamine)
    """
    _permission = 'ylesanded'

    _MODEL = model.Ylesandelogi
    _INDEX_TEMPLATE = 'ekk/ylesanded/muutjad.mako'
    _LIST_TEMPLATE = 'ekk/ylesanded/muutjad_list.mako'
    _ITEM_FORM = None #forms.ekk.ylesanded.MuutjadForm 
    _DEFAULT_SORT = '-id'

    def show(self):
        id = self.request.matchdict.get('id')

        self.c.item = model.Ylesanne.get(id)
        return self.index()

    def _query(self):
        id = self.request.matchdict.get('id')
        return model.Ylesandelogi.query.filter_by(ylesanne_id=id)

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        self.set_debug()
        if c.liik:
            q = q.filter(model.Ylesandelogi.liik.like(c.liik))
        if c.vanad:
            q = q.filter(model.Ylesandelogi.vanad_andmed.like(c.vanad))
        if c.uued:
            q = q.filter(model.Ylesandelogi.uued_andmed.like(c.uued))
        return q

    def __before__(self):
        self.c.ylesanne = model.Ylesanne.get(self.request.matchdict.get('id'))

    def _perm_params(self):
        return {'obj':self.c.ylesanne}

