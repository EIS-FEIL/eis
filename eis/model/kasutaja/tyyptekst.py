# -*- coding: utf-8 -*-

from eis.model.entityhelper import *
log = logging.getLogger(__name__)

class Tyyptekst(EntityHelper, Base):
    """Kirjade tüüptekstid
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tyyp = Column(String(25), nullable=False, unique=True) # kirja tüüp (vt Kiri.TYYP_*)
    teema = Column(String(256), nullable=False) # kirja teema
    sisu = Column(Text, nullable=False) # kirja sisu
    
