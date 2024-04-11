# -*- coding: utf-8 -*-
# $Id: kiirvalik.py 485 2016-03-18 11:32:55Z ahti $
"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import Opt
from eis.model.kasutaja import *
from eis.model.koht import *

class Kiirvalik(EntityHelper, Base):
    """Testimiskordade kiirvalik, kiirendab sooritajal mitmele testile korraga registreerimist
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    testiliik_kood = Column(String(10), nullable=False) # kiirvalikusse kuuluvate testide liik, klassifikaator TESTILIIK
    nimi = Column(String(100), nullable=False) # nimetus
    staatus = Column(Integer, nullable=False) # olek: 1 - kasutusel; 0 - pole kasutusel
    selgitus = Column(String(1024)) # selgitus
    testimiskorrad = relationship('Testimiskord', secondary='testimiskord_kiirvalik', back_populates='kiirvalikud') # testimiskorrad, mis antud kiirvalikusse kuuluvad

    @property
    def kehtib(self):
        return bool(self.staatus)

    @property
    def vajab_tapsustamist(self):
        "Kas kiirvaliku valimisel on vaja kuvada täpsustuste aken"
        for tk in self.testimiskorrad:
            if tk.test.on_kursused:
                return True
        return False

    def default(self):
        if not self.staatus:
            self.staatus = const.B_STAATUS_KEHTIV
