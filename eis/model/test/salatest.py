# -*- coding: utf-8 -*-
# $Id: salatest.py 1096 2017-01-11 06:17:05Z ahti $
"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import Opt
from eis.model.kasutaja import *
from eis.model.koht import *

class Salatest(EntityHelper, Base):
    """Krüptitud testi sisu
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    parool = Column(Text) # SK sertifikaatidele krüptitud parool .cdoc (<EncryptedData>) kujul
    data = Column(LargeBinary) # parooliga krüptitud andmed
    test_id = Column(Integer, ForeignKey('test.id'), index=True) # viide testile
    test = relationship('Test', foreign_keys=test_id, back_populates='salatest') 
    _parent_key = 'test_id' 
    salatestiisikud = relationship('Salatestiisik', back_populates='salatest')

    def delete_subitems(self):    
        self.delete_subrecords(['salatestiisikud'])
        
