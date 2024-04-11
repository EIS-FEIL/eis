# -*- coding: utf-8 -*-
"Testi andmemudel"
from eis.model.entityhelper import *

class Eeltest_komplekt(Base):
    __tablename__ = 'eeltest_komplekt'
    eeltest_id = Column(Integer, ForeignKey('eeltest.id'), index=True, primary_key=True)
    komplekt_id = Column(Integer, ForeignKey('komplekt.id'), index=True, primary_key=True)
    #stat_filedata = Column(LargeBinary) # eeltesti statistika PDF faili sisu
    #stat_ts = Column(DateTime) # eeltesti statistika PDF koostamise aeg
