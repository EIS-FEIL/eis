# -*- coding: utf-8 -*-
"Testi andmemudel"
from eis.model.entityhelper import *

class Piirkond_kord(Base):
    __tablename__ = 'piirkond_kord'
    piirkond_id = Column(Integer, ForeignKey('piirkond.id'), index=True, primary_key=True)
    testimiskord_id = Column(Integer, ForeignKey('testimiskord.id'), index=True, primary_key=True)
