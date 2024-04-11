"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.countchar import CountChar
from .alatest import Alatest
from .alatestigrupp import Alatestigrupp
_ = usersession._

class Normipunkt(EntityHelper, Base):
    """Testisoorituse tagasiside andmiseks arvutatavate suuruste kirjeldus.
    Psühholoogilise testi alatesti või testiülesande normipunktide tüübid.
    Ülesande tagasiside.
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    seq = Column(Integer) # järjekorranumber vanema sees (testiosa korral)
    testiosa_id = Column(Integer, ForeignKey('testiosa.id'), index=True) # viide testiosale (kui on testiga seotud)
    testiosa = relationship('Testiosa', foreign_keys=testiosa_id, back_populates='normipunktid')    
    alatest_id = Column(Integer, ForeignKey('alatest.id'), index=True) # viide alatestile (alatesti või testiylesande normipunktide korral, lisaks on antud testiosa_id)
    alatest = relationship('Alatest', foreign_keys=alatest_id, back_populates='normipunktid')    
    testiylesanne_id = Column(Integer, ForeignKey('testiylesanne.id'), index=True) # viide testiülesandele (testiülesande normipunktide korral, lisaks on antud testiosa_id)
    testiylesanne = relationship('Testiylesanne', foreign_keys=testiylesanne_id, back_populates='normipunktid')    
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True) # viide ülesandele (ülesande normipunktide korral, mis pole seotud testiga, st testiosa_id on NULL)
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='normipunktid')
    ylesandegrupp_id = Column(Integer, ForeignKey('ylesandegrupp.id'), index=True) # viide ülesandegrupile (diagnoosiva testi (tüüp 2) korral)
    ylesandegrupp = relationship('Ylesandegrupp', back_populates='normipunktid')   
    nimi = Column(String(330)) # nimetus, mida tulemuste kuvamisel kasutatakse
    kood = Column(String(50)) # kood, mida kasutada valemites 
    lang = Column(String(2)) # soorituskeele kood, määrab õpipädevuse normipunkti korral, millistele sooritajatele kirje kehtib (kui on tühi, siis kehtib kõigis keeltes sooritajatele)
    normityyp = Column(Integer, nullable=False) # normipunktide (protsentiilide) tüüp: 1=const.NORMITYYP_PALLID - pallid; 2=const.NORMITYYP_SUHE - õigete vastuste suhe kõikidesse vastustesse; 3=const.NORMITYYP_AEG - aeg sekundites; 4=const.NORMITYYP_VEAD - vigade arv; 5=const.NORMITYYP_VASTUS - antud koodiga küsimuse vastus; 6=const.NORMITYYP_KPALLID - antud koodiga küsimuste keskmine pallide arv; 7=const.NORMITYYP_VALEM - valem vastustest; 8=const.NORMITYYP_PROTSENT - protsent maksimaalsest võimalikust tulemusest; 9=const.NORMITYYP_PUNKTID - küsimuse toorpunktid
    on_opilane = Column(Boolean, sa.DefaultClause('true'), nullable=False) # kas normipunkt kuvatakse õpilase individuaalsel profiililehel
    on_grupp = Column(Boolean, sa.DefaultClause('true'), nullable=False) # kas normipunkt kuvatakse grupi profiililehel
    normiprotsentiilid = relationship('Normiprotsentiil', order_by='Normiprotsentiil.protsent', back_populates='normipunkt')
    sooritusryhmad = relationship('Sooritusryhm', order_by='Sooritusryhm.ryhm', back_populates='normipunkt')
    kysimus_kood = Column(String(2000)) # avaldis: küsimuse kood, kui protsentiil käib küsimuse kohta (alatesti korral liidetakse alatesti vastava koodiga küsimuste vastused); küsimuse baastüüp peab olema "täisarv"; valemi korral valem nt TASK_1.K01 + TASK_2.K02
    on_oigedvaled = Column(Boolean) # kas kuvada profiililehel õigete ja valede vastuste arvud (koolipsühholoogi testi korral)
    pooratud = Column(Boolean) # kas on pööratud (kahanev), nt aja ja vigade arvu korral
    pooratud_varv = Column(Boolean) # kas värvid kuvada teistpidi, st tumedast heledani, vaikimisi on heledast tumedani (õpipädevuse testis)
    varv2_mk = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas kahe sooritusrühma kattumisel kasutada äärmise rühma värvi (vaikimisi kuvatakse keskmise rühma värv) (õpipädevuse testis)
    min_vaartus = Column(Float) # min väärtus
    max_vaartus = Column(Float) # max väärtus
    min_max = Column(String(20)) # võimalikud väärtused, komaga eraldatud (õpipädevuse testis)
    tahemargid = Column(Integer) # tähemärkide arv originaalkeeles
    alatestigrupp_id = Column(Integer, ForeignKey('alatestigrupp.id'), index=True) # viide grupile (testiosa normipunktide korral)
    alatestigrupp = relationship('Alatestigrupp', foreign_keys=alatestigrupp_id, back_populates='normipunktid') 
    nptagasisided = relationship('Nptagasiside', order_by='Nptagasiside.seq', back_populates='normipunkt')
    trans = relationship('T_Normipunkt', cascade='all', back_populates='orig')
    
    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from eis.model.ylesanne.ylesanne import Ylesanne
        from .testiylesanne import Testiylesanne
        from .ylesandegrupp import Ylesandegrupp
        from .testiosa import Testiosa
        
        if self.logging:
            parent = self.ylesanne or self.ylesanne_id and Ylesanne.get(self.ylesanne_id) or \
                     self.testiylesanne or self.testiylesanne_id and Testiylesanne.get(self.testiylesanne_id) or \
                     self.ylesandegrupp or self.ylesandegrupp_id and Ylesandegrupp.get(self.ylesandegrupp_id) or \
                     self.alatest or self.alatest_id and Alatest.get(self.alatest_id) or \
                     self.alatestigrupp or self.alatestigrupp_id and Alatestigrupp.get(self.alatestigrupp_id) or \
                     self.testiosa or self.testiosa_id and Testiosa.get(self.testiosa_id)
            if parent:
                buf = 'Tunnus %s' % (self.id or '')
                nimi = self.nimi or self.kood or ''
                if nimi:
                    buf += ' (%s)' % nimi
                parent.logi('%s %s' % (buf, liik), vanad_andmed, uued_andmed, logitase)
                
    @property
    def default_nimi(self):
        ty = self.testiylesanne
        if ty and not ty.nimi:
            for vy in ty.valitudylesanded:
                y = vy.ylesanne
                if y:
                    nimi = '%s %s - %s' % (_("Ülesanne"), y.id, y.nimi)
                    return nimi
        r = ty or self.alatest
        if r:
            return r.nimi or ''
        if self.ylesandegrupp:
            nimi = self.ylesandegrupp.nimi or ''
            plain =  re.sub('<[^>]+>','', nimi)
            return plain
        return ''

    @property
    def d_nimi(self):
        return self.nimi or self.default_nimi

    @property
    def normityyp_nimi(self):
        for k, v in usersession.get_opt().normityyp:
            if k == self.normityyp:
                return v
    
    def get_seq(self):
        if self.testiosa_id:
            return self.get_seq_parent('testiosa_id', self.testiosa_id)            
        elif self.alatest_id:
            return self.get_seq_parent('alatest_id', self.alatest_id)
        elif self.testiylesanne_id:
            return self.get_seq_parent('testiylesanne_id', self.testiylesanne_id)

    def copy(self):
        cp = EntityHelper.copy(self)
        self.copy_subrecords(cp, ['normiprotsentiilid',
                                  'sooritusryhmad',
                                  'nptagasisided',
                                  'trans'])
        return cp

    def delete_subitems(self):    
        self.delete_subrecords(['normiprotsentiilid',
                                'sooritusryhmad',
                                'nptagasisided',
                                ])
        from eis.model.eksam.npvastus import Npvastus
        q = Session.query(Npvastus).filter_by(normipunkt_id=self.id)
        for r in q.all():
            r.delete()
        
    def pack_subrecords(self, delete=True, modified=None):
        li = []
        if self.ylesanne_id:
            # testi normipunktid pakime raw_export.py failis,
            # kuna testi normipunktides võib olla viiteid ylesannetele,
            # mille jaoks vaja vastavusi säilitada
            for ns in self.nptagasisided:
                li += ns.pack(False, None)
        return li

    def count_tahemargid(self, lang):
        """Loetakse kokku testis olevad tähemärgid tekstiväljadelt,
        et selle põhjal saaks arvestada toimetajate ja tõlkijate töötasu.
        """
        cch = CountChar(self.testiosa.test.lang, lang)
        total = 0        

        tr = cch.tran(self, True)
        total += cch.count(tr.nimi, False)
        for ns in self.nptagasisided:
            tr2 = cch.tran(ns)
            if tr2:
                total += cch.count(tr2.tagasiside, True) + \
                         cch.count(tr2.op_tagasiside, True)
        if tr:
            tr.tahemargid = total
        return total

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.id, self.kood)
    
class Normiprotsentiil(EntityHelper, Base):
    """Psühholoogilise testi alatesti või testiülesande normipunktide tüübile vastavad protsentiilid.
    """
    OPIP_MADAL = 1
    OPIP_KESK = 2
    OPIP_KORGE = 3
    id = Column(Integer, primary_key=True, autoincrement=True)
    normipunkt_id = Column(Integer, ForeignKey('normipunkt.id'), index=True, nullable=False) # viide alatesti või testiülesandega seotud normipunkti tüübi kirjele
    normipunkt = relationship('Normipunkt', back_populates='normiprotsentiilid')
    protsent = Column(Integer, nullable=False) # psühholoogi testis protsent (10,25,50,75,90)
    protsentiil = Column(Float) # psühholoogi testis protsentiil (mitu punkti on selle sooritaja tulemus, kes paikneb tulemuste järjekorras antud protsendi peal (vahemiku lõpp)
    _parent_key = 'normipunkt_id'

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        if self.logging:
            np = self.normipunkt or self.normipunkt_id and Normipunkt.get(self.normipunkt_id)
            if np:
                np.logi('Normiprotsentiil %s %s' % (self.protsent or '', liik), vanad_andmed, uued_andmed, logitase)

class Sooritusryhm(EntityHelper, Base):
    """Õpipädevuse testis normipunkti sooritusrühmad (madal, keskmine, kõrge)
    """
    OPIP_MADAL = 1
    OPIP_KESK = 2
    OPIP_KORGE = 3
    id = Column(Integer, primary_key=True, autoincrement=True)
    normipunkt_id = Column(Integer, ForeignKey('normipunkt.id'), index=True, nullable=False) # viide alatesti või testiülesandega seotud normipunkti tüübi kirjele
    normipunkt = relationship('Normipunkt', back_populates='sooritusryhmad')
    ryhm = Column(Integer, nullable=False) # sooritusrühm (1 - madal, 2 - keskmine, 3 - kõrge)
    lavi = Column(Float) # sooritusrühma kuulumise lävi (vahemiku algus - nt kui vahemikud on 0-15,16-21,22-30, siis andmebaasis on väärtused 0,16,22)
    _parent_key = 'normipunkt_id'

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        if self.logging:
            np = self.normipunkt or self.normipunkt_id and Normipunkt.get(self.normipunkt_id)
            if np:
                np.logi('Sooritusrühm %s %s' % (self.ryhm or '', liik), vanad_andmed, uued_andmed, logitase)
