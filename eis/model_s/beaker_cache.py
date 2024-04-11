from eiscore.entitybase import *
from .meta import Base, DBSession

class Beaker_cache(Base):
    """Kasutajate seansid
    """
    __tablename__ = 'beaker_cache'
    id = Column(Integer, primary_key=True, autoincrement=True)        
    namespace = Column(String(255), primary_key=True) # seansi identifikaator
    accessed = Column(DateTime, nullable=False) # viimase kasutamise aeg
    created = Column(DateTime, nullable=False) # loomise aeg
    data = Column(sa.PickleType, nullable=False) # andmed
    kasutaja_id = Column(Integer) # kasutaja ID
    autentimine = Column(String(2)) # autentimisviis
    kehtetu = Column(Boolean) # kas seanss on kehtiv
    remote_addr = Column(String(60)) # kasutaja aadress
    app = Column(String(6)) # rakenduse nimi
