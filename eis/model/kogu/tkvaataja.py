# -*- coding: utf-8 -*-
"Töökogumiku jagamine õpetajale"

from eis.model.entityhelper import *

class Tkvaataja(EntityHelper, Base):
    """Töökogumiku jagamine teisele õpetajale. Jagamisel tekib töökogumiku vaatamise õigus
    ja võimalus töökogumikust enda jaoks koopia teha.
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    tookogumik_id = Column(Integer, ForeignKey('tookogumik.id'), index=True, nullable=False) # töökogumik
    tookogumik = relationship('Tookogumik', back_populates='tkvaatajad')
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # õpetaja, kellele töökogumik jagati
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='tkvaatajad')
