# -*- coding: utf-8 -*-
"Testikorralduse andmemudel"

from eis.s3file import S3File
from eis.model.entityhelper import *
_ = usersession._

class Vaidefail(EntityHelper, Base, S3File):
    """Vaide juurde lisatud fail
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    vaie_id = Column(Integer, ForeignKey('vaie.id'), index=True, nullable=False)
    vaie = relationship('Vaie', foreign_keys=vaie_id, back_populates='vaidefailid') # viide vaidele
    filename = Column(String(128), nullable=False) # failinimi
    #filedata_db = deferred(Column('filedata', LargeBinary)) # faili sisu
    filesize = Column(Integer) # faili suurus
    fileversion = Column(String(8)) # versioon
    _parent_key = 'vaie_id'
    _cache_dir = 'vaidefail'
