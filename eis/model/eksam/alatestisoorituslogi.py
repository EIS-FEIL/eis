"Testimise andmemudel"
from eis.model.entityhelper import *

class Alatestisoorituslogi(EntityHelper, Base):
    """Alatestisoorituse kirje muudatuste logi
    """
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    alatestisooritus_id = Column(Integer, ForeignKey('alatestisooritus.id'), index=True, nullable=False) # viide alatestisooritusele
    alatestisooritus = relationship('Alatestisooritus', foreign_keys=alatestisooritus_id, back_populates='alatestisoorituslogid')
    staatus = Column(Integer, nullable=False) # sooritamise olek
    pallid = Column(Float) # saadud hindepallid
    url = Column(String(200)) # andmeid muutnud tegevuse URL
    remote_addr = Column(String(60)) # muutja klient
    server_addr = Column(String(60)) # muutja server
    _parent_key = 'alatestisooritus_id'
    
    @property 
    def staatus_nimi(self):
        return usersession.get_opt().S_STAATUS.get(self.staatus)
