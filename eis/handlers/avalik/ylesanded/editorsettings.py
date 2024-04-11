# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController

log = logging.getLogger(__name__)

class EditorsettingsController(BaseResourceController):
    """Lahendaja tekstitoimeti seadistamine"""

    _permission = 'ylesanded'

    _MODEL = model.Ylesanne
    _EDIT_TEMPLATE = 'ekk/ylesanded/editorsetting.mako'
    _ITEM_FORM = forms.ekk.ylesanded.EditorsettingForm 
    
    def _update(self, item):
        lahendusjuhis = item.give_lahendusjuhis()
        #lahendusjuhis.nupujuhis = self.form.data.get('nupujuhis')
        icons = self.form.data.get('icon')
        if not icons:
            self.error(_("Palun valida vähemalt üks nupp"))
            return
        lahendusjuhis.nupuriba = ','.join(icons)
        
        if 'Maximize' in icons:
            found = False
            for sp in item.sisuplokid:
                for k in sp.kysimused:
                    if k.rtf and not k.rtf_notshared:
                        found = k.rtf_notshared = True
            if found:
                self.notice(_("Küsimuse seadeid muudeti, sest maksimeerimise nupp eeldab nupuriba asumist lahtri sees"))
                
        self.c.updated = True

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """
        self.success()
        return self.edit()

    def __before__(self):
        """Väärtustame self.c.item ylesandega ning self.c.lang keelega,
        seejuures kontrollime, et self.c.lang oleks selle ülesande tõlkekeel.
        """
        self.c.lang = self.params_lang()
        id = self.request.matchdict.get('id')
        if id:
            self.c.item = model.Ylesanne.get(id)
            if self.c.lang and (self.c.lang == self.c.item.lang or self.c.lang not in self.c.item.keeled):
                self.c.lang = None
        else:
            self.c.lang = None
        super(EditorsettingsController, self).__before__()

    def _perm_params(self):
        return {'obj':self.c.item}
