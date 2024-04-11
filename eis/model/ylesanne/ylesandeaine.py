# -*- coding: utf-8 -*-
"Ülesande andmemudel"

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *

from .ylesanne import Ylesanne

class Ylesandeaine(EntityHelper, Base):
    """Ülesande õppeaine
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True, nullable=False) # viide ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='ylesandeained')
    seq = Column(Integer) # õppeaine järjekorranumber, ülesande peamise õppeaine korral 0
    aine_kood = Column(String(10), nullable=False) # õppeaine, klassifikaator AINE
    oskus_kood = Column(String(10)) # osaoskus, klassifikaator OSKUS
    ylesandeteemad = relationship('Ylesandeteema', order_by='Ylesandeteema.id', back_populates='ylesandeaine') # ülesande valdkonnad ja teemad
    ylopitulemused = relationship('Ylopitulemus', order_by='Ylopitulemus.id', back_populates='ylesandeaine') # ülesande õpitulemused
    _parent_key = 'ylesanne_id'

    @property
    def teemad2(self):
        return [r.teema_kood + (r.alateema_kood and ('.' + r.alateema_kood) or '') \
                for r in self.ylesandeteemad]

    @property
    def opitulemused_idd(self):
        return [r.opitulemus_klrida_id for r in self.ylopitulemused]
    
    def copy(self):
        cp = EntityHelper.copy(self)
        self.copy_subrecords(cp, ['ylesandeteemad',
                                  'ylopitulemused',
                                  ])
        return cp

    def pack_subrecords(self, delete=True, modified=None):
        li = []
        for rcd in self.ylesandeteemad:
            li.extend(rcd.pack(delete, modified))
        for rcd in self.ylopitulemused:
            li.extend(rcd.pack(delete, modified))
        return li

    def delete_subitems(self):    
        self.delete_subrecords(['ylesandeteemad',
                                'ylopitulemused',
                                ])

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        ylesanne = self.ylesanne or self.ylesanne_id and Ylesanne.get(self.ylesanne_id)
        if ylesanne:
            ylesanne.logi('Ülesande õppeaine', vanad_andmed, uued_andmed, logitase)
    
