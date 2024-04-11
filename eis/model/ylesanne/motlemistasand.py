# -*- coding: utf-8 -*-
# $Id: motlemistasand.py 1096 2017-01-11 06:17:05Z ahti $
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

class Motlemistasand(EntityHelper, Base):
    """Ülesande mõtlemistasandid
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    kood = Column(String(10)) # mõtlemistasandi kood, klassifikaator MOTE
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True, nullable=False) # viide ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='motlemistasandid')
    _parent_key = 'ylesanne_id'
    __table_args__ = (
        sa.UniqueConstraint('ylesanne_id','kood'),
        )

    @property
    def nimi(self):
        return Klrida.get_str('MOTE', self.kood)
