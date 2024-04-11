# -*- coding: utf-8 -*-
"Ülesande andmemudel"

from PIL import Image
import mimetypes
import re
from lxml import etree
import urllib.request, urllib.parse, urllib.error
from eis.s3file import S3File
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *

t_meta_fields = ('id',
                 'created',
                 'creator',
                 'modified',
                 'modifier',
                 'orig_id',
                 'lang',
                 'ylesandeversioon_id',
                 )

class T_Ylesanne(EntityHelper, Base):
    """Tabeli Ylesanne tõlge
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    orig_id = Column(Integer, ForeignKey('ylesanne.id'), index=True, nullable=False) # viide lähtetabelile
    orig = relationship('Ylesanne', foreign_keys=orig_id)
    lang = Column(String(2)) # tõlkekeel
    ylesandeversioon_id = Column(Integer, ForeignKey('ylesandeversioon.id'), index=True) # versioon
    ylesandeversioon = relationship('Ylesandeversioon', foreign_keys=ylesandeversioon_id)
    nimi = Column(String(256)) # nimetus
    marksonad = Column(String(256)) # otsingu märksõnad  
    #hindamisjuhend = Column(Text)
    dlgop_tekst = Column(String(256)) # dialoogiakna tekst, kui vastamist ei alustata ooteaja jooksul (õpipädevuse ülesannetes sisuplokis "piltide lohistamine kujunditele")
    tahemargid = Column(Integer) # ülesande tõlke tähemärkide arv
    yl_tagasiside = Column(Text) # tagasiside terve ülesande kohta sõltumata tulemusest    
    __table_args__ = (
        sa.UniqueConstraint('orig_id','lang', 'ylesandeversioon_id'),
        )

    logging = True
    _flush_on_delete = True
    
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .ylesanne import Ylesanne
        parent = self.orig or self.orig_id and Ylesanne.get(self.orig_id)
        if parent:
            parent.logi('Ülesande tõlge [%s]' % (self.lang), vanad_andmed, uued_andmed, logitase)


class T_Lahendusjuhis(EntityHelper, Base):
    """Tabeli Lahendusjuhis tõlge
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    orig_id = Column(Integer, ForeignKey('lahendusjuhis.id'), index=True, nullable=False) # viide lähtetabelile
    orig = relationship('Lahendusjuhis', foreign_keys=orig_id)
    lang = Column(String(2)) # tõlkekeel
    ylesandeversioon_id = Column(Integer, ForeignKey('ylesandeversioon.id'), index=True) # versioon
    ylesandeversioon = relationship('Ylesandeversioon', foreign_keys=ylesandeversioon_id)
    juhis = Column(Text) # juhis
    #nupujuhis = Column(Text) # lahendaja tekstitoimeti nupurea juhend
    tahemargid = Column(Integer) # lahendusjuhise tõlke tähemärkide arv
    _flush_on_delete = True
    __table_args__ = (
        sa.UniqueConstraint('orig_id','lang', 'ylesandeversioon_id'),
        )
    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .lahendusjuhis import Lahendusjuhis

        parent = self.orig or self.orig_id and Lahendusjuhis.get(self.orig_id)
        if parent:
            parent.logi('Lahendusjuhise tõlge [%s]' % (self.lang), vanad_andmed, uued_andmed, logitase)

