# -*- coding: utf-8 -*-
# $Id: joonistamine.py 1096 2017-01-11 06:17:05Z ahti $
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

from .kysimus import Kysimus

class Joonistamine(EntityHelper, Base):
    """Täiendavad vaikimisi seaded joonistamise sisuploki juurde
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    kysimus_id = Column(Integer, ForeignKey('kysimus.id'), index=True, nullable=False) # viide küsimusele
    kysimus = relationship('Kysimus', foreign_keys=kysimus_id, back_populates='joonistamine')
    on_arvutihinnatav = Column(Boolean) # kas on arvutihinnatav murdjoon/vabakäejoon või muidu joonistus
    on_seadistus = Column(Boolean) # kas lahendaja saab vaikimisi seadeid muuta
    tarbed = Column(String(256)) # kasutatavad joonistustarbed, semikooloniga eraldatult
    stroke_width = Column(Integer) # joone laius
    stroke_color = Column(String(7)) # joone värv
    fill_none = Column(Boolean) # kas joonistatava kujundi sisu on tühi
    fill_color = Column(String(7)) # kujundi sisu värv
    fill_opacity = Column(String(2)) # sisu läbipaistvus, vahemikus 0.1, 0.2, 0.3 kuni 1
    fontsize = Column(Integer) # kirja suurus
    textfill_color = Column(String(7)) # kirja värv
    _parent_key = 'kysimus_id'

    @property
    def tarbed_list(self):
        return self.tarbed and self.tarbed.split(';') or []

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        kysimus = self.kysimus or self.kysimus_id and Kysimus.get(self.kysimus_id)
        if kysimus:
            kysimus.logi('Küsimus %s %s %s' % (kysimus.kood or '', self.kysimus_id, liik), vanad_andmed, uued_andmed, logitase)
    
