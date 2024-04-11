# -*- coding: utf-8 -*-
from eis.model.entityhelper import *

class Ylesandekogulogi(EntityHelper, Base):
    """Ülesandekogu koostamise ajalugu
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    aeg = Column(DateTime, nullable=False) # logi aeg
    liik = Column(String(256)) # logitava olemi kirjeldus
    vanad_andmed = Column(Text) # vanad andmed
    uued_andmed = Column(Text) # uued andmed
    ylesandekogu_id = Column(Integer, ForeignKey('ylesandekogu.id'), index=True, nullable=False) # viide ülesandekogule
    ylesandekogu = relationship('Ylesandekogu', foreign_keys=ylesandekogu_id, back_populates='ylesandekogulogid')
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    _parent_key = 'ylesandekogu_id'
    
    def set_modifier(self):
        EntityHelper.set_modifier(self)
        self.aeg = datetime.now()

