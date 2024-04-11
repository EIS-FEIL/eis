"Testi andmemudel"
from eis.model.entityhelper import *

class Taustakysitlus(EntityHelper, Base):
    """Õpilase testi ja õpetaja testi seos, mis koos moodustavad taustaküsitluse
    """
        
    id = Column(Integer, primary_key=True, autoincrement=True)
    opilase_test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False, unique=True) # viide õpilase testile
    opilase_test = relationship('Test', foreign_keys=opilase_test_id, back_populates='opilase_taustakysitlus')
    opetaja_test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False, unique=True) # viide õpetaja testile
    opetaja_test = relationship('Test', foreign_keys=opetaja_test_id, back_populates='opetaja_taustakysitlus')
    _parent_key = 'opilase_test_id'

