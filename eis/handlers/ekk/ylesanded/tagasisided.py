# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.lib.basegrid import *
_ = i18n._

log = logging.getLogger(__name__)

class TagasisidedController(BaseResourceController):
    """Ülesande tagasiside
    """
    _permission = 'ylesanded'

    _MODEL = model.Normipunkt
    _INDEX_TEMPLATE = 'ekk/ylesanded/tagasisided.mako'
    _EDIT_TEMPLATE = 'ekk/ylesanded/tagasisided.mako'    
    _no_paginate = True
    _ITEM_FORM = forms.ekk.ylesanded.TagasisideForm

    def _index_d(self):
        res = BaseResourceController._index_d(self)
        c = self.c
        if c.lang and (c.lang == c.ylesanne.lang or c.lang not in c.ylesanne.keeled):
            c.lang = None
        return res
            
    def _new_d(self):
        return self.response_dict
    
    def _create(self, **kw):
        data = self.form.data
        ylesanne = self.c.ylesanne
        ylesanne.from_form(data, 'f_', lang=self.c.lang)

        if self.c.lang:
            npts = [r for r in data['np']['npts']]
        else:
            npts = [r for r in data['np']['npts'] if r['tagasiside']]
            ylesanne.kuva_tulemus = data['kuva_tulemus']
        is_np = len(npts) > 0
        np = None
        if is_np:
            # salvestada 1 normipunkt
            for np in ylesanne.normipunktid:
                break
            if not np:
                np = model.Normipunkt(ylesanne=ylesanne)
            np.normityyp = data['np']['normikood']
            ctrl = BaseGridController(np.nptagasisided, model.Nptagasiside)
            if self.c.lang:
                for r in npts:
                    del r['jatka']
                ctrl.save(npts, lang=self.c.lang, update_only=True)
            else:
                ctrl.save(npts)

        if not self.c.lang:
            # kustutame liigsed
            for r in list(ylesanne.normipunktid):
                if r != np:
                    r.delete()
                    
        ylesanne.sum_tahemargid_lang(self.c.lang)
                
    def _after_create(self, id):
        if not self.has_errors():
            self.success()
        return self._redirect('index', lang=self.c.lang)
    
    def __before__(self):
        c = self.c
        ylesanne_id = self.request.matchdict.get('ylesanne_id')
        c.ylesanne = model.Ylesanne.get(ylesanne_id)
        c.lang = self.params_lang()
        if c.lang and (c.lang == c.ylesanne.lang or c.lang not in c.ylesanne.keeled):
            c.lang = None

    def _perm_params(self):
        return {'obj':self.c.ylesanne}

    def _get_permission(self):
        base = self._permission
        if self.request.params.get('is_tr'):
            if self.params_lang():
                return '%s-tolkimine' % base
            else:
                return '%s-toimetamine' % base
        return base

    def _get_perm_bit(self):
        action = self.c.action
        if action in ('create','edit', 'update'):
            return const.BT_UPDATE
        else:
            return BaseController._get_perm_bit(self)
