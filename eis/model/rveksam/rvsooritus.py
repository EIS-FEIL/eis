"Testi andmemudel"
from eis.model.entityhelper import *

class Rvsooritus(EntityHelper, Base):
    """Rahvusvahelise eksami osaoskuse soorituse andmed
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    rvsooritaja_id = Column(Integer, ForeignKey('rvsooritaja.id'), index=True, nullable=False) # viide eksamisooritusele
    rvsooritaja = relationship('Rvsooritaja', foreign_keys=rvsooritaja_id, back_populates='rvsooritused')
    rvosaoskus_id = Column(Integer, ForeignKey('rvosaoskus.id'), index=True, nullable=False) # osaoskus
    rvosaoskus = relationship('Rvosaoskus', foreign_keys=rvosaoskus_id)
    rvosatulemus_id = Column(Integer, ForeignKey('rvosatulemus.id'), index=True) # viide tulemusele
    rvosatulemus = relationship('Rvosatulemus', foreign_keys=rvosatulemus_id)
    tulemus = Column(Float) # tulemus pallides või protsentides
    on_labinud = Column(Boolean) # kas vastab osaoskusega nõutud tasemele (kui eksami juures on märgitud rveksam.on_osaoskused_jahei)
