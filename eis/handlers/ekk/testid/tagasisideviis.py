# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class TagasisideviisController(BaseResourceController):
    """Tagasiside kuvamise viis
    """
    _permission = 'ekk-testid'
    _INDEX_TEMPLATE = 'ekk/testid/tagasiside.viis.mako'
    _EDIT_TEMPLATE = 'ekk/testid/tagasiside.viis.mako'    
    _actions = 'index,create'
    _index_after_create = True
    _ITEM_FORM = forms.ekk.testid.TagasisideViisForm
    
    def _index_d(self):
        return self.response_dict

    def _new_d(self):
        return self.response_dict
    
    def _create(self, **kw):
        item = self.c.test
        data = self.form.data
        item.from_form(data, 'f_')
        return item

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)

        testiosa_id = int(self.request.matchdict.get('testiosa_id'))
        if testiosa_id:
            self.c.testiosa = model.Testiosa.get(testiosa_id)
            if self.c.testiosa.test_id != self.c.test.id:
                self.c.testiosa = None
        if not self.c.testiosa:
            for self.c.testiosa in self.c.test.testiosad:
                break
            
    def _perm_params(self):
        return {'obj':self.c.test}

