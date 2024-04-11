"Testikorralduse andmemudel"

from eis.model.entityhelper import *
from eis.s3file import S3File

class Skannfail(EntityHelper, Base, S3File):
    """Skannitud eksamitööde failide viited
    """
    __tablename__ = 'skannfail'
    id = Column(Integer, primary_key=True)
    filename = Column(String(256)) # failinimi
    filesize = Column(Integer) # faili suurus baitides
    fileversion = Column(String(8)) # versioon
    sooritus_id = Column(Integer, ForeignKey('sooritus.id'), index=True, unique=True, nullable=False) # viide soorituse kirjele
    sooritus = relationship('Sooritus', foreign_keys=sooritus_id)
    teatatud = Column(DateTime) # millal saadeti sooritajale e-postiga teade skannitud faili saadvale jõudmise kohta
    _cache_dir = 'skannfail'
