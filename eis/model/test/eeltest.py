# -*- coding: utf-8 -*-
"Testi andmemudel"
from eis.model.entityhelper import *

class Eeltest(EntityHelper, Base):
    """Testikomplekti avaldamine eeltestimiseks.
    Kirje jääb alles ka peale eeltesti kustutamist.
    """
        
    id = Column(Integer, primary_key=True, autoincrement=True)
    algne_test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False) # viide algsele testile, millest eeltest loodi
    algne_test = relationship('Test', foreign_keys=algne_test_id, back_populates='eeltestid')
    avalik_test_id = Column(Integer) # viide avalikule testile, mis on algse testi testimiseks loodud (jääb alles ka peale avaliku testi kustutamist)
    avalik_test = relationship('Test', foreign_keys='Test.eeltest_id', uselist=False, back_populates='eeltest')
    tagasiside_sooritajale = Column(Boolean) # kas sooritaja võib testimiskorraga testis tagasisidet näha kohe peale sooritamist, enne koondtulemuse avaldamist
    tagasiside_koolile = Column(Boolean) # kas õpetaja võib testimiskorraga testis tagasisidet näha kohe peale sooritamist, enne koondtulemuse avaldamist

    markus_korraldajatele = Column(String(512)) # testi koostaja märkused korraldajatele
    stat_filedata = Column(LargeBinary) # eeltesti statistika PDF faili sisu
    stat_ts = Column(DateTime) # eeltesti statistika PDF koostamise aeg
    komplektid = relationship('Komplekt', secondary='eeltest_komplekt', back_populates='eeltestid') # algse testi komplektid, mis anti eeltestimiseks
    _parent_key = 'algne_test_id'

    def __repr__(self):
        return '<%s id=%r, test_id=%s>' % \
            (self.__class__.__name__, self.id, self.test_id)

