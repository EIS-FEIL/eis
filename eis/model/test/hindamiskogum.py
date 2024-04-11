"Testi andmemudel"
from eis.model.entityhelper import *

class Hindamiskogum(EntityHelper, Base):
    """Ülesannete hindamiskogum.
    Hindamiskogumil on sisuline tähendus eeskätt kirjalikus testis (e-test või p-test),
    kuna hindamiskogumite kaupa antakse kirjaliku testi ülesandeid hindajatele hindamiseks.
    Kui hindamiskogumid on määratud suulises e-testis, siis antakse läbiviijale võimalus
    valida hindamiskogumit, aga ta hindab ikkagi soorituse kõik hindamiskogumid.
    Hindamiskogumite kaupa rühmitatakse ka süsteemi sees soorituse hindamisolekuid ja 
    seetõttu peab andmebaasis tegelikult igasuguse testi iga testiülesanne 
    kuuluma hindamiskogumisse. Kui kasutaja pole testiülesannet hindamiskogumisse määranud, 
    siis paigutatakse see automaatselt loodavasse vaikimisi hindamiskogumisse. 
    Ühe hindamiskogumi kõik ülesanded peavad kuuluma samasse komplektivalikusse.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    testiosa_id = Column(Integer, ForeignKey('testiosa.id'), index=True, nullable=False) # viide testiosale
    testiosa = relationship('Testiosa', foreign_keys=testiosa_id, back_populates='hindamiskogumid')
    tahis = Column(String(10)) # tähis (vaikimisi hindamiskogumi korral võib olla NULL)
    nimi = Column(String(100)) # nimetus
    staatus = Column(Integer, sa.DefaultClause('0'), nullable=False) # olek: kui kogum sisaldab ülesandeid, siis 1=const.B_STAATUS_KEHTIV, muidu 0=const.B_STAATUS_KEHTETU.
    vaikimisi = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas on vaikimisi (automaatselt loodud) hindamiskogum
    kursus_kood = Column(String(10)) # lai või kitsas (matemaatika korral), klassifikaator KURSUS
    hindamine_kood = Column(String(10)) # hindamise liik, klassifikaator HINDAMINE
    kahekordne_hindamine = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas on kahekordne hindamine (mitte-valimi korral)
    kahekordne_hindamine_valim = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas on kahekordne hindamine (valimi korral)   
    paarishindamine = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas kahekordne hindamisel määratakse hindajate paarid või eraldi hindajad (paarishindamine on kasutusel ainult kirjaliku kahekordse hindamise korral)
    kontrollijaga_hindamine = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas on kahe hindajaga ühekordne hindamine (üks hindab, teine kontrollib)
    on_digiteerimine = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kirjaliku p-testi skannimise korral (kui sisestuskogumis on määratud, et skannitakse): kas vastused digiteeritakse (tuvastatakse) või hõivatakse ainult pilt
    on_hindamisprotokoll = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kirjaliku p-testi sisestamise korral: kas sisestatakse hindamisprotokoll või sisestatakse vastused
    erinevad_komplektid = Column(Boolean, sa.DefaultClause('0'), nullable=False) # hindamisprotokolliga p-testi korral: False - kõigil komplektidel on toorpunktid samad, printida kõigi komplektide kohta ühine hindamisprotokoll; True - eri komplektides on toorpunktid erinevad, tuleb printida iga komplekti jaoks eraldi hindamisprotokoll
    arvutihinnatav = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas kõik testiülesanded on arvutihinnatavad
    on_markus_sooritajale = Column(Boolean) # kas hindaja saab hindamisel sooritajale märkusi kirjutada
    hindajate_erinevus = Column(Float) # lubatud erinevus hindajate vahel protsentides hindamiskogumi maksimaalse võimaliku hindepallide arvu suhtes
    hindamine3_loplik = Column(Boolean, sa.DefaultClause('0')) # mida tehakse III hindamise tulemusega: true - III hindamise tulemus on lõplik tulemus; false - leitakse I,II,III hindamiste seast lähim paar ja kui ka selle paari hindamiserinevus on suur, siis tehakse IV hindamine
    max_pallid = Column(Float, sa.DefaultClause('0'), nullable=False) # hindamiskogumisse kuuluvate testiülesannete pallide summa (uuendatakse testiülesande salvestamisel ning hindamiskogumisse määramisel)
    arvutus_kood = Column(String(10), sa.DefaultClause('k'), nullable=False) # hindamistulemuse arvutusviis, klassifikaator ARVUTUS: k=const.ARVUTUS_KESKMINE - hindajate punktide keskmine; s=const.ARVUTUS_SUMMA - kahe hindaja punktide summa (eeldab kahekordset hindamist)
    oma_kool_tasuta = Column(Boolean, sa.DefaultClause('0'), nullable=False) # true - hindaja ja intervjueerija tasu arvestatakse ainult nende sooritajate eest, kes ei ole läbiviija oma kooli õpilased; false - tasu arvestatakse kõigi hinnatud tööde eest
    tasu = Column(Float) # kogumi hindamise tasu (korrutatakse sooritajate arvuga)
    intervjuu_lisatasu = Column(Float) # kogumi intervjueerimise eest hindamistasule juurde makstav tasu hindaja-intervjueerijale (korrutatakse sooritajate arvuga ja lisatakse hindaja tasule)
    intervjuu_tasu = Column(Float) # kogumi intervjueerimise tasu intervjueerijale, kes ei ole hindaja (korrutatakse sooritajate arvuga)
    sisestuskogum_id = Column(Integer, ForeignKey('sisestuskogum.id'), index=True) # viide sisestuskogumile, kui mõni sisestuskogum sisaldab antud hindamiskogumit
    sisestuskogum = relationship('Sisestuskogum', foreign_keys=sisestuskogum_id, back_populates='hindamiskogumid')
    komplektivalik_id = Column(Integer, ForeignKey('komplektivalik.id'), index=True, nullable=False) # viide komplektivalikule
    komplektivalik = relationship('Komplektivalik', foreign_keys=komplektivalik_id, back_populates='hindamiskogumid') 
    testiylesanded = relationship('Testiylesanne', order_by='Testiylesanne.alatest_seq, Testiylesanne.seq', back_populates='hindamiskogum')
    valitudylesanded = relationship('Valitudylesanne', order_by='Valitudylesanne.testiylesanne_id,Valitudylesanne.seq', back_populates='hindamiskogum')    
    labiviijad = relationship('Labiviija', back_populates='hindamiskogum')
    hindamisolekud = relationship('Hindamisolek', back_populates='hindamiskogum')
    hindamiskriteeriumid = relationship('Hindamiskriteerium', order_by='Hindamiskriteerium.seq', back_populates='hindamiskogum')
    tagastusymbrikuliigid = relationship('Tagastusymbrikuliik', secondary='tagastusymbrikuliik_hk', back_populates='hindamiskogumid')
    _parent_key = 'testiosa_id'
    __table_args__ = (
        sa.UniqueConstraint('testiosa_id','tahis'),
        )

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .testiosa import Testiosa

        testiosa = self.testiosa or self.testiosa_id and Testiosa.get(self.testiosa_id)
        if testiosa:
            testiosa.logi('Hindamiskogum %s (%s) %s' % (self.id, self.tahis, liik), vanad_andmed, uued_andmed, logitase)

    @property
    def on_kriteeriumid(self):
        for r in self.hindamiskriteeriumid:
            return True
        return False

    def post_create(self):
        self.gen_tahis()

    def gen_tahis(self):
        from .testiosa import Testiosa

        if not self.tahis:
            testiosa = self.testiosa or Testiosa.get(self.testiosa_id)
            for n in range(1,1000):
                tahis = '%02d' % n
                for rcd in testiosa.hindamiskogumid:
                    if rcd.tahis == tahis:
                        tahis = None
                        break
                if tahis:
                    self.tahis = tahis
                    break

    def arvuta_pallid(self, lotv):
        arvutihinnatav = True
        max_pallid = 0
        in_use = False

        kriteeriumid = list(self.hindamiskriteeriumid)
        if kriteeriumid:
            for krit in kriteeriumid:
                max_pallid += (krit.max_pallid or 0) * krit.kaal

        if lotv:
            kvalikud = dict()
            for vy in self.valitudylesanded:
                in_use = True
                ylesanne = vy.ylesanne
                if ylesanne is not None:
                    if ylesanne.max_pallid or kriteeriumid:
                        #max_pallid += ylesanne.max_pallid
                        arvutihinnatav &= ylesanne.arvutihinnatav or False
                        log.debug('y%d.arvutihinnatav=%s, hk%s.arvutihinnatav=%s' % (ylesanne.id, ylesanne.arvutihinnatav, self.id, arvutihinnatav))
                        komplekt = vy.komplekt
                        kvalik_id = komplekt.komplektivalik_id
                        if kvalik_id not in kvalikud:
                            kvalikud[kvalik_id] = dict()
                        if komplekt.id not in kvalikud[kvalik_id]:
                            kvalikud[kvalik_id][komplekt.id] = 0
                        kvalikud[kvalik_id][komplekt.id] += ylesanne.max_pallid or 0

            if not kriteeriumid:
                for kvalik_id in kvalikud:
                    max_pallid += max(kvalikud[kvalik_id].values())
        else:
            for ty in self.testiylesanded:
                in_use = True
                if ty.max_pallid or kriteeriumid:
                    if not kriteeriumid:
                        max_pallid += ty.max_pallid
                    # loeme hindamiskogumi arvutihinnatavaks siis, kui kõik palle andvad ülesanded on arvutihinnatavad
                    # võib olla nii, et kõik päris ülesanded on arvutihinnatavad, 
                    # aga lõpus on tagasiside küsimise ülesanne, mis annab 0p, aga ei ole arvutihinnatav
                    arvutihinnatav &= ty.arvutihinnatav or False
        staatus = in_use and const.B_STAATUS_KEHTIV or const.B_STAATUS_KEHTETU
        if self.staatus != staatus:
            self.staatus = staatus
        if self.max_pallid != max_pallid:
            self.max_pallid = max_pallid
        if self.arvutihinnatav != arvutihinnatav:
            self.arvutihinnatav = arvutihinnatav

    def get_hindamistase(self, valimis, toimumisaeg=None):
        """Leitakse hindamisolekute vajalik algne hindamistase (1 või 2)
        Kasutatakse ainult KIRJALIKU testi korral, sest suulise testi
        hindamistaseme määrab toimumisaeg.
        """
        testiosa = self.testiosa
        if toimumisaeg and testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP)\
               and not testiosa.test.on_tseis:
            # kui suulise testi korral on toimumisajale ette nähtud kaks hindajat, 
            # siis on kahekordne hindamine, muidu yhekordne
            #if ta.hindaja1_maaraja and (ta.hindaja2_maaraja or ta.hindaja_v_maaraja):
            if toimumisaeg.hindaja1_maaraja and toimumisaeg.hindaja2_maaraja:
                hindamistase = const.HINDAJA2
            else:
                hindamistase = const.HINDAJA1
            
        elif testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I, const.VASTVORM_SH) and \
                self.arvutihinnatav:
            # arvutihinnatav e-test ei vaja hindamist ega sisestamist
            hindamistase = const.HTASE_ARVUTI
        elif self.on_digiteerimine and \
                self.arvutihinnatav:
            # arvutihinnatav p-test ei vaja hindamist ega sisestamist
            hindamistase = const.HTASE_ARVUTI
        else:
            # vajab hindamist või sisestamist
            if valimis:
                kkh = self.kahekordne_hindamine_valim
            else:
                kkh = self.kahekordne_hindamine
            if kkh:
                # vajab kahekordset hindamist
                hindamistase = const.HINDAJA2
            else:
                hindamistase = const.HINDAJA1
        return hindamistase

    def get_komplektivalik(self):
        """Yhe hindamiskogumi kõik ylesanded peavad kuuluma samasse komplektivalikusse.
        Leiame selle komplektivaliku.
        """
        return self.komplektivalik

    def get_testiylesanded(self, komplekt):
        testiosa = self.testiosa
        if not testiosa.lotv:
            li = list(self.testiylesanded)
        elif komplekt:
            # lõtv struktuur
            komplektis_ty_id = komplekt.get_testiylesanded_id()
            kogumis_ty_id = [vy.testiylesanne_id for vy in self.valitudylesanded if vy.ylesanne_id]
            li = [ty for ty in testiosa.testiylesanded \
                  if ty.id in kogumis_ty_id \
                  and ty.id in komplektis_ty_id]
        else:
            # lõtv struktuur, aga komplekti pole veel valitud
            li = []
        return li

    def tk_tasu(self, grupp_id):
        "Aktil kasutamiseks - leitakse 1 töö tasu"
        if grupp_id == const.GRUPP_INTERVJUU:
            return self.intervjuu_tasu or 0
        elif grupp_id == const.GRUPP_HIND_INT:
            return self.intervjuu_lisatasu or 0
        else:
            return self.tasu or 0
    
