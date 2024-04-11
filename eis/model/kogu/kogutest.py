# -*- coding: utf-8 -*-
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from .ylesandekogu import Ylesandekogu

class Kogutest(EntityHelper, Base):
    """Ülesandekogusse kuuluv test
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    ylesandekogu_id = Column(Integer, ForeignKey('ylesandekogu.id'), index=True, nullable=False) # viide kogule
    ylesandekogu = relationship('Ylesandekogu', foreign_keys=ylesandekogu_id, back_populates='kogutestid')
    test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False) # viide kogusse kuuluvale testile
    test = relationship('Test', foreign_keys=test_id, back_populates='kogutestid') # viide testile 
    _parent_key = 'ylesandekogu_id'

    logging = True
    logging_type1 = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        kogu = self.ylesandekogu or Ylesandekogu.get(self.ylesandekogu_id)
        if kogu:
            map_liik = {LOG_UPDATE: 'test',
                        LOG_INSERT: 'testi lisamine',
                        LOG_DELETE: 'testi eemaldamine'}
            liik = map_liik.get(liik)
            kogu.logi(liik, vanad_andmed, uued_andmed, logitase)


