"Testikorralduse andmemudel"

from eis.s3file import S3File
from eis.model.entityhelper import *

class Ruumifail(EntityHelper, Base, S3File):
    """Toimumise protokollile lisatud fail, nt ruumi istumisplaan
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    toimumisprotokoll_id = Column(Integer, ForeignKey('toimumisprotokoll.id'), index=True, nullable=False) # viide toimumise protokollile (määrab soorituskeele)
    toimumisprotokoll = relationship('Toimumisprotokoll', foreign_keys=toimumisprotokoll_id, back_populates='ruumifailid')    
    testiruum_id = Column(Integer, ForeignKey('testiruum.id'), index=True, nullable=False) # viide testiruumile, mille kohta fail käib
    testiruum = relationship('Testiruum', foreign_keys=testiruum_id, back_populates='ruumifailid')
    filename = Column(String(256)) # failinimi laadimisel
    filesize = Column(Integer) # faili suurus
    fileversion = Column(String(8)) # versioon

    _cache_dir = 'ruumifail'