class T_Hindamisaspekt(EntityHelper, Base):
    """Tabeli Hindamisaspekt tõlge 
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    orig_id = Column(Integer, ForeignKey('hindamisaspekt.id'), index=True, nullable=False) # viide lähtetabelile
    orig = relationship('Hindamisaspekt', foreign_keys=orig_id)
    lang = Column(String(2)) # tõlkekeel
    ylesandeversioon_id = Column(Integer, ForeignKey('ylesandeversioon.id'), index=True) # versioon
    ylesandeversioon = relationship('Ylesandeversioon', foreign_keys=ylesandeversioon_id)
    hindamisjuhis = Column(Text)  # juhis
    #lahendusjuhis = Column(String(8000))
    _flush_on_delete = True
    __table_args__ = (
        sa.UniqueConstraint('orig_id','lang', 'ylesandeversioon_id'),
        )

    # logging = True
    # def logi(self, liik, vanad_andmed, uued_andmed, logitase):
    #     from hindamisaspekt import Hindamisaspekt
    #     parent = self.orig or Hindamisaspekt.get(self.orig_id)
    #     parent.logi(u'Hindamisaspekti tõlge [%s]' % (self.lang), vanad_andmed, uued_andmed, logitase)

class T_Punktikirjeldus(EntityHelper, Base):
    """Tabeli Punktikirjeldus tõlge 
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    orig_id = Column(Integer, ForeignKey('punktikirjeldus.id'), index=True, nullable=False) # viide lähtetabelile
    orig = relationship('Punktikirjeldus', foreign_keys=orig_id)
    lang = Column(String(2)) # tõlkekeel
    ylesandeversioon_id = Column(Integer, ForeignKey('ylesandeversioon.id'), index=True) # versioon
    ylesandeversioon = relationship('Ylesandeversioon', foreign_keys=ylesandeversioon_id)
    kirjeldus = Column(Text)  # kirjeldus
    _flush_on_delete = True
    __table_args__ = (
        sa.UniqueConstraint('orig_id','lang', 'ylesandeversioon_id'),
        )

class T_Sisuplokk(EntityHelper, Base):
    """Tabeli Sisuplokk tõlge
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    orig_id = Column(Integer, ForeignKey('sisuplokk.id'), index=True, nullable=False) # viide lähtetabelile
    orig = relationship('Sisuplokk', foreign_keys=orig_id)
    lang = Column(String(2))     #  tõlkekeel
    ylesandeversioon_id = Column(Integer, ForeignKey('ylesandeversioon.id'), index=True) # versioon
    ylesandeversioon = relationship('Ylesandeversioon', foreign_keys=ylesandeversioon_id)
    nimi = Column(String(2000)) # nimetus
    tehn_tookask = Column(String(512)) # tehniline töökäsk
    sisu = Column(Text) # toimetajale näidatav sisu
    sisuvaade = Column(Text) # lahendajale näidatav sisu
    laius = Column(Integer) # veergude arv (ristsõna korral)
    korgus = Column(Integer) # ridade arv (ristsõna korral)
    tahemargid = Column(Integer) # sisuploki tõlke tähemärkide arv
    __table_args__ = (
        sa.UniqueConstraint('orig_id','lang', 'ylesandeversioon_id'),
        )

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .sisuplokk import Sisuplokk

        parent = self.orig or self.orig_id and Sisuplokk.get(self.orig_id)
        if parent:
            parent.logi('Sisuploki tõlge [%s]' % (self.lang), vanad_andmed, uued_andmed, logitase)
    
class T_Sisuobjekt(EntityHelper, Base, S3File):
    """Tabeli Sisuobjekt tõlge
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    orig_id = Column(Integer, ForeignKey('sisuobjekt.id'), index=True, nullable=False) # viide lähtetabelile
    orig = relationship('Sisuobjekt', foreign_keys=orig_id)
    lang = Column(String(2)) # tõlkekeel  
    ylesandeversioon_id = Column(Integer, ForeignKey('ylesandeversioon.id'), index=True) # versioon
    ylesandeversioon = relationship('Ylesandeversioon', foreign_keys=ylesandeversioon_id)
    tiitel = Column(String(256)) # pildi atribuut title (kasutatakse pildi algallikate märkimiseks)
    #filedata_db = deferred(Column('filedata', LargeBinary)) # faili sisu
    #filedata_ver = Column(Integer) # faili sisu muudatuste loendur (vajalik puhvri uuendamiseks)
    filesize = Column(Integer) # faili suurus baitides
    fileversion = Column(String(8)) # versioon
    fileurl = Column(String(200)) # faili URL
    laius = Column(Integer) # kuvamisel kasutatav laius
    korgus = Column(Integer) # kuvamisel kasutatav kõrgus
    laius_orig = Column(Integer) # pildi tegelik laius
    korgus_orig = Column(Integer) # pildi tegelik kõrgus
    __table_args__ = (
        sa.UniqueConstraint('orig_id','lang', 'ylesandeversioon_id'),
        )
    _cache_dir = 't_sisuobjekt'
    _id_seq_name = 't_sisuobjekt_id_seq'

    @property
    def fileext(self):
        orig = self.orig
        if orig:
            return orig.fileext

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .sisuobjekt import Sisuobjekt

        parent = self.orig or self.orig_id and Sisuobjekt.get(self.orig_id)
        if parent:
            parent.logi('Sisuobjekti tõlge [%s]' % (self.lang), vanad_andmed, uued_andmed, logitase)

