# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class MuutjadController(BaseResourceController):
    """Koostamise ajalugu (logi vaatamine)
    """
    _permission = 'ylesandekogud'

    _MODEL = model.Ylesandekogulogi
    _INDEX_TEMPLATE = 'ekk/ylesandekogud/muutjad.mako'
    _LIST_TEMPLATE = 'ekk/ylesandekogud/muutjad_list.mako'
    _ITEM_FORM = None #forms.ekk.ylesanded.MuutjadForm 
    _DEFAULT_SORT = '-ylesandekogulogi.id'
    _actions = 'show'
    
    def show(self):
        return self.index()

    def _query(self):
        id = self.request.matchdict.get('id')
        return model.Ylesandekogulogi.query.filter_by(ylesandekogu_id=id)

    def __before__(self):
        self.c.ylesandekogu = model.Ylesandekogu.get(self.request.matchdict.get('id'))

    def _perm_params(self):
        return {'obj':self.c.ylesandekogu}

