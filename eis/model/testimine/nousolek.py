# -*- coding: utf-8 -*-
# $Id: nousolek.py 1096 2017-01-11 06:17:05Z ahti $
"Testikorralduse andmemudel"

import pickle
from cgi import FieldStorage
import mimetypes

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *

class Nousolek(EntityHelper, Base):
    """Testi läbiviimise nõusolekud.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    staatus = Column(Integer, sa.DefaultClause('1'), nullable=False) # olek
    toimumisaeg_id = Column(Integer, ForeignKey('toimumisaeg.id'), index=True, nullable=False) # viide toimumisajale
    toimumisaeg = relationship('Toimumisaeg', foreign_keys=toimumisaeg_id, back_populates='nousolekud')
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide läbiviija kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='nousolekud')
    on_vaatleja = Column(Boolean) # kas on nõus vaatlema
    on_hindaja = Column(Boolean) # kas on nõus hindama
    on_intervjueerija = Column(Boolean) # kas on nõus intervjueerima

    vaatleja_ekk = Column(Boolean) # kas vaatlemise nõusoleku sisestas eksamikeskus
    hindaja_ekk = Column(Boolean) # kas hindamise nõusoleku sisestas eksamikeskus
    intervjueerija_ekk = Column(Boolean) # kas intervjueerimise nõusoleku sisestas eksamikeskus
    
    vaatleja_aeg = Column(DateTime) # millal anti vaatlemise nõusolek
    hindaja_aeg = Column(DateTime) # millal anti hindamise nõusolek
    intervjueerija_aeg = Column(DateTime) # millal anti intervjueerimise nõusolek
    
