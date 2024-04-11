from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

import eis.handlers.ekk.regamine.erivajadused as erivajadused

class ErivajadusedController(erivajadused.ErivajadusedController):
    """Soorituse erivajadused
    """
    _permission = 'ekk-testid'
    _MODEL = model.Sooritus
    _EDIT_TEMPLATE = 'ekk/testid/erivajadus.mako'
    _ITEM_FORM = forms.ekk.regamine.ErivajadusedForm

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)
        self.c.komplekt_id = self.request.matchdict.get('komplekt_id')
        self.c.komplekt = model.Komplekt.get(self.c.komplekt_id)
        self.c.komplektivalik = self.c.komplekt.komplektivalik
        self.c.testiosa = self.c.komplektivalik.testiosa
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}
    
