# -*- coding: utf-8 -*-
# $Id: testifailimarkus.py 1096 2017-01-11 06:17:05Z ahti $
"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import Opt
from eis.model.kasutaja import *
from eis.model.koht import *

class Testifailimarkus(EntityHelper, Base):
    """Testifaili märkused
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    testifail_id = Column(Integer, ForeignKey('testifail.id'), index=True, nullable=False) # viide testifaili kirjele
    testifail = relationship('Testifail', foreign_keys=testifail_id, back_populates='testifailimarkused')
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    aeg = Column(DateTime) # märkuse kirjutamise aeg
    sisu = Column(Text) # märkuse sisu
    teema = Column(String(100)) # märkuse teema
    ylem_id = Column(Integer, ForeignKey('testifailimarkus.id'), index=True) # viide ülemale märkusele, mida antud märkus kommenteerib
    ylem = relationship('Testifailimarkus', foreign_keys=ylem_id, remote_side=id, back_populates='alamad')
    alamad = relationship('Testifailimarkus', back_populates='ylem') 
    _parent_key = 'testifail_id'
    
    def set_creator(self):
        EntityHelper.set_creator(self)
        self.aeg = datetime.now()

    def delete_subitems(self):    
        self.delete_subrecords(['alamad'])

    @property
    def alamate_arv(self):
        return sum([m.alamate_arv + 1 for m in self.alamad]) or 0

