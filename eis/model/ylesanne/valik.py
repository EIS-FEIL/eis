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

from . import util
from .kysimus import Kysimus

# kui pikalt kuvada valiku sees valiku nime algust
SISESTUSNIMI_LEN = 10

class Sisuvalik(object):
    """Valik, mida ei hoita eraldi kirjes, vaid ploki sisu sees.
    """
    def __init__(self, id=None, kood=None, nimi=None, grupp=None, sisuplokk=None, seq=None, selgitus=None):
        self.id = id
        self.kood = kood
        self.tran_nimi = None
        self.nimi = nimi
        self.grupp = grupp
        self.max_vastus = 1
        self.sisuplokk = sisuplokk
        self.seq = seq
        self.selgitus = selgitus
        # kui seda klassi kasutada sisukysimusena, 
        # siis võivad olla selle all sisuvalikud
        self.valikud = [] 

    def get_min_vastus(self):
        return 0

    def get_max_vastus(self):
        return self.max_vastus or 1

    def tran(self, lang, original_if_missing=True):
        return self

    def get_sisestusnimi(self, rtf=False):
        """Vastuste sisestamise vormi valikus kasutatav nimetus"""
        # eemaldame tekstiosa valiku algusest sulgudes oleva koodi
        if self.nimi and self.nimi.startswith('('):
            nimi = re.sub(r'\([^\)]+\)','',self.nimi)
        else:
            nimi = self.nimi
        if nimi:
            if len(nimi) > SISESTUSNIMI_LEN+3:
                return '%s (%s...)' % (self.kood, nimi[:SISESTUSNIMI_LEN])
            else:
                return '%s (%s)' % (self.kood, nimi)
        else:
            return self.kood

class Valik(EntityHelper, Base):
    """Valikülesande valik.
    """
    __tablename__ = 'valik'
    id = Column(Integer, primary_key=True, autoincrement=True)
    seq = Column(Integer, nullable=False) # valiku järjekorranumber küsimuse sees
    kood = Column(String(100)) # kood, kasutusel hindamismaatriksis
    min_vastus = Column(Integer) # min vastuste arv
    max_vastus = Column(Integer) # max vastuste arv
    nimi = Column(Text) # valiku sisu
    selgitus = Column(String(255)) # selgitus
    varv = Column(String(7)) # valiku värv (alade värvimise korral)
    kysimus_id = Column(Integer, ForeignKey('kysimus.id'), index=True, nullable=False) # viide küsimusele
    kysimus = relationship('Kysimus', foreign_keys=kysimus_id, back_populates='valikud')
    eraldi = Column(Boolean) # kui esinemiste arv on ühest suurem, siis kas pilti kuvada pangas ühekordselt või iga eksemplar eraldi (tekstide lohistamine)
    joondus = Column(String(10)) # lohistatava kirjavahemärgi joondus lünkadeta pangaga lünktekstis: left=const.JUSTIFY_LEFT - vasak; center=const.JUSTIFY_CENTER - kesk; right=const.JUSTIFY_RIGHT - parem
    fikseeritud = Column(Boolean) # kas valiku asukoht on fikseeritud (järjestamise korral)
    trans = relationship('T_Valik', cascade='all', back_populates='orig')
    row_type = Column(String(40))
    kohustuslik_kys = Column(String(70)) # nende küsimuste koodid, mis muutuvad valiku valimisel kohustuslikuks
    sp_peida = Column(String(70))  # nende sisuplokkide tähised, mis valiku valimisel peidetakse
    sp_kuva = Column(String(70))  # nende sisuplokkide tähised, mis valiku valimisel kuvatakse
    max_pallid = Column(Float) # valiku maksimaalne pallide arv; kasutusel paarisvastustega küsimustes statistikute jaoks
    __mapper_args__ = {'polymorphic_on': row_type, 'polymorphic_identity': 'valik'}
    
    _parent_key = 'kysimus_id'

    # ei saa unikaalsuse piirangut kasutada, sest PostgreSQL võimaldab initially='deferred' ainult foreign key jaoks
    #sa.UniqueConstraint('kysimus_id','kood') 

    tran_nimi = None # Sisuvalikuga sobimiseks

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        kysimus = self.kysimus or self.kysimus_id and Kysimus.get(self.kysimus_id)
        if kysimus:
            kysimus.logi('Valik %s %s %s' % (self.kood or '', self.id or '', liik), vanad_andmed, uued_andmed, logitase)

    def copy(self):
        cp = EntityHelper.copy(self)
        self.copy_subrecords(cp, ['trans'])
        return cp

    def pack_subrecords(self, delete=True, modified=None):
        li = []
        for rcd in self.trans:
            li.extend(rcd.pack(delete, modified))
        return li

    def set_modifier(self):
        EntityHelper.set_modifier(self)
        self.gen_kood()
        
    def gen_kood(self):
        if not self.kood:
            seq = self.seq or self.get_seq()
            if seq:
                self.kood = 'V%02d' % self.get_seq()

    def delete_subitems(self):    
        self.delete_subrecords(['trans',
                                ])

    def get_seq(self):
        # funktsioon üle laaditud selleks, et Valikupiirkonnas toimiks
        seq = 0
        if self.kysimus:
            for v in self.kysimus.valikud:
                seq = max(seq, v.seq)
            return seq + 1

    def get_min_vastus(self):
        return self.min_vastus or 0

    def get_max_vastus(self):
        return self.max_vastus or 1

    def get_sisestusnimi(self, rtf=False):
        """Vastuste sisestamise vormi valikus kasutatav nimetus"""
        nimi = (self.selgitus or '').strip()
        if not nimi and not self.is_valikupiirkond:
            nimi = (self.nimi or '').strip()
            if rtf:
                nimi = re.sub(r'<[^>]+>', '', nimi)

        if self.kood == nimi:
            return self.kood
        elif len(nimi) > SISESTUSNIMI_LEN + 3:
            return '%s (%s...)' % (self.kood, nimi[:SISESTUSNIMI_LEN])
        elif nimi:
            return '%s (%s)' % (self.kood, nimi)
        else:
            return self.kood

    @property
    def is_valikupiirkond(self):
        return self.row_type == const.CHOICE_HOTSPOT

class Valikupiirkond(Valik):
    """Piirkond pildil (hotspot).
    """
    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': const.CHOICE_HOTSPOT}
    kujund = Column(String(10)) # piirkonna kujund: rect, circle, elliplse,...
    nahtamatu = Column(Boolean) # kas piirkond on lahendajale nähtamatu (st kontuuri lahendajale ei kuvata, valikupiirkonna korral)
    
    @property
    def koordinaadid(self):
        return self.nimi

    @koordinaadid.setter
    def koordinaadid(self, value):
        self.nimi = value

    @property
    def cx(self):
        return util.cx(self.koordinaadid, self.kujund)
    
    @property
    def cy(self):
        return util.cy(self.koordinaadid, self.kujund)

    def copy(self):
        cp = Valik.copy(self)
        cp.kujund = self.kujund
        return cp

    def border_pos(self):
        return util.border_pos(self.koordinaadid, self.kujund)

    def list_koordinaadid(self):
        return util.coords_to_list(self.koordinaadid)
