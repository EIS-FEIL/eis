# -*- coding: utf-8 -*-
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

class Hindamisaspekt(EntityHelper, Base):
    """Ülesandega seotud hindamisaspekt
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True) # viide ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='hindamisaspektid')
    aine_kood = Column(String(10), nullable=False) # õppeaine, mille hindamisaspekt see on (peab olema ka tabelis Ylesandeaine)
    aspekt_kood = Column(String(10)) # viide aspektile, klassifikaator ASPEKT
    max_pallid = Column(Float) # max toorpunktide arv, mida selle aspektiga hinnatakse
    pintervall = Column(Float) # lubatud punktide intervall (käsitsi hindamisel)    
    kaal = Column(Float, sa.DefaultClause('1'), nullable=False) # kaal, millega aspekti toorpunktid korrutatakse, kui arvutatakse kogu ülesande toorpunkte
    hindamisjuhis = Column(Text) # kirjeldus (kui puudub, siis kasutatakse vaikimisi kirjeldusena aspektide klassifikaatoris olevat)
    seq = Column(Integer, nullable=False) # aspekti järjekord ülesandes (sh hindamisprotokollil)
    kuvada_statistikas = Column(Boolean, sa.DefaultClause('1')) # kas kuvada aspekt statistikaraportis
    pkirj_sooritajale = Column(Boolean) # kas kuvada punktide kirjeldused sooritajale
    aspektihinded = relationship('Aspektihinne', back_populates='hindamisaspekt')
    punktikirjeldused = relationship('Punktikirjeldus', order_by=sa.desc(sa.text('Punktikirjeldus.punktid')), back_populates='hindamisaspekt')
    trans = relationship('T_Hindamisaspekt', cascade='all', back_populates='orig')
    _parent_key = 'ylesanne_id'

    def copy(self):
        cp = EntityHelper.copy(self)
        self.copy_subrecords(cp, ['trans',
                                  'punktikirjeldused',
                                  ])
        return cp

