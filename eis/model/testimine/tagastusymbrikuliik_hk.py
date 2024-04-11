# -*- coding: utf-8 -*-
"Testi andmemudel"
from eis.model.entityhelper import *

class Tagastusymbrikuliik_hk(Base):
    __tablename__ = 'tagastusymbrikuliik_hk'
    tagastusymbrikuliik_id = Column(Integer, ForeignKey('tagastusymbrikuliik.id'), index=True, primary_key=True)
    hindamiskogum_id = Column(Integer, ForeignKey('hindamiskogum.id'), index=True, primary_key=True)
