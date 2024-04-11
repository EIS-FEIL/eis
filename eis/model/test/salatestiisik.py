# -*- coding: utf-8 -*-
# $Id: salatestiisik.py 1096 2017-01-11 06:17:05Z ahti $
"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import Opt
from eis.model.kasutaja import *
from eis.model.koht import *
      
class Salatestiisik(EntityHelper, Base):
    """Krüptitud testi lahti krüptida suutev isik
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    salatest_id = Column(Integer, ForeignKey('salatest.id'), index=True) # viide krüptitud andmete kirjele
    salatest = relationship('Salatest', foreign_keys=salatest_id, back_populates='salatestiisikud')
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale, kes saab lahti krüptida
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    _parent_key = 'salatest_id'


