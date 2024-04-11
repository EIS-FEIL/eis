"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Helivastusfail(EntityHelper, Base, S3File):
    """Soorituse helifail (võib sisaldada mitme sooritaja vastuseid)
    """
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    filename = Column(String(256)) # failinimi laadimisel
    filesize = Column(Integer) # faili suurus
    fileversion = Column(String(8)) # versioon
    helivastused = relationship('Helivastus', back_populates='helivastusfail')
    kestus = Column(Integer) # kestus sekundites
    valjast = Column(Boolean) # true - muu vahendiga salvestatud ja EISi üles laaditud helifail; false - EISi-siseselt salvestatud helifail
    _cache_dir = 'helivastusfail'

    def delete_subitems(self):
        self.delete_subrecords(['helivastused',
                                ])
