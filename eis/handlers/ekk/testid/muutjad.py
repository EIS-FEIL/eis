# -*- coding: utf-8 -*- 
# $Id: muutjad.py 406 2016-03-07 19:18:48Z ahti $

from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class MuutjadController(BaseResourceController):

    _permission = 'ekk-testid'

    _MODEL = model.Testilogi
    _INDEX_TEMPLATE = 'ekk/testid/muutjad.mako'
    _LIST_TEMPLATE = 'ekk/testid/muutjad_list.mako'
    _ITEM_FORM = None #forms.ekk.testid.MuutjadForm 
    _DEFAULT_SORT = '-id'

    def show(self):
        self.c.item = self.c.test
        return self.index()

    def _query(self):
        id = self.request.matchdict.get('id')
        return model.Testilogi.query.filter_by(test_id=id)

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        self.set_debug()
        if c.liik:
            q = q.filter(model.Testilogi.liik.like(c.liik))
        if c.vanad:
            q = q.filter(model.Testilogi.vanad_andmed.like(c.vanad))
        if c.uued:
            q = q.filter(model.Testilogi.uued_andmed.like(c.uued))
        return q

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('id')
        self.c.test = model.Test.get(test_id)
        
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}

