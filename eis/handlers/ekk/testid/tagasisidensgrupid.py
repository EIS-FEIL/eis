from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
from eis.lib.validationerror import neworder
_ = i18n._

log = logging.getLogger(__name__)

class TagasisidensgrupidController(BaseResourceController):
    """Tagasiside grupid
    """
    _permission = 'ekk-testid'
    _MODEL = model.Nsgrupp
    _INDEX_TEMPLATE = 'ekk/testid/tagasiside.nsgrupid.mako'
    _ERROR_TEMPLATE = 'ekk/testid/tagasiside.nsgrupid.mako'    
    _ITEM_FORM = forms.ekk.testid.TagasisideNsgrupidForm 
    _index_after_create = True
    
    def _index(self):
        return self.render_to_response(self._INDEX_TEMPLATE)

    def _create(self):
        "normipunktid.mako seest avatud dialoogiaknas salvestamine"
        nsg = self.form.data['nsg']
        nsg = neworder(self, 'nsg', nsg)
        BaseGridController(self.c.testiosa.nsgrupid,
                           model.Nsgrupp,
                           parent_controller=self).save(nsg, lang=self.c.lang)        
        model.Session.flush()
        self.c.test.sum_tahemargid_lang(self.c.lang)
        return None
    
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        testiosa_id = self.request.matchdict.get('testiosa_id')
        self.c.testiosa = model.Testiosa.get(testiosa_id)
        self.c.test = self.c.testiosa.test
        self.c.lang = self.params_lang()
        
    def _perm_params(self):
        return {'obj':self.c.test}
