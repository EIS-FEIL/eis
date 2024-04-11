# -*- coding: utf-8 -*-
"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import Opt
from eis.model.kasutaja import *
from eis.model.koht import *

from .valitudylesanne import Valitudylesanne   
from .alatest import Alatest
from .testiplokk import Testiplokk
from .testiosa import Testiosa
from .hindamiskogum import Hindamiskogum
_ = usersession._

class Testiylesanne(EntityHelper, Base):
    """Testiülesanne (ülesandepesa, mis määratakse testi struktuuris
    ning mille sisse igas ülesandekomplektis valitakse ise ülesanne)
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alatest_seq = Column(Integer) # välja alatest.seq koopia, et oleks mugavam sortida
    seq = Column(Integer) # testiülesande järjekorranumber alatesti sees
    nimi = Column(String(256)) # testiülesande nimetus
    yhisosa_kood = Column(String(10)) # testiülesande kood (laia ja kitsa matemaatikaeksami ülesannete sidumiseks, samadel testiülesannetel peab olema sama kood)
    #jrk = Column(Integer) # järjekorranumber kuvamisel
    tahis = Column(String(10)) # testiülesande järjekorranumber: alatestisisese nummerdamise korral koos alatesti järjekorranumbriga, üldise nummerdamise korral ilma; diagnoosiva testi jätkuülesande korral eelmise kobara ülesande number, punkt ja jätkuülesande jrk nr
    on_jatk = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas ülesanne on jätkuülesanne, milleni lahendaja jõuab ainult tabelis Nptagasiside kirjeldatud suunamise korral (diagnoosivas testis)
    eristusindeks = Column(Float) # nõutav eristusindeks
    hindamine_kood = Column(String(10)) # nõutav hindamise liik: subj=const.HINDAMINE_SUBJ - subjektiivne; obj=const.HINDAMINE_OBJ - objektiivne
    arvutihinnatav = Column(Boolean) # kas on nõutav, et oleks arvutihinnatav
    kasutusmaar = Column(Float) # nõutav kasutusmäär
    aste_kood = Column(String(10)) # nõutav kooliaste/eriala, klassifikaator ASTE
    mote_kood = Column(String(10)) # nõutav mõtlemistasand, klassifikaator MOTE
    max_pallid = Column(Float) # max pallide arv, peab olema määratud enne struktuuri kinnitamist
    yhisosa_max_pallid = Column(Float) # max pallide arv testimiskordade ühisossa kuuluvatest küsimustest
    raskus = Column(Float) # nõutav raskus
    teema_kood = Column(String(10)) # nõutav teema (varasem nimetus: valdkond) testi aines, klassifikaator TEEMA
    alateema_kood = Column(String(10)) # nõutav alateema (varasem nimetus: teema), klassifikaator ALATEEMA
    keeletase_kood = Column(String(10)) # nõutav keeleoskuse tase, klassifikaator KEELETASE
    tyyp = Column(String(10)) # nõutav ülesandetüüp (vt sisuplokk.tyyp)
    valikute_arv = Column(Integer, sa.DefaultClause('1'), nullable=False) # valikülesannete arv (mille seast lahendaja saab ise valida)
    valik_auto = Column(Boolean, sa.DefaultClause('0'), nullable=False) # true - valikülesande valib arvuti automaatselt; false - valikülesande valib lahendaja (kui valikute_arv > 1)
    testiosa_id = Column(Integer, ForeignKey('testiosa.id'), index=True, nullable=False) # viide testiosale
    testiosa = relationship('Testiosa', foreign_keys=testiosa_id, back_populates='testiylesanded')
    _parent_key = 'testiosa_id'     
    testiplokk_id = Column(Integer, ForeignKey('testiplokk.id'), index=True) # viide testiplokile (kui testiplokid on kasutusel, foreign_keys=testiplokk_id)
    testiplokk = relationship('Testiplokk', foreign_keys=testiplokk_id, back_populates='testiylesanded')
    alatest_id = Column(Integer, ForeignKey('alatest.id'), index=True) # viide alatestile (kui alatestid on kasutusel, foreign_keys=alatest_id)
    alatest = relationship('Alatest', foreign_keys=alatest_id, back_populates='testiylesanded')
    valitudylesanded = relationship('Valitudylesanne', back_populates='testiylesanne') 
    hindamiskogum_id = Column(Integer, ForeignKey('hindamiskogum.id'), index=True, nullable=False) # viide hindamiskogumile, millesse testiülesanne kuulub
    hindamiskogum = relationship('Hindamiskogum', foreign_keys=hindamiskogum_id, back_populates='testiylesanded')
    trans = relationship('T_Testiylesanne', cascade='all', back_populates='orig')
    sisestusviis = Column(Integer, sa.DefaultClause('3'), nullable=False) # vastuste sisestamise viis: 1=const.SISESTUSVIIS_VASTUS - e-test või p-testi vastuste sisestamine (ainult arvutihinnatava ülesande korral); 2=const.SISESTUSVIIS_OIGE - p-testi õige/vale hinnangu sisestamine; 3=const.SISESTUSVIIS_PALLID - p-testi toorpunktide sisestamine
    hyppamisviis = Column(Integer, sa.DefaultClause('1'), nullable=False) # vastuste sisestamisel valikväljalt: 1 - kursor hüppab peale valikut automaatselt järgmisele väljale; 0 - ei hüppa automaatselt
    sooritajajuhend = Column(String(1024)) # juhend sooritajale (kasutusel valikülesande korral)       
    pealkiri = Column(String(512)) # pealkiri (kasutusel valikülesande korral)
    liik = Column(String(1), sa.DefaultClause('Y'), nullable=False) # testiülesande liik testi struktuuris: Y - ülesanne; T - tiitelleht; E - näide; G - juhend; K - küsimustik
    kuvada_statistikas = Column(Boolean, sa.DefaultClause('1')) # kas kuvada ülesanne statistikas
    piiraeg = Column(Integer) # ülesande sooritamiseks lubatud aja ülemine piir sekundites
    piiraeg_sek = Column(Boolean) # true - aeg kuvada kohe sekundites; false, null - minutist suurem aeg kuvada ilma sekunditeta
    min_aeg = Column(Integer) # ülesande sooritamiseks lubatud aja alumine piir sekundites
    hoiatusaeg = Column(Integer) # piirajaga testiülesande korral: mitu sekundit enne lõppu antakse hoiatusteade
    normipunktid = relationship('Normipunkt', order_by='Normipunkt.seq', back_populates='testiylesanne')
    naita_max_p = Column(Boolean, sa.DefaultClause('true')) # kas ülesande max pallid kuvada lahendajale
    ise_jargmisele = Column(Boolean) # kas kohustusliku arvu vastuste andmisel minna automaatselt edasi järgmisele ülesandele
    on_markus_sooritajale = Column(Boolean) # kas hindaja saab hindamisel sooritajale märkusi kirjutada
    ei_naita_tulemustes = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas ülesannet tulemustes ei näidata (jagatud töö korral)
    ahel_nptagasisided = relationship('Nptagasiside', foreign_keys='Nptagasiside.ahel_testiylesanne_id', back_populates='ahel_testiylesanne')
    uus_nptagasisided = relationship('Nptagasiside', foreign_keys='Nptagasiside.uus_testiylesanne_id', back_populates='uus_testiylesanne')
    
    SISESTUSVIIS_VASTUS = 1
    SISESTUSVIIS_BOOL = 2
    SISESTUSVIIS_PALLID = 3
    teema_id = None

    @classproperty
    def opt_liik(cls):
        return ((const.TY_LIIK_Y, _("Ülesanne")),
                (const.TY_LIIK_T, _("Tiitelleht")),
                (const.TY_LIIK_E, _("Näide")),
                (const.TY_LIIK_G, _("Juhend")),
                (const.TY_LIIK_K, _("Küsimustik")),
                )
    @property
    def liik_nimi(self):
        for kood, nimi in self.opt_liik:
            if kood == self.liik:
                return nimi
    
    def get_seq(self):
        if self.alatest_id:
            return self.get_seq_parent('alatest_id', self.alatest_id)
        else:
            return self.get_seq_parent('testiosa_id', self.testiosa_id)
           
    def get_valitudylesanded(self, toimumisaeg=None):
        """Koostatakse dict, milles iga komplekti id on key, millele vastab
        list vastava komplekti valitudylesannetest.
        """
        q = Session.query(Valitudylesanne).\
            filter(Valitudylesanne.testiylesanne_id==self.id)
        if toimumisaeg:
            # otsime ainult antud toimumisajal kasutusel olevate komplektide seast
            komplektid_id = [k.id for k in toimumisaeg.komplektid]
            if len(komplektid_id) == 1:
                q = q.filter(Valitudylesanne.komplekt_id==komplektid_id[0])
            else:
                q = q.filter(Valitudylesanne.komplekt_id.in_(komplektid_id))
        q = q.order_by(Valitudylesanne.komplekt_id, Valitudylesanne.seq)

        di = {}
        for vy in q.all():
            if vy.komplekt_id not in di:
                di[vy.komplekt_id] = []
            di[vy.komplekt_id].append(vy)
        return di

    def get_aspektid(self, toimumisaeg=None, vy_seq=None, with_max=False):
        """
        Leitakse list selle testiylesande kõigi valitudylesannete aspektidest.
        Igale aspektile tekitatakse dict y_hindamisaspektid, 
        mille võtmeteks on vy_id ja väärtusteks vastavas komplektis ylesande hindamisaspekti kirje
        """
        from eis.model.ylesanne import Ylesanne, Hindamisaspekt
        q = (Session.query(Hindamisaspekt, Valitudylesanne.id)
             .join((Valitudylesanne, Hindamisaspekt.ylesanne_id==Valitudylesanne.ylesanne_id))
             .filter(Valitudylesanne.testiylesanne_id==self.id)
             .join(Valitudylesanne.ylesanne)
             )

        if vy_seq is not None:
            q = q.filter(Valitudylesanne.seq==vy_seq)
        
        if toimumisaeg:
            # otsime ainult antud toimumisajal kasutusel olevate komplektide seast
            komplektid_id = [k.id for k in toimumisaeg.komplektid]
            if len(komplektid_id) == 1:
                q = q.filter(Valitudylesanne.komplekt_id==komplektid_id[0])
            else:
                q = q.filter(Valitudylesanne.komplekt_id.in_(komplektid_id))

        q = q.order_by(Hindamisaspekt.seq)
        li = []
        #aine_kood = self.testiosa.test.aine_kood
        aspekt = None
        for ha, vy_id  in q.all():
            a_kood = ha.aspekt_kood
            if not aspekt or aspekt.kood != a_kood:
                aspekt = Klrida.get_by_kood('ASPEKT', a_kood, ylem_kood=ha.aine_kood)
                if not aspekt:
                    log.error('ylesande %d aspekti %s pole aines %s olemas' % \
                              (ha.ylesanne_id, a_kood, ha.aine_kood))
                    continue
                if aspekt not in li:
                    li.append(aspekt)
            try:
                aspekt.y_hindamisaspektid[vy_id] = ha
            except AttributeError:
                # dicti y_hindamisaspektid pole loodud
                # dicti loomine võis toimuda selle funktsiooni sees,
                # aga võis olla ka juba mõne varasema ty.get_aspektid() sees
                aspekt.y_hindamisaspektid = {}
                aspekt.y_hindamisaspektid[vy_id] = ha

        if with_max:
            res = list()
            for aspekt in li:
                # max pallid ülesande skaalal, st kaalu arvestades
                max_pallid = max([(ha.max_pallid or 0)*ha.kaal for \
                                  ha in list(aspekt.y_hindamisaspektid.values())])
                res.append((aspekt, max_pallid))
            return res
        return li

    def get_normipunkt(self, normityyp):
        for r in self.normipunktid:
            if r.normityyp == normityyp:
                return r

    def copy_to(self, cp_testiplokk, cp_alatest, cp_testiosa, map_komplektid, map_hk, map_atk, map_grupp):
        """Testiülesanne ja selle antud komplekti valitudülesanded kopeeritakse
        antud testiploki, alatesti testiosa ja komplektide alla.
        map_komplektid on dict, mille key on vana komplekti id ja value on uus komplekt
        kopeeritakse ainult need valitudylesanded, mis on map_komplektid komplektide seas
        """
        cp = EntityHelper.copy(self)
        cp.testiplokk = cp_testiplokk
        cp.alatest = cp_alatest
        cp.testiosa = cp_testiosa
        self.copy_subrecords(cp, ['trans'])
    
        cp_hk = map_hk.get(self.hindamiskogum_id)
        if cp_hk:
            cp_hk.testiylesanded.append(cp)
        else:
            cp.hindamiskogum_id = None
            
        #cp_testiosa.give_default_hindamiskogum().testiylesanded.append(cp)
        map_vy = {}
        for komplekt_id, cp_komplekt in map_komplektid.items():
            #for vy in ty.valitudylesanded: - see ei leidnud yhel juhul kõiki millegipärast üles
            valitudylesanded = list(Valitudylesanne.query.filter_by(testiylesanne_id=self.id).filter_by(komplekt_id=komplekt_id).all())
            for vy in valitudylesanded:
                cp_vy = EntityHelper.copy(vy)
                cp_vy.test_id = None
                cp_vy.komplekt = cp_komplekt
                cp_vy.testiylesanne = cp
                map_vy[vy.id] = cp_vy
                cp_hk = map_hk.get(vy.hindamiskogum_id)
                if cp_hk:
                    cp_hk.valitudylesanded.append(cp_vy)
                else:
                    cp_vy.hindamiskogum_id = None

            for vy in valitudylesanded:
                cp_vy = map_vy[vy.id]
                for gy in vy.grupiylesanded:
                    cp_gy = gy.copy(ignore=['valitudylesnne_id'])
                    cp_vy.grupiylesanded.append(cp_gy)
                    cp_gy.ylesandegrupp = map_grupp[gy.ylesandegrupp_id]
        # for normipunkt in self.normipunktid:
        #     cp_normipunkt = normipunkt.copy()
        #     cp_normipunkt.alatestigrupp = map_atk.get(normipunkt.alatestigrupp_id)
        #     cp.normipunktid.append(cp_normipunkt)
        return cp

    @property
    def aine_kood(self):
        testiosa = self.testiosa or Testiosa.get(self.testiosa_id)
        return testiosa.test.aine_kood

    @property
    def teema_nimi(self):
        if self.teema_kood:
            teema = Klrida.get_by_kood('TEEMA', self.teema_kood, ylem_kood=self.aine_kood)
            if teema:
                self.teema_id = teema.id
                return teema.nimi
        self.teema_id = None # valdkond puudub

    @property
    def alateema_nimi(self):
        if self.teema_kood and self.alateema_kood:
            if not self.teema_id:
                self.teema_nimi # leitakse self.teema_id
            return Klrida.get_str('ALATEEMA', self.alateema_kood, ylem_id=self.teema_id)

    @property
    def tyyp_nimi(self):
        "Sisuploki tüübi nimetus eesti keeles"
        opt = usersession.get_opt()
        return opt.get_name('interaction_block', self.tyyp) or \
               opt.get_name('interaction', self.tyyp)

    @property
    def on_valikylesanne(self):
        return self.valikute_arv > 1

    @property
    def sisestusviis_nimi(self):
        sisestusviis = {const.SISESTUSVIIS_VASTUS: _("Vastused"),
                        const.SISESTUSVIIS_OIGE: _("Õige/vale"),
                        const.SISESTUSVIIS_PALLID: _("Punktid"),
                        }
        return sisestusviis.get(self.sisestusviis)

    def give_valitudylesanne(self, komplekt, seq=1, ylesanne_id=None):
        """Kontrollitakse, kas antud komplektis on valitudülesanne olemas.
        Kui pole, siis luuakse (tühi kirje).
        """
        item = self.get_valitudylesanne(komplekt, seq, ylesanne_id)
        if not item:
            item = Valitudylesanne(komplekt=komplekt,
                                   testiylesanne=self,
                                   seq=seq,
                                   ylesanne_id=ylesanne_id)
            self.valitudylesanded.append(item)
        return item

    def get_valitudylesanne(self, komplekt, seq=1, ylesanne_id=None):
        found = None
        for item in self.valitudylesanded:
            if komplekt is None or item.komplekt_id == komplekt.id or \
                   not komplekt.id and item.komplekt == komplekt:
                if ylesanne_id:
                    if item.ylesanne_id == ylesanne_id:
                        found = item
                        break
                elif item.seq == int(seq):
                    found = item
                    break
        return found

    def getq_valitudylesanne(self, komplekt_id, seq=1, ylesanne_id=None, vali=False):
        q = (Session.query(Valitudylesanne)
             .filter(Valitudylesanne.testiylesanne_id==self.id)
             )
        if komplekt_id:
            q = q.filter_by(komplekt_id=komplekt_id)
        if ylesanne_id:
            q = q.filter_by(ylesanne_id=ylesanne_id)
        else:
            if vali and self.valik_auto and self.valikute_arv > 1:
                seq = random.randint(1, self.valikute_arv)
            q = q.filter_by(seq=seq)
        return q.first()

    def give_valitudylesanded(self, komplekt):
        """Kontrollitakse, kas antud komplektis on valitudülesanne olemas.
        Kui pole, siis luuakse (tühi kirje).
        """
        #on_diagnoosiv = self.testiosa.diagnoosiv
        indeks = list(range(1, (self.valikute_arv or 1) + 1))
        li = []
        for item in self.valitudylesanded:
            if item.komplekt == komplekt:
                if item.seq in indeks:
                    indeks.remove(item.seq)
                    li.append(item)
                else:
                    #if item.id and not on_diagnoosiv:
                    item.delete()

        for seq in indeks:
            item = Valitudylesanne(komplekt=komplekt,
                                   testiylesanne=self,
                                   seq=seq)
            self.valitudylesanded.append(item)
            li.append(item)
                
        return li

    def get_komplektivalik(self):
        if self.alatest:
            return self.alatest.komplektivalik
        else:
            return self.testiosa.get_komplektivalik()

    def update_parent_stat(self):
        if self.testiplokk_id:
            testiplokk = self.testiplokk or Testiplokk.get(self.testiplokk_id)
            testiplokk.ylesannete_arv = len(testiplokk.testiylesanded)
            testiplokk.max_pallid = sum([y.max_pallid or 0 for y in testiplokk.testiylesanded if y.max_pallid])
            self.alatest_id = testiplokk.alatest_id
        if self.alatest_id:
            alatest = self.alatest or Alatest.get(self.alatest_id)
            alatest.ylesannete_arv = len(alatest.testiylesanded)
            alatest.max_pallid = sum([y.max_pallid or 0 for y in alatest.testiylesanded if y.max_pallid])

        testiosa = self.testiosa or Testiosa.get(self.testiosa_id)
        testiosa.ylesannete_arv = len(testiosa.testiylesanded)
        testiosa.test.arvuta_pallid(True)
            
        hkogum = self.hindamiskogum or \
            self.hindamiskogum_id and Hindamiskogum.get(self.hindamiskogum_id)
        if hkogum:
            hkogum.arvuta_pallid(testiosa.lotv)

    def update_koefitsient(self):
        for vy in self.valitudylesanded:
            vy.update_koefitsient(self)

    def delete_subitems(self):    
        self.delete_subrecords(['valitudylesanded',
                                'normipunktid',
                                ])

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        testiosa = self.testiosa or self.testiosa_id and Testiosa.get(self.testiosa_id)
        if testiosa:
            testiosa.logi('Testiülesanne %s %s' % (self.id, liik), vanad_andmed, uued_andmed, logitase)
