# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from .klread import KlreadController
log = logging.getLogger(__name__)

class TKlreadController(KlreadController):
    """Klassifikaatori ridade AJAXiga uuendamine klassifikaatori haldamise lehel
    """
    _permission = 'klassifikaatorid'
    _MODEL = model.Klrida
    _INDEX_TEMPLATE = '/admin/tklread.mako'
    _LIST_TEMPLATE = '/admin/tklread.mako'    
    _DEFAULT_SORT = 'klrida.jrk,klrida.id'
    _no_paginate = True
    
    def __before__(self):
        self.c.lang = self.request.matchdict.get('lang')        
