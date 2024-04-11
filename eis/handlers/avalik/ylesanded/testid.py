# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class TestidController(BaseResourceController):
    """Kasutamise ajalugu
    """
    _permission = 'avylesanded'
    _INDEX_TEMPLATE = 'avalik/ylesanded/testid.mako'
    _MODEL = model.Ylesanne
    _ITEM_FORM = None #forms.ekk.ylesanded.MuutjadForm 
    _DEFAULT_SORT = 'test.id'
    _actions = 'index'
    _no_paginate = True
    
    def _query(self):
        return model.SessionR.query(model.Test.id,
                                   model.Test.nimi)

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        q = (q.join(model.Test.testiosad)
             .join(model.Testiosa.testiylesanded)
             .join(model.Testiylesanne.valitudylesanded)
             .filter(model.Valitudylesanne.ylesanne_id==self.c.ylesanne.id))
        return q

    def __before__(self):
        ylesanne_id = self.request.matchdict.get('ylesanne_id')
        self.c.item = self.c.ylesanne = model.Ylesanne.get(ylesanne_id)

    def _perm_params(self):
        return {'obj':self.c.ylesanne}
