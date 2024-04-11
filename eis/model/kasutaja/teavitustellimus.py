# -*- coding: utf-8 -*-
from eis.model.entityhelper import *

log = logging.getLogger(__name__)

class Teavitustellimus(EntityHelper, Base):
    """Kasutaja poolt tellitud teavitusviisid eesti.ee vanas teavituskalendris
    (uuelt me ei saa enam seda infot küsida)
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='teavitustellimused')
    teatekanal = Column(Integer, nullable=False) # tellimuse kanal: 3=const.TEATEKANAL_KALENDER - eesti.ee teavituskalendri kaudu
    syndmuseliik = Column(String(10)) # testiliigi kood, millele vastavad sündmused on tellitud (teavituskalendri korral)

    __table_args__ = (
        sa.UniqueConstraint('kasutaja_id','teatekanal','syndmuseliik'),
        )