class T_Tulemus(EntityHelper, Base):
    """Tabeli Tulemus tõlge 
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    orig_id = Column(Integer, ForeignKey('tulemus.id'), index=True, nullable=False) # viide lähtetabelile
    orig = relationship('Tulemus', foreign_keys=orig_id)
    lang = Column(String(2)) # tõlkekeel
    ylesandeversioon_id = Column(Integer, ForeignKey('ylesandeversioon.id'), index=True) # versioon
    ylesandeversioon = relationship('Ylesandeversioon', foreign_keys=ylesandeversioon_id)
    naidisvastus = Column(Text) # näidisvastus (avatud vastusega küsimuse korral)
    _flush_on_delete = True
    __table_args__ = (
        sa.UniqueConstraint('orig_id','lang', 'ylesandeversioon_id'),
        )

class T_Ylesandefail(EntityHelper, Base, S3File):
    """Tabeli Ylesandefail tõlge
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    orig_id = Column(Integer, ForeignKey('ylesandefail.id'), index=True, nullable=False) # viide lähtetabelile
    orig = relationship('Ylesandefail', foreign_keys=orig_id)
    lang = Column(String(2)) # tõlkekeel   
    ylesandeversioon_id = Column(Integer, ForeignKey('ylesandeversioon.id'), index=True) # versioon
    ylesandeversioon = relationship('Ylesandeversioon', foreign_keys=ylesandeversioon_id)
    #filedata_db = deferred(Column('filedata', LargeBinary)) # faili sisu
    filesize = Column(Integer) # faili suurus baitides
    fileversion = Column(String(8)) # versioon
    fileurl = Column(String(200)) # faili URL
    __table_args__ = (
        sa.UniqueConstraint('orig_id','lang', 'ylesandeversioon_id'),
        )
    _cache_dir = 't_ylesandefail'
    _id_seq_name = 't_ylesandefail_id_seq'

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .ylesandefail import Ylesandefail

        parent = self.orig or self.orig_id and Ylesandefail.get(self.orig_id)
        if parent:
            parent.logi('Ülesandefaili tõlge [%s]' % (self.lang), vanad_andmed, uued_andmed, logitase)    

