from eis.s3file import S3File
from eis.model.entityhelper import *

class Eristuskiri(EntityHelper, Base, S3File):
    """Testi eristuskiri
    """
        
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False, unique=True) # viide testile
    test = relationship('Test', foreign_keys=test_id, back_populates='eristuskiri')
    sisu = Column(Text) # eristuskiri tekstina
    filename = Column(String(256)) # failinimi
    filesize = Column(Integer) # faili suurus baitides
    fileversion = Column(String(8)) # versioon
    _parent_key = 'test_id'
    _cache_dir = 'eristuskiri'
