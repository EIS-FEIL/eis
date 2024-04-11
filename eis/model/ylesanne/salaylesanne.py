"Ülesande andmemudel"

from PIL import Image
import mimetypes
import re
from lxml import etree
import urllib.request, urllib.parse, urllib.error

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
    
class Salaylesanne(EntityHelper, Base):
    """Krüptitud ülesande sisu
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    parool = Column(Text) # SK sertifikaatidele krüptitud parool .cdoc (<EncryptedData>) kujul
    data = Column(LargeBinary) # parooliga krüptitud andmed
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True) # viide ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='salaylesanne')
    _parent_key = 'ylesanne_id'
    salaylesandeisikud = relationship('Salaylesandeisik', back_populates='salaylesanne')

    def delete_subitems(self):    
        self.delete_subrecords(['salaylesandeisikud'])
        
