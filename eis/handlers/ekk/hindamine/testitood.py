# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
from eis.lib.resultentry import ResultEntry

import logging
log = logging.getLogger(__name__)

class TestitoodController(BaseResourceController):
    """Testitöö hindamiskogumite kaupa vaatamine
    """
    _permission = 'hindamisanalyys'
    _MODEL = model.Sooritus
    _EDIT_TEMPLATE = 'ekk/hindamine/analyys.testitoo.mako'
    _actions = 'show'

    def _show(self, item):
        self.c.show_tulemus = True
        if item.staatus != const.S_STAATUS_TEHTUD:
            self.notice(_("Sooritamise olek: {s}").format(s=item.staatus_nimi))
        self.c.test = self.c.testiosa.test
        if item.sooritaja:
            self.c.lang = item.sooritaja.lang

    def __before__(self):           
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))

        self.c.testiosa = self.c.toimumisaeg.testiosa
        self.c.test = self.c.testiosa.test
        tos_id = self.request.matchdict.get('id')
        self.c.sooritus = model.Sooritus.get(tos_id)
        self.c.sooritaja = self.c.sooritus.sooritaja

    def _perm_params(self):
        return {'obj': self.c.test}
        
