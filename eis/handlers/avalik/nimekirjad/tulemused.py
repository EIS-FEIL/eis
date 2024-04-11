# -*- coding: utf-8 -*- 
# $Id: tulemused.py 889 2016-09-29 13:36:33Z ahti $

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.xtee import ehis

log = logging.getLogger(__name__)

class TulemusedController(BaseResourceController):
    """Sooritaja tulemuse vaatamine
    """
    _MODEL = model.Sooritaja
    _permission = 'nimekirjad'
    _EDIT_TEMPLATE = 'avalik/nimekirjad/kontroll.tulemus.mako'
    _no_paginate = True
    
    def __before__(self):
        id = self.request.matchdict.get('id')
        self.c.item = model.Sooritaja.get(id)

    def _has_permission(self):
        if self.c.item:
            if self.c.item.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
                return self.c.item.esitaja_kasutaja_id == self.c.user.id
            else:
                opilane = self.c.item.kasutaja.opilane
                return opilane and opilane.koht_id == self.c.user.koht_id
    
