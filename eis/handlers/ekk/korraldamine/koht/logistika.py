# -*- coding: utf-8 -*- 
# $Id: logistika.py 406 2016-03-07 19:18:48Z ahti $

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister
log = logging.getLogger(__name__)

class LogistikaController(BaseResourceController):
    _permission = 'korraldamine'
    _INDEX_TEMPLATE = '/ekk/korraldamine/koht.logistika.mako' 

    def _query(self):
        return None

    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        self.c.testikoht = model.Testikoht.get(self.request.matchdict.get('testikoht_id'))

    def _perm_params(self):
        return {'obj':self.c.testikoht}

