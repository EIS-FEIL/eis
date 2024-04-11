from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class TestsessioonidController(BaseResourceController):
    _permission = 'sessioonid'
    _MODEL = model.Testsessioon
    _EDIT_TEMPLATE = 'admin/testsessioonid.mako'
    _INDEX_TEMPLATE = 'admin/testsessioonid.mako'
    _LIST_TEMPLATE = 'admin/testsessioonid_list.mako'
    _ITEM_FORM = forms.admin.TestsessioonForm
    _DEFAULT_SORT = '-testsessioon.seq,testsessioon.oppeaasta'

    _no_paginate = True

    def _edit(self, item):
        q = model.Testsessioon.query
        liigid = self.c.user.get_testiliigid(self._permission)
        if None not in liigid:
            q = q.filter(model.Testsessioon.testiliik_kood.in_(liigid))
        
        self.c.items = q.order_by(sa.desc(model.Testsessioon.seq), 
                                  model.Testsessioon.oppeaasta).\
            all()

    def _perm_params(self):
        item_id = self.request.matchdict.get('id')
        if item_id:
            item = self._MODEL.get(item_id)
            return {'testiliik': item.testiliik_kood}
        
