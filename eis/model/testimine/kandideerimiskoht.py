"Testimise andmemudel"
from eis.model.entityhelper import *

class Kandideerimiskoht(EntityHelper, Base):
    """Sooritaja valitud kool, kuhu ta kandideerib ja mis võib näha tema testi tulemusi (gümnaasiumi sisseastumistesti korral)
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    sooritaja_id = Column(Integer, ForeignKey('sooritaja.id'), index=True, nullable=False) # viide registreeringule
    sooritaja = relationship('Sooritaja', foreign_keys=sooritaja_id, back_populates='kandideerimiskohad')
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True, nullable=False) # viide koolile
    koht = relationship('Koht', foreign_keys=koht_id)
    automaatne = Column(Boolean, sa.DefaultClause('0'), nullable=False) # true - valitud seetõttu, et on.sooritaja õppimiskoht, aga õpilane sinna ei kandideeri; false - valitud seepärast, et õpilane sinna kandideerib
    _parent_key = 'sooritaja_id'
