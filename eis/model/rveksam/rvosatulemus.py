"Testi andmemudel"
from eis.model.entityhelper import *

class Rvosatulemus(EntityHelper, Base):
    """Rahvusvahelise eksami osaoskuse tulemuse esitamise valikud
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    rvosaoskus_id = Column(Integer, ForeignKey('rvosaoskus.id'), index=True) # viide osaoskusele
    rvosaoskus = relationship('Rvosaoskus', foreign_keys=rvosaoskus_id, back_populates='rvosatulemused')
    seq = Column(Integer, nullable=False) # järjekorranumber  
    tahis = Column(String(30)) # tulemuse tähis
    alates = Column(Float) # pallide või protsentide vahemiku algus
    kuni = Column(Float) # pallide või protsentide vahemiku lõpp

    @property
    def in_use(self):
        from .rvsooritus import Rvsooritus
        a = SessionR.query(Rvsooritus.id).\
            filter(Rvsooritus.rvosatulemus==self).\
            first()
        if a:
            return True
        else:
            return False
