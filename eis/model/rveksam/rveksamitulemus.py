"Testi andmemudel"
from eis.model.entityhelper import *

class Rveksamitulemus(EntityHelper, Base):
    """Rahvusvahelise eksami kogutulemuse esitamise valikud
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    rveksam_id = Column(Integer, ForeignKey('rveksam.id'), index=True) # viide eksamile
    rveksam = relationship('Rveksam', foreign_keys=rveksam_id, back_populates='rveksamitulemused')
    seq = Column(Integer, nullable=False) # järjekorranumber  
    tahis = Column(String(30)) # tulemuse tähis
    alates = Column(Float) # pallide või protsentide vahemiku algus
    kuni = Column(Float) # pallide või protsentide vahemiku lõpp
    keeletase_kood = Column(String(10)) # keeleoskuse tase, klassifikaator KEELETASE

    @property
    def in_use(self):
        from .rvsooritaja import Rvsooritaja
        a = SessionR.query(Rvsooritaja.id).\
            filter(Rvsooritaja.rveksamitulemus==self).\
            first()
        if a:
            return True
        else:
            return False
