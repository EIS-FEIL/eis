# -*- coding: utf-8 -*- 
# $Id: asukohamaarus.py 383 2016-02-29 16:28:53Z ahti $

from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController

log = logging.getLogger(__name__)

class AsukohamaarusController(BaseResourceController):

    _permission = 'admin'

    _MODEL = model.Asukohamaarus
    _ITEM_FORM = forms.admin.AsukohamaarusForm
    _INDEX_TEMPLATE = 'admin/asukohamaarus.mako'
    _EDIT_TEMPLATE = 'admin/asukohamaarus.mako'
    _DEFAULT_SORT = 'id' # vaikimisi sortimine
    _index_after_create = True
    
    def _paginate(self, q):
        # ei soovita paginaatorit, soovitakse kõik grupid ühel lehel kuvada
        return q.all()

    def _create(self, **kw):
        items = self.form.data.get('r')
        collection = model.Asukohamaarus.query.all()
        BaseGridController(collection, model.Asukohamaarus, None, self).save(items)
