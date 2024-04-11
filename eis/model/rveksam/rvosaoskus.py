"Testi andmemudel"
from eis.model.entityhelper import *

class Rvosaoskus(EntityHelper, Base):
    """Rahvusvahelise eksami osaoskuse kirjeldus
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    rveksam_id = Column(Integer, ForeignKey('rveksam.id'), index=True, nullable=False) # viide eksamile
    rveksam = relationship('Rveksam', foreign_keys=rveksam_id, back_populates='rvosaoskused')
    seq = Column(Integer, nullable=False) # osaoskuse järjekorranumber  
    nimi = Column(String(256)) # osaoskuse nimetus
    rvosatulemused = relationship('Rvosatulemus', order_by='Rvosatulemus.seq', back_populates='rvosaoskus')
    alates = Column(Float) # pallide või protsentide vahemiku algus
    kuni = Column(Float) # pallide või protsentide vahemiku lõpp    

    @property
    def in_use(self):
        from .rvsooritus import Rvsooritus
        a = SessionR.query(Rvsooritus.id).\
            filter(Rvsooritus.rvosaoskus==self).\
            first()
        if a:
            return True
        else:
            return False

    def delete_subitems(self):    
        self.delete_subrecords(['rvosatulemused',
                                ])
