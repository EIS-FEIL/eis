# -*- coding: utf-8 -*-
# $Id: plokimarkus.py 1096 2017-01-11 06:17:05Z ahti $
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
    
class Plokimarkus(EntityHelper, Base):
    """Sisuploki märkused
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sisuplokk_id = Column(Integer, ForeignKey('sisuplokk.id'), index=True, nullable=False) # viide sisuplokile
    sisuplokk = relationship('Sisuplokk', foreign_keys=sisuplokk_id, back_populates='plokimarkused')
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    aeg = Column(DateTime) # märkuse kirjutamise aeg
    sisu = Column(Text) # märkuse sisu
    teema = Column(String(100)) # märkuse teema
    ylem_id = Column(Integer, ForeignKey('plokimarkus.id'), index=True) # viide ülemale märkusele (mida antud märkus kommenteerib)
    ylem = relationship('Plokimarkus', foreign_keys=ylem_id, remote_side=id, back_populates='alamad')
    alamad = relationship('Plokimarkus', back_populates='ylem')
    _parent_key = 'sisuplokk_id'
    
    def set_modifier(self):
        EntityHelper.set_modifier(self)
        self.aeg = datetime.now()

    def delete_subitems(self):    
        self.delete_subrecords(['alamad'])

    @property
    def alamate_arv(self):
        return sum([m.alamate_arv + 1 for m in self.alamad]) or 0

