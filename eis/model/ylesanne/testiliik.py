# -*- coding: utf-8 -*-
# $Id: testiliik.py 1096 2017-01-11 06:17:05Z ahti $
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

from .ylesanne import Ylesanne

class Testiliik(EntityHelper, Base):
    """Ülesande testiliigid
    """
    # selles tabelis on id selleks, et sqlalchemy kaudu delete lihtsam oleks
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kood = Column(String(10), nullable=False) # testiliigi kood, klassifikaator TESTILIIK
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True, nullable=False) # viide ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='testiliigid')
    __table_args__ = (
        sa.UniqueConstraint('ylesanne_id','kood'),
        )
    _parent_key = 'ylesanne_id'
    @property
    def nimi(self):
        return Klrida.get_str('TESTILIIK', self.kood)

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        ylesanne = self.ylesanne or self.ylesanne_id and Ylesanne.get(self.ylesanne_id)
        if ylesanne:
            ylesanne.logi('Testiliik', vanad_andmed, uued_andmed, logitase)

