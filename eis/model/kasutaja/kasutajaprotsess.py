"Testi andmemudel"
from eis.model.entityhelper import *
_ = usersession._

class Kasutajaprotsess(EntityHelper, Base):
    """Sooritaja seos registreerimise arvutusprotsessiga
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # seos kasutajaga
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='kasutajaprotsessid')
    arvutusprotsess_id = Column(Integer, ForeignKey('arvutusprotsess.id'), index=True) # seos arvutusprotsessiga
    arvutusprotsess = relationship('Arvutusprotsess', foreign_keys=arvutusprotsess_id)

