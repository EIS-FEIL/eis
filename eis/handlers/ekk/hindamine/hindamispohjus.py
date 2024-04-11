from eis.lib.baseresource import *
_ = i18n._

import logging
log = logging.getLogger(__name__)

class HindamispohjusController(BaseResourceController):
    """Sisestatakse VI hindamise põhjus
    """
    _permission = 'ekk-hindamine6'    
    _MODEL = model.Sooritus
    _EDIT_TEMPLATE = 'ekk/hindamine/ekspert.hindamispohjus.mako'
    _ITEM_FORM = forms.ekk.hindamine.HindamispohjusForm

    def _edit(self, item):
        holek = self.c.sooritus.give_hindamisolek(self.c.hindamiskogum)
        liik = const.HINDAJA6
        self.c.hindamine = holek.get_hindamine(liik)

    def _update(self, item):
        if not self.c.sooritus.toimumisaeg.testimiskord.tulemus_kinnitatud:
            raise ValidationError(self, {}, _("Tulemused pole kinnitatud, ei saa VI hindamist teha"))
            
        hindamine = self._give_hindamine()
        hindamine.hindamispohjus = self.form.data['hindamispohjus']

    def _give_hindamine(self):           
        holek = self.c.sooritus.give_hindamisolek(self.c.hindamiskogum)
        liik = const.HINDAJA6
        self.c.hindamine = holek.give_hindamine(liik,
                                                hindaja_kasutaja_id=self.c.user.id)
        lv = model.Labiviija.give_hindaja(self.c.toimumisaeg.id, 
                                          self.c.user.id,
                                          liik, 
                                          self.c.toimumisaeg.testiosa, 
                                          self.c.hindamiskogum_id)
        self.c.hindamine.labiviija = lv
        holek.hindamistase = liik
        self.c.hindamine.komplekt = holek.komplekt
        return self.c.hindamine

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """
        c = self.c
        url = self.url('hindamine_ekspert_hindamised', toimumisaeg_id=c.toimumisaeg.id, sooritus_id=c.sooritus.id, hindamiskogum_id=c.hindamiskogum_id)
        return HTTPFound(location=url)

    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        self.c.hindamiskogum_id = int(self.request.matchdict.get('hindamiskogum_id'))
        self.c.hindamiskogum = model.Hindamiskogum.get(self.c.hindamiskogum_id)
        tos_id = self.request.matchdict.get('id')
        self.c.sooritus = model.Sooritus.get(tos_id)

