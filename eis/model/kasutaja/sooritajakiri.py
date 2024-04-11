from eis.model.entityhelper import *

log = logging.getLogger(__name__)

class Sooritajakiri(EntityHelper, Base):
    """Sooritaja kirje seos välja saadetud kirjadega
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kiri_id = Column(Integer, ForeignKey('kiri.id'), index=True, nullable=False) # viide kirjale
    kiri = relationship('Kiri', foreign_keys=kiri_id, back_populates='sooritajakirjad')
    sooritaja_id = Column(Integer, ForeignKey('sooritaja.id'), index=True) # viide sooritaja kirjele, kui on registreeringuga seotud kiri
    sooritaja = relationship('Sooritaja', foreign_keys=sooritaja_id, back_populates='sooritajakirjad')
