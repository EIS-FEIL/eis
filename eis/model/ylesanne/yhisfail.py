"Ülesande andmemudel"

from PIL import Image
import mimetypes
import re
from lxml import etree
import urllib.request, urllib.parse, urllib.error
from eis.s3file import S3File
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
  
class Yhisfail(EntityHelper, Base, S3File):
    """Ühised failid, mida paljudes ülesannetes saab kasutada.
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(256), nullable=False, unique=True) # failinimi
    filesize = Column(Integer) # faili suurus baitides
    #filedata_db = deferred(Column('filedata', LargeBinary)) # faili sisu
    fileversion = Column(String(8)) # versioon
    mimetype = Column(String(256)) # failitüüp
    teema = Column(String(256)) # teema
    yhisfail_kood = Column(String(10)) # faili tüüp, klassifikaator YHISFAIL

    _cache_dir = 'yhisfail'
    
    @classmethod
    def get_by_name(cls, filename):
        return cls.query.filter_by(filename=filename).first()

    def set_modifier(self):
        EntityHelper.set_modifier(self)
        self.set_mimetype()

    def set_mimetype(self):
        mimetype = self.guess_type()        
        if mimetype:
            self.mimetype = mimetype

    def guess_type(self):
        """Failinime või URLi järgi arvatakse ära MIME tüüp.
        """        
        if not self.filename:
            return 
        (mimetype, encoding) = mimetypes.guess_type(self.filename)
        return mimetype

    @property
    def is_image(self):
        return self.mimetype_main == 'image'

    @property
    def is_audio(self):
        return self.mimetype_main == 'audio'

    @property
    def is_video(self):
        return self.mimetype_main in ('video', 'application')
              
    @property
    def mimetype_main(self):
        if not self.mimetype:
            self.set_mimetype()
        if self.mimetype:
            return self.mimetype.split('/')[0]

