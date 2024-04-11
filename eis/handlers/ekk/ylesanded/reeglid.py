# -*- coding: utf-8 -*- 
# $Id: reeglid.py 406 2016-03-07 19:18:48Z ahti $

from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class ReeglidController(BaseResourceController):
    """Ülesande hindamise reeglid"""

    _permission = 'ylesanded'

    _MODEL = model.Ylesanne
    _EDIT_TEMPLATE = 'ekk/ylesanded/reeglid.mako'
    _ITEM_FORM = forms.ekk.ylesanded.ReeglidForm 

    def _update(self, item):
        BaseResourceController._update(self, item)

        # order = self.form.data.get('order')
        # if order:
        #     # order on kujul: item_1,item_3,item_2
        #     li = [int(i.split('_')[1]) for i in order.split(',')]
        #     for block in item.asBlock_list:
        #         block.seq = li.index(block.id) + 1

    def __before__(self):
        self.c.ylesanne = model.Ylesanne.get(self.request.matchdict.get('id'))
        
    def _perm_params(self):
        return {'obj':self.c.ylesanne}
