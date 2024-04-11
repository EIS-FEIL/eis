"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Toovaataja(EntityHelper, Base):
    """Testitöö vaatamise õigus
    (kasutusel gümnaasiumite sisseastumistestides, kui.sooritaja vaidlustab oma tulemuse
    ning kooli töötajale antakse õigus tema testitööd vaadata)
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sooritaja_id = Column(Integer, ForeignKey('sooritaja.id'), index=True) # viide testitööle, mille vaatamiseks on õigus
    sooritaja = relationship('Sooritaja', foreign_keys=sooritaja_id)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide kasutajale, kellel on õigus testitööd vaadata
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    kehtib_kuni = Column(Date, nullable=False) # õiguse kehtimise lõpp

