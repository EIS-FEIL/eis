# -*- coding: utf-8 -*-
"Testi andmemudel"
from eis.model.entityhelper import *

class Regkoht_kord(Base):
    "Koolid, millel on lubatud testile registreerida"
    __tablename__ = 'regkoht_kord'
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True, primary_key=True)
    testimiskord_id = Column(Integer, ForeignKey('testimiskord.id'), index=True, primary_key=True)
