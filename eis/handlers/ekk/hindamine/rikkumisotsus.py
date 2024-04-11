from eis.lib.baseresource import *
from eis.lib.resultentry import ResultEntry
_ = i18n._

import logging
log = logging.getLogger(__name__)

class RikkumisotsusController(BaseResourceController):
    """Töö hindamine rikkumise tõttu 0 punktiga, VI hindamise käigus
    """
    _permission = 'ekk-hindamine6'    
    _MODEL = model.Sooritus
    _EDIT_TEMPLATE = 'ekk/hindamine/ekspert.rikkumisotsus.mako'
    _ITEM_FORM = forms.ekk.hindamine.RikkumisotsusForm
    _actions = 'edit,update'

    def _update(self, item):
        oli_rikkumine = item.on_rikkumine or False
        on_rikkumine = self.form.data.get('on_rikkumine') or False
        item.on_rikkumine = on_rikkumine
        if oli_rikkumine != on_rikkumine:
            model.Session.flush()
            testiosa = item.testiosa
            sooritaja = item.sooritaja
            test = sooritaja.test
            resultentry = ResultEntry(self, const.SISESTUSVIIS_PALLID, test, testiosa)
            resultentry.update_sooritus(sooritaja, item, True)
        item.rikkumiskirjeldus = self.form.data['rikkumiskirjeldus']
            
    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """
        c = self.c
        # tagasi hindamiskogumite loetellu
        url = self.url('hindamine_ekspert_kogum', toimumisaeg_id=c.toimumisaeg.id, id=c.sooritus.id)
        return HTTPFound(location=url)

    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        tos_id = self.request.matchdict.get('id')
        self.c.sooritus = model.Sooritus.get(tos_id)

    #def _perm_params(self):
    #    return {'obj':self.c.toimumisaeg.testimiskord}
        
