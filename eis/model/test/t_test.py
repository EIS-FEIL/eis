# -*- coding: utf-8 -*-
"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import Opt
from eis.model.kasutaja import *
from eis.model.koht import *

class T_Test(EntityHelper, Base):
    """Tabeli Test tõlge
    """
    orig_id = Column(Integer, ForeignKey('test.id'), index=True, primary_key=True) # viide lähtekirjele
    orig = relationship('Test', foreign_keys=orig_id, back_populates='trans')
    lang = Column(String(2), primary_key=True) # tõlkekeel
    nimi = Column(String(256)) # pealkiri
    tahemargid = Column(Integer) # tähemärkide arv tõlkekeeles
    _parent_key = 'orig_id'

class T_Testiosa(EntityHelper, Base):
    """Tabeli Testiosa tõlge
    """
    orig_id = Column(Integer, ForeignKey('testiosa.id'), index=True, primary_key=True) # viide lähtekirjele
    orig = relationship('Testiosa', foreign_keys=orig_id, back_populates='trans')
    lang = Column(String(2), primary_key=True) # tõlkekeel
    nimi = Column(String(256)) # testiosa nimetus
    alustajajuhend = Column(Text) # juhend sooritajale, mis kuvatakse enne testi alustamist
    sooritajajuhend = Column(Text) # sooritajajuhend, mis kuvatakse siis, kui sooritamist on alustatud
    _parent_key = 'orig_id'
    
class T_Alatest(EntityHelper, Base):
    """Tabeli Alatest tõlge
    """
    orig_id = Column(Integer, ForeignKey('alatest.id'), index=True, primary_key=True) # viide lähtekirjele
    orig = relationship('Alatest', foreign_keys=orig_id, back_populates='trans')
    lang = Column(String(2), primary_key=True) # tõlkekeel    
    nimi = Column(String(256)) # nimetus
    sooritajajuhend = Column(String(1024)) # sooritajajuhend
    _parent_key = 'orig_id'

class T_Alatestigrupp(EntityHelper, Base):
    """Tabeli Alatestigrupp tõlge
    """
    orig_id = Column(Integer, ForeignKey('alatestigrupp.id'), index=True, primary_key=True) # viide lähtekirjele
    orig = relationship('Alatestigrupp', foreign_keys=orig_id, back_populates='trans')
    lang = Column(String(2), primary_key=True) # tõlkekeel    
    nimi = Column(String(256)) # grupi nimetus
    _parent_key = 'orig_id'

class T_Testiplokk(EntityHelper, Base):
    """Tabeli Testiplokk tõlge
    """
    orig_id = Column(Integer, ForeignKey('testiplokk.id'), index=True, primary_key=True) # viide lähtekirjele
    orig = relationship('Testiplokk', foreign_keys=orig_id, back_populates='trans')
    lang = Column(String(2), primary_key=True) # tõlkekeel
    nimi = Column(String(256)) # nimetus
    _parent_key = 'orig_id'

class T_Testitagasiside(EntityHelper, Base):
    """Tabeli Testitagasiside tõlge
    """
    orig_id = Column(Integer, ForeignKey('testitagasiside.id'), index=True, primary_key=True) # viide lähtekirjele
    orig = relationship('Testitagasiside', foreign_keys=orig_id, back_populates='trans')
    lang = Column(String(2), primary_key=True) # tõlkekeel
    sissejuhatus_opilasele = Column(Text) # sissejuhatus õpilasele
    kokkuvote_opilasele = Column(Text) # kokkuvõte õpilasele
    sissejuhatus_opetajale = Column(Text) # sissejuhatus õpetajale
    kokkuvote_opetajale = Column(Text) # kokkuvõte õpetajale    
    tahemargid = Column(Integer) # tähemärkide arv
    _parent_key = 'orig_id'
    
class T_Testiylesanne(EntityHelper, Base):
    """Tabeli Testiylesanne tõlge
    """
    orig_id = Column(Integer, ForeignKey('testiylesanne.id'), index=True, primary_key=True) # viide lähtekirjele
    orig = relationship('Testiylesanne', foreign_keys=orig_id, back_populates='trans')
    lang = Column(String(2), primary_key=True) # tõlkekeel    
    nimi = Column(String(256)) # nimetus
    sooritajajuhend = Column(String(1024)) # juhend sooritajale (kasutusel valikülesande korral)       
    pealkiri = Column(String(512)) # pealkiri (kasutusel valikülesande korral)
    _parent_key = 'orig_id'

