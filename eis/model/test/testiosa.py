"Testi andmemudel"
from eis.model.entityhelper import *

from .test import Test
from .hindamiskogum import Hindamiskogum

class Testiosa(EntityHelper, Base):
    """Testiosa
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nimi = Column(String(256)) # testiosa nimi
    max_pallid = Column(Float) # max pallide arv
    skoorivalem = Column(String(256)) # tulemuse arvutamise valem (kasutusel siis, kui tulemus ei ole ülesannete pallide summa)
    alustajajuhend = Column(Text) # juhend sooritajale, mis kuvatakse enne testi alustamist
    sooritajajuhend = Column(Text) # juhend sooritajale, mis kuvatakse siis, kui sooritamist on alustatud
    tulemus_tunnistusele = Column(Boolean) # kas tulemus läheb tunnistusele
    seq = Column(Integer) # testiosa järjekorranumber testis
    tahis = Column(String(10)) # testiosa tähis 
    vastvorm_kood = Column(String(10), nullable=False) # vastamise vorm, klassifikaator VASTVORM: ke=const.VASTVORM_KE - kirjalik e-test; se=const.VASTVORM_SE - suuline e-test; i=const.VASTVORM_I - suuline (intervjuu); sh=const.VASTVORM_SH - suuline (hindajaga); kp=const.VASTVORM_KP - kirjalik (p-test); sp=const.VASTVORM_SP - suuline (p-test); n=const.VASTVORM_KONS - konsultatsioon
    piiraeg = Column(Integer) # testiosa sooritamiseks lubatud aeg sekundite
    piiraeg_sek = Column(Boolean) # true - aeg kuvada kohe sekundites; false, null - minutist suurem aeg kuvada ilma sekunditeta
    hoiatusaeg = Column(Integer) # piirajaga testiosa korral: mitu sekundit enne lõppu antakse hoiatusteade
    aeg_peatub = Column(Boolean) # kas testi sooritamise katkestamisel aeg peatub
    ylesannete_arv = Column(Integer) # ülesannete arv
    on_alatestid = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas testiosal on alatestid
    testiylesanded = relationship('Testiylesanne', order_by='Testiylesanne.alatest_seq, Testiylesanne.seq', back_populates='testiosa')
    alatestid = relationship('Alatest', order_by='Alatest.kursus_kood,Alatest.seq', back_populates='testiosa')
    alatestigrupid = relationship('Alatestigrupp', order_by='Alatestigrupp.seq', back_populates='testiosa')
    test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False) # viide testile
    test = relationship('Test', foreign_keys=test_id, back_populates='testiosad')
    komplektivalikud = relationship('Komplektivalik', order_by='Komplektivalik.id', back_populates='testiosa') 
    toimumisajad = relationship('Toimumisaeg', order_by='Toimumisaeg.tahised', back_populates='testiosa')
    hindamiskogumid = relationship('Hindamiskogum', order_by='Hindamiskogum.tahis', back_populates='testiosa')
    sisestuskogumid = relationship('Sisestuskogum', order_by='Sisestuskogum.tahis', back_populates='testiosa')
    kysimusestatistikad = relationship('Kysimusestatistika', back_populates='testiosa') # kysimuste statistika avaliku vaate testi korral
    rvosaoskus_id = Column(Integer, ForeignKey('rvosaoskus.id'), index=True) # seos rahvusvahelise tunnistuse osaoskusega, mis vastab sellele (alatestideta, foreign_keys=rvosaoskus_id) testiosale
    rvosaoskus = relationship('Rvosaoskus', foreign_keys=rvosaoskus_id)
    naita_max_p = Column(Boolean, sa.DefaultClause('true')) # kas testiosa max pallid ja soorituse olek kuvada lahendajale
    lotv = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas on lõdva struktuuriga testiosa
    yhesuunaline = Column(Boolean) # kas testiosa on ühesuunaliselt lahendatav (ülesanded tuleb lahendada kindlas järjekorras)
    yl_lahk_hoiatus = Column(Boolean) # kas ühesuunalises testiosas ülesandelt lahkumisel kuvada hoiatus
    yl_pooleli_hoiatus = Column(Boolean) # kas ühesuunalises testiosas pooleliolevalt ülesandelt lahkumisel kuvada hoiatus    
    yl_lahendada_lopuni = Column(Boolean) # kas kõigi ülesannete korral on vajalik kõik väljad täita ja ülesanne lõpuni lahendada
    yl_segamini = Column(Boolean) # kas ülesanded kuvatakse lahendajale segatud järjekorras
    ala_lahk_hoiatus = Column(Boolean) # kas ühekordselt alatestilt lahkumisel kuvada hoiatus
    kuva_yl_nimetus = Column(Boolean) # kas lahendajale kuvada ülesande jrknr asemel nimetus (nii vasakul ribal kui ka ülesande kohal pealkirjas)
    peida_yl_pealkiri = Column(Boolean) # kas lahendajale kuvada ülesande kohal ülesande jrknr/nimetus
    pos_yl_list = Column(Integer, sa.DefaultClause('1'), nullable=False) # ülesannete loetelu kuvamine lahendajale: 0=const.POS_NAV_HIDDEN - ei kuva; 1=const.POS_NAV_LEFT - vasakul; 2=const.POS_NAV_TOP - ülal (ei saa kasutada)
    peida_pais = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas lahendajale kuvada EISi päis ja jalus või ainult ülesanded
    yl_jrk_alatestiti = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas ülesannete järjekorranumbrid algavad igas alatestis uuesti 1st
    katkestatav = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas sooritajale kuvatakse katkestamise nupp
    lopetatav = Column(Boolean, sa.DefaultClause('true'), nullable=False) # kas testi lõpetamise nupp on sooritajale alati nähtav (või ainult peale kõigi alatestide sooritamist)
    normipunktid = relationship('Normipunkt', order_by='Normipunkt.seq', back_populates='testiosa')    
    testikohad = relationship('Testikoht', back_populates='testiosa')
    ylesandegrupid = relationship('Ylesandegrupp', order_by='Ylesandegrupp.seq', back_populates='testiosa')
    nsgrupid = relationship('Nsgrupp', order_by='Nsgrupp.seq', back_populates='testiosa')    

    _parent_key = 'test_id'    

    trans = relationship('T_Testiosa', cascade='all', back_populates='orig')
    __table_args__ = (
        sa.UniqueConstraint('test_id','tahis'),
        )

    @property
    def peida_yl_list(self):
        return self.pos_yl_list == const.POS_NAV_HIDDEN

    @property
    def on_piiraeg(self):
        """Kas testiosal või mõnel selle alatestil on piiraeg
        """
        if self.piiraeg:
            return True
        for rcd in self.alatestid:
            if rcd.piiraeg:
                return True
        return False

    @property
    def vastvorm_nimi(self):
        return usersession.get_opt().VASTVORM.get(self.vastvorm_kood)

    @property
    def alatest_kood(self):
        return None

    @property
    def opt_alatestid(self):
        return [(item.id, item.nimi) for item in self.alatestid]

    @property
    def oma_kavaaeg(self):
        "Kas sooritajatele määratakse oma alustamise aeg"
        vastvorm_s = (const.VASTVORM_SE,
                      const.VASTVORM_I,
                      const.VASTVORM_SH,
                      const.VASTVORM_SP)
        return self.vastvorm_kood in vastvorm_s

    def get_opt_komplektivalikud(self, komplektide_arv=False, kursus=None, naita_kursus=False):
        li = []
        katmata_alatestid = ', '.join([str(r.seq) for r in self.alatestid if not r.komplektivalik_id])
        for item in self.komplektivalikud:
            if kursus and item.kursus_kood != kursus:
                continue
            cnt = len(item.komplektid)
            buf = item.str_alatestid
            if not buf and cnt == 0 and katmata_alatestid:
                buf = katmata_alatestid
            li_s = []
            if naita_kursus and item.kursus_kood:
                li_s.append(item.kursus_nimi)
            if komplektide_arv:
                li_s.append('%s %s' % (cnt, cnt == 1 and 'komplekt' or 'komplekti'))
            if li_s:
                buf += ' (%s)' % (', '.join(li_s))
            li.append((item.id, buf))
        return li

    def gen_tahis(self):
        if not self.tahis:
            test = self.test or Test.get(self.test_id)
            for n in range(1,100):
                tahis = '%d' % n
                for tosa in test.testiosad:
                    if tosa.tahis == tahis:
                        tahis = None
                        break
                if tahis:
                    self.tahis = tahis
                    break

    def delete_subitems(self):    
        for r in self.testikohad:
            if not r.toimumisaeg_id:
                r.delete()
        self.delete_subrecords(['testiylesanded',
                                'kysimusestatistikad',
                                'alatestigrupid',
                                'alatestid',
                                'sisestuskogumid',
                                'hindamiskogumid',
                                'komplektivalikud',
                                'ylesandegrupid',
                                'nsgrupid',
                                'normipunktid',
                                ])


    def get_sooritused(self, kasutaja_id, toimumisaeg_id=None):
        from eis.model.testimine import Sooritus
        
        q = Sooritus.query.\
            filter_by(testiosa_id=self.id).\
            filter(Sooritus.sooritaja.has(kasutaja_id=kasutaja_id))
        if toimumisaeg_id:
            q = q.filter(Sooritus.toimumisaeg_id==toimumisaeg_id)
        return q.all()

    def arvuta_pallid(self, arvuta_ty=True):
        """Arvutatakse kokku testiosa max pallid
        tagastame:
        - (määramata kursusega) max pallide arv testiosas
        - dict pallide koguarvuga kursuste kaupa
        """
        def _add_none(p1, p2):
            # Kui lõdva struktuuriga testiosas mõnel testiylesandel pole max_palle,
            # siis ei saa olla ka kogupallide arvu
            if p1 is None or p2 is None and self.lotv:
                return None
            else:
                return p1 + (p2 or 0)
            
        kursuspallid = dict()
        to_max_pallid = 0

        # ylesanded, mida hinnatakse kriteeriumitega ja milles ylesande punkte ei arvestata
        krit_hk = {}
        for hk in self.hindamiskogumid:
            hk.arvuta_pallid(self.lotv)
            if hk.on_kriteeriumid:
                krit_hk[hk.id] = hk.max_pallid

        testiylesanded = list(self.testiylesanded)
        self.ylesannete_arv = len(testiylesanded)
        
        jrk = a_jrk = 0
        alatestid = list(self.alatestid)
        cnt_alatestid = len(alatestid)
        self.on_alatestid = cnt_alatestid > 0
        for n_alatest, alatest in enumerate(alatestid or [None]):
            if arvuta_ty or not alatest:
                # arvutame iga alatesti max_pallid yle
                a_krit_hk_id = set()
                max_pallid = 0

                vbl_testivaline = True
                if alatest:
                    a_testiylesanded = list(alatest.testiylesanded)
                    alatest.ylesannete_arv = len(a_testiylesanded)
                    if alatest.numbrita:
                        alatest.tahis = None
                    else:
                        a_jrk += 1
                        alatest.tahis = str(a_jrk)
                else:
                    a_testiylesanded = testiylesanded
                    
                # testiylesannete tähiste määramine
                jrk = self.gen_a_ty_tahis(alatest, a_testiylesanded, jrk)
                # testiylesannete seq ja pallid
                seq = 0
                for ty in a_testiylesanded:
                    seq += 1
                    if ty.seq != seq:
                        ty.seq = seq
                    hk_id = ty.hindamiskogum_id
                    if hk_id in krit_hk:
                        # ylesannet hinnatakse hindamiskogumi hindamiskriteeriumiga
                        if hk_id not in a_krit_hk_id:
                            a_krit_hk_id.add(hk_id)
                            max_pallid = _add_none(max_pallid, krit_hk[hk_id])
                    else:
                        # ylesande oma pallid
                        max_pallid = _add_none(max_pallid, ty.max_pallid)

                    if alatest and ty.alatest_seq != alatest.seq:
                        ty.alatest_seq = alatest.seq
                    if ty.liik != const.TY_LIIK_K:
                        vbl_testivaline = False

                if alatest:
                    alatest.testivaline = vbl_testivaline and (alatest.max_pallid == 0) and (n_alatest == cnt_alatestid - 1)
                    if not alatest.skoorivalem:
                        alatest.max_pallid = max_pallid

                    for plokk in alatest.testiplokid:
                        p_max_pallid = 0
                        p_testiylesanded = list(plokk.testiylesanded)
                        for ty in p_testiylesanded:
                            if ty.hindamiskogum_id not in krit_hk:
                                p_max_pallid = _add_none(p_max_pallid, ty.max_pallid)
                        plokk.max_pallid = p_max_pallid
                        plokk.ylesannete_arv = len(p_testiylesanded)                    
            else:
                # eeldame, et alatesti max_pallid on õige
                max_pallid = alatest.max_pallid

            kursus = alatest and alatest.kursus_kood
            if kursus:
                if kursus in kursuspallid:
                    kursuspallid[kursus] = _add_none(kursuspallid[kursus], max_pallid)
                else:
                    kursuspallid[kursus] = max_pallid
            else:
                to_max_pallid = _add_none(to_max_pallid, max_pallid)


        # kontrollime, et iga komplektivaliku sees oleks kõigil alatestidel sama kursus
        for kv in self.komplektivalikud:
            kursus = None
            for alatest in kv.alatestid:
                if alatest.kursus_kood != kv.kursus_kood:
                    alatest.komplektivalik_id = None
                    log.error('Alatest %s eemaldatud komplektivalikust, kuna kursus ei sobi' % (alatest.id))

            # lõdva struktuuri korral lisame kõik hindamiskogumita ylesanded vaikimisi hindamiskogumisse
            hk0 = kv.give_default_hindamiskogum()
            if self.lotv:
                for komplekt in kv.komplektid:
                    for vy in komplekt.valitudylesanded:
                        if not vy.hindamiskogum_id:
                            hk0.valitudylesanded.append(vy)
            hk0.arvuta_pallid(self.lotv)
                
        # liidame kursuseta alatestide pallid kõigile kursustele
        is_max_p = to_max_pallid is not None
        for kursus in kursuspallid:
            kursuspallid[kursus] = _add_none(kursuspallid[kursus], to_max_pallid)
            if kursuspallid[kursus] is None:
                is_max_p = False
                
        if kursuspallid:
            if is_max_p:
                to_max_pallid = max(to_max_pallid, max(kursuspallid.values()))
            else:
                to_max_pallid = None

        if self.skoorivalem:
            # kui tulemused arvutatakse, siis on testiosa max alati 100
            self.max_pallid = const.MAX_SCORE
        else:
            if self.max_pallid != to_max_pallid:
                self.max_pallid = to_max_pallid

        return self.max_pallid, kursuspallid

    def gen_a_ty_tahis(self, alatest, a_testiylesanded, jrk):
        "Testiosa/alatesti ülesannetele tähiste genereerimine ja salvestamine"
        jatk_jrk = 0
        kobar_tahis = None
        if self.yl_jrk_alatestiti:
            # igal alatestil oma jrk
            jrk = 0
        for ty in a_testiylesanded:
            if ty.on_jatk:
                # d-testi jätkuülesanne
                jatk_jrk += 1
                ty.tahis = '%s.%d' % (kobar_tahis or '0', jatk_jrk)
            else:
                ty.tahis, jrk = gen_ty_tahis(ty, alatest, jrk, self.yl_jrk_alatestiti)
                kobar_tahis = ty.tahis
        return jrk
    
    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        test = self.test or self.test_id and Test.get(self.test_id)
        if test:
            test.logi('Testiosa %s (%s) %s' % (self.id, self.tahis, liik), vanad_andmed, uued_andmed, logitase)

    def copy(self, cp_test=None, komplektid=[]):
        cp = EntityHelper.copy(self)
        cp.test = cp_test
        self.copy_subrecords(cp, ['trans'])
        
        map_sk = {}
        for sk in self.sisestuskogumid:
            cp_sk = EntityHelper.copy(sk)
            cp_sk.testiosa = cp
            map_sk[sk.id] = cp_sk

        map_komplektid = {}
        map_hk = {}
        alatestid = set() # kopeeritavad alatestid
        
        # kopeerime esmalt komplektid ilma valitudylesanneteta
        for kvalik in self.komplektivalikud:
            kv_komplektid = list(kvalik.komplektid)
            # kui komplektid on antud, siis kopeerida ainult need komplektid
            # muidu kopeerida kõik komplektid
            if komplektid:
                kv_komplektid = [k for k in kv_komplektid if k in komplektid]
                if not kv_komplektid:
                    # selles komplektivalikus ei ole komplekte kopeerida
                    continue

            for alatest in kvalik.alatestid:
                alatestid.add(alatest)
                
            cp_kvalik = EntityHelper.copy(kvalik)
            cp_kvalik.testiosa = cp

            cp.komplektivalikud.append(cp_kvalik)
            cp_kvalik.alatestid_seq = [a.seq for a in kvalik.alatestid]

            for k in kv_komplektid:
                #log.debug('cp %d,%s' % (k.komplektivalik_id, k.tahis))
                cp_komplekt = EntityHelper.copy(k)
                cp_komplekt.staatus = const.T_STAATUS_KOOSTAMISEL
                cp_komplekt.lukus = None
                cp_komplekt.komplektivalik = cp_kvalik
                cp_kvalik.komplektid.append(cp_komplekt)
                if komplektid:
                    # kui kopeeriti kindlaid komplekte (eeltesti loomiseks)
                    cp_komplekt.staatus = const.K_STAATUS_KINNITATUD
                    cp_komplekt.eeltestid = []
                    
                map_komplektid[k.id] = cp_komplekt
                k.copy_subrecords(cp_komplekt, ['testifailid'])
                
            for hk in kvalik.hindamiskogumid:
                cp_hk = EntityHelper.copy(hk)
                cp_hk.testiosa = cp
                cp_kvalik.hindamiskogumid.append(cp_hk)
                map_hk[hk.id] = cp_hk
                if hk.sisestuskogum_id:
                    cp_hk.sisestuskogum = map_hk.get(hk.sisestuskogum_id)
                for kr in hk.hindamiskriteeriumid:
                    cp_kr = EntityHelper.copy(kr)
                    cp_hk.hindamiskriteeriumid.append(cp_kr)

        map_atk = {}
        for atk in self.alatestigrupid:
            cp_atk = EntityHelper.copy(atk)
            cp_atk.testiosa = cp
            map_atk[atk.id] = cp_atk

        map_grupp = {}
        for grupp in self.ylesandegrupid:
            cp_grupp = grupp.copy()
            cp.ylesandegrupid.append(cp_grupp)
            map_grupp[grupp.id] = cp_grupp

        map_alatest = {}
        map_ty = {}
        # kopeerime struktuuri ja paigutame uute komplektide alla
        if self.on_alatestid:
            for alatest in self.alatestid:
                if alatest not in alatestid:
                    # ei ole kopeeritavate komplektidega kaetud alatest
                    continue
                cp_alatest = EntityHelper.copy(alatest)
                cp_alatest.testiosa = cp
                alatest.copy_subrecords(cp_alatest, ['trans'])                
                map_alatest[alatest.id] = cp_alatest
                    
                for kvalik in cp.komplektivalikud:
                    if alatest.seq in kvalik.alatestid_seq and alatest.kursus_kood == kvalik.kursus_kood:
                        cp_alatest.komplektivalik = kvalik
                        
                for testiplokk in alatest.testiplokid:
                    cp_testiplokk = EntityHelper.copy(testiplokk)
                    cp_testiplokk.alatest = cp_alatest
                    testiplokk.copy_subrecords(cp_testiplokk, ['trans'])
                    for ty in testiplokk.testiylesanded:
                        # testiploki sees olevad ylesanded
                        cp_ty = ty.copy_to(cp_testiplokk, cp_alatest, cp, map_komplektid, map_hk, map_atk, map_grupp)
                        map_ty[ty.id] = cp_ty

                for ty in alatest.testiylesanded:
                    # ylesanded ilma testiplokita
                    if ty.testiplokk is None:
                        cp_ty = ty.copy_to(None, cp_alatest, cp, map_komplektid, map_hk, map_atk, map_grupp)
                        map_ty[ty.id] = cp_ty                        
        else:
            for ty in self.testiylesanded:
                # ylesanded ilma alatestita
                if ty.alatest is None:
                    cp_ty = ty.copy_to(None, None, cp, map_komplektid, map_hk, map_atk, map_grupp)
                    map_ty[ty.id] = cp_ty                    

        map_nsg = {}
        for nsg in self.nsgrupid:
            cp_nsg = nsg.copy()
            map_nsg[nsg.id] = cp_nsg
            cp.nsgrupid.append(cp_nsg)
            
        for normipunkt in self.normipunktid:
            cp_normipunkt = normipunkt.copy()
            cp_normipunkt.alatestigrupp = map_atk.get(normipunkt.alatestigrupp_id)
            if normipunkt.alatest_id:
                cp_normipunkt.alatest = map_alatest.get(normipunkt.alatest_id)
            if normipunkt.testiylesanne_id:
                cp_normipunkt.testiylesanne = map_ty.get(normipunkt.testiylesanne_id)
            if normipunkt.ylesandegrupp_id:
                cp_normipunkt.ylesandegrupp = map_grupp.get(normipunkt.ylesandegrupp_id)
            cp.normipunktid.append(cp_normipunkt)

            cp_nptagasisided = list(cp_normipunkt.nptagasisided)
            for ind, ns in enumerate(normipunkt.nptagasisided):
                cp_ns = cp_nptagasisided[ind]
                cp_ns.uus_testiylesanne = map_ty.get(ns.uus_testiylesanne_id)
                if ns.nsgrupp_id:
                    cp_ns.nsgrupp = map_nsg.get(ns.nsgrupp_id)
                
        for cp_kv in cp.komplektivalikud:
            for hk in cp_kv.hindamiskogumid:
                hk.arvuta_pallid(cp.lotv)
        return cp

    def get_kysimusestatistika(self, kysimus_id, vy_id, tkorraga, nimekiri_id=None):
        "Avaliku vaate testi statistika"
        from eis.model.testimine import Kysimusestatistika
        q = (Session.query(Kysimusestatistika)
             .filter_by(testiosa_id=self.id)
             .filter_by(kysimus_id=kysimus_id)
             .filter_by(valitudylesanne_id=vy_id))
        if nimekiri_id:
            q = q.filter_by(nimekiri_id=nimekiri_id)
        else:
            q = (q.filter_by(toimumisaeg_id=None)
                 .filter_by(tkorraga=tkorraga))
        return q.first()

    def give_kysimusestatistika(self, kysimus_id, vy_id, tkorraga, nimekiri_id=None):
        "Avaliku vaate testi statistika"
        from eis.model.testimine import Kysimusestatistika

        rcd = self.get_kysimusestatistika(kysimus_id, vy_id, tkorraga, nimekiri_id)
        if not rcd:
            rcd = Kysimusestatistika(testiosa=self,
                                     toimumisaeg=None, 
                                     kysimus_id=kysimus_id,
                                     tkorraga=tkorraga,
                                     valitudylesanne_id=vy_id,
                                     nimekiri_id=nimekiri_id)
            #self.kysimusestatistikad.append(rcd)
        return rcd

    def get_komplektivalik(self, alatest_id=None, alatest=None):
        if alatest_id:
            from .alatest import Alatest
            alatest = Alatest.get(alatest_id)
        if alatest:
            return alatest.komplektivalik
        for kvalik in self.komplektivalikud:
            return kvalik
        
    def give_komplektivalik(self, alatest_id=None, alatest=None):
        kvalik = self.get_komplektivalik(alatest_id, alatest)
        if not kvalik:
            from .komplektivalik import Komplektivalik
            kvalik = Komplektivalik(testiosa=self)
            #self.komplektivalikud.append(kvalik)
            if alatest_id:
                from .alatest import Alatest
                alatest = Alatest.get(alatest_id)
            if alatest:
                assert alatest.testiosa_id == self.id, 'Vale alatest'
                alatest.komplektivalik = kvalik
            else:
                if len(self.alatestid) == 0:
                    kvalik.alatestideta = True
        return kvalik

    @property
    def testiylesanded_kuvada(self):
        return [ty for ty in self.testiylesanded if ty.kuvada_statistikas]

def gen_ty_tahis(ty, alatest, jrk, yl_jrk_alatestiti):
    "Testiülesande tähise genereerimine (ei salvesta siin)"
    if ty.liik == const.TY_LIIK_Y:
        jrk += 1
        if yl_jrk_alatestiti and alatest and alatest.tahis:
            tahis = '%s.%d' % (alatest.tahis, jrk)
        else:
            tahis = '%d' % jrk
    else:
        tahis = None
    return tahis, jrk
    
    
