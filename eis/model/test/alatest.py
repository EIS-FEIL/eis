"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import Klrida

from .testiosa import Testiosa

class Alatest(EntityHelper, Base):
    """Alatest
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    seq = Column(Integer) # alatesti järjekorranumber testiosas
    nimi = Column(String(256)) # alatesti nimetus
    numbrita = Column(Boolean) # kas kuvada ilma järjekorranumbrita (nt juhendi alatesti korral)
    tahis = Column(String(10)) # alatesti järjekorranumber kasutajaliideses (kui nubrita alatestid välja jätta)
    alatest_kood = Column(String(10)) # alatesti liik (tasemeeksami korral), klassifikaator ALATEST
    kursus_kood = Column(String(10)) # lai või kitsas (matemaatika korral), klassifikaator KURSUS
    piiraeg = Column(Integer) # alatesti sooritamiseks lubatud aeg sekundites
    piiraeg_sek = Column(Boolean) # true - aeg kuvada kohe sekundites; false, null - minutist suurem aeg kuvada ilma sekunditeta
    hoiatusaeg = Column(Integer) # piirajaga alatesti korral: mitu sekundit enne lõppu antakse hoiatusteade    
    max_pallid = Column(Float) # max pallide arv
    skoorivalem = Column(String(256)) # tulemuse arvutamise valem (kasutusel siis, kui tulemus ei ole ülesannete pallide summa)
    vastvorm_kood = Column(String(10), nullable=False) # vastamise vorm, klassifikaator VASTVORM (EISis loodud testide korral sama, mis testiosa vastamise vorm; TSEISist üle kantud testide korral võib olla erinev)
    sooritajajuhend = Column(String(1024)) # juhend sooritajale
    ylesannete_arv = Column(Integer, sa.DefaultClause('0')) # ülesannete arv
    on_yhekordne = Column(Boolean) # kas alatest on ühekordselt lahendatav (peale kinnipanekut uuesti avada ei saa)
    yhesuunaline = Column(Boolean) # kas alatest on ühesuunaliselt lahendatav (ülesanded tuleb lahendada kindlas järjekorras)
    peida_pais = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas lahendajale kuvada EISi päis ja jalus või ainult ülesanded
    testiosa_id = Column(Integer, ForeignKey('testiosa.id'), index=True, nullable=False) # viide testiosale
    testiosa = relationship('Testiosa', foreign_keys=testiosa_id, back_populates='alatestid')
    komplektivalik_id = Column(Integer, ForeignKey('komplektivalik.id'), index=True, nullable=False) # viide komplektivalikule, mille komplektid antud alatesti katavad
    komplektivalik = relationship('Komplektivalik', foreign_keys=komplektivalik_id, back_populates='alatestid')
    testiplokid = relationship('Testiplokk', order_by='Testiplokk.seq', back_populates='alatest')
    testiylesanded = relationship('Testiylesanne', order_by='Testiylesanne.seq', back_populates='alatest')
    erialatestid = relationship('Erialatest', back_populates='alatest')
    normipunktid = relationship('Normipunkt', order_by='Normipunkt.normityyp', back_populates='alatest')    
    testivaline = Column(Boolean) # kas vastatakse peale testi lõppemist (kasutatakse küsimustiku alatesti korral)
    yl_segamini = Column(Boolean) # kas ülesanded kuvatakse lahendajale segatud järjekorras
    trans = relationship('T_Alatest', cascade='all', back_populates='orig')
    rvosaoskus_id = Column(Integer, ForeignKey('rvosaoskus.id'), index=True) # seos rahvusvahelise tunnistuse osaoskusega, mis vastab sellele alatestile
    rvosaoskus = relationship('Rvosaoskus', foreign_keys=rvosaoskus_id)
    _parent_key = 'testiosa_id'    

    @property
    def opt_testiplokid(self):
        return [(item.id, item.nimi) for item in self.testiplokid]

    @property
    def kursus_nimi(self):
        if self.kursus_kood:
            test = self.testiosa and self.testiosa.test
            aine = test and test.aine_kood
            if aine:
                return Klrida.get_str('KURSUS', self.kursus_kood, ylem_kood=aine)            

    @property
    def testiylesanded_kuvada(self):
        return [ty for ty in self.testiylesanded if ty.kuvada_statistikas]
    
    def default(self):
        if not self.max_pallid:
            self.max_pallid = 0
        if not self.ylesannete_arv:
            self.ylesannete_arv = 0

    def delete_subitems(self):    
        self.delete_subrecords(['testiplokid',
                                'erialatestid',
                                'normipunktid',
                                ])

    def get_seq_parent(self, parent_key, parent_id):
        rc = Session.query(sa.func.max(Alatest.seq)).\
            filter(Alatest.testiosa_id==self.testiosa_id).\
            filter(Alatest.kursus_kood==self.kursus_kood).\
            scalar()
        return (rc or 0) + 1

    def get_normipunkt(self, normityyp):
        for r in self.normipunktid:
            if r.normityyp == normityyp:
                return r

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        testiosa = self.testiosa or self.testiosa_id and Testiosa.get(self.testiosa_id)
        if testiosa:
            testiosa.logi('Alatest %s (%s) %s' % (self.id, self.nimi, liik), vanad_andmed, uued_andmed, logitase)

