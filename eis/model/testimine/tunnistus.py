"Testikorralduse andmemudel"

import mimetypes

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *
from .tunnistusekontroll import Tunnistusekontroll
from eis.s3file import S3File

class Tunnistus(EntityHelper, Base, S3File):
    """Eksamitunnistus
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide tunnistatud kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='tunnistused')
    tunnistusenr = Column(String(30)) # tunnistuse nr, riigieksami korral kujul 2AA-KKKSSS-J, kus: AA - aasta; KKK - kooli kood; SSS - tunnistus.seq sooritaja järjenr oma koolis); J - 1,2,3... (tunnistuse järjenr sooritaja jaoks)
    valjastamisaeg = Column(DateTime) # väljaandmise aeg
    avaldamisaeg = Column(DateTime) # tunnistuse avaldamise aeg (vajalik tasemeeksami sooritusteatel kuvamiseks)
    testsessioon_id = Column(Integer, ForeignKey('testsessioon.id'), index=True) # testsessioon, mille soorituste kohta tunnistus antakse (EISi antud tunnistuste korral kohustuslik)
    testsessioon = relationship('Testsessioon', foreign_keys=testsessioon_id)
    oppeaasta = Column(Integer) # õppeaasta (EISi antud tunnistuste korral kohustuslik)
    kool_koht_id = Column(Integer, ForeignKey('koht.id'), index=True) # kool, milles sooritaja õppis
    kool_koht = relationship('Koht', foreign_keys=kool_koht_id)
    kool_kood = Column(String(4)) # kooli kood - algselt tunnistuse numbri sees olev kooli tähistav arv, enam ei kasutata
    seq = Column(Integer) # sooritaja järjekorranumber testiliigi ja aasta piires (kasutusel tunnistuse numbri sees)
    filename = Column('filename',String(256)) # failinimi
    filesize = Column(Integer) # faili suurus baitides
    fileversion = Column(String(8)) # versioon
    staatus = Column(Integer, sa.DefaultClause('1'), nullable=False) # olek: 0=const.N_STAATUS_KEHTETU - kehtetu; 1=const.N_STAATUS_KEHTIV - kehtiv, dok salvestamata; 3=const.N_STAATUS_SALVESTATUD - kehtiv, dok salvestatud; 2=const.N_STAATUS_AVALDATUD - avaldatud
    uuendada = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas on vaja uus tunnistus teha (seatakse peale vaideotsust)
    eesnimi = Column(String(50), nullable=False) # sooritaja eesnimi tunnistuse andmise ajal
    perenimi = Column(String(50), nullable=False) # sooritaja perekonnanimi tunnistuse andmise ajal
    testiliik_kood = Column(String(10)) # tunnistuse liik, klassifikaator TESTILIIK
    mallinimi = Column(String(100)) # kasutatud PDF malli nimi
    alus = Column(String(100)) # väljastamise alus (käskkirja nr)
    pohjendus = Column(String(256)) # väljastamise põhjendus (sisestatakse samas sessioonis sooritajale tunnistuse korduva väljastamise korral)
    tyh_pohjendus = Column(String(256)) # tühistamise põhjendus
    aeg_registris = Column(DateTime) # tunnistuste registris andmete lisamise või muutmise aeg või NULL, kui on lisamata
    testitunnistused = relationship('Testitunnistus', order_by='Testitunnistus.id', back_populates='tunnistus')
    rvsooritaja = relationship('Rvsooritaja', uselist=False, back_populates='tunnistus') # viide rahvusvahelise eksami sooritusele, kui tunnistus on rahvusvahelise eksami sertifikaat
    tunnistusekontroll = relationship('Tunnistusekontroll', uselist=False, back_populates='tunnistus')

    _cache_dir = 'tunnistus'

    @property
    def staatus_nimi(self):
        return usersession.get_opt().N_STAATUS.get(self.staatus)

    @property
    def eelmine(self):
        "Leiame tunnistuse eelmise eksemplari"
        tyvi, n_nr = self.tunnistusenr.rsplit('-', 1)
        prev_nr = int(n_nr) - 1
        if prev_nr > 0:
            prev_tunnistusenr = '%s-%d' % (tyvi, prev_nr)
            rcd = (Tunnistus.query
                   .filter_by(kasutaja_id=self.kasutaja_id)
                   .filter_by(testiliik_kood=self.testiliik_kood)
                   .filter_by(tunnistusenr=prev_tunnistusenr)
                   .first())
            return rcd

    def set_filedata(self, filedata, filename):
        self.filename = filename
        self.filedata = filedata
        if self.fileext in (const.BDOC, const.ASICE):
            ktr = self.tunnistusekontroll
            if not ktr:
                ktr = Tunnistusekontroll()
                self.tunnistusekontroll = ktr
            ktr.seisuga = None
            ktr.korras = True
            ktr.viga = None
