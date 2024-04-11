"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import Klrida
from eis.model.test import Test

from .statistikaraport import Statistikaraport
from .testikonsultatsioon import Testikonsultatsioon
from .toimumisaeg import Toimumisaeg
from .regkoht_kord import Regkoht_kord
_ = usersession._

class Testimiskord(EntityHelper, Base):
    """Testimiskord (ühel testil võib olla mitu testimiskorda)
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tahis = Column(String(10), nullable=False) # tähis
    nimi = Column(String(256)) # nimetus (malli korral)
    aasta = Column(Integer) # aastaarv, statistika päringute jaoks
    alates = Column(Date) # varaseim toimumisaja algus, dubleeritud otsingute optimeerimiseks
    kuni = Column(Date) # hiliseim toimumisaja lõpp, dubleeritud otsingute optimeerimiseks
    reg_sooritaja = Column(Boolean) # kas sooritaja võib ise end EISi kasutajaliideses registreerida
    reg_sooritaja_alates = Column(Date) # sooritaja poolt EISis ise registreerimise algus
    reg_sooritaja_kuni = Column(Date) # sooritaja poolt EISis ise registreerimise lõpp
    reg_xtee = Column(Boolean) # kas sooritaja võib ise end eesti.ee portaali kaudu registreerida
    reg_xtee_alates = Column(Date) # sooritaja poolt eesti.ee kaudu ise registreerimise algus
    reg_xtee_kuni = Column(Date) # sooritaja poolt eesti.ee kaudu ise registreerimise lõpp
    reg_kool_ehis = Column(Boolean) # kas õppeasutus võib EHISe kaudu sooritajaid registreerida
    reg_kool_eis = Column(Boolean) # kas õppeasutus võib EISi kaudu sooritajaid registreerida
    reg_kool_valitud = Column(Boolean) # kas õppeasutus võib EISi kaudu sooritajaid registreerida (lubatud õppeasutuste loetelu on Innove poolt valitud)
    reg_kool_alates = Column(Date) # õppeasutuste poolt registreerimise algus
    reg_kool_kuni = Column(Date) # õppeasutuste poolt registreerimise lõpp
    reg_ekk = Column(Boolean) # kas eksamikeskus võib sooritajaid registreerida
    korduv_reg_keelatud = Column(Boolean) # kas on keelatud registreerida isikuid, kes on sama testi mõnele teisele testimiskorrale juba olnud registreeritud
    cae_eeltest = Column(Boolean) # kas registreerimiseks on vajalik CAE eeltesti sooritamine (rahvusvahelisele ingl k eksami korral)
    reg_piirang = Column(String(3)) # registreerimise piirang: H=const.REGPIIRANG_H - haridustöötajad
    erivajadus_alates = Column(Date) # õppeasutuste poolt väljaspool registreerimisaega erivajaduste taotluste sisestamise algus
    erivajadus_kuni = Column(Date) # õppeasutuste poolt väljaspool registreerimisaega erivajaduste taotluste sisestamise lõpp
    reg_kohavalik = Column(Boolean) # kas registreerimisel on võimalik valida soorituskoht
    reg_voorad = Column(Boolean) # kas kool võib sooritajaks registreerida neid, kes ei ole oma kooli õpilased
    kordusosalemistasu = Column(Float) # kordusosalemistasu
    osalemistasu = Column(Float) # osalemistasu
    sooritajad_peidus_kuni = Column(DateTime) # aeg, enne mida koolid ei näe sooritajate identiteete (kui puudub, siis näevad)
    korraldamata_teated = Column(Boolean, sa.DefaultClause('1'), nullable=False) # kas saata koolile automaatseid korraldamise meeldetuletusi
    arvutada_hiljem = Column(Boolean) # kas tulemuse arvutamine peale testi sooritamist ära jätta (jõudluse huvides)
    tulemus_kinnitatud = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas tulemused on kinnitatud
    tulemus_kontrollitud = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas tulemused on kontrollitud; kui on kontrollitud, siis saab ainult administraator tulemusi ja statistikat arvutada, ainespetsialist ei saa   
    statistika_arvutatud = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas tulemuste statistika on arvutatud
    osalemise_naitamine = Column(Boolean, sa.DefaultClause('1')) # kas näidata sooritamist lahendajale oma tulemuste all sooritatud testide loetelus (nt eeltestidel osalemist ei soovita näidata)
    prot_vorm = Column(Integer, sa.DefaultClause('0'), nullable=False) # toimumise protokolli vorm: 0=const.PROT_VORM_VAIKIMISI- vaikimisi; 1=const.PROT_VORM_DOKNR - protokoll dok numbritega; 2=const.PROT_VORM_TULEMUS - protokoll tulemusega; 3=const.PROT_VORM_YLTULEMUS - protokoll ülesannete tulemustega; 5=const.PROT_VORM_ALATULEMUS - protokoll alatestide tulemustega
    on_helifailid = Column(Boolean) # kas toimumise protokolli sisestamisel on helifailide laadimise sakk
    on_turvakotid = Column(Boolean) # kas toimumise protokolli sisestamisel avalikus vaates on helifailide laadimise sakk
    analyys_eraldi = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas vastuste analüüs toimub testimiskorra kaupa (või kogu testi kaupa)
    tulemus_koolile = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas kool saab tulemusi vaadata
    tulemus_admin = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas testi administraator saab hiljem oma läbiviidud testis oma kooli õpilaste tulemusi vaadata
    koondtulemus_avaldet = Column(Boolean) # kas koondtulemus on avaldatud
    koondtulemus_aval_kpv = Column(Date) # koondtulemuse avaldamise kuupäev
    alatestitulemused_avaldet = Column(Boolean) # kas alatestide tulemused on avaldatud    
    alatestitulemused_aval_kpv = Column(Date) # alatestide tulemuste avaldamise kuupäev
    ylesandetulemused_avaldet = Column(Boolean) # kas ülesannete tulemused on avaldatud
    ylesandetulemused_aval_kpv = Column(Date) # ülesannete tulemuste avaldamise kuupäev
    aspektitulemused_avaldet = Column(Boolean) # kas aspektide tulemused on avaldatud
    aspektitulemused_aval_kpv = Column(Date) # aspektide tulemuste avaldamise kuupäev    
    ylesanded_avaldet = Column(Boolean) # kas ülesanded ja vastused on avaldatud
    ylesanded_aval_kpv = Column(Date) # ülesannete avaldamise kuupäev
    statistika_aval_kpv = Column(Date) # eksamistatistika avaldamise kuupäev
    statistika_ekk_kpv = Column(Date) # kuupäev, millest alates on eksamistatistika Innove vaates (enne avaldamist üle vaatamiseks)
    testsessioon_id = Column(Integer, ForeignKey('testsessioon.id'), index=True) # viide testsessioonile
    testsessioon = relationship('Testsessioon', foreign_keys=testsessioon_id, back_populates='testimiskorrad')
    testilepingud = relationship('Testileping', back_populates='testimiskord')
    test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False) # viide testile
    test = relationship('Test', foreign_keys=test_id)
    #test = relationship('Test', foreign_keys=test_id, back_populates='testimiskorrad')
    #kiirvalikud = relationship('Kiirvalik', secondary='testimiskord_kiirvalik', back_populates='testimiskorrad') # viide kiirvalikutele, millesse testimiskord kuulub
    vaide_algus = Column(Date) # vaiete esitamise ajavahemiku algus (kui puudub, siis saab vaidlustada kohe peale tulemuste kinnitamist)
    vaide_tahtaeg = Column(Date) # vaiete esitamise ajavahemiku lõpp (kui puudub, siis ei saa üldse vaidlustada)
    on_avalik_vaie = Column(Boolean, sa.DefaultClause('1'), nullable=False) # kas sooritaja saab vaiete esitamise ajavahemikul ise avalikus vaates vaide esitada (false - vaideid saab ainult Innove vaates sisestada, vajalik tasemeeksamitel)
    toimumisajad = relationship('Toimumisaeg', order_by='Toimumisaeg.id', back_populates='testimiskord')
    kool_testikohaks = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas sooritajate õppeasutustest teha automaatselt testikohad
    sisestus_isikukoodiga = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas on võimalik töid ja hindamisprotokolle sisestada isikukoodi järgi
    skeeled = Column(String(60)) # testimiskorra keelte koodid eraldatuna tühikuga
    on_mall = Column(Boolean) # kas testimiskorra andmeid kasutatakse korraldamise mallina teiste testimiskordade loomiseks
    sisaldab_valimit = Column(Boolean) # kas valim on eraldatud testimiskorra siseselt (ilma valimi jaoks eraldi testimiskorda loomata)
    valim_testimiskord_id = Column(Integer, ForeignKey('testimiskord.id'), index=True) # valimi korral viide testimiskorrale, millest valim eraldati ja millelt saab tulemuste arvutamisel lõpptulemusi kopeerida
    valim_testimiskord = relationship('Testimiskord', foreign_keys=valim_testimiskord_id, remote_side=id, back_populates='valimid') # valimi korral viide testimiskorrale, millest valim eraldati ja millelt saab tulemuste arvutamisel lõpptulemusi kopeerida
    valimid = relationship('Testimiskord', back_populates='valim_testimiskord')
    stat_valim = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas on statistikas arvestatav valim (valimi korral); õpilaste tulemuste tabelis (gtbl) kuvatakse konkreetse õpilase tulemuste erinevusi ka nende valimitega, kus stat_valim=False
    tutv_taotlus_alates = Column(Date) # testitööga tutvumise taotlemise esitamise ajavahemiku alguskuupäev
    tutv_taotlus_kuni = Column(Date) # testitööga tutvumise taotlemise esitamise ajavahemiku lõppkuupäev
    tutv_hindamisjuhend_url = Column(String(512)) # hindamisjuhendi URL, lisatakse teatele, mis saadetakse sooritajale, kui tema töö on skannitud
    markus = Column(String(1024)) # selgitus selle kohta, mille jaoks testimiskorda kasutatakse
    piirkonnad = relationship('Piirkond', secondary='piirkond_kord') # viide piirkondadele, kus testi läbi viiakse
    regkohad = relationship('Koht', secondary='regkoht_kord', order_by='Koht.nimi') # viide koolidele, millel on lubatud testile registreerida (kui reg_kool_valitud=true)
    nimekirjad = relationship('Nimekiri', back_populates='testimiskord') 
    sooritajad = relationship('Sooritaja', back_populates='testimiskord')
    konskorrad = relationship('Testikonsultatsioon',
                              order_by='Testikonsultatsioon.id',
                              foreign_keys='Testikonsultatsioon.eksam_testimiskord_id',
                              back_populates='eksam_testimiskord')
    eksamikorrad = relationship('Testikonsultatsioon',
                                order_by='Testikonsultatsioon.id',
                                foreign_keys='Testikonsultatsioon.kons_testimiskord_id',
                                back_populates='kons_testimiskord')
    toimumisprotokollid = relationship('Toimumisprotokoll', back_populates='testimiskord')
    arvutusprotsessid = relationship('Arvutusprotsess', back_populates='testimiskord')
    _parent_key = 'test_id'
    __table_args__ = (
        sa.UniqueConstraint('test_id','tahis'),
        )

    @property
    def prot_tulemusega(self):
        return self.prot_vorm in (const.PROT_VORM_TULEMUS, const.PROT_VORM_YLTULEMUS)   

    @property
    def on_ruumiprotokoll(self):
        """Kas igas testiruumis on oma toimumise protokoll või on testikoha peale üks.
        Üldjuhul on tesitkoha kohta üks protokoll,
        ainult SE ja TE eksamite puhul on igal testiruumil oma protokoll.
        Vastavalt on ka komisjoni esimees kas igas testiruumis eraldi või testikoha peale üks.
        """
        return self.test.on_tseis and not self.prot_tulemusega
    
    @property
    def sooritajad_peidus(self):
        return self.sooritajad_peidus_kuni and self.sooritajad_peidus_kuni > datetime.now()

    @property
    def on_eeltest(self):
        # kas on eeltesti testimiskord
        # eeltesti testimiskorral võib õpetaja alati tulemusi näha, eraldi avaldamist ei toimu
        return self.tahis == 'EELTEST'
   
    def post_create(self):
        self.on_avalik_vaie = True
        self.gen_tahis()

    def gen_tahis_new(self, dflt=None):
        test = self.test or Test.get(self.test_id)
        for n in range(1,1000):
            tahis = '%d' % n
            if dflt and isinstance(dflt, str):
                if n == 1:
                    tahis = dflt
                else:
                    tahis = dflt + tahis
            for tk in test.testimiskorrad:
                if tk.tahis == tahis:
                    tahis = None
                    break
            if tahis:
                return tahis

    def gen_tahis(self):
        if not self.tahis:
            self.tahis = self.gen_tahis_new()

    @property
    def tahised(self):
        return '%s-%s' % (self.test_id, self.tahis)

    @property
    def millal(self):
        buf = ''
        if self.alates:
            buf = self.alates.strftime('%d.%m.%Y')
            if self.kuni:
                kuni = self.kuni.strftime('%d.%m.%Y')
                if kuni != buf:
                    buf += '–' + kuni
        return buf

    def copy_lang(self, t):
        """Kopeerime testilt kõik keeled.
        """
        self.skeeled = t.skeeled

    @property
    def keeled(self):
        if not self.skeeled:
            return []
        return self.skeeled.split()

    def get_keeled(self):
        return self.keeled

    def set_lang_value(self, lang, value):
        keeled = self.get_keeled()
        if lang in keeled and not value:
            # eemaldada
            keeled = [r for r in keeled if r != lang]
            self.skeeled = ' '.join(keeled)
        elif lang not in keeled and value:
            # lisada
            self.skeeled = ' '.join(keeled + lang)

    @property
    def opt_keeled(self):
        return [(lang, Klrida.get_lang_nimi(lang)) for lang in self.get_keeled()]

    def get_piirkonnad_opt(self):
        return [(p.id, p.nimi) for p in self.piirkonnad]

    def get_piirkonnad_id(self):
        """Leitakse kõik piirkondade ning nende alam- ja ylempiirkondade id-d
        """
        li = []
        for p in self.piirkonnad:
            li += p.get_alamad_id() + p.get_ylemad_id()
        return set(li)

    def get_kons_prk(self, piirkond_id=None):
        "Leitakse konsultatsioonide toimumised piirkondade kaupa"
        from eis.lib.helpers import str_from_datetime
        from eis.model.koht import Koht, Ruum, Aadress, Piirkond
        from eis.model.testimine import Testiruum, Testikoht
        q = (SessionR.query(Koht.piirkond_id,
                           Koht.nimi,
                           Aadress.tais_aadress,
                           Ruum.tahis,
                           Testiruum.algus)
             .filter(Testiruum.algus >= datetime.now())
             .join(Testikoht.koht)
             .outerjoin(Koht.aadress)
             .join(Testikoht.testiruumid)
             .outerjoin(Testiruum.ruum)
             .join(Testikoht.toimumisaeg)
             .join((Testikonsultatsioon,
                    sa.and_(Testikonsultatsioon.kons_testimiskord_id==Toimumisaeg.testimiskord_id,
                            Testikonsultatsioon.eksam_testimiskord_id==self.id)))
             )
        if piirkond_id:
            prk = Piirkond.get(piirkond_id)
            alamad_id = prk.get_alamad_id()
            q = q.filter(Koht.piirkond_id.in_(alamad_id))
        q = q.order_by(Koht.nimi,
                       Ruum.tahis,
                       Testiruum.algus)
        data = {}
        for prk_id, koht_nimi, aadress, ruum_tahis, algus in q.all():
            buf = koht_nimi
            if aadress:
                buf += f' ({aadress})'
            if ruum_tahis:
                buf += f' {_("ruum")} {ruum_tahis}'
            buf += ' - ' + str_from_datetime(algus, hour0=False)

            prk = Piirkond.get(prk_id)
            for prk_id in prk.get_ylemad_id():
                if prk_id not in data:
                    data[prk_id] = []
                data[prk_id].append(buf)
        if piirkond_id:
            return data.get(piirkond_id) or []
        return data
    
    @classmethod
    def get_opt(cls, testsessioon_id=None, testiliik_kood=None, test_id=None, testityyp=None):
        """Leitakse testimiskorrad
        """
        if not test_id and not testiliik_kood and not testsessioon_id:
            return []

        q = SessionR.query(Testimiskord.id,
                          Testimiskord.test_id,
                          Testimiskord.tahis, 
                          Test.nimi)
        q = q.join(Testimiskord.test)
        if testityyp:
            q = q.filter(Test.testityyp==testityyp)
        if testsessioon_id:
            q = q.filter(Testimiskord.testsessioon_id==testsessioon_id)
        if test_id:
            q = q.filter(Test.id==int(test_id))
        elif testiliik_kood:
            q = q.filter(Test.testiliik_kood==testiliik_kood)

        items = q.order_by(Test.nimi,Testimiskord.tahis).all()
        return [(tk_id, '%s %d-%s' % (nimi, test_id, tk_tahis)) \
                    for (tk_id, test_id, tk_tahis, nimi) in items]

    def give_toimumisaeg(self, testiosa):
        item = self.get_toimumisaeg(testiosa)
        if not item:
            # kirjalikes e-testides on vaja testiruumi administraatorit
            admin_maaraja = testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE)
            # kirjalikes e-testides on vaikimisi nõutav arvutite registreerimine
            on_arvuti_reg = admin_maaraja or None
            # kirjalikes SE ja TE eksamites on esimehe sisestamine kohustuslik
            esimees_maaraja = testiosa.test.on_tseis and \
                              testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE)
            item = Toimumisaeg(testiosa=testiosa, 
                               testimiskord=self, 
                               admin_maaraja=admin_maaraja,
                               esimees_maaraja=esimees_maaraja,
                               on_arvuti_reg=on_arvuti_reg)
            item.set_tahised()
        return item

    def get_toimumisaeg(self, testiosa):
        for item in self.toimumisajad:
            if testiosa is None or item.testiosa == testiosa:
                return item

    def give_toimumisajad(self, komplektid=False):
        """Luuakse toimumisaegade kirjed.
        """
        test = self.test or Test.get(self.test_id)
        for testiosa in test.testiosad:
            ta = self.give_toimumisaeg(testiosa)
            if komplektid:
                for kvalik in testiosa.komplektivalikud:
                    for k in kvalik.komplektid:
                        if k not in ta.komplektid:
                            ta.komplektid.append(k)
                        
        return self.toimumisajad

    def get_sooritaja(self, kasutaja_id):
        """Leitakse antud kasutaja sooritajakirje sellest testimiskorrast
        """
        from eis.model.testimine import Sooritaja
        return Sooritaja.query.\
            filter_by(kasutaja_id=kasutaja_id).\
            filter_by(testimiskord_id=self.id).\
            first()

    def on_regkoht(self, koht_id):
        # kas on kool on registreerimiseks valitud kool
        q = (SessionR.query(sa.func.count(Regkoht_kord.koht_id))
             .filter(Regkoht_kord.testimiskord_id==self.id)
             .filter(Regkoht_kord.koht_id==koht_id))
        return q.scalar() > 0
    
    def has_permission_s(self, perm_bit, kasutaja_id):
        """Kontrollitakse, kas antud kasutaja saab seda testimiskorda sooritada.
        Tagastatakse: kas saab ja Sooritaja kirje, kui on olemas (test on suunatud)
        """
        from eis.model.testimine import Sooritaja, Nimekiri
        dt = date.today()
        test = self.test
        if test.salastatud:
            return False, None
        if test.staatus != const.T_STAATUS_KINNITATUD:
            return False, None
    
        # kas on .sooritaja kirje olemas?
        q = Sooritaja.query.filter_by(kasutaja_id=kasutaja_id).\
            filter(Sooritaja.testimiskord_id==self.id)

        for rcd in q:
            return True, rcd

        #.sooritaja kirjet polnud
        # kas testi võib ilma suunamiseta igaüks lahendada?
        if test.avaldamistase == const.AVALIK_SOORITAJAD and \
           (test.avalik_alates is None or test.avalik_alates <= dt) and \
           (test.avalik_kuni is None or test.avalik_kuni > dt - timedelta(1)):
            return True, None

        return False, None

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        test = self.test or self.test_id and Test.get(self.test_id)
        if test:
            test.logi('Testimiskord %s (%s) %s' % (self.id, self.tahis, liik), vanad_andmed, uued_andmed, logitase)

    def copy(self, gen_tahis=False):
        test = self.test
        tahis = gen_tahis and self.gen_tahis_new(gen_tahis)
        cp = EntityHelper.copy(self,
                               ignore=['koondtulemus_avaldet',
                                       'koondtulemus_aval_kpv',
                                       'alatestitulemused_avaldet',
                                       'alatestitulemused_aval_kpv',
                                       'ylesandetulemused_avaldet',
                                       'ylesandetulemused_aval_kpv',
                                       'aspektitulemused_avaldet',
                                       'aspektitulemused_aval_kpv',
                                       'ylesanded_avaldet',
                                       'ylesanded_aval_kpv',
                                       'statistika_aval_kpv',
                                       'statistika_ekk_kpv',
                                       'valim_testimiskord_id',
                                       'sisaldab_valimit'])
        cp.test_id = test.id
        cp.test = test
        Session.autoflush = False # integrity errori pärast
        if not tahis:
            tahis = 'Koopia' + (cp.tahis or '')
        cp.tahis = tahis
        self.copy_subrecords(cp, ['toimumisajad',
                                  ])
        for cp_ta in cp.toimumisajad:
            cp_ta.set_tahised()
        for r in self.regkohad:
            cp.regkohad.append(r)
        for r in self.piirkonnad:
            cp.piirkonnad.append(r)
            
        Session.autoflush = True    
        return cp

    def delete_subitems(self):
        if len(self.sooritajad):
            raise Exception(_("Testimiskorda ei saa kustutada, kuna on registreeritud sooritajaid"))
        self.delete_subrecords(['toimumisajad',
                                'nimekirjad',
                                'testilepingud',
                                ])            

    def has_permission(self, permission, perm_bit, user):
        rc = False
        if permission.startswith('nimekirjad') or permission == 'erivmark' or permission == 'erivmark_p':
            rc = self._has_permission_reg(permission, perm_bit, user)
        elif permission == 'sooritamine':
            rc, sooritaja = self._has_permission_s(perm_bit, user.id)
        return rc
    
    def _has_permission_reg(self, permission, perm_bit, user):        
        """Kontrollime, kas kasutajal on luba sooritajaid registreerida
        """
        dt = date.today()
        test = self.test
        rc = None
        if test.staatus != const.T_STAATUS_KINNITATUD:
            log.debug('test %s ei ole kinnitatud' % test.id)
            rc = False

        elif user.has_permission('klass', perm_bit, koht_id=user.koht_id):        
            # on õpetaja
            if perm_bit & const.BT_MODIFY == 0:
                # ei soovita muutmisõigust
                rc = True
            else:
                reg_kool = self.reg_kool_eis or \
                    self.reg_kool_valitud and user and self.on_regkoht(user.koht_id)
                if reg_kool and \
                   (self.reg_kool_alates is None or self.reg_kool_alates <= dt) and \
                   (self.reg_kool_kuni is None or self.reg_kool_kuni > dt - timedelta(1)) and \
                   (test.avaldamistase == const.AVALIK_EKSAM or  test.avaldamistase == const.AVALIK_OPETAJAD) \
                   and (test.avalik_alates is None or test.avalik_alates <= dt) \
                   and (test.avalik_kuni is None or test.avalik_kuni > dt - timedelta(1)):
                    # õpetajal on õigus
                    rc = True

                elif permission == 'erivmark' and self.erivajadus_alates and self.erivajadus_kuni and \
                     self.erivajadus_alates <= dt and self.erivajadus_kuni > dt - timedelta(1):
                    # registreerimise õigust ei ole, aga on õigus märkida erivajadusi
                    rc = True

            if permission == 'erivmark_p':
                # alati võib muuta neid eritingimusi, mida Innove ei pea kinnitama
                # selliseid tingimusi on põhikooli eksamite korral
                rc = self.test.testiliik_kood == const.TESTILIIK_POHIKOOL

        if rc is None and \
           test.avaldamistase == const.AVALIK_SOORITAJAD and \
           (test.avalik_alates is None or test.avalik_alates <= dt) and \
           (test.avalik_kuni is None or test.avalik_kuni > dt - timedelta(1)):
            # avalik test
            rc = True

        # määratud test
        if rc is None and test.avaldamistase==const.AVALIK_MAARATUD:
            for rcd in test.testiisikud:
                if rcd.kasutaja_id == user.id and \
                   rcd.kasutajagrupp_id == const.GRUPP_T_KORRALDAJA and\
                   rcd.kehtib_alates <= dt and rcd.kehtib_kuni > dt - timedelta(1):
                    rc = True
                    break

        # oma test
        if rc is None:
            for rcd in test.testiisikud:
                if rcd.kasutaja_id == user.id and \
                   rcd.kasutajagrupp_id==const.GRUPP_T_OMANIK:
                    rc = True

        return rc or False

    def set_modifier(self):
        EntityHelper.set_modifier(self)
        self.set_aval_kpv()

    def set_aval_kpv(self):
        kpv = date.today()
        
        if self.koondtulemus_avaldet and not self.koondtulemus_aval_kpv:
            self.koondtulemus_aval_kpv = kpv
            Statistikaraport.remove_raportid(self.test_id, self.aasta, None)
        elif not self.koondtulemus_avaldet and self.koondtulemus_aval_kpv:
            self.koondtulemus_aval_kpv = None
            Statistikaraport.remove_raportid(self.test_id, self.aasta, None)
            
        if self.alatestitulemused_avaldet and not self.alatestitulemused_aval_kpv:
            self.alatestitulemused_aval_kpv = kpv
        elif not self.alatestitulemused_avaldet and self.alatestitulemused_aval_kpv:
            self.alatestitulemused_aval_kpv = None

        if self.ylesandetulemused_avaldet and not self.ylesandetulemused_aval_kpv:
            self.ylesandetulemused_aval_kpv = kpv
        elif not self.ylesandetulemused_avaldet and self.ylesandetulemused_aval_kpv:
            self.ylesandetulemused_aval_kpv = None

        if self.aspektitulemused_avaldet and not self.aspektitulemused_aval_kpv:
            self.aspektitulemused_aval_kpv = kpv
        elif not self.aspektitulemused_avaldet and self.aspektitulemused_aval_kpv:
            self.aspektitulemused_aval_kpv = None

        if self.ylesanded_avaldet and not self.ylesanded_aval_kpv:
            self.ylesanded_aval_kpv = kpv
        elif not self.ylesanded_avaldet and self.ylesanded_aval_kpv:
            self.ylesanded_aval_kpv = None                            
