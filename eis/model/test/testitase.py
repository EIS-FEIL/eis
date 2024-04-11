# -*- coding: utf-8 -*-
"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *

class Testitase(EntityHelper, Base):
    """Testiga hinnatav keeleoskuse tase (võib sõltuda saadud tulemusest, näiteks: 75-100p on B2, 50-74p on B1, alla 50p taset pole).
    Test annab vastava taseme ainult juhul, kui testiliik on rahvusvaheline eksam, riigieksam, põhikooli eksam või tasemeeksam.
    Muudel juhtudel (nt eeltest) on tase kasutusel ainult testi kirjeldamiseks.
    """
        
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False) # viide testile
    test = relationship('Test', foreign_keys=test_id, back_populates='testitasemed')
    aine_kood = Column(String(10)) # õppeaine, klassifikaator AINE (dubleerib välja Test.aine_kood)
    keeletase_kood = Column(String(10), nullable=False) # keeleoskuse tase (riigikeele eksami korral), klassifikaator KEELETASE
    pallid = Column(Float) # minimaalne tulemuse protsent sooritajale võimalikust kogutulemusest (mitte pallide arv!), mis peab olema tulemuseks, et vastata antud tasemele; kui on NULL, siis süsteem taset ei anna
    seq = Column(Integer, nullable=False) # mitmes tase (kõige kõrgem peab olema 1, järgmine on 2)
    _parent_key = 'test_id'

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .test import Test
        test = self.test or self.test_id and Test.get(self.test_id)
        if test:
            test.logi('Testitase %s (%s) %s' % (self.id, self.keeletase_kood, liik), vanad_andmed, uued_andmed, logitase)
