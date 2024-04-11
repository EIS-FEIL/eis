# -*- coding: utf-8 -*-
"Tööde PDF failid koos hindamisjuhendiga koolidele jagamiseks"

import mimetypes
import re
from lxml import etree
import urllib.request, urllib.parse, urllib.error
from eis.s3file import S3File
from eis.model.entityhelper import *
  
class Toofail(EntityHelper, Base, S3File):
    """Tööde PDF failid koos hindamisjuhendiga koolidele jagamiseks
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(256), nullable=False) # failinimi
    #filedata_db = deferred(Column('filedata', LargeBinary)) # faili sisu
    filesize = Column(Integer) # faili suurus baitides
    fileversion = Column(String(8)) # versioon
    mimetype = Column(String(256)) # failitüüp
    kirjeldus = Column(String(256)) # kirjeldus
    test_id = Column(Integer, ForeignKey('test.id'), index=True) # viide testile, kui fail käib teatud testi kohta ja on loetav koolides, kus on selle testi sooritajaid
    test = relationship('Test', foreign_keys=test_id, back_populates='toofailid')
    oppetase_kood = Column(String(1)) # õppetase, EISi klassifikaator OPPETASE: y=const.OPPETASE_YLD - üldharidus; u=const.OPPETASE_KUTSE - kutseharidus; o=const.OPPETASE_KORG - kõrgharidus; NULL - plangivaba tase (alusharidus või huviharidus); fail on loetav koolides, millel on antud tase
    avalik_alates = Column(DateTime, nullable=False) # kuupäev ja kellaaeg, millest alates fail on koolidele nähtav
    toofailitasemed = relationship('Toofailitase', back_populates='toofail')

    _cache_dir = 'toofail'
    
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
    def mimetype_main(self):
        if not self.mimetype:
            self.set_mimetype()
        if self.mimetype:
            return self.mimetype.split('/')[0]

    def delete_subitems(self):    
        self.delete_subrecords(['toofailitasemed',
                                ])
