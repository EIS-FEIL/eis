from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
from eis.lib.validationerror import neworder
_ = i18n._

log = logging.getLogger(__name__)

class TagasisideatgrupidController(BaseResourceController):
    """Testiosa normipunktid (profiililehe seaded)
    """
    _permission = 'ekk-testid'
    _MODEL = model.Alatestigrupp
    _INDEX_TEMPLATE = 'ekk/testid/tagasiside.atgrupid.mako'
    _EDIT_TEMPLATE = 'ekk/testid/tagasiside.atgrupid.mako'
    _ITEM_FORM = forms.ekk.testid.TagasisideAtgrupidForm 
    _index_after_create = True
    _create_is_tr = True
    
    def _index(self):
        return self.render_to_response(self._INDEX_TEMPLATE)

    def _create(self):
        "normipunktid.mako seest avatud dialoogiaknas salvestamine"
        atg = self.form.list_in_posted_order('atg')
        atg = neworder(self, 'atg', atg)
        BaseGridController(self.c.testiosa.alatestigrupid,
                           model.Alatestigrupp).save(atg, lang=self.c.lang)

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

