"Testi andmemudel"
from eis.s3file import S3File
from eis.model.entityhelper import *

class Tagasisidefail(EntityHelper, Base, S3File):
    """Testi tagasisidevormil kasutatud piltide failid
    """
        
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False) # viide testile
    test = relationship('Test', foreign_keys=test_id, back_populates='tagasisidefailid')
    filename = Column(String(256)) # failinimi
    filesize = Column(Integer) # faili suurus baitides
    fileversion = Column(String(8)) # versioon
    mimetype = Column(String(256)) # failitüüp
    _parent_key = 'test_id'
    _cache_dir = 'tagasisidefail'
