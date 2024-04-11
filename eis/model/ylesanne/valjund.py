# -*- coding: utf-8 -*-
# $Id: valjund.py 1096 2017-01-11 06:17:05Z ahti $
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

class Valjund(EntityHelper, Base):
    """Väljundmuutujate deklareerimine (nt SCORE). EISi siseselt ei kasutata.
    QTI outcomeDeclaration
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    kood = Column(String(30), nullable=False) # QTI identifier
    kardinaalsus = Column(String(10)) # QTI cardinality: single, multiple, ordered
    baastyyp = Column(String(15)) # QTI baseType
    interpretatsioon = Column(String(256)) # interpretation
    max_norm = Column(Float) # QTI normalMaximum
    min_norm = Column(Float) # QTI normalMinimum
    oskus_norm = Column(Float) # QTI masteryValue
    vaikimisi = Column(String(100)) # QTI lookupTable/defaultValue
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True) # viide ülesandele       
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='valjundid')
    _parent_key = 'ylesanne_id'
    
