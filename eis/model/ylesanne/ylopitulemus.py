# -*- coding: utf-8 -*-
"Ülesande andmemudel"

from eis.model.entityhelper import *
from eis.model.klassifikaator import *

from .ylesandeaine import Ylesandeaine
from .ylesanne import Ylesanne

class Ylopitulemus(EntityHelper, Base):
    """Ülesande õpitulemused
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    opitulemus_klrida_id = Column(Integer, ForeignKey('klrida.id'), index=True, nullable=False) # õpitulemus, klassifikaator OPITULEMUS
    opitulemus_klrida = relationship('Klrida', foreign_keys=opitulemus_klrida_id)
    ylesandeaine_id = Column(Integer, ForeignKey('ylesandeaine.id'), index=True, nullable=False) # viide ülesande õppeainele
    ylesandeaine = relationship('Ylesandeaine', foreign_keys=ylesandeaine_id, back_populates='ylopitulemused')
    _parent_key = 'ylesanne_id'

    @property
    def aine_kood(self):
        ylesandeaine = self.ylesandeaine or Ylesandeaine.get(self.ylesandeaine_id)
        return ylesandeaine.aine_kood

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        ylesandeaine = self.ylesandeaine or Ylesandeaine.get(self.ylesandeaine_id)        
        if ylesandeaine:
            ylesanne = ylesandeaine.ylesanne or Ylesanne.get(ylesandeaine.ylesanne_id)
            if ylesanne:
                ylesanne.logi('Ülesande õpitulemus', vanad_andmed, uued_andmed, logitase)
    
    def pack_row(self):
        di = EntityHelper.pack_row(self)

        # et saaks baaside vahel eksportida-importida,
        # pakime õpitulemuse ID asemel IDURLi
        kr = self.opitulemus_klrida
        del di['opitulemus_klrida_id']
        di['_opitulemus_klrida_idurl'] = kr.idurl
        return di
