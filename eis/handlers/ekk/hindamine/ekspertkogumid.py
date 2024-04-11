# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
_ = i18n._

import logging
log = logging.getLogger(__name__)

class EkspertkogumidController(BaseResourceController):
    """Eksperthindaja hindab lahendaja kirjalikku lahendust.
    """
    _permission = 'eksperthindamine'
    _MODEL = model.Sooritus
    _EDIT_TEMPLATE = 'ekk/hindamine/ekspert.hindamiskogumid.mako'

    def _show(self, item):
        self.c.show_tulemus = True
        if item.staatus != const.S_STAATUS_TEHTUD:
            self.notice(_("Sooritamise olek: {s}").format(s=item.staatus_nimi))

        self.c.lang = item.sooritaja.lang

    def _edit(self, item):
        self._show(item)

    def __before__(self):
        c = self.c
        c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        c.testiosa = c.toimumisaeg.testiosa
        c.testimiskord = c.toimumisaeg.testimiskord
        c.test = c.testiosa.test
        c.hindamiskogum_opt = [(k.id, k.tahis) \
                                        for k in c.testiosa.hindamiskogumid \
                                        if k.staatus]

        tos_id = self.request.matchdict.get('id')
        c.sooritus = model.Sooritus.get(tos_id)
        c.sooritaja = c.sooritus.sooritaja
        self._kas_ekspert()

    def _kas_ekspert(self):
        c = self.c
        test = c.testimiskord.test            
        if c.testimiskord.tulemus_kinnitatud and test.testiliik_kood != const.TESTILIIK_RV:
            # kui tulemused on kinnitatud, siis on võimalik V ja VI hindamine
            if c.sooritaja.vaie and \
                   c.sooritaja.vaie.staatus in (const.V_STAATUS_MENETLEMISEL, const.V_STAATUS_ETTEPANDUD):
                # töö kohta käib vaidemenetlus
                # kas olen vaide ekspert
                q = (model.Labiviija.query
                     .filter(model.Labiviija.kasutaja_id==c.user.id)
                     .filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAMISEKSPERT)
                     .filter(model.Labiviija.toimumisaeg_id==c.toimumisaeg.id))
                c.ekspert_labiviija = q.first()
            elif c.user.has_permission('ekk-hindamine6', const.BT_UPDATE, obj=test):
                holek = c.sooritus.get_hindamisolek(c.hindamiskogum)
                if holek and holek.hindamistase == const.HINDAJA6:
                    c.olen_hindaja6 = True 

        elif not c.toimumisaeg.tulemus_kinnitatud or test.testiliik_kood == const.TESTILIIK_RV:
            # kas olen IV hindaja
            # EH-289: rahvusvahelise eksami korral toimub IV hindamine ka peale kinnitamist,
            # kuna vaidlustamine ei käi EISi kaudu
            c.olen_ekspert = c.user.has_group(const.GRUPP_HINDAMISEKSPERT, aine_kood=test.aine_kood)

    def _perm_params(self):
        return {'obj': self.c.test}

