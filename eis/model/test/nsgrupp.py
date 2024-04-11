# -*- coding: utf-8 -*-
"Testi andmemudel"
from eis.model.entityhelper import *
from .testiosa import Testiosa
_ = usersession._

class Nsgrupp(EntityHelper, Base):
    """Diagnoosiva testi tagasiside grupp (nt "sa oskad", "sa ei oska")
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    testiosa_id = Column(Integer, ForeignKey('testiosa.id'), index=True, nullable=False) # viide testiosale
    testiosa = relationship('Testiosa', foreign_keys=testiosa_id, back_populates='nsgrupid')    
    seq = Column(Integer) # järjekorranumber testiosa sees
    nimi = Column(String(1024)) # grupi nimetus
    nptagasisided = relationship('Nptagasiside', order_by='Nptagasiside.seq', back_populates='nsgrupp')
    trans = relationship('T_Nsgrupp', cascade='all')

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        if self.logging:
            testiosa = self.testiosa or self.testiosa_id and Testiosa.get(self.testiosa_id)
            if testiosa:
                testiosa.logi('Tagasiside grupp %s %s' % (self.id or '', liik), vanad_andmed, uued_andmed, logitase)
    
    def get_seq(self):
        return self.get_seq_parent('testiosa_id', self.testiosa_id)            

    def copy(self, ignore=[], **di):
        cp = EntityHelper.copy(self, ignore=ignore, **di)
        self.copy_subrecords(cp, ['trans'])
        return cp
