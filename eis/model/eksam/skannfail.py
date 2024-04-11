"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Skannfail(EntityHelper, Base, S3File):
    """Skannitud eksamitööde failide viited
    """
    __tablename__ = 'skannfail'
    id = Column(BigInteger, primary_key=True)
    filename = Column(String(256)) # failinimi
    filesize = Column(Integer) # faili suurus baitides
    fileversion = Column(String(8)) # versioon
    sooritus_id = Column(Integer, ForeignKey('sooritus.id'), index=True, unique=True, nullable=False) # viide soorituse kirjele
    sooritus = relationship('Sooritus', foreign_keys=sooritus_id, back_populates='skannfail')
    teatatud = Column(DateTime) # millal saadeti sooritajale e-postiga teade skannitud faili saadvale jõudmise kohta
    _cache_dir = 'skannfail'
