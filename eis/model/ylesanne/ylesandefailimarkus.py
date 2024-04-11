# -*- coding: utf-8 -*-
# $Id: ylesandefailimarkus.py 444 2016-03-11 16:18:31Z ahti $
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

class Ylesandefailimarkus(EntityHelper, Base):
    """Ülesandefaili märkused
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ylesandefail_id = Column(Integer, ForeignKey('ylesandefail.id'), index=True, nullable=False) # viide ülesandefailile
    ylesandefail = relationship('Ylesandefail', foreign_keys=ylesandefail_id, back_populates='ylesandefailimarkused') 
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide märkuse kirjutanud kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id) 
    aeg = Column(DateTime) # märkuse kirjutamise aeg
    sisu = Column(Text) # märkuse sisu
    teema = Column(String(100)) # märkuse teema
    ylem_id = Column(Integer, ForeignKey('ylesandefailimarkus.id'), index=True) # viide ülemale märkusele (mida antud kirje kommenteerib)
    ylem = relationship('Ylesandefailimarkus', foreign_keys=ylem_id, remote_side=id, back_populates='alamad')
    alamad = relationship('Ylesandefailimarkus', back_populates='ylem')
    _parent_key = 'ylesandefail_id'
    
    def set_creator(self):
        EntityHelper.set_creator(self)
        self.aeg = datetime.now()

    def delete_subitems(self):    
        self.delete_subrecords(['alamad'])

    @property
    def alamate_arv(self):
        return sum([m.alamate_arv + 1 for m in self.alamad]) or 0