class T_Kysimus(EntityHelper, Base):
    """Tabeli Kysimus tõlge
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    orig_id = Column(Integer, ForeignKey('kysimus.id'), index=True, nullable=False) # viide lähtetabelile
    orig = relationship('Kysimus', foreign_keys=orig_id)
    lang = Column(String(2)) # tõlkekeel
    ylesandeversioon_id = Column(Integer, ForeignKey('ylesandeversioon.id'), index=True) # versioon
    ylesandeversioon = relationship('Ylesandeversioon', foreign_keys=ylesandeversioon_id)
    pikkus = Column(Integer) # avatud lünga pikkus; ristsõna sõna pikkus
    max_pikkus = Column(Integer) # avatud lünga vastuse max pikkus
    ridu = Column(Integer) # avatud lünga korral ridade arv
    mask = Column(String(256)) # avatud lünga mask
    vihje = Column(String(256)) # vihje, mis kuvatakse lahendajale enne vastuse sisestamist
    pos_x = Column(Integer) # ristsõna korral: mitmes veerg
    pos_y = Column(Integer) # ristsõna korral: mitmes rida
    joondus = Column(String(10)) # ristsõna korral: teksti suund
    
    __table_args__ = (
        sa.UniqueConstraint('orig_id','lang', 'ylesandeversioon_id'),
        )
    
    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .kysimus import Kysimus
        parent = self.orig or self.orig_id and Kysimus.get(self.orig_id)
        if parent:
            parent.logi('Küsimuse tõlge [%s]' % (self.lang), vanad_andmed, uued_andmed, logitase)

class T_Kyslisa(EntityHelper, Base):
    """Tabeli Kyslisa tõlge
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    orig_id = Column(Integer, ForeignKey('kyslisa.id'), index=True, nullable=False) # viide lähtetabelile
    orig = relationship('Kyslisa', foreign_keys=orig_id)
    lang = Column(String(2)) # tõlkekeel
    ylesandeversioon_id = Column(Integer, ForeignKey('ylesandeversioon.id'), index=True) # versioon
    ylesandeversioon = relationship('Ylesandeversioon', foreign_keys=ylesandeversioon_id)
    yhik = Column(String(15)) # liuguriga mõõdetava ühiku nimetus
    __table_args__ = (
        sa.UniqueConstraint('orig_id','lang', 'ylesandeversioon_id'),
        )
    
    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .kyslisa import Kyslisa
        parent = self.orig or self.orig_id and Kyslisa.get(self.orig_id)
        if parent:
            parent.logi('Küsimuse tõlge [%s]' % (self.lang), vanad_andmed, uued_andmed, logitase)
    
class T_Valik(EntityHelper, Base):
    """Tabeli Valik tõlge
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    orig_id = Column(Integer, ForeignKey('valik.id'), index=True, nullable=False) # viide lähtetabelile
    orig = relationship('Valik', foreign_keys=orig_id)
    lang = Column(String(2)) # tõlkekeel
    ylesandeversioon_id = Column(Integer, ForeignKey('ylesandeversioon.id'), index=True) # versioon
    ylesandeversioon = relationship('Ylesandeversioon', foreign_keys=ylesandeversioon_id)
    nimi = Column(Text) # nimetus
    __table_args__ = (
        sa.UniqueConstraint('orig_id','lang', 'ylesandeversioon_id'),
        )

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .valik import Valik

        parent = self.orig or self.orig_id and Valik.get(self.orig_id)
        if parent:
            parent.logi('Valiku tõlge [%s]' % (self.lang), vanad_andmed, uued_andmed, logitase)

class T_Hindamismaatriks(EntityHelper, Base):
    """Tabeli Hindamismaatriks tõlge
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    orig_id = Column(Integer, ForeignKey('hindamismaatriks.id'), index=True, nullable=False) # viide lähtetabelile 
    orig = relationship('Hindamismaatriks', foreign_keys=orig_id)
    lang = Column(String(2)) # tõlkekeel
    ylesandeversioon_id = Column(Integer, ForeignKey('ylesandeversioon.id'), index=True) # versioon
    ylesandeversioon = relationship('Ylesandeversioon', foreign_keys=ylesandeversioon_id)
    kood1 = Column(String(2000)) # kood1
    kood2 = Column(String(256)) # kood2
    __table_args__ = (
        sa.UniqueConstraint('orig_id','lang', 'ylesandeversioon_id'),
        )

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .hindamismaatriks import Hindamismaatriks

        parent = self.orig or self.orig_id and Hindamismaatriks.get(self.orig_id)
        if parent:
            parent.logi('Hindamismaatriksi tõlge [%s]' % (self.lang), vanad_andmed, uued_andmed, logitase)

class T_Abivahend(EntityHelper, Base):
    """Tabeli Abivahend tõlge
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    orig_id = Column(Integer, ForeignKey('abivahend.id'), index=True, nullable=False) # viide lähtetabelile
    orig = relationship('Abivahend', foreign_keys=orig_id)
    lang = Column(String(2)) # tõlkekeel
    nimi = Column(String(500)) # nimetus
    kirjeldus = Column(Text) # täiendav kirjeldus
    pais = Column(Text) # HTML päisesse lisatav osa (vahendite korral)

    _flush_on_delete = True
    __table_args__ = (
        sa.UniqueConstraint('orig_id','lang'),
        )
    logging = False
