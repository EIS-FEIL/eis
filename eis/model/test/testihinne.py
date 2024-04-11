# -*- coding: utf-8 -*-
# $Id: testihinne.py 1096 2017-01-11 06:17:05Z ahti $
"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from .test import Test

class Testihinne(EntityHelper, Base):
    """Testi tulemuse eest antav hinne vastavalt tulemuseks saadud protsendile
    """
        
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False) # viide testile
    test = relationship('Test', foreign_keys=test_id, back_populates='testihinded')
    hinne = Column(Integer) # hinne, vahemikus 1-5
    pallid = Column(Float) # minimaalne tulemuse protsent sooritajale võimalikust kogutulemusest (mitte pallide arv!), mis peab olema tulemuseks, et saada hinne
    _parent_key = 'test_id'

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        test = self.test or self.test_id and Test.get(self.test_id)
        if test:
            test.logi('Testihinne %s (%s) %s' % (self.id, self.hinne, liik), vanad_andmed, uued_andmed, logitase)

    def get_pallid(self, max_pallid):
        "Hinde jaoks vajalik tulemus pallides"
        return max_pallid * self.pallid / 100.
    
