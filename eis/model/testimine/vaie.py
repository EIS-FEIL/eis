"Testikorralduse andmemudel"

import pickle
from cgi import FieldStorage
import mimetypes

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *
from .vaidelogi import Vaidelogi

class Vaie(EntityHelper, Base):
    """Tesi.sooritaja vaie Haridus- ja Teadusministeeriumile
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    sooritaja_id = Column(Integer, ForeignKey('sooritaja.id'), index=True, nullable=False) # viide.sooritaja kirjele
    sooritaja = relationship('Sooritaja', foreign_keys=sooritaja_id, back_populates='vaie')
    vaide_nr = Column(Integer) # vaide number, sisestatakse vaide registreerimisel, hiljem kasutatakse otsuse numbrina
    markus = Column(Text) #.sooritaja antud lisainfo, vaidlustamise põhjendus
    esitamisaeg = Column(DateTime) # vaide esitamise aeg
    avaldus_dok = Column(LargeBinary) # vaide avalduse digiallkirjastatud dokument
    avaldus_ext = Column(String(5)) # avalduse vorming: ddoc või bdoc või asice
    #ettepanek_txt = Column(Text) # ettepaneku tekst
    ettepanek_pohjendus = Column(Text) # ettepaneku põhjendus
    ettepanek_pdok = Column(LargeBinary) # pooleli digiallkirjastamisega ettepaneku dokument (kui allkirjastamine pole pooleli, siis tühi)
    ettepanek_dok = Column(LargeBinary) # vaide kohta tehtud ettepaneku digiallkirjastatud dokument
    ettepanek_ext = Column(String(5)) # ettepaneku vorming: ddoc või bdoc või asice
    h_arvestada = Column(Boolean) # kas tulemuse arvutamisel arvestada vaidehindamist: kui otsuse eelnõu on juba olemas, siis jah; enne eelnõu loomist loetakse hindamist pooleliolevana ja tulemust pole
    eelnou_pohjendus = Column(Text) # otsuse eelnõu põhjendus
    eelnou_pdf = Column(LargeBinary) # otsuse eelnõu PDFina
    arakuulamine_kuni = Column(Date) # ärakuulamise tähtaeg, kuni milleni on vaidlustajal võimalik eelnõu kohta arvamust esitada (peale seda läheb vaie otsustamisele)
    tagasivotmine_dok = Column(LargeBinary) # avaldus vaide tagasivõtmiseks (vaiet saab tagasi võtta kuni otsuse langetamiseni)
    tagasivotmine_ext = Column(String(5)) # tagasivõtmise avalduse failitüüp
    otsus_pohjendus = Column(Text) # otsuse põhjendus
    otsus_kp = Column(Date) # otsuse kuupäev
    otsus_pdf = Column(LargeBinary) # vaide kohta tehtud otsus PDFina
    otsus_pdok = Column(LargeBinary) # pooleli digiallkirjastamisega otsuse dokument (kui allkirjastamine pole pooleli, siis tühi)
    otsus_dok = Column(LargeBinary) # vaide kohta tehtud otsuse digiallkirjastatud dokument
    otsus_ext = Column(String(5)) # otsuse vorming: ddoc või bdoc või asice
    otsus_epostiga = Column(Boolean) # kas vaidlustaja soovib otsust e-postiga
    staatus = Column(Integer, sa.DefaultClause('0'), nullable=False) # staatus: 0=const.V_STAATUS_ESITAMATA - esitamata; 1=const.V_STAATUS_ESITATUD - esitatud; 2=const.V_STAATUS_MENETLEMISEL - menetlemisel; 4=const.V_STAATUS_ETTEPANDUD - ettepanek esitatud vaidekomisjonile; 5=const.V_STAATUS_OTSUSTAMISEL - ärakuulamise tähtaeg on läbi; 6=const.V_STAATUS_OTSUSTATUD - otsustatud; 7=const.V_STAATUS_TAGASIVOETUD - tagasi võetud
    valjaotsitud = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas on välja otsitud (vaiete loetelus linnukesega)
    allkirjad = Column(Integer, sa.DefaultClause('0'), nullable=False) # antud allkirjade arv otsusel
    vaideallkirjad = relationship('Vaideallkiri', order_by='Vaideallkiri.jrk', back_populates='vaie')
    pallid_enne = Column(Float, nullable=False) # vaide esitamise ajal kehtinud tulemus
    pallid_parast = Column(Float) # vaidlustusjärgne tulemus
    muutus = Column(Float) # hindepallide muutus (pallid_parast-pallid_enne)
    tunnistada = Column(Integer) # mida teha tunnistusega: NULL - mitte midagi (pole vaja tunnistust muuta või on juba tehtud); 1=const.U_STAATUS_UUENDADA - uuendada; 2=const.U_STAATUS_VALJASTADA - väljastada uus; 3=const.U_STAATUS_TYHISTADA - tühistada
    vaidelogid = relationship('Vaidelogi', order_by='Vaidelogi.id', back_populates='vaie')    
    vaidefailid = relationship('Vaidefail', order_by='Vaidefail.id', back_populates='vaie')
    _parent_key = 'sooritaja_id'

    @property
    def staatus_nimi(self):
        return usersession.get_opt().V_STAATUS.get(self.staatus)

    @property
    def tunnistada_nimi(self):
        return usersession.get_opt().U_STAATUS.get(self.tunnistada)

    @property
    def tulemus_arvutatud(self):
        if not self.ettepanek_dok:
            return False
        for r in self.vaidelogid:
            if r.tegevus == Vaidelogi.TEGEVUS_ARVUTUSED:
                return True
        return False

    def gen_ettepanek_txt(self):
        if self.pallid_enne is None or self.pallid_parast is None:
            return
        testiliik = self.sooritaja.test.testiliik_kood
        if testiliik == const.TESTILIIK_RIIGIEKSAM:
            # lõpus tyhik
            eksami = 'riigieksami '
        elif testiliik == const.TESTILIIK_POHIKOOL:
            eksami = 'ühtse põhikooli lõpueksami '
        else:
            # lõpus pole tyhikut
            eksami = 'eksami'

        if self.pallid_enne == self.pallid_parast: 
            buf = 'jätta %stulemus muutmata' % eksami
        else:
            d = self.pallid_parast - self.pallid_enne
            buf = '%s %stulemust %s hindepalli võrra' % \
                  (d > 0 and 'tõsta' or 'langetada',
                   eksami,
                   fstr(abs(d)))
        return buf

    def delete_subitems(self):
        self.delete_subrecords(['vaidelogid',
                                'vaideallkirjad',
                                'vaidefailid',
                                ])
        
