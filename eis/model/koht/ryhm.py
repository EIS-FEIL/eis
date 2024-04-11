from eis.model.entityhelper import *
from eis.model.koht import Koht

log = logging.getLogger(__name__)

class Ryhm(EntityHelper, Base):
    """Lasteaiarühm
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True) # rühma ID, pärit EHISest
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True) # koha id
    koht = relationship('Koht', foreign_keys=koht_id, back_populates='ryhmad')
    nimi = Column(String(100)) # rühma nimetus
    liik = Column(String(60)) # rühma liik
    opilased = relationship('Opilane', back_populates='ryhm')
