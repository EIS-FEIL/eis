import sys
import os
import pickle
import re

from eis.lib.base import *
from eis.lib.block import BlockController
log = logging.getLogger(__name__)

class ImportPackage(object):
    def __init__(self):
        self.is_error = False # kas importimine õnnestus
        self.items = [] # imporditud kirjed
        self.messages = [] # importimise sõnaline väljund kasutajale
        self.handler = None
        
    def notice(self, txt):
        self.messages.append((True, txt))

    def error(self, txt):
        self.messages.append((False, txt)) 

    def after_import_ylesanne(self, item):
        """Peale ylesande kopeerimist või importimist võib olla vaja
        muuta sisuploki teksti sisu (nt sisuploki ID)
        (vajalik hottext, colorText, inlineTextEntry ja gapMatchInteraction korral)
        """
        BlockController.after_copy_task(item, self.handler)
        item.check(self.handler)

        # avaliku staatusega ylesannetele ei pääse siseveebis ligi
        if item.staatus == const.Y_STAATUS_AV_KOOSTAMISEL:
            item.staatus = const.Y_STAATUS_KOOSTAMISEL
        elif item.staatus == const.Y_STAATUS_AV_VALMIS:
            item.staatus = const.Y_STAATUS_VALMIS
        elif item.staatus == const.Y_STAATUS_AV_ARHIIV:
            item.staatus = const.Y_STAATUS_ARHIIV

        if item.salastatud and self.handler.is_devel:
            item.salastatud = const.SALASTATUD_POLE
            
    def after_import(self):
        model.Session.flush()
        for item in self.items:
            if isinstance(item, model.Ylesanne):
                # DetachedInstanceError: Parent instance <Ylesanne at 0x6fff009bb50> is not bound to a Session; lazy load operation of attribute 'sisuplokid' cannot proceed
                #item = model.Ylesanne.get(item.id)
                #print('yl %s: %s' % (item.id, item.nimi))
                self.after_import_ylesanne(item)
            elif isinstance(item, model.Test):
                #item = model.Test.get(item.id)
                item.arvuta_pallid(True)

class ImportException(Exception):
    def __init__(self, message):
        self.message = message
        
