# -*- coding: utf-8 -*-
"Ülesande andmemudel"

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from .ylesanne import Ylesanne

class Kasutliik(EntityHelper, Base):
    """Ülesande kasutuse liigid
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutliik_kood = Column(String(10), nullable=False) # kasutusliigi kood, klassifikaator KASUTLIIK
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True, nullable=False) # viide ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='kasutliigid')
    __table_args__ = (
        sa.UniqueConstraint('ylesanne_id','kasutliik_kood'),
        )
    _parent_key = 'ylesanne_id'

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        ylesanne = self.ylesanne or self.ylesanne_id and Ylesanne.get(self.ylesanne_id)
        if ylesanne:
            ylesanne.logi('Kasutusliik', vanad_andmed, uued_andmed, logitase)

