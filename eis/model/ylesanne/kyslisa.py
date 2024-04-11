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
        
class Kyslisa(EntityHelper, Base):
    """Täiendavad andmed lahtri juurde (liuguri ja faili laadimise korral)
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    kysimus_id = Column(Integer, ForeignKey('kysimus.id'), index=True, nullable=False) # viide küsimusele
    kysimus = relationship('Kysimus', foreign_keys=kysimus_id, back_populates='kyslisa') 
    # Slider
    min_vaartus = Column(Float) # liuguri min väärtus
    max_vaartus = Column(Float) # liuguri max vääruts
    samm = Column(Float) # liuguri samm
    samm_nimi = Column(Boolean) # kas liuguril kuvada sammude skaalat
    tagurpidi = Column(Boolean) # kas liuguri vahemik on tagurpidi
    vertikaalne = Column(Boolean) # kas liugur on vertikaalne
    yhik = Column(String(15)) # liuguriga mõõdetava ühiku nimetus
    asend_vasakul = Column(Boolean) # kas kuvada vastus vasakul
    asend_paremal = Column(Boolean) # kas kuvada vastus paremal
    # Upload
    mimetype = Column(String(256)) # oodatav failitüüp
    # Trail
    algus = Column(String(256)) # teekonna sisuplokis algusruudud (nt 1_3)
    labimatu = Column(String(256)) # teekonna sisuplokis läbimatud ruudud (nt 2_0;3_1;1_1)
    lopp = Column(String(256)) # teekonna sisuplokis lõpuruudud (nt 1_3)
    
    trans = relationship('T_Kyslisa', cascade='all', back_populates='orig')   
    _parent_key = 'kysimus_id'

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .kysimus import Kysimus
        kysimus = self.kysimus or self.kysimus_id and Kysimus.get(self.kysimus_id)
        if kysimus:
            kysimus.logi('Küsimus %s %s %s' % (kysimus.kood or '', self.kysimus_id, liik), vanad_andmed, uued_andmed, logitase)

    def copy(self):
        cp = EntityHelper.copy(self)
        self.copy_subrecords(cp, ['trans'])
        return cp

    def pack_subrecords(self, delete=True, modified=None):
        li = []
        for rcd in self.trans:
            li.extend(rcd.pack(delete, modified))
        return li
