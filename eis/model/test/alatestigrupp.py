"Testi andmemudel"
from eis.model.entityhelper import *
from .testiosa import Testiosa

class Alatestigrupp(EntityHelper, Base):
    """Tagasisidetunnuste grupp
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    seq = Column(Integer) # grupi järjekorranumber
    nimi = Column(String(256)) # grupi nimetus
    testiosa_id = Column(Integer, ForeignKey('testiosa.id'), index=True, nullable=False) # viide testiosale
    testiosa = relationship('Testiosa', foreign_keys=testiosa_id, back_populates='alatestigrupid') 
    normipunktid = relationship('Normipunkt', order_by='Normipunkt.seq', back_populates='alatestigrupp')    
    _parent_key = 'testiosa_id'    
    trans = relationship('T_Alatestigrupp', cascade='all')
    
    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        if self.logging:
            testiosa =  self.testiosa or self.testiosa_id and Testiosa.get(self.testiosa_id)
            if testiosa:
                testiosa.logi('Alatestigrupp %s (%s) %s' % (self.id or '', self.nimi or self.seq or '', liik), vanad_andmed, uued_andmed, logitase)
                
    def copy(self):
        cp = EntityHelper.copy(self)
        self.copy_subrecords(cp, ['trans'])
        return cp
