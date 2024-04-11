# -*- coding: utf-8 -*-
# $Id: salaylesandeisik.py 1096 2017-01-11 06:17:05Z ahti $
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
    
class Salaylesandeisik(EntityHelper, Base):
    """Krüptitud ülesannet lahti krüptida suutev isik
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    salaylesanne_id = Column(Integer, ForeignKey('salaylesanne.id'), index=True) # viide krüptitud ülesandele
    salaylesanne = relationship('Salaylesanne', foreign_keys=salaylesanne_id, back_populates='salaylesandeisikud')
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale, kes saab lahti krüptida
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    _parent_key = 'salaylesanne_id'

