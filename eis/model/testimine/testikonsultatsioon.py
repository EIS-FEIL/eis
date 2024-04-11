# -*- coding: utf-8 -*-
# $Id: testikonsultatsioon.py 389 2016-03-03 13:51:55Z ahti $
"Testi andmemudel"
from eis.model.entityhelper import *

class Testikonsultatsioon(EntityHelper, Base):
    """Eksamite testimiskordade seos konsultatsioonikordadega
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    eksam_testimiskord_id = Column(Integer, ForeignKey('testimiskord.id'), index=True, nullable=False) # viide eksami testimiskorrale
    eksam_testimiskord = relationship('Testimiskord', foreign_keys=eksam_testimiskord_id, back_populates='konskorrad')
    kons_testimiskord_id = Column(Integer, ForeignKey('testimiskord.id'), index=True, nullable=False) # viide konsultatsiooni toimumiskorrale
    kons_testimiskord = relationship('Testimiskord', foreign_keys=kons_testimiskord_id, back_populates='eksamikorrad') 
    __table_args__ = (
        sa.UniqueConstraint('eksam_testimiskord_id','kons_testimiskord_id'),
        )
