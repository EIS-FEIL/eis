# -*- coding: utf-8 -*-
import hashlib

from eis.model.entityhelper import *
from eis.model.koht import Koht
from eis.model.klassifikaator import Klrida

log = logging.getLogger(__name__)

class Kasutajaoigus(EntityHelper, Base):
    """Kasutajaõigus (kasutajagrupile antud õigus)
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    nimi = Column(String(80), unique=True) # õiguse nimi ehk kood
    kirjeldus = Column(String(255)) # õiguse kirjeldus
    kasutajagrupp_oigused = relationship('Kasutajagrupp_oigus') # viited gruppidele

    @classmethod
    def all(cls):
        return cls.query.order_by(Kasutajaoigus.nimi).all()
    
    def __repr__(self):
        return '<Kasutajaoigus %r>' % (self.nimi)

