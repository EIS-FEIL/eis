"Testikorralduse andmemudel"
from eis.model.entityhelper import *

class Testitunnistus(EntityHelper, Base):
    """Tunnistuse seos tunnistusele kantud testisooritustega
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tunnistus_id = Column(Integer, ForeignKey('tunnistus.id'), index=True, nullable=False) # viide tunnistusele
    tunnistus = relationship('Tunnistus', foreign_keys=tunnistus_id, back_populates='testitunnistused')
    sooritaja_id = Column(Integer, ForeignKey('sooritaja.id'), index=True, nullable=False) # viide sooritajale (testisoorituse kirjele)
    sooritaja = relationship('Sooritaja', foreign_keys=sooritaja_id, back_populates='testitunnistused')
