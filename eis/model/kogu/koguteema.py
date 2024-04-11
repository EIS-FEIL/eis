# -*- coding: utf-8 -*-
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from .ylesandekogu import Ylesandekogu

class Koguteema(EntityHelper, Base):
    """Ülesandekogu valdkonnad ja teemad
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    teema_kood = Column(String(10), nullable=False) # teema (varasem valdkond) kogu õppeaines, klassifikaator TEEMA
    alateema_kood = Column(String(10)) # alateema (varasem teema), klassifikaator ALATEEMA
    ylesandekogu_id = Column(Integer, ForeignKey('ylesandekogu.id'), index=True) # viide kogule
    ylesandekogu = relationship('Ylesandekogu', foreign_keys=ylesandekogu_id, back_populates='koguteemad')
    _parent_key = 'kogu_id'

    @property
    def aine_kood(self):
        kogu = self.ylesandekogu or Ylesandekogu.get(self.ylesandekogu_id)
        return kogu.aine_kood

    @property
    def alateema_nimi(self):
        if self.teema_id:
            return Klrida.get_str('ALATEEMA', self.alateema_kood, ylem_id=self.teema_id)        

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        kogu = self.ylesandekogu or Ylesandekogu.get(self.ylesandekogu_id)        
        if kogu:
            kogu.logi('Teema', vanad_andmed, uued_andmed, logitase)
    
