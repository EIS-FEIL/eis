"Testimise andmemudel"
from eis.model.entityhelper import *

class Testiparoolilogi(EntityHelper, Base):
    """Testiparoolide andmise logi
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    sooritaja_id = Column(Integer, ForeignKey('sooritaja.id'), index=True, nullable=False) # viide testisooritusele
    sooritaja = relationship('Sooritaja', foreign_keys=sooritaja_id, back_populates='testiparoolilogid')
    testiparool = Column(String(97)) # testiparooli räsi

    _parent_key = 'sooritaja_id'
    
