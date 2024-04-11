"Testi andmemudel"
from eis.model.entityhelper import *
from .testiylesanne import Testiylesanne
from .valitudylesanne import Valitudylesanne
from .grupiylesanne import Grupiylesanne
from .testiosa import Testiosa

class Ylesandegrupp(EntityHelper, Base):
    """Ülesannete grupp, millest moodustatakse normipunkte
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    seq = Column(Integer) # järjekorranumber testiosa sees
    nimi = Column(String(1024), nullable=False) # grupi nimetus
    testiosa_id = Column(Integer, ForeignKey('testiosa.id'), index=True, nullable=False) # viide testiosale, mille ülesandeid grupp rühmitab
    testiosa = relationship('Testiosa', foreign_keys=testiosa_id, back_populates='ylesandegrupid')
    grupiylesanded = relationship('Grupiylesanne', order_by='Grupiylesanne.id', back_populates='ylesandegrupp')
    normipunktid = relationship('Normipunkt', order_by='Normipunkt.seq', back_populates='ylesandegrupp')
    trans = relationship('T_Ylesandegrupp', cascade='all', back_populates='orig')
    _parent_key = 'testiosa_id'    

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        if self.logging:
            testiosa =  self.testiosa or self.testiosa_id and Testiosa.get(self.testiosa_id)
            if testiosa:
                testiosa.logi('Ülesandegrupp %s (%s) %s' % (self.id or '', self.nimi or '', liik), vanad_andmed, uued_andmed, logitase)
                

    @property
    def max_pallid(self):
        q = (SessionR.query(sa.func.sum(Testiylesanne.max_pallid))
             .join(Testiylesanne.valitudylesanded)
             .join(Valitudylesanne.grupiylesanded)
             .filter(Grupiylesanne.ylesandegrupp_id==self.id))
        return q.scalar()

    def delete_subitems(self):    
        self.delete_subrecords(['grupiylesanded',
                                'normipunktid',
                                ])

    def copy(self, ignore=[], **di):
        cp = EntityHelper.copy(self, ignore=ignore, **di)
        self.copy_subrecords(cp, ['trans'])
        return cp
