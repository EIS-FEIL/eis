"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import Klrida
from eis.model.opt import Opt
from eis.model.kasutaja import Kasutaja, Kasutajagrupp, Kasutajaroll, Kasutajagrupp_oigus
from eis.model.countchar import CountChar

from .testilogi import Testilogi
from .testiisik import Testiisik
from .salatest import Salatest
from .testitase import Testitase
from .tagasisidevorm import Tagasisidevorm
from eis.recordwrapper.testwrapper import TestWrapper
_ = usersession._

class Test(EntityHelper, Base, TestWrapper):
    """Test
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    nimi = Column(String(256)) # testi nimi
    staatus = Column(Integer, nullable=False) # olek: 1=const.T_STAATUS_KOOSTAMISEL - koostamisel; 2=const.T_STAATUS_KINNITATUD - kinnitatud; 8=const.T_STAATUS_ARHIIV - arhiveeritud
    testityyp = Column(Integer, nullable=False) # testi tüüp: 0=const.TESTITYYP_AVALIK - avaliku vaate test; 1=const.TESTITYYP_EKK - eksamikeskuse test; 2=const.TESTITYYP_KONS - konsultatsioon; 3=const.TESTITYYP_TOO - õpilasele jagatud töö
    testiklass_kood = Column(String(10)) # klass, klassifikaator TESTIKLASS
    aste_mask = Column(Integer) # kooliastmed/erialad kodeeritud bittide summana; biti järjekorranumber on astme kood (või vaikimisi astmete korral 0 - I aste; 1 - II aste; 2 - III aste; 3 - gümnaasium)
    periood_kood = Column(String(10)) # periood, klassifikaator PERIOOD
    max_pallid = Column(Float) # max hindepallide arv
    yhisosa_max_pallid = Column(Float) # laia ja kitsa matemaatika ühisossa kuuluvate ülesannete max hindepallide arv    
    salastatud = Column(Integer, sa.DefaultClause('0'), nullable=False) # salastatus: 0 - pole salastatud; 1 - salastatud, kuid sooritatav; 2 - loogiline salastatus; 2 - krüptitud (enam ei saa)
    testiliik_kood = Column(String(10)) # testi liik, klassifikaator TESTILIIK
    aine_kood = Column(String(10)) # õppeaine, klassifikaator AINE
    aine_muu = Column(String(50)) # õppeaine nimetus, kui ei leidu klassifikaatoris (avaliku vaate testi korral)
    testiosad = relationship('Testiosa', order_by='Testiosa.seq', back_populates='test')
    testikursused = relationship('Testikursus', order_by='Testikursus.id', back_populates='test')    
    testimiskorrad = relationship('Testimiskord', order_by='Testimiskord.tahis', back_populates='test')
    testiisikud = relationship('Testiisik', back_populates='test')
    testilogid = relationship('Testilogi', back_populates='test')
    salatest = relationship('Salatest', uselist=False, back_populates='test')
    #logitase = Column(Integer) # logitase: 1 - logida õiguste andmine; 2 - logida andmete muutmine
    eeltest_id = Column(Integer, ForeignKey('eeltest.id'), index=True) # eeltesti andmed ja seos algse testiga, kui antud test on mingi teise testi eeltest
    eeltest = relationship('Eeltest', foreign_keys=eeltest_id, back_populates='avalik_test')
    eeltestid = relationship('Eeltest', foreign_keys='Eeltest.algne_test_id', back_populates='algne_test') # antud testist loodud eeltestid
    opilase_taustakysitlus = relationship('Taustakysitlus', foreign_keys='Taustakysitlus.opilase_test_id', back_populates='opilase_test', uselist=False) # õpilase taustaküsitluse korral viide seosele õpetaja testiga
    opetaja_taustakysitlus = relationship('Taustakysitlus', foreign_keys='Taustakysitlus.opetaja_test_id', back_populates='opetaja_test', uselist=False) # õpetaja taustaküsitluse korral viide seosele õpilase testiga    
    avaldamistase = Column(Integer, sa.DefaultClause('0'), nullable=False) # avaldamistase: 4=const.AVALIK_SOORITAJAD - kõigile lahendajatele; 3=const.AVALIK_OPETAJAD - kõikidele pedagoogidele; 2=const.AVALIK_MAARATUD - määratud kasutajatele; 1=const.AVALIK_EKSAM - testimiskorraga test; 0=const.AVALIK_POLE - keegi ei saa kasutada
    avalik_alates = Column(Date) # kuupäev, millest alates test on avalikus vaates (kõigile sooritajatele, kõigile pedagoogidele või määratud pedagoogidele)
    avalik_kuni = Column(Date) # kuupäev, milleni test on avalikus vaates
    korduv_sooritamine = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas on võimalik testimiskorrata sooritamisel korduvalt sooritada
    korduv_sailitamine = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas korduvalt sooritamisel jätta varasemad sooritused alles
    valitudylesanded = relationship('Valitudylesanne', back_populates='test') # dubleeriv otsetee ülesanneteni (loogiline tee on testiosa ja komplekti kaudu)
    oige_naitamine = Column(Boolean, sa.DefaultClause('1')) # kas näidata õiget vastust lahendajale peale sooritamist (kasutatakse avaliku vaate testi korral)
    arvutihinde_naitamine = Column(Boolean, sa.DefaultClause('0')) # kas näidata arvutihinnatavat osa tulemusest kohe
    #tulemus_vaade = Column(Integer, sa.DefaultClause('0'), nullable=False) # millises vaates kool tulemusi näeb: 0=const.VAADE_TOIMUMISAEG - toimumisaegade kaupa; 1=const.VAADE_TEST - tasemetöö mall (testide kaupa); 2=const.VAADE_POHIKOOL - põhikooli vaade; 3=const.VAADE_OPIPADEVUS - õpipädevuse testi vaade; 4=const.VAADE_RIIGIEKSAM - riigieksami vaade; 5=const.VAADE_TASEMETOO - tasemetöö vaade profiililehtedega
    tulemus_tugiisikule = Column(Boolean) # kas tugiisik võib näha testi tulemust
    vastus_tugiisikule = Column(Boolean) # kas tugiisik võib näha antud vastuseid ja soorituse kirjet
    osalemise_peitmine = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas peita osalemine sooritaja eest (testimiskorrata lahendamisel): tugiisiku kasutamise korral ei näidata sooritajale testi kuskil; tugiisikuta sooritamisel näeb sooritaja testi ainult sooritamise ajal; ei mõjuta tulemuse ja vastuste kuvamist tugiisikule
    ajakulu_naitamine = Column(Integer, sa.DefaultClause('1'), nullable=False) # soorituste ajakulu näitamine koolile klassi tulemuste vaatamisel: 0=const.AJAKULU_POLE - ei näidata; 1=const.AJAKULU_OSA - ainult osade kaupa; 2=const.AJAKULU_TEST - ainult koguaeg (osade summa); 3=const.AJAKULU_KOIK - osade kaupa ja koguaeg
    opetajale_peidus = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas peita õpilase vastused ja tagasiside õpetaja eest (testimiskorrata lahendamisel, kasutusel taustaküsitlustes)
    tagasiside_mall = Column(Integer) # tagasiside mall: NULL - ei ole tagasisidet; 0=const.TSMALL_VABA - vabalt kujundatav; 1=const.TSMALL_DIAG - diagnoosiva testi mall; 2=const.TSMALL_PSYH - koolipsühholoogi testi mall
    diagnoosiv = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas on diagnoosiv test
    pallideta = Column(Boolean) # kas avalikus vaates ei kuvata tulemust pallides ega protsentides (õpipädevuse, koolipsühholoogi ja diagnoosiva testi korral sees) ja ei kuvata vastuste analüüsi
    protsendita = Column(Boolean) # kas pallides tulemuse kuvamisel ei kuvata protsenti (CAE korral sees, sest CAE osapunktide summa ei ole testi tulemus ja protsenti ei saa arvutada)
    lang = Column(String(2), sa.DefaultClause(const.LANG_ET), nullable=False) # põhikeele kood
    skeeled = Column(String(60)) # testi keelte koodid eraldatuna tühikuga
    ui_lang = Column(Boolean) # true - sooritamise kasutajaliides peab olema soorituskeeles; false, null - kasutatakse tavalist kasutajaliidese keelt 
    markus = Column(Text) # märkused
    lavi_pr = Column(Integer) # minimaalne tulemus protsentides, mille korral väljastatakse tunnistus (TE, SE korral)
    tulemuste_vahemikud_pr = Column(String(20)) # protsendivahemikud, mis kuvatakse tunnistusel saadud pallide asemel (TE, SE korral); väärtus "1,50,60,76,91" tähendab vahemikke 0-0, 1-49, 50-59, 60-75, 76-90, 91-100
    ymardamine = Column(Boolean, sa.DefaultClause('1'), nullable=False) # kas testi kogutulemuseks arvutatud pallid ümardada
    kvaliteet_kood = Column(String(10), index=True) # kvaliteedimärk
    autor = Column(String(128)) # testi autor (informatiivne, kasutusel d-testi korral)
    eristuskiri = relationship('Eristuskiri', uselist=False, back_populates='test')
    trans = relationship('T_Test', cascade='all', back_populates='orig')
    testimarkused = relationship('Testimarkus', order_by='Testimarkus.id', back_populates='test')
    nimekirjad = relationship('Nimekiri', back_populates='test') 
    sooritajad = relationship('Sooritaja', back_populates='test')
    testitasemed = relationship('Testitase', order_by='Testitase.seq', back_populates='test')
    testihinded = relationship('Testihinne', order_by=sa.desc(sa.text('Testihinne.hinne')), back_populates='test')
    rveksam_id = Column(Integer, ForeignKey('rveksam.id'), index=True) # seos rahvusvahelise tunnistusega, mida võidakse selle testi tulemuste põhjal väljastada
    rveksam = relationship('Rveksam', foreign_keys=rveksam_id)
    tahemargid = Column(Integer) # tähemärkide arv originaalkeeles
    toofailid = relationship('Toofail', order_by='Toofail.id', back_populates='test')
    tagasisidefailid = relationship('Tagasisidefail', order_by='Tagasisidefail.id', back_populates='test')
    tagasisidevormid = relationship('Tagasisidevorm', order_by='Tagasisidevorm.liik', back_populates='test')
    statistikaraportid = relationship('Statistikaraport', order_by='Statistikaraport.id', back_populates='test')    
    kogutestid = relationship('Kogutest', order_by='Kogutest.id', back_populates='test')
    testitagasiside = relationship('Testitagasiside', uselist=False, back_populates='test')
    arvutusprotsessid = relationship('Arvutusprotsess', back_populates='test')
    
    @property 
    def lang_nimi(self):
        return Klrida.get_lang_nimi(self.lang)

    @property
    def aine_nimi(self):
        return self.aine_muu or \
               self.aine_kood and Klrida.get_str('AINE', self.aine_kood)

    @property
    def testiliik_nimi(self):
        if self.testiliik_kood:
            return Klrida.get_str('TESTILIIK', self.testiliik_kood)
        else:
            return _("Avaliku vaate test")

    @property
    def keeletase_kood(self):
        for r in self.testitasemed:
            return r.keeletase_kood

    @property
    def keeletase_nimi(self):
        kood = self.keeletase_kood
        if kood:
            return Klrida.get_str('KEELETASE', kood, ylem_kood=self.aine_kood)

    @property
    def test_pallideta(self):
        "Millal ei kuvata testi tulemust pallidena"
        return self.pallideta

    @property
    def kooliastmed(self):
        "Leiame astmete koodid"
        astmed = []
        mask = self.aste_mask or 0
        opt = usersession.get_opt()
        for r in opt.astmed(self.aine_kood):
            aste_kood = r[0]
            bit = opt.aste_bit(aste_kood, self.aine_kood)
            if bit & mask:
                astmed.append(aste_kood)
        return astmed

    @property
    def aste_nimed(self):
        li = []
        for kood in self.kooliastmed:
            li.append(Klrida.get_str('ASTE', kood))
        return ', '.join(li)


    @property
    def on_tseis(self):
        # kas on TSEISi liiki test (neid koheldakse pisut erinevalt muudest)
        return self.testiliik_kood in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS)

    @property
    def on_kutse(self):
        # kas on kutseeksam
        return self.testiliik_kood == const.TESTILIIK_KUTSE

    @property
    def on_jagatudtoo(self):
        return self.testityyp == const.TESTITYYP_TOO

    @property
    def on_avaliktest(self):
        return self.testityyp == const.TESTITYYP_AVALIK
    
    @classmethod
    def get_opt(cls, testsessioon_id=None, testiliik_kood=None, test_id=None, keeletase=None, testityyp=None, vastvorm=None, disp_test_id=False, testsessioonid_id=None, testiliigid_kood=None):
        """Leitakse testimiskorrad
        """
        from eis.model.testimine.testimiskord import Testimiskord
        from .testiosa import Testiosa
        if not test_id \
          and not (testiliik_kood or testiliigid_kood) \
          and not (testsessioon_id or testsessioonid_id):
            return []

        q = SessionR.query(Test.id, Test.nimi)
        if testityyp:
            q = q.filter(Test.testityyp==testityyp)
        if testsessioon_id:
            q = q.filter(Test.testimiskorrad.any(Testimiskord.testsessioon_id==testsessioon_id))
        elif testsessioonid_id:
            q = q.filter(Test.testimiskorrad.any(Testimiskord.testsessioon_id.in_(testsessioonid_id)))
        if test_id:
            q = q.filter(Test.id==int(test_id))
        elif testiliik_kood:
            q = q.filter(Test.testiliik_kood==testiliik_kood)
        elif testiliigid_kood:
            q = q.filter(Test.testiliik_kood.in_(testiliigid_kood))
        if keeletase:
            q = q.filter(Test.testitasemed.any(Testitase.keeletase_kood==keeletase))
        if vastvorm:
            q = q.filter(Test.testiosad.any(Testiosa.vastvorm_kood==vastvorm))
        items = q.order_by(Test.nimi).all()
        if disp_test_id:
            return [(t_id, '%s %s' % (t_nimi, t_id)) for t_id, t_nimi in items]
        else:
            return [(t_id, t_nimi) for t_id, t_nimi in items]

    def set_lang(self):
        if self.skeeled is None:
            self.skeeled = self.lang + ' '
        elif self.lang not in self.skeeled:
            self.skeeled = self.lang + ' ' + self.skeeled

    def has_lang(self, lang):
        return self.skeeled and (lang in self.skeeled)

    def update_lang_by_y(self):
        "Avaliku vaate testile määratakse need keeled, mis on kõigis ülesannetes olemas"
        from eis.model.ylesanne import Ylesanne
        from .valitudylesanne import Valitudylesanne
        from .testiylesanne import Testiylesanne
        from .testiosa import Testiosa
        if self.id:
            q = (Session.query(Ylesanne.skeeled).distinct()
                 .join(Ylesanne.valitudylesanded)
                 .join(Valitudylesanne.testiylesanne)
                 .join(Testiylesanne.testiosa)
                 .filter(Testiosa.test_id==self.id)
                 )
            li_set = [set(sk.split()) for sk, in q.all()]
            t_keeled = list(li_set and set.intersection(*li_set) or {})

            if not t_keeled:
                self.skeeled = self.lang = const.LANG_ET
            elif const.LANG_ET in t_keeled:
                # kui eesti keel on keelte seas, siis on see põhikeel
                self.lang = const.LANG_ET
                self.skeeled = ' '.join(t_keeled)
            else:
                self.lang = t_keeled[0]
                self.skeeled = ' '.join(t_keeled)
            
    @property
    def keeled(self):
        if not self.skeeled:
            return []
        return self.skeeled.split()

    def get_keeled(self):
        return self.keeled

    @property
    def opt_keeled(self):
        return [(lang, Klrida.get_str('SOORKEEL', lang)) for lang in self.keeled]

    @property
    def avaldamistase_nimi(self):
        return usersession.get_opt().AVALIK.get(self.avaldamistase)

    @property
    def opt_testiosad(self):
        return [(item.id, '%s %s' % (item.tahis, item.nimi)) for item in self.testiosad]

    @property
    def opt_kursused(self):
        # esmalt leiame kõik aine kursused
        li = usersession.get_opt().klread_kood('KURSUS',  self.aine_kood, ylem_required=True)
        if li:
            # kui ainel on kursusi, siis valime need, mis on sellel testil lubatud
            lubatud = self.get_kursused()
            li = [r for r in li if r[0] in lubatud]
        return li

    def get_kursused(self):
        return [r.kursus_kood for r in self.testikursused if r.kursus_kood]        
    
    @property
    def on_kursused(self):
        for r in self.testikursused:
            if r.kursus_kood:
                return True
        return False

    @property
    def fileext(self):
        if self.filename:
            return self.filename.split('.')[-1]

    @property
    def mimetype(self):
        if self.filename:
            mimetype, encoding = mimetypes.guess_type(self.filename)
            return mimetype

    def get_korraldajad(self):
        if self.avaldamistase == const.AVALIK_MAARATUD:
            q = Kasutaja.query.\
                join(Testiisik.kasutaja).\
                filter(Testiisik.kasutajagrupp_id==const.GRUPP_T_KORRALDAJA).\
                filter(Testiisik.test_id==self.id).\
                order_by(Kasutaja.nimi)
        else:
            from eis.model.testimine import Nimekiri
            q = Kasutaja.query.\
                join(Nimekiri.esitaja_kasutaja).\
                filter(Nimekiri.test_id==self.id).\
                order_by(Kasutaja.nimi)
        return q.all()

    @property
    def opt_korraldajad(self):
        return [(k.id, k.nimi) for k in self.get_korraldajad()]

    @property
    def is_encrypted(self):
        return self.salastatud == const.SALASTATUD_KRYPTITUD

    def set_salastatud(self, salastatud):
        self.salastatud = salastatud
        if salastatud and self.avaldamistase in (const.AVALIK_SOORITAJAD, const.AVALIK_OPETAJAD):
            self.avaldamistase = const.AVALIK_POLE

    @property
    def on_kasitsihinnatav(self):
        # Kas testis on mõni käsitsihinnatav ylesanne
        q = self._q_kasitsihinnatav()
        return q.scalar() > 0

    def _q_kasitsihinnatav(self):
        # Kas testis on mõni käsitsihinnatav ylesanne
        from .hindamiskogum import Hindamiskogum
        from .testiosa import Testiosa
        q = (SessionR.query(sa.func.count(Hindamiskogum.id))
             .filter(Hindamiskogum.arvutihinnatav==False)
             .filter(Hindamiskogum.staatus==const.B_STAATUS_KEHTIV)
             .join(Hindamiskogum.testiosa)
             .filter(Testiosa.test_id==self.id))
        return q
    
    def kasitsihinnatav(self, testiruum_id):
        # Kas testis on mõni käsitsihinnatav ylesanne
        from .hindamiskogum import Hindamiskogum
        from eis.model.testimine import Sooritus, Hindamisolek
        q = self._q_kasitsihinnatav()
        if q.scalar() > 0:
            # test on kyll käsitsihinnatav
            # kas testiruumis on mõnel sooritajal midagi käsitsi hinnata?
            if testiruum_id and testiruum_id != '0':
                q = q.filter(sa.exists().where(
                    sa.and_(Sooritus.testiruum_id==testiruum_id,
                            Sooritus.id==Hindamisolek.sooritus_id,
                            Hindamisolek.hindamiskogum_id==Hindamiskogum.id,
                            Hindamisolek.mittekasitsi==False)
                    ))
                return q.scalar() > 0
        return False

    def default(self):
        if not self.salastatud:
            self.salastatud = const.SALASTATUD_POLE
        if not self.staatus:
            self.staatus = const.T_STAATUS_KOOSTAMISEL

    def salastatud_nimi(self, salastatud=None):
        if salastatud is None:
            salastatud = self.salastatud
        if salastatud == const.SALASTATUD_SOORITATAV:
            return _("Salastatud (sooritatav)")        
        elif salastatud == const.SALASTATUD_LOOGILINE:
            return _("Salastatud")
        elif salastatud == const.SALASTATUD_KRYPTITUD:
            return _("Krüptitud")
        elif salastatud == const.SALASTATUD_POLE:
            return _("Pole salastatud")

    def on_testitase(self, keeletase_kood):
        for r in self.testitasemed:
            if r.keeletase_kood == keeletase_kood:
                return True
        return False

    def get_testitase(self, n):
        "Leitakse testitase, cnt on 1 või 2"
        for r in self.testitasemed:
            if r.seq == n:
                return r

    def give_testitase(self, n):
        "Luuakse testitase, cnt on 1 või 2"
        r = self.get_testitase(n)
        if not r:
            from .testitase import Testitase
            r = Testitase(aine_kood=self.aine_kood,
                          seq=n)
            self.testitasemed.append(r)
        return r

    def get_testihinne(self, hinne):
        "Leitakse testihinne"
        for r in self.testihinded:
            if r.hinne == hinne:
                return r

    def give_testihinne(self, hinne):
        "Luuakse testihinne"
        r = self.get_testihinne(hinne)
        if not r:
            from .testihinne import Testihinne
            r = Testihinne(hinne=hinne)
            self.testihinded.append(r)
        return r

    def get_testikursus(self, kursus):
        "Leitakse testikursus"
        for r in self.testikursused:
            if r.kursus_kood == kursus:
                return r

    def give_testikursus(self, kursus):
        "Luuakse testikursus"
        r = self.get_testikursus(kursus)
        if not r:
            from .testikursus import Testikursus
            r = Testikursus(aine_kood=self.aine_kood,
                            kursus_kood=self.kursus_kood)
            self.testikursused.append(r)
        return r

    def log_delete(self):
        # logimist ei toimu
        pass

    def delete_subitems(self):    
        Session.autoflush = False # integrity errori pärast
        self.logging = False
        for r in [self.testitagasiside,
                  self.opilase_taustakysitlus,
                  self.opetaja_taustakysitlus]:
            if r:
                r.delete()

        self.delete_subrecords(['arvutusprotsessid',
                                'testimiskorrad',
                                'testiosad',
                                'testitasemed',
                                'statistikaraportid',
                                'testiisikud',
                                'testikursused',
                                'testilogid',
                                'toofailid',
                                'tagasisidefailid',
                                'tagasisidevormid',
                                'kogutestid'
                                ])
        if self.eristuskiri:
            self.eristuskiri.delete()
        for rcd in self.testimarkused:
            if rcd.ylem_id is None:
                rcd.delete()
        Session.autoflush = True # integrity errori pärast

    def has_permission(self, permission, perm_bit, lang=None, user=None):
        """Kontrollitakse jooksva kasutaja õigust 
        antud tegevusele antud testis.
        """
        if not user:
            user = usersession.get_user()
        if not user:
            return False

        kasutaja = user.get_kasutaja()
        if not kasutaja:
            return False

        rc = False

        if permission == 'omanimekirjad':
            if self.testityyp == const.TESTITYYP_TOO:
                # jagatud tööd saab õpilastele sooritada anda ainult töö koostaja ise
                rc = self._has_ind_permission('testid', const.BT_MODIFY, lang, kasutaja)                
                return rc

            # muid teste saab sooritamiseks jagada siis, kui on vaatamisõigus või test on avalik
        
        if self.testityyp not in (const.TESTITYYP_AVALIK, const.TESTITYYP_TOO):
            if permission == 'testid' and perm_bit & const.BT_MODIFY:
                # avalikus vaates saab muuta ainult avalikke teste
                return False

        if self.testityyp == const.TESTITYYP_AVALIK and user.handler.c.app_ekk:
            # avalik test EKK vaates
            # lubame adminil vaadata kõiki teste
            if perm_bit in (const.BT_SHOW, const.BT_INDEX) and user.on_admin:
                return True
            # peab olema individuaalne õigus testile ja avaliku õiguse roll
            if not user.has_permission(permission, perm_bit, gtyyp=const.USER_TYPE_AV):
                # pole lubatud EKK vaates avalikke teste teha
                return False
            rc = self._has_ind_permission(permission, perm_bit, lang, kasutaja)
            # kui õigust pole, siis koostajal on kõik õigused
            if not rc and permission != 'ekk-testid':
                rc = Testiisik.has_role(const.GRUPP_T_KOOSTAJA, user.id, self.id)
                # avaliku vaate testi omanikul ka
                if not rc:
                    rc = Testiisik.has_role(const.GRUPP_T_OMANIK, user.id, self.id)
            return rc
            
        if self.avaldamistase == const.AVALIK_LITSENTS:
            if self.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
                # koolipsyhholoogidele lubatud
                rc = user.on_koolipsyh
            elif self.testiliik_kood == const.TESTILIIK_LOGOPEED:
                # logopeedidele lubatud
                rc = user.on_logopeed
            else:
                rc = False
            return rc

        if self.testityyp in (const.TESTITYYP_EKK, const.TESTITYYP_KONS):
            if self.testityyp == const.TESTITYYP_EKK and permission == 'konsultatsioonid':
                return False
            if self.testityyp == const.TESTITYYP_KONS and permission == 'ekk-testid':
                return False
            
            # eksamikeskuse testile võib õigus tulla grupi kaudu
            # kas kasutajal on ainespetsialisti õigus 
            # kõigile sarnastele testidele
            # (ei anna õigust lisada või muuta nimekirju)
            if not (permission == 'omanimekirjad' and (perm_bit & const.BT_MODIFY)):
                rc = user.has_permission(permission, 
                                         perm_bit,
                                         aine=self.aine_kood, 
                                         testiliik=self.testiliik_kood)
        else:
            # kas kasutajal on ainespetsialisti õigus 
            # kõigile selle aine avaliku vaate testidele
            ained = user.get_ained(permission, perm_bit)
            rc = self.aine_kood in ained

        if self.staatus != const.T_STAATUS_KINNITATUD \
           and permission == 'omanimekirjad' and (perm_bit & const.BT_MODIFY):
            # arhiveeritud testi ei peaks sooritajatele rohkem suunama
            return False

        today = date.today()
        if not rc \
           and (permission == 'testid' and not (perm_bit & const.BT_MODIFY) \
                or permission == 'omanimekirjad'):
            if self.avaldamistase == const.AVALIK_OPETAJAD \
               and user.on_pedagoog \
               and (not self.avalik_alates or self.avalik_alates <= today) \
               and (not self.avalik_kuni or self.avalik_kuni >= today):
                # pedagoog võib vaadata avaldatud testi
                return True
            elif self.avaldamistase == const.AVALIK_SOORITAJAD \
               and (not self.avalik_alates or self.avalik_alates <= today) \
               and (not self.avalik_kuni or self.avalik_kuni >= today):
                # kõigile lubatud test
                return True

            if permission == 'omanimekirjad':
                # sama kontroll, mis testiruumi ja nimekirja korral
                if self.avaldamistase in (const.AVALIK_OPETAJAD, const.AVALIK_MAARATUD):
                    # kontrollime avaldamise ajavahemikku
                    if self.avalik_alates and self.avalik_alates > today or \
                           self.avalik_kuni and self.avalik_kuni < today:
                        # pole enam avalik test
                        log.debug('pole enam avalik')
                        return False

        # avaliku vaate testile või eksamikeskuse testile võib olla
        # antud isiklik õigus
        if not rc:
            rc = self._has_ind_permission(permission, perm_bit, lang, kasutaja)
        return rc

    def _has_ind_permission(self, permission, perm_bit, lang, kasutaja):
        """Kontrollime, kas kasutajal on antud testile eraldi õigus antud
        (sh vastusteanalyys)
        """
        today = date.today()
        q = (SessionR.query(sa.func.count(Testiisik.id))
             .filter(Testiisik.kasutaja_id==kasutaja.id)
             .filter(Testiisik.test_id==self.id)
             .filter(Testiisik.kehtib_alates<=today)
             .filter(Testiisik.kehtib_kuni>=today)
             .join(Testiisik.kasutajagrupp)
             .join(Kasutajagrupp.kasutajagrupp_oigused)
             .filter(sa.literal(permission).startswith(Kasutajagrupp_oigus.nimi))
             .filter(Kasutajagrupp_oigus.bitimask.op('&')(perm_bit)==perm_bit)
             )
        cnt = q.scalar()
        rc = bool(cnt)
        #log_query(q)
        #log.debug('TULEMUS:%s %s' % (permission, rc))
        return rc

    def get_rollitegelejad(self):
        """Ametnikud, kellel on rolli järgi õigus selliste ülesannetega tegeleda.
        """
        aine_kood = self.aine_kood
        testiliigikoodid = [self.testiliik_kood]

        today = date.today()
        q = Kasutajaroll.queryR.\
            filter(Kasutajaroll.kasutajagrupp_id.in_(Kasutajagrupp.ainegrupid)).\
            filter(Kasutajaroll.kehtib_alates<=today).\
            filter(Kasutajaroll.kehtib_kuni>=today)

        if aine_kood:
            # kui ainet pole sisestatud, siis lubame kõiki ligi 
            q = q.filter(Kasutajaroll.aine_kood==aine_kood)
        q = q.join(Kasutajaroll.kasutaja)\
            .options(sa.orm.contains_eager(Kasutajaroll.kasutaja))
        q = q.join(Kasutajaroll.kasutajagrupp)\
            .options(sa.orm.contains_eager(Kasutajaroll.kasutajagrupp))

        li = []
        for r in q.all():
            if r.kasutajagrupp.id == const.GRUPP_OSASPETS:
                if r.testiliik_kood != self.testiliik_kood:
                    continue
            li.append(r)

        # lisame administraatorid ka
        #g_admin = Kasutajagrupp.get_by_kood(const.GRUPP_ADMIN)
        #for r in g_admin.kasutajarollid:
        #    li.append(r)

        return li

    def get_kasutajad(self):
        """Leitakse loetelu kasutajatest, kellel on sellele testile õiguseid.
        Iga kasutaja esineb loetelus üheainsa korra.
        Igale kasutajale tehakse atribuut "testigrupid", mis
        sisaldab tema kasutajagruppe selle testi suhtes.
        """
        li = []
        for isik in self.testiisikud:
            kasutaja = isik.kasutaja
            if kasutaja not in li:
                kasutaja.testigrupid = []
                li.append(kasutaja)
            grupp = isik.kasutajagrupp
            if grupp not in kasutaja.testigrupid:
                kasutaja.testigrupid.append(grupp)

        for roll in self.get_rollitegelejad():
            kasutaja = roll.kasutaja
            if kasutaja not in li:
                kasutaja.testigrupid = []
                li.append(kasutaja)
            grupp = roll.kasutajagrupp
            if grupp not in kasutaja.testigrupid:
                kasutaja.testigrupid.append(grupp)
        return li

    @property 
    def staatus_nimi(self):
        return Klrida.get_str('T_STAATUS', str(self.staatus))

    def post_create(self):
        if self.staatus is None:
            self.staatus = const.T_STAATUS_KOOSTAMISEL

    def save_encrypted(self, encrypted_password, encrypted_data, isikukoodid):
        # salvestame krüptitud testi sisu
        if not self.salatest:
            self.salatest = Salatest(test=self)

        self.salatest.parool = encrypted_password
        self.salatest.data = encrypted_data

        # salvestame andmebaasis ka isikud, kes saavad lahti krüptida
        li = [rcd.kasutaja_id for rcd in self.salatest.salatestiisikud]
        for ik in isikukoodid:
            kasutaja = Kasutaja.get_by_ik(ik)
            if not kasutaja:
                # ik on asutuse dn
                continue
            try:
                n = li.index(kasutaja.id)
                li.pop(n)
            except ValueError:
                # lisame
                rcd = Salatestiisik(salatest=self.salatest,
                                    kasutaja=kasutaja)
                self.salatest.salatestiisikud.append(rcd)

        # eemaldame vanast ajast jäänud ülearused
        for kasutaja_id in li:
            for rcd in self.salatest.salatestiisikud:
                if rcd.id == kasutaja_id:
                    rcd.delete()
                    break

    # def pack_subrecords(self, delete=True, modified=None):
    #     """Pakitakse kohalikku serverisse viimiseks
    #     ülemad enne alamaid
    #     """
    #     li = []
    #     for to in self.testiosad:
    #         li.extend(to.pack(delete, modified))                   
    #         for alatest in to.alatestid:
    #             li.extend(alatest.pack(delete, modified))
    #             for tp in alatest.testiplokid:
    #                 li.extend(tp.pack(delete, modified))
                      
    #         for ty in to.testiylesanded:
    #             li.extend(ty.pack(delete, modified))
    #             for vy in ty.valitudylesanded:
    #                 li.extend(vy.pack(delete, modified))
    #                 ylesanne = vy.ylesanne
    #                 if ylesanne:
    #                     li.extend(ylesanne.pack(delete, modified))
    #     return li

    def pack_crypt(self):
        """Pakitakse krüptimiseks
        """
        Session.autoflush = False 
        di_y = {}
        li_k = []

        for to in self.testiosad:
            for ty in to.testiylesanded:
                for vy in ty.valitudylesanded:
                    ylesanne = vy.ylesanne
                    if ylesanne:
                        di_y[ylesanne.id] = ylesanne.pack_crypt()
                        ylesanne.set_salastatud(const.SALASTATUD_T_KRYPTITUD)
                    li_k.extend(vy.pack())
                li_k.extend(ty.pack())

            for kv in to.komplektivalikud:
                for k in kv.komplektid:
                    for testifail in k.testifailid:
                        li_k.extend(testifail.pack())

        Session.autoflush = True
        return [di_y, li_k]

    def depack_crypt(self, li):
        """Pakitud andmed on list.
        Listi esimene element on dict, mille võti on ylesanne.id 
        ja väärtus on selle ülesande pakitud andmed (vt ylesanne.depack()).
        Listi teine element on list testi kirjetest 
        (Testifail, Testiylesanne, Valitudylesanne)
        """
        # kontrollime, et on õige formaat
        assert len(li) == 2

        # komplektide id list
        li_k_id = []
        # testiosade id list
        li_to_id = []
        # koostame kontrolli mõttes listi selle testi andmetest
        for to in self.testiosad:
            li_k_id.extend([k.id for k in to.komplektid])
            li_to_id.append(to.id)

        # pakime testi kirjed lahti
        for di in li[1]:
            cls_name = di.pop('class')
            if cls_name == 'Testifail' and di['komplekt_id'] in li_k_id or \
               cls_name == 'Testifailimarkus' or \
               cls_name == 'Valitudylesanne' and di['komplekt_id'] in li_k_id or \
               cls_name == 'Testiylesanne' and di['testiosa_id'] in li_to_id:
                cls = eval(cls_name)
                item = cls.unpack(**di)
                item.logging = False
                item.flush()
            else:
                raise Exception('Pakis on valed andmed (%s)' % cls_name)

        # pakime ylesanded lahti
        from eis.model.ylesanne import Ylesanne
        di_y = li[0]
        for ylesanne_id, ylesanne_data in di_y.items():
            log.debug('depack ylesanne %d' % ylesanne_id)
            ylesanne = Ylesanne.get(ylesanne_id)
            ylesanne.depack_crypt(ylesanne_data)
            ylesanne.set_salastatud(const.SALASTATUD_LOOGILINE)

    @classmethod
    def gen_avalik_id(cls):
        "Avaliku vaate testi ID genereerimine"
        return Session.execute(sa.Sequence('test_jagatudtoo_id_seq'))
            
    def copy(self):
        di = {}
        if self.testityyp in (const.TESTITYYP_AVALIK, const.TESTITYYP_TOO):
            # avaliku vaate testidel on suured ID
            di['id'] = self.gen_avalik_id()
        cp = EntityHelper.copy(self, ignore=['tookogumik_id'], **di)
        Session.autoflush = False # integrity errori pärast
        cp.logging = False
        cp.nimi = 'Koopia ' + (cp.nimi or '')
        self.copy_subrecords(cp, ['testiosad',
                                  'testitasemed',
                                  'testikursused',
                                  'tagasisidefailid',
                                  'tagasisidevormid',
                                  'trans'])
        tts = self.testitagasiside
        if tts:
            cp.testitagasiside = tts.copy(ignore=['test_id'])
        ek = self.eristuskiri
        if ek:
            cp.eristuskiri = ek.copy(ignore=['test_id'])
        cp.staatus = const.T_STAATUS_KOOSTAMISEL
        Session.autoflush = True
        return cp

    def _on_testiisik(self, kasutaja_id, kasutajagrupp_id):
        """Kontrollitakse, kas isik on juba antud rollis testiisik.
        """
        for isik in self.testiisikud:
            if isik.kasutaja_id == kasutaja_id \
                    and isik.kasutajagrupp_id == kasutajagrupp_id:
                return isik
        return False

    def add_testiisik(self, kasutajagrupp_id):
        """Jooksev kasutaja lisatakse testiga seotud isikuks
        """
        g = Kasutajagrupp.get(kasutajagrupp_id)
        isik = Testiisik(kasutaja_id=usersession.get_user().id,
                         kasutajagrupp=g,
                         test=self)
        self.testiisikud.append(isik)    
    
    def get_testimiskord(self):
        if len(self.testimiskorrad) > 0:
            return self.testimiskorrad[0]

    def give_testimiskord(self):
        from eis.model.testimine import Testimiskord

        tk = self.get_testimiskord()
        if not tk:
            tk = Testimiskord(test=self, tahis='T')
            self.testimiskorrad.append(tk)
        return tk

    def get_testiosa(self):
        if len(self.testiosad) > 0:
            return self.testiosad[0]

    def give_testiosa(self):
        from .testiosa import Testiosa
        to = self.get_testiosa()
        if to is None:
            if self.testityyp == const.TESTITYYP_KONS:
                vastvorm_kood = const.VASTVORM_KONS
            else:
                vastvorm_kood = const.VASTVORM_KE
            to = Testiosa(test=self, 
                          tahis='K',
                          nimi='Testiosa',
                          vastvorm_kood=vastvorm_kood,
                          naita_max_p=True)
            if self.diagnoosiv:
                to.lopetatav = False
                to.katkestatav = False
                to.pos_yl_list = const.POS_NAV_HIDDEN
                to.peida_yl_pealkiri = True
                to.naita_max_p = False
        return to

    def get_valimata_ylesanded(self):
        """Leitaske valimata ülesanded
        """
        ylesanded = []
        for testiosa in self.testiosad:
            for ty in testiosa.testiylesanded:
                for vy in ty.valitudylesanded:
                    if not vy.ylesanne_id:
                        ylesanded.append(vy)
        return ylesanded

    def arvuta_pallid(self, arvuta_ty=True):
        def _add_none(p1, p2):
            if p1 is None or p2 is None:
                return None
            else:
                return p1 + p2
        max_pallid = 0
        kursuspallid = dict()
        is_max_p = True
        for testiosa in self.testiosad:
            to_max_pallid, to_kursuspallid = testiosa.arvuta_pallid(arvuta_ty=arvuta_ty)
            max_pallid = _add_none(max_pallid, to_max_pallid)
            for kursus, pallid in to_kursuspallid.items():
                if kursus in kursuspallid:
                    kursuspallid[kursus] = _add_none(kursuspallid[kursus], pallid)
                else:
                    kursuspallid[kursus] = pallid
                if pallid is None:
                    is_max_p = False
            if max_pallid is None:
                is_max_p = False
        if kursuspallid:
            if is_max_p:
                max_pallid = max(max_pallid, max(kursuspallid.values()))
            else:
                max_pallid = None
        #if self.protsendita:
        #    self.max_pallid = None
        #else:
        rveksam = self.rveksam
        if rveksam and rveksam.kuni:
            # erand ingl k C1 eksami jaoks, kus testi max pallid ei ole testiosade max pallide summa
            max_pallid = rveksam.kuni
        if self.max_pallid != max_pallid:
            self.max_pallid = max_pallid
        for kursus, pallid in kursuspallid.items():
            r = self.give_testikursus(kursus)
            r.max_pallid = pallid
        for r in self.testikursused:
            if r.kursus_kood and r.kursus_kood not in list(kursuspallid.keys()):
                r.max_pallid = None
        return max_pallid

    @property
    def lavi_pallid(self):
        if self.lavi_pr and self.max_pallid:
            return round(self.max_pallid * self.lavi_pr / 100)

    def get_vahemik_by_protsent(self, protsent):
        "Leiab protsendi järgi vahemiku järjekorranumbri, alguse ja lõpu"
        vahemikulaved = list(map(int, self.tulemuste_vahemikud_pr.split(','))) # [1,50,60,76,91]
        vahemikulaved.append(101)
        for n in range(5,0,-1):
            vahemik_algus = vahemikulaved[n-1]
            if protsent + .000001 >= vahemik_algus:
                vahemik_lopp = vahemikulaved[n] - 1
                return n, vahemik_algus, vahemik_lopp
        # kõige madalam vahemik
        return 0, 0, vahemikulaved[0]

    def get_vahemiknimi_by_protsent(self, protsent):
        n, vahemik_algus, vahemik_lopp = self.get_vahemik_by_protsent(protsent)
        return const.VAHEMIK[n]

    def tulemuste_vahemikud_str(self):
        if self.tulemuste_vahemikud_pr:
            prev = 0
            li = []
            for k in self.tulemuste_vahemikud_pr.split(','):
                k = int(k)
                s = '%d-%d' % (prev, k-1)
                li.append(s)
                prev = k
            s = '%d-100' % prev
            li.append(s)
            return '; '.join(li)

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase, tyyp=None):
        if self.logging:
            test_id = self.id
            if liik and len(liik) > 256:
                liik = liik[:256]
            logi = Testilogi(kasutaja_id=usersession.get_user().id or None,
                             liik=liik,
                             vanad_andmed=vanad_andmed,
                             uued_andmed=uued_andmed,
                             tyyp=tyyp)
            if test_id:
                logi.test_id = test_id
            else:
                logi.test = self
                
    def calc_yhisosa(self):       
        from .valitudylesanne import Valitudylesanne
        from eis.model.ylesanne.tulemus import Tulemus
        
        diff = 1e-12
        def find_yhisosa(kursus):
            errors = []
            data = dict()
            log.debug('kursus %s' % (kursus))
            for ta in self.testiosad:
                for alatest in ta.alatestid:
                    if alatest.kursus_kood == kursus:
                        for ty in alatest.testiylesanded:
                            total = 0
                            if ty.yhisosa_kood:
                                typref = '%s %s: ' % (kursus, ty.tahis)
                                q = SessionR.query(Valitudylesanne.id,
                                                  Valitudylesanne.komplekt_id,
                                                  Valitudylesanne.koefitsient,
                                                  Valitudylesanne.ylesanne_id,
                                                  Valitudylesanne.seq,
                                                  Tulemus.yhisosa_kood,
                                                  Tulemus.max_pallid,
                                                  Tulemus.max_pallid_arv).\
                                    filter(Valitudylesanne.testiylesanne_id==ty.id).\
                                    join((Tulemus, Tulemus.ylesanne_id==Valitudylesanne.ylesanne_id)).\
                                    filter(Tulemus.yhisosa_kood!=None)
                                vy_data = dict()
                                ty_data = dict()
                                for vy_id, komplekt_id, koefitsient, ylesanne_id, vy_seq, t_kood, t_pallid, t_pallid_arv in q.all():
                                    pallid = (t_pallid or t_pallid_arv or 0) * koefitsient
                                    key = komplekt_id, t_kood, vy_seq
                                    log.debug('  VY %s, Y %s, YK %s - pallid %s, arvut %s, koef %s - kokku %s p' % \
                                              (vy_id, ylesanne_id, t_kood, t_pallid, t_pallid_arv, koefitsient, pallid))
                                    if key in vy_data:
                                        errors.append(typref + _("ülesandes {id} esineb kood {s} korduvalt").format(id=ylesanne_id, s=t_kood))
                                    else:
                                        vy_data[key] = pallid
                                        if t_kood in ty_data and abs(ty_data[t_kood]-pallid) > diff:
                                            errors.append(typref + \
                                                          _("ülesandes {s1} annab koodiga {s2} küsimus eri komplektides erineval hulgal palle (ühes {p1}p, teises {p2}p)").format(
                                                              s1=ty.yhisosa_kood, s2=t_kood, p1=fstr(ty_data[t_kood]), p2=fstr(pallid)))
                                        else:
                                            ty_data[t_kood] = pallid
                                for t_kood in ty_data:
                                    pallid = ty_data[t_kood]
                                    total += pallid
                                    key = ty.yhisosa_kood, t_kood
                                    if key in data:
                                        errors.append(typref + _("ülesande {s1} küsimus {s2} esineb testis mitmes ülesandes").format(
                                            s1=ty.yhisosa_kood, s2=t_kood))
                                    else:
                                        data[key] = ty_data[t_kood]
                                        log.debug('%s,%s=%s' % (ty.yhisosa_kood, t_kood, ty_data[t_kood]))
                                log.debug('TY %s yhisosa %s' % (ty.tahis, total))
                            ty.yhisosa_max_pallid = total
            return data, errors

        data = []
        errors = []

        kpallid = set()
        for r in self.testikursused:
            kursus = r.kursus_kood
            if kursus:
                k_data, k_errors = find_yhisosa(kursus)
                data.append((kursus, k_data))
                errors = errors + k_errors
                kpallid.add(r.max_pallid)

        if len(kpallid) > 1:
            errors.append(_("Eri kursustel on erinev max pallide arv"))

        total = None
        cnt = len(data)
        for i in range(cnt):
            for j in range(cnt):
                if i < j:
                    kursus1, data1 = data[i]
                    kursus2, data2 = data[j]
                    total = 0
                    for key in data1:
                        if key not in data2:
                            errors.append(_("Kursusel {s1} puudub ülesande {s2} küsimus {s3}").format(
                                s1=kursus2, s2=key[0], s3=key[1]))
                        else:
                            pallid1 = data1.get(key)
                            pallid2 = data2.get(key)
                            total += pallid1
                            if abs(pallid1 - pallid2) > diff:
                                errors.append(_("Ülesande {s1} küsimus {s2} annab erineva arvu palle (kursusel {s3} - {p3}p, kursusel {s4} - {p4}p)").format(
                                    s1=key[0], s2=key[1], s3=kursus1, p3=fstr(pallid1), s4=kursus2, p4=fstr(pallid2)))
                    for key in data2:
                        if key not in data1:
                            errors.append(_("Kursusel {s1} puudub ülesande {s2} küsimus {s3}").format(
                                s1=kursus1, s2=key[0], s3=key[1]))

        # kontrollime, et hindamiskogumite kursused vastavad alatestide kursustele
        vigased_hk = set()
        for ta in self.testiosad:
            for alatest in ta.alatestid:
                for ty in alatest.testiylesanded:
                    hk = ty.hindamiskogum
                    if hk and not hk.vaikimisi and hk.kursus_kood != alatest.kursus_kood:
                        vigased_hk.add(hk.tahis)
        if len(vigased_hk):
            errors.append(_("Hindamiskogumites ({s}) on vastuolu, palun salvestada need uuesti").format(
                s=', '.join(vigased_hk)))
            
        if errors:
            return '<br/>\n'.join(errors)

        if self.yhisosa_max_pallid != total:
            self.yhisosa_max_pallid = total

    def count_tahemargid(self):
        #print('TEST %d' % self.id)
        for lang in self.keeled:        
            tts = self.testitagasiside
            if tts:
                tts.count_tahemargid(lang)
            for osa in self.testiosad:
                for np in osa.normipunktid:
                    np.count_tahemargid(lang)
        self.sum_tahemargid()
        
    def sum_tahemargid(self):
        "Arvutatakse kokku tähemärgid"
        for lang in self.keeled:
            self.sum_tahemargid_lang(lang)

    def sum_tahemargid_lang(self, lang):
        """Loetakse kokku testis olevad tähemärgid tekstiväljadelt,
        et selle põhjal saaks arvestada toimetajate ja tõlkijate töötasu.
        """
        cch = CountChar(self.lang, lang)
        total = 0

        # test
        tr = cch.tran(self, True)
        total += cch.count(tr.nimi, False)
            
        # testitagasiside
        tts = self.testitagasiside
        if tts:
            tr2 = cch.tran(tts)
            if tr2:
                total += tr2.tahemargid or 0

        # testiosad
        for osa in self.testiosad:
            for alatest in osa.alatestid:
                tr2 = cch.tran(alatest)
                if tr2:
                    total += cch.count(tr2.nimi, False) + \
                             cch.count(tr2.sooritajajuhend, False)
            for ty in osa.testiylesanded:
                tr2 = cch.tran(ty)
                if tr2:
                    total += cch.count(tr2.nimi, False)
                    
            tr2 = cch.tran(osa)
            if tr2:
                total += cch.count(tr2.nimi, False) + \
                         cch.count(tr2.alustajajuhend, False) + \
                         cch.count(tr2.sooritajajuhend, False)

            for ag in osa.alatestigrupid:
                tr2 = cch.tran(ag)
                if tr2:
                    total += cch.count(tr2.nimi, False)

            for yg in osa.ylesandegrupid:
                tr2 = cch.tran(yg)
                if tr2:
                    total += cch.count(tr2.nimi, True)
            
            for ng in osa.nsgrupid:
                tr2 = cch.tran(ng)
                if tr2:
                    total += cch.count(tr2.nimi, True)

            for np in osa.normipunktid:
                tr2 = cch.tran(np, True)
                total += tr2.tahemargid or 0

        tr.tahemargid = total
        return total
