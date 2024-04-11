from eis.model.entityhelper import *

log = logging.getLogger(__name__)

class Kirjasaaja(EntityHelper, Base):
    """Kirja saaja
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kiri_id = Column(Integer, ForeignKey('kiri.id'), index=True, nullable=False) # viide kirjale
    kiri = relationship('Kiri', foreign_keys=kiri_id, back_populates='kirjasaajad')
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide saaja kasutajale (puudub soorituskohale saadetud kirjas)
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='kirjasaajad')
    epost = Column(String(255)) # e-posti aadress
    isikukood = Column(String(50)) # isikukood (StateOS)
    staatus = Column(Integer, sa.DefaultClause('1'), nullable=False) # kirja olek: 1=const.KIRI_UUS - lugemata; 2=const.KIRI_LOETUD - loetud; 3=const.KIRI_ARHIIV - arhiveeritud
    koht_id = Column(Integer, ForeignKey('koht.id')) # viide soorituskohale, kuhu kiri saadeti
    koht = relationship('Koht', foreign_keys=koht_id)
    toimumisaeg_id = Column(Integer, ForeignKey('toimumisaeg.id')) # viide toimumisajale
    toimumisaeg = relationship('Toimumisaeg', foreign_keys=toimumisaeg_id)
    
