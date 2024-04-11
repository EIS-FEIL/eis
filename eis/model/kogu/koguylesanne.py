# -*- coding: utf-8 -*-
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from .ylesandekogu import Ylesandekogu

class Koguylesanne(EntityHelper, Base):
    """Ülesandekogusse kuuluv ülesanne
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    ylesandekogu_id = Column(Integer, ForeignKey('ylesandekogu.id'), index=True, nullable=False) # viide kogule
    ylesandekogu = relationship('Ylesandekogu', foreign_keys=ylesandekogu_id, back_populates='koguylesanded')
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True, nullable=False) # viide kogusse kuuluvale ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='koguylesanded')
    _parent_key = 'ylesandekogu_id'

    logging = True
    logging_type1 = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        kogu = self.ylesandekogu or Ylesandekogu.get(self.ylesandekogu_id)
        if kogu:
            map_liik = {LOG_UPDATE: 'ülesanne',
                        LOG_INSERT: 'ülesande lisamine',
                        LOG_DELETE: 'ülesande eemaldamine'}
            liik = map_liik.get(liik)
            kogu.logi(liik, vanad_andmed, uued_andmed, logitase)
    
