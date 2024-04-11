from .entityhelper import *
from .meta import Base, DBSession

log = logging.getLogger(__name__)

class Taralog(EntityHelper, Base):
    """TARA autentimispäringute logi
    """
    __tablename__ = 'taralog'
    id = Column(Integer, primary_key=True)
    state = Column(String(50), index=True) # genereeritud juharvu räsi
    nonce = Column(String(32), index=True) # genereeritud juhuarv
    aut_aeg = Column(DateTime, index=True) # autentimispäringu aeg
    aut_params = Column(String(512)) # autentimispäringu parameetrid
    resp_params = Column(String(512)) # autentimispäringu vastus GET URL
    resp_aeg = Column(DateTime) # autentimispäringu vastuse aeg
    token_data = Column(Text) # identifitseerimistõendi kest
    token_msg = Column(Text) # identifitseerimistõendi sisu peale lahti kodeerimist
    isikukood = Column(String(50)) # autenditud kasutaja riik ja isikukood
    eesnimi = Column(String(50)) # autenditud kasutaja eesnimi
    perenimi = Column(String(50)) # autenditud kasutaja perekonnanimi
    err = Column(Integer) # vea kood (vt logintara.py)
    request_url = Column(String(200)) # EISi URL, mille poole pöördudes suunati kasutaja autentima ja kuhu peale autentimist kasutaja tagasi suuname
    remote_addr = Column(String(36)) # klient    
