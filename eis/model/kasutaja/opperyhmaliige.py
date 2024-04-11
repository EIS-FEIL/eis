# -*- coding: utf-8 -*-
"Õpilaste rühma liige"

from eis.model.entityhelper import *
from eis.model.kasutaja import *

class Opperyhmaliige(EntityHelper, Base):
    """Õpilaste rühma liige
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    opperyhm_id = Column(Integer, ForeignKey('opperyhm.id'), index=True, nullable=False) # rühm
    opperyhm = relationship('Opperyhm', foreign_keys=opperyhm_id, back_populates='opperyhmaliikmed')
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # õpilane
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='opperyhmaliikmed')
