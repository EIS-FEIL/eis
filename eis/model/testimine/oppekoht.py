"Testimise andmemudel"
from eis.model.entityhelper import *

class Oppekoht(EntityHelper, Base):
    """Sooritaja eesti keele õppimise koht (tasemeeksami korral) või vene keele õppimise koht (vene keele rahvusvahelise eksami korral)
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    sooritaja_id = Column(Integer, ForeignKey('sooritaja.id'), index=True, nullable=False) # viide registreeringule
    sooritaja = relationship('Sooritaja', foreign_keys=sooritaja_id, back_populates='oppekohad')
    oppekoht_kood = Column(String(10)) # kus on vene keelt õppinud (kasutusel oli kuni 2017-10)
    oppekohtet_kood = Column(String(10)) # kus on eesti keelt õppinud
    oppekoht_muu = Column(String(100)) # keeltekooli nimi või muu õppimiskoht, kus on eesti keelt õppinud 
    _parent_key = 'sooritaja_id'
