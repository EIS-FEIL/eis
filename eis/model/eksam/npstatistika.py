# -*- coding: utf-8 -*-
"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Npstatistika(EntityHelper, Base):
    """Normipunktide vastuste statistika
    """
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    statistika_id = Column(Integer, ForeignKey('statistika.id'), index=True, nullable=False) # viide statistika kirjele
    statistika = relationship('Statistika', foreign_keys=statistika_id, back_populates='npstatistikad')
    normipunkt_id = Column(Integer, ForeignKey('normipunkt.id'), index=True, nullable=False) # viide normipunkti kirjele
    normipunkt = relationship('Normipunkt', foreign_keys=normipunkt_id, back_populates='npstatistikad') 
    vastuste_arv = Column(Integer) # selle vastusega sooritajate arv
    nvaartus = Column(Float) # arvuline väärtus (kui on arv)
    svaartus = Column(String(256)) # tekstiline väärtus (kui pole arv)
