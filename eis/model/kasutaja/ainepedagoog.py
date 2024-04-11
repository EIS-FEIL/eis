# -*- coding: utf-8 -*-
from eis.model.entityhelper import *

log = logging.getLogger(__name__)

class Ainepedagoog(EntityHelper, Base):
    """Pedagoogi seos õppeainetega, mida õpetab
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    pedagoog_id = Column(Integer, ForeignKey('pedagoog.id'), index=True, nullable=False) # pedagoogi kirje
    pedagoog = relationship('Pedagoog', foreign_keys=pedagoog_id, back_populates='ainepedagoogid')
    ehis_aine_kood = Column(String(25), nullable=False) # aine (EHISe klassifikaator)
    ehis_aste_kood = Column(String(25), nullable=False) # kooliaste (EHISe klassifikaator)
    seisuga = Column(DateTime, nullable=False) # viimane EHISest andmete kontrollimise aeg
    __table_args__ = (
        sa.UniqueConstraint('pedagoog_id', 'ehis_aine_kood', 'ehis_aste_kood'),
        )
