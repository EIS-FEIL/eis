# -*- coding: utf-8 -*-
"Soorituskoha nimed"

from eis.model.entityhelper import *

class Koolinimi(EntityHelper, Base):
    """Soorituskoha kõik nimed, mille järgi saab kohta otsida 
    (nii endised kui ka praegune)
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True) 
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True, nullable=False) # viide kohale
    koht = relationship('Koht', foreign_keys=koht_id, back_populates='koolinimed')
    nimi = Column(String(100), nullable=False) # nimi
    alates = Column(Date, nullable=False) # kuupäev, millest alates nimi kehtib
    _parent_key = 'koht_id'
