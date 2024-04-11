from eis.s3file import S3File
from eis.model.entityhelper import *

class Kogufail(EntityHelper, Base, S3File):
    """Ülesandekogu eristuskiri
    """
        
    id = Column(Integer, primary_key=True, autoincrement=True)
    ylesandekogu_id = Column(Integer, ForeignKey('ylesandekogu.id'), index=True, nullable=False, unique=True) # viide ülesandekogule
    ylesandekogu = relationship('Ylesandekogu', foreign_keys=ylesandekogu_id, back_populates='kogufail')
    sisu = Column(Text) # eristuskiri tekstina
    filename = Column(String(256)) # failinimi
    filesize = Column(Integer) # faili suurus baitides
    fileversion = Column(String(8)) # versioon
    _parent_key = 'ylesandekogu_id'
    _cache_dir = 'kogufail'
