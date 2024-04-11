from eis.lib.baseresource import *
from eis.lib.examclient import ExamClient
_ = i18n._

log = logging.getLogger(__name__)

class KlastridController(BaseResourceController):
    _permission = 'admin'
    _MODEL = model.Klaster
    _EDIT_TEMPLATE = 'admin/klaster.mako'
    _INDEX_TEMPLATE = 'admin/klastrid.mako'
    _LIST_TEMPLATE = 'admin/klastrid_list.mako'
    _ITEM_FORM = forms.admin.KlasterForm
    _DEFAULT_SORT = 'klaster.id'
    _actions = 'index,new,create,edit,update,delete'
    _index_after_create = True
    _no_search_default = True
    
    def _search(self, q):
        c = self.c
        c.active = q.filter_by(staatus=const.B_STAATUS_KEHTIV).count()
        return q

    def _update(self, item):
        super()._update(item)

        # sekventside kordaja salvestamine
        res = ExamClient(self, item.int_host).check()
        item.seqmult = res['seqmult'] 
        
