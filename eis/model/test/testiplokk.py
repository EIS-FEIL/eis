# -*- coding: utf-8 -*-
"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import Opt
from eis.model.kasutaja import *
from eis.model.koht import *

from .alatest import Alatest

class Testiplokk(EntityHelper, Base):
    """Testiplokk
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    seq = Column(Integer) # järjekorranumber alatesti sees
    nimi = Column(String(256)) # testiploki nimetus
    max_pallid = Column(Float) # max pallide arv
    ylesannete_arv = Column(Integer) # ülesannete arv
    alatest_id = Column(Integer, ForeignKey('alatest.id'), index=True, nullable=False) # viide alatestile
    alatest = relationship('Alatest', foreign_keys=alatest_id, back_populates='testiplokid')
    testiylesanded = relationship('Testiylesanne', order_by='Testiylesanne.seq', back_populates='testiplokk')
    _parent_key = 'alatest_id'    

    trans = relationship('T_Testiplokk', cascade='all')

    def default(self):
        if not self.max_pallid:
            self.max_pallid = 0
        if not self.ylesannete_arv:
            self.ylesannete_arv = 0

    def delete_subitems(self):    
        self.delete_subrecords(['testiylesanded',
                                ])

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        alatest = self.alatest or self.alatest_id and Alatest.get(self.alatest_id)
        if alatest:
            alatest.logi('Testiplokk %s (%s) %s' % (self.id, self.nimi, liik), vanad_andmed, uued_andmed, logitase)