class T_Nptagasiside(EntityHelper, Base):
    """Tabeli Nptagasiside tõlge
    """
    orig_id = Column(Integer, ForeignKey('nptagasiside.id'), index=True, primary_key=True) # viide lähtekirjele
    orig = relationship('Nptagasiside', foreign_keys=orig_id, back_populates='trans')
    lang = Column(String(2), primary_key=True) # tõlkekeel    
    tagasiside = Column(Text) # sooritajale kuvatava tagasiside tekst
    op_tagasiside = Column(Text) # õpetajale kuvatava tagasiside tekst
    stat_tagasiside = Column(Text) # statistikas kasutatav tagasiside (grupi kohta)
    _parent_key = 'orig_id'
    
class T_Valitudylesanne(EntityHelper, Base):
    """Tabeli Valitudylesanne tõlge
    """
    orig_id = Column(Integer, ForeignKey('valitudylesanne.id'), index=True, primary_key=True) # viide lähtekirjele
    orig = relationship('Valitudylesanne', foreign_keys=orig_id, back_populates='trans')
    lang = Column(String(2), primary_key=True) # tõlkekeel    
    selgitus = Column(Text) # selgitav tekst lahendajale (jagatud töö korral)
    _parent_key = 'orig_id'

class T_Ylesandegrupp(EntityHelper, Base):
    """Tabeli Nsgrupp tõlge
    """
    orig_id = Column(Integer, ForeignKey('ylesandegrupp.id'), index=True, primary_key=True) # viide lähtekirjele
    orig = relationship('Ylesandegrupp', foreign_keys=orig_id, back_populates='trans')
    lang = Column(String(2), primary_key=True) # tõlkekeel    
    nimi = Column(String(1024)) # grupi nimetus
    _parent_key = 'orig_id'

class T_Normipunkt(EntityHelper, Base):
    """Tabeli Normipunkt tõlge
    """
    orig_id = Column(Integer, ForeignKey('normipunkt.id'), index=True, primary_key=True) # viide lähtekirjele
    orig = relationship('Normipunkt', foreign_keys=orig_id, back_populates='trans')
    lang = Column(String(2), primary_key=True) # tõlkekeel
    nimi = Column(String(330)) # nimetus, mida tulemuste kuvamisel kasutatakse
    tahemargid = Column(Integer) # tähemärkide arv
    _parent_key = 'orig_id'

class T_Nsgrupp(EntityHelper, Base):
    """Tabeli Nsgrupp tõlge
    """
    orig_id = Column(Integer, ForeignKey('nsgrupp.id'), index=True, primary_key=True) # viide lähtekirjele
    orig = relationship('Nsgrupp', foreign_keys=orig_id, back_populates='trans')
    lang = Column(String(2), primary_key=True) # tõlkekeel    
    nimi = Column(String(1024)) # grupi nimetus    
    _parent_key = 'orig_id'

class T_Hindamiskriteerium(EntityHelper, Base):
    """Tabeli Hindamiskriteerium tõlge 
    """
    orig_id = Column(Integer, ForeignKey('hindamiskriteerium.id'), index=True, primary_key=True) # viide lähtekirjele
    orig = relationship('Hindamiskriteerium', foreign_keys=orig_id, back_populates='trans')
    lang = Column(String(2), primary_key=True) # tõlkekeel
    hindamisjuhis = Column(Text)  # juhis
    _parent_key = 'orig_id'

class T_Kritkirjeldus(EntityHelper, Base):
    """Tabeli Kritkirjeldus tõlge 
    """
    orig_id = Column(Integer, ForeignKey('kritkirjeldus.id'), index=True, primary_key=True) # viide lähtekirjele
    orig = relationship('Kritkirjeldus', foreign_keys=orig_id, back_populates='trans')
    lang = Column(String(2), primary_key=True) # tõlkekeel
    kirjeldus = Column(Text)  # juhis
    _parent_key = 'orig_id'

