# -*- coding: utf-8 -*-
"Ülesande andmemudel"

from eis.model.entityhelper import *
from eis.model.klassifikaator import *

from .ylesandeaine import Ylesandeaine
from .ylesanne import Ylesanne

class Ylesandeteema(EntityHelper, Base):
    """Ülesande valdkonnad ja teemad
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    teema_kood = Column(String(10), nullable=False) # teema (varasem nimetus: valdkond) ülesande õppeaines, klassifikaator TEEMA
    alateema_kood = Column(String(10)) # alateema (varem nimetus: teema) teemas, klassifikaator ALATEEMA
    ylesandeaine_id = Column(Integer, ForeignKey('ylesandeaine.id'), index=True, nullable=False) # viide ülesande õppeainele
    ylesandeaine = relationship('Ylesandeaine', foreign_keys=ylesandeaine_id, back_populates='ylesandeteemad')
    _parent_key = 'ylesanne_id'

    @property
    def aine_kood(self):
        ylesandeaine = self.ylesandeaine or Ylesandeaine.get(self.ylesandeaine_id)
        return ylesandeaine.aine_kood

    @property
    def alateema_nimi(self):
        if self.teema_id:
            return Klrida.get_str('ALATEEMA', self.alateema_kood, ylem_id=self.teema_id)        

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        ylesandeaine = self.ylesandeaine or Ylesandeaine.get(self.ylesandeaine_id)        
        if ylesandeaine:
            ylesanne = ylesandeaine.ylesanne or Ylesanne.get(ylesandeaine.ylesanne_id)
            if ylesanne:
                ylesanne.logi('Ülesandeteema', vanad_andmed, uued_andmed, logitase)
    
