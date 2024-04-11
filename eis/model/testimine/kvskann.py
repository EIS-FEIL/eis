"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Kvskann(EntityHelper, Base):
    """Küsimuse vastuse skann
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kysimusevastus_id = Column(Integer, index=True, nullable=False) # viide sooritusele
    #kysimusevastus = relationship('Kysimusevastus', foreign_keys=kysimusevastus_id, back_populates='kvskannid')
    seq = Column(Integer, nullable=False) # mitmes skann (küsimuse piires)
    skann = Column(LargeBinary) # skannitud vastus JPG-pildina
    laius_orig = Column(Integer) # pildi tegelik laius
    korgus_orig = Column(Integer) # pildi tegelik kõrgus
    __table_args__ = (
        sa.UniqueConstraint('kysimusevastus_id','seq'),
        )
    _parent_key = 'kysimusevastus_id'
