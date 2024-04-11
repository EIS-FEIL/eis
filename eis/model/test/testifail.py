"Testi andmemudel"
from eis.s3file import S3File
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import Opt
from eis.model.kasutaja import *
from eis.model.koht import *
from .komplekt import Komplekt

class Testifail(EntityHelper, Base, S3File):
    """Testi ülesandekomplekti juurde salvestatud fail
    """
        
    id = Column(Integer, primary_key=True, autoincrement=True)
    komplekt_id = Column(Integer, ForeignKey('komplekt.id'), index=True, nullable=False) # viide ülesandekomplektile
    komplekt = relationship('Komplekt', foreign_keys=komplekt_id, back_populates='testifailid')
    nimi = Column(String(256)) # selgitav nimetus
    filename = Column(String(256)) # failinimi
    filesize = Column(Integer) # faili suurus baitides
    #filedata_db = deferred(Column('filedata', LargeBinary)) # faili sisu
    fileversion = Column(String(8)) # versioon
    mimetype = Column(String(256)) # failitüüp
    testifailimarkused = relationship('Testifailimarkus', order_by='Testifailimarkus.id', back_populates='testifail')
    _parent_key = 'komplekt_id'
    _cache_dir = 'testifail'

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        komplekt = self.komplekt or self.komplekt_id and Komplekt.get(self.komplekt_id)
        if komplekt:
            komplekt.logi('Testifail %s (%s) %s' % (self.id, self.komplekt_id, liik), vanad_andmed, uued_andmed, logitase)

    def delete_subitems(self):    
        for rcd in self.testifailimarkused:
            if rcd.ylem_id is None:
                rcd.delete()

