# -*- coding: utf-8 -*-
# $Id: kasutajakoht.py 1096 2017-01-11 06:17:05Z ahti $

import hashlib

from eis.model.entityhelper import *
from eis.model.koht import Koht
from eis.model.klassifikaator import Klrida

log = logging.getLogger(__name__)

class Kasutajakoht(EntityHelper, Base):
    """Kasutajaga seotud soorituskohad (kus kasutaja on hindajate, korraldajate jne kiirvalikus)
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='kasutajakohad')
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True, nullable=False) # viide soorituskohale
    koht = relationship('Koht', foreign_keys=koht_id, back_populates='kasutajakohad')
