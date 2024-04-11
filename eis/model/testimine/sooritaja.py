"Testikorralduse andmemudel"

from eis.model.entityhelper import *
from eis.model.klassifikaator import Klrida
from eis.model.kasutaja import *
from eis.model.test import *
from .kandideerimiskoht import Kandideerimiskoht
from .labiviija import Labiviija
from .sooritajalogi import Sooritajalogi
from .sooritus import Sooritus
from .vaie import Vaie
from .testikoht import Testikoht
from .testimiskord import Testimiskord
from .testiopetaja import Testiopetaja
from .testiparoolilogi import Testiparoolilogi
from .toovaataja import Toovaataja
_ = usersession._

class Sooritaja(EntityHelper, Base):
    """Testi.sooritaja (registreerimisnimekirja kanne)
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False) # viide testile
    test = relationship('Test', foreign_keys=test_id)
    #test = relationship('Test', foreign_keys=test_id, back_populates='sooritajad')
    testimiskord_id = Column(Integer, ForeignKey('testimiskord.id'), index=True) # viide testimiskorrale (avaliku vaate testi korral puudub)
    testimiskord = relationship('Testimiskord', back_populates='sooritajad')
    kursus_kood = Column(String(10)) # valitud kursus, lai või kitsas (matemaatika korral), klassifikaator KURSUS
    nimekiri_id = Column(Integer, ForeignKey('nimekiri.id'), index=True) # viide registreerimisnimekirjale
    nimekiri = relationship('Nimekiri', foreign_keys=nimekiri_id, back_populates='sooritajad')
    klaster_id = Column(Integer) # sooritamiseks määratud klaster
    staatus = Column(Integer, nullable=False) # olek, soorituste madalaim olek, välja arvatud "registreeritud": 0=const.S_STAATUS_TYHISTATUD - tühistatud; 1=const.S_STAATUS_REGAMATA - registreerimata; 2=const.S_STAATUS_TASUMATA - tasumata; 3=const.S_STAATUS_REGATUD - registreeritud; 5=const.S_STAATUS_ALUSTAMATA - alustamata; 6=const.S_STAATUS_POOLELI - pooleli; 7=const.S_STAATUS_KATKESTATUD - ise katkestanud; 8=const.S_STAATUS_TEHTUD - tehtud; 9=const.S_STAATUS_EEMALDATUD - eemaldatud; 10=const.S_STAATUS_PUUDUS - puudus; 12=const.S_STAATUS_KATKESPROT - protokollil katkestanuks märgitud
    opetajatest = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas on õpetaja test.sooritus (taustaküsitluse korral, kus nimekirjas on koos õpilaste küsitlused ja õpetaja küsitlus)
    reg_aeg = Column(DateTime, nullable=False) # registreerimise aeg
    regviis_kood = Column(String(10), nullable=False, index=True) # registreerimisviis: 1=const.REGVIIS_SOORITAJA - ise EISi kaudu; 3=const.REGVIIS_KOOL_EIS - kool EISi kaudu; 4=const.REGVIIS_EKK - eksamikeskus; 5=const.REGVIIS_XTEE - ise eesti.ee portaali kaudu; 6=const.REGVIIS_EELVAADE - testi sooritamine eelvaates (ajutine kirje)
    reg_auto = Column(Boolean) # kas registreering jäi pooleli ja kinnitati Innove poolt automaatselt
    muutmatu = Column(Integer) # NULL - kool saab registreeringut muuta ja kustutada; 1=const.MUUTMATU_TYHISTAMATU - kool saab registreeringut muuta, kuid ei saa kustutada; 2=const.MUUTMATU_MUUTMATU - kool ei saa registreeringut muuta ega kustutada
    vanem_nous = Column(Boolean) # vanema nõusolek (psühholoogilise testi korral)
    testiopetajad = relationship('Testiopetaja', order_by='Testiopetaja.opetaja_kasutaja_id', cascade='all', back_populates='sooritaja')
    esitaja_kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # nimekirja esitaja
    esitaja_kasutaja = relationship('Kasutaja', foreign_keys=esitaja_kasutaja_id, back_populates='esitatud_sooritajad')
    esitaja_koht_id = Column(Integer, ForeignKey('koht.id'), index=True) # õppeasutus, nimekirja esitaja
    esitaja_koht = relationship('Koht', foreign_keys=esitaja_koht_id, back_populates='sooritajad')
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide.sooritaja kirjele
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='sooritajad')
    eesnimi = Column(String(50)) # testi sooritamise ajal kehtinud eesnimi
    perenimi = Column(String(50)) # testi sooritamise ajal kehtinud perekonnanimi
    algus = Column(DateTime) # varaseima soorituse algus
    lang = Column(String(2), nullable=False) # soorituskeel 
    piirkond_id = Column(Integer, ForeignKey('piirkond.id'), index=True) # soovitud piirkond
    piirkond = relationship('Piirkond', foreign_keys=piirkond_id)
    sooritused = relationship('Sooritus', order_by='Sooritus.id', back_populates='sooritaja')
    pallid = Column(Float) # testi eest saadud hindepallid, testi lõpptulemus pallides
    osapallid = Column(Float) # testiosade hindepallide summa (riigieksami korral võib see erineda lõpptulemusest, juhul kui.sooritaja on mõnest testiosast vabastatud)
    tulemus_protsent = Column(Float) # testiosade hindepallide summa protsentides.sooritaja suurimast võimalikust pallide summast
    tulemus_piisav = Column(Boolean) # kas test on sooritatud positiivselt (TE, SE korral saab väljastada tunnistuse)
    yhisosa_pallid = Column(Float) # testimiskordade ühisossa kuuluvate küsimuste eest saadud hindepallid
    hinne = Column(Integer) # testi eest saadud hinne, vahemikus 1-5
    hindamine_staatus = Column(Integer, sa.DefaultClause('0'), nullable=False) # hindamise olek: 0=const.H_STAATUS_HINDAMATA - kõik testiosad hindamata; 1=const.H_STAATUS_POOLELI - mõni testiosa hindamisel; 6=const.H_STAATUS_HINNATUD - kõik testiosad hinnatud; 10=const.H_STAATUS_TOOPUUDU - töö puudub ja ei hinnata
    mujalt_tulemus = Column(Boolean) # kas testi kogutulemus on saadud mujalt (rv tunnistuselt) või liidab EIS testiosade tulemused kokku
    keeletase_kood = Column(String(10)) # eksamiga hinnatud keeleoskuse tase
    ajakulu = Column(Integer) # kulutatud sekundite arv kõigi testiosade peale kokku
    tasu = Column(Float) # testi sooritamise eest tasutav summa
    tasutud = Column(Boolean) # kas on tasutud (NULL - pole tasuline, false - tasuline ja tasumata, true - tasuline ja tasutud)
    soovib_konsultatsiooni = Column(Boolean) # kas.sooritaja soovib konsultatsiooni
    reg_markus = Column(Text) #.sooritaja enda märkused
    markus = Column(Text) # märkused
    on_erivajadused = Column(Boolean) # kas on eritingimusi
    kontakt_nimi = Column(String(100)) # eritingimustega.sooritaja kontaktisiku nimi
    kontakt_epost = Column(String(100)) # eritingimustega.sooritaja kontaktisiku e-posti aadress
    regteateaeg = Column(DateTime) # viimati registreerimise teate saatmise aeg
    meeldetuletusaeg = Column(DateTime) # viimati meeldetuletuse (soorituskoha teate) aeg
    teavitatud_epost = Column(DateTime) # viimati tulemusest e-postiga teavitamise aeg
    teavitatud_sms = Column(DateTime) # viimati tulemusest SMSiga teavitamise aeg
    kool_koht_id = Column(Integer, ForeignKey('koht.id'), index=True) # viide.sooritaja õppeasutusele, kui sooritaja käib kuskil koolis
    kool_koht = relationship('Koht', foreign_keys=kool_koht_id, back_populates='sooritajad')
    koolinimi_id = Column(Integer, ForeignKey('koolinimi.id'), index=True) # viide testi sooritamise ajal kehtinud õppimiskoha nime kirjele
    koolinimi = relationship('Koolinimi')
    kool_aadress_kood1 = Column(String(4)) # õppimiskoha maakonna kood testi sooritamise ajal (statistika jaoks)
    kool_aadress_kood2 = Column(String(4)) # õppimiskoha omavalitsuse kood testi sooritamise ajal (statistika jaoks)
    kool_piirkond_id = Column(Integer, ForeignKey('piirkond.id'), index=True) # õppimiskoha piirkond testi sooritamise ajal (statistika jaoks)
    kool_piirkond = relationship('Piirkond', foreign_keys=kool_piirkond_id)
    klass = Column(String(10)) # klass, milles õpib (statistika jaoks)
    paralleel = Column(String(40)) # paralleel, milles õpib (statistika jaoks)
    oppekeel = Column(String(25)) # õppekeele kood EHISe klassifikaatoris: E - eesti; I - inglise; D - saksa; S - soome; V - vene
    oppeaasta = Column(Integer) # õppeaasta (kevade aasta), millal.sooritaja oli näidatud klassis (statistika jaoks)
    oppevorm_kood = Column(String(10)) # õppevorm, klassifikaator OPPEVORM (statistika jaoks)
    oppekava_kood = Column(String(25)) # õppekava EHISe klassifikaatoris (statistika jaoks)
    amet_kood = Column(String(10)) #.sooritaja amet, klassifikaator AMET
    amet_muu = Column(String(100)) # amet (kui amet_kood on muu või kui pole klassifikaatorist valitud)
    tvaldkond_kood = Column(String(10)) #.sooritaja töövaldkond, klassifikaator TVALDKOND
    tvaldkond_muu = Column(String(100)) # töövaldkond (kui tvaldkond_kood on muu)
    isikukaart_id = Column(Integer) # EHISe isikukaardi ID (kui testimiskord.reg_piirang=H)
    haridus_kood = Column(String(10)) # sooritaja haridus, klassifikaator HARIDUS
    rahvus_kood = Column(String(10)) # rahvus (rahvusvahelise keeleeksami korral), klassifikaatorist
    synnikoht_kodakond_kood = Column(String(10)) # sünnikoha riik (rahvusvahelise keeleeksami korral), kodakondsuse klassifikaatorist
    synnikoht = Column(String(100)) # sünnikoha asula
    kodakond_kood = Column(String(3)) # sooritaja kodakondsus, klassifikaator KODAKOND (Statistikaameti riikide ja territooriumide klassifikaator RTK)
    ema_keel_kood = Column(String(10)) # emakeel (oli kuni 2017-10 rahvusvahelise vene keele eksami korral), keelte klassifikaatorist
    doknr = Column(String(20)) # passi või id-kaardi number (oli kuni 2017-10 rahvusvahelise vene keele eksami korral)
    oppimisaeg = Column(Integer) # mitu aastat on keelt õppinud (oli kuni 2017-10 rahvusvahelise vene keele eksami korral)
    eesnimi_ru = Column(String(75)) # eesnimi vene keeles (rahvusvahelise vene keele eksami korral)
    perenimi_ru = Column(String(75)) # perekonnanimi vene keeles (rahvusvahelise vene keele eksami korral)
    valimis = Column(Boolean, sa.DefaultClause('0'), nullable=False) # true - sooritaja on valimis (kui valim on eraldatud testimiskorra sees, mitte eraldi testimiskorraga)
    vaie = relationship('Vaie', uselist=False, back_populates='sooritaja')
    vabastet_kirjalikust = Column(Boolean) # kas soovib vabastust kirjalikust osast (B1 tasemeeksami korral, kui.sooritaja on vähemalt 65-aastane)
    tulemus_aeg = Column(DateTime) # tulemuse viimase muutmise aeg
    testiparool = Column(String(97)) # testiparooli räsi
    testiparoolilogid = relationship('Testiparoolilogi', order_by=sa.desc(Testiparoolilogi.id), back_populates='sooritaja')
    sooritajalogid = relationship('Sooritajalogi', order_by='Sooritajalogi.id', back_populates='sooritaja')
    testitunnistused = relationship('Testitunnistus', order_by='Testitunnistus.id', back_populates='sooritaja')
    sooritajakirjad = relationship('Sooritajakiri', order_by='Sooritajakiri.id', back_populates='sooritaja')
    oppekohad = relationship('Oppekoht', order_by='Oppekoht.id', back_populates='sooritaja')    
    rvsooritajad = relationship('Rvsooritaja', back_populates='sooritaja')
    kandideerimiskohad = relationship('Kandideerimiskoht')
    __table_args__ = (
        sa.UniqueConstraint('kasutaja_id','testimiskord_id', 'test_id'),
        )
    _parent_key = 'nimekiri_id'
    logi_pohjus = None # seatakse siis, kui on vaja andmete muutmisel logisse põhjus märkida
    _logi = None # jooksev muudatuste logimise kirje
    
    @property
    def lang_nimi(self):
        if self.lang:
            return Klrida.get_lang_nimi(self.lang)        

    @property
    def max_pallid(self):
        test = self.test
        if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
            # riigieksami max pallid on kõigile 100
            return test.max_pallid
        else:
            # muude eksamite max pallid on võimalike testiosade pallide summa
            return self.max_osapallid

    @property
    def max_osapallid(self):
        "Testiosade soorituste võimalike max pallide summa"
        p = sum([s.max_pallid for s in self.sooritused \
                 if s.max_pallid and s.staatus != const.S_STAATUS_VABASTATUD])
        if p and round(p) != p:
            if self.test.ymardamine:
                p = round(p)
        return p
    
    @property
    def keeletase_nimi(self):
        kood = self.keeletase_kood
        if kood:
            return Klrida.get_str('KEELETASE', kood, ylem_kood=self.test.aine_kood)

    @property
    def kursus_nimi(self):
        if self.kursus_kood:
            aine = self.test and self.test.aine_kood
            if aine:
                return Klrida.get_str('KURSUS', self.kursus_kood, ylem_kood=aine)            

    @property 
    def staatus_nimi(self):
        return usersession.get_opt().S_STAATUS.get(self.staatus)

    @property
    def hindamine_staatus_nimi(self):
        return usersession.get_opt().H_STAATUS.get(self.hindamine_staatus)

    @property
    def piirkond_nimi(self):
        if self.piirkond_id:
            rcd = Piirkond.get(self.piirkond_id)
            if rcd:
                return rcd.nimi

    @property
    def kohavalik_nimi(self):
        """Esimese testiosa sooritamise koht ja aeg,
        kasutusel siis, kui tk.reg_kohavalik=true ja koht on regamisel valitud
        """
        from eis.lib.helpers import str_from_datetime, str_time_from_datetime
        for tos in self.sooritused:
            try:
                txt = tos.testikoht.koht.nimi
                testiruum = tos.testiruum
                if not testiruum.lopp:
                    algus = str_from_datetime(testiruum.algus, hour0=False)
                elif testiruum.lopp.date() == testiruum.algus.date():
                    algus = str_from_datetime(testiruum.algus) + ' - ' + str_time_from_datetime(testiruum.lopp)
                else:
                    algus = str_from_datetime(testiruum.algus, hour0=False) + ' - ' + str_from_datetime(testiruum.lopp, hour23=False)
                if algus:
                    txt += ' ' + algus
                return txt
            except Exception as ex:
                log.debug(f'kohavalik_nimi: {ex}')
            
    @property
    def synnikoht_kodakond_nimi(self):
        return Klrida.get_str('KODAKOND', self.synnikoht_kodakond_kood)

    def osalemine_nahtav(self, tugi, test, testimiskord):
        "Kas sooritamise kirje on sooritajale või tugiisikule nähtav"
        if tugi:
            osalemine = test.vastus_tugiisikule
        else:
            if testimiskord:
                osalemine = testimiskord.osalemise_naitamine
            else:
                osalemine = not test.osalemise_peitmine
        return osalemine

    def tulemus_nahtav(self, sooritus, app_ekk, isik, test=None, testimiskord=None, nimekiri=None):
        "Kas vastused ja tulemus on nähtavad"
        # vastus nähtav, kogutulemus nähtav, alatestide tulemused nähtavad, tagasiside nähtav

        is_resp = is_k = is_a = is_y = is_ts = False

        item = sooritus or self
        if not testimiskord:
            testimiskord = self.testimiskord
        if not test:
            test = self.test

        # kas võib näha sooritamise kirjet?
        tugi = isik == const.ISIK_TUGI
        osalemine = app_ekk or self.osalemine_nahtav(tugi, test, testimiskord)
        
        # kas võib näha tulemusi?
        if item.staatus == const.S_STAATUS_TEHTUD and osalemine:
            is_resp = is_k = is_a = is_y = True
            if not app_ekk:
                # avalik vaade, kontrollime nähtavust sooritajale või tugiisikule
                if isik == const.ISIK_TUGI and not test.tulemus_tugiisikule:
                    # kas tulemus on tugiisikule lubatud
                    is_k = is_a = is_y = False

                #elif testimiskord and testimiskord.on_eeltest and test.testiliik_kood == const.TESTILIIK_DIAG2:
                #    # tulemused on nähtavad EI VÕI NII vt ES-2139
                #    pass
                
                elif testimiskord:
                    # testimiskorraga test
                    is_resp = testimiskord.ylesanded_avaldet
                    is_k = testimiskord.koondtulemus_avaldet
                    is_a = testimiskord.alatestitulemused_avaldet
                    is_y = testimiskord.ylesandetulemused_avaldet
                    eeltest = test.eeltest
                    if eeltest:
                        if isik in (const.ISIK_SOORITAJA, const.ISIK_TUGI):
                            is_ts = eeltest.tagasiside_sooritajale
                        elif isik == const.ISIK_KOOL:
                            is_ts = eeltest.tagasiside_koolile
                    if self.vaie_ettepandud:
                        is_k = is_a = is_y = False

                elif test.testiliik_kood == const.TESTILIIK_KUTSE:
                    # testimiskorrata kutseeksami tulemus on nähtav siis, kui nimekirjas on nii seatud
                    if not nimekiri:
                        nimekiri = self.nimekiri

                    if nimekiri:
                        is_k = nimekiri.tulemus_nahtav
                        is_a = nimekiri.alatestitulemus_nahtav
                        is_resp = is_y = not nimekiri.vastus_peidus
                else:
                    # testimiskorrata test
                    if not nimekiri:
                        nimekiri = self.nimekiri
                    if nimekiri:
                        is_k = nimekiri.tulemus_nahtav
                        is_a = is_y = nimekiri.alatestitulemus_nahtav

                if test.salastatud:
                    is_resp = False

        class Visibility:
            def __init__(self, osalemine, is_resp, is_k, is_a, is_y, is_ts):
                self.osalemine = osalemine # kas võib soorituse kirjet näha
                self.is_resp = is_resp # kas võib vastuseid vaadata
                self.is_k = is_k # kas võib koondtulemust vaadata
                self.is_a = is_a # kas võib alatesti tulemust vaadata
                self.is_y = is_y # kas võib ylesande tulemust vaadata
                self.is_ts = is_ts or is_k # kas võib tagasisidet vaadata
        return Visibility(osalemine, is_resp, is_k, is_a, is_y, is_ts)

    def get_tulemus(self, nl=True, st=True, digits=3):
        """Leitakse testi lõplikud pallid koos max pallide ja protsentidega
        """
        pallid = self.pallid
        max_pallid = self.max_pallid
        if pallid is None:
            return None
        test = self.test
        buf = ''
        if not test.pallideta:
            # pallid on
            buf = '%sp' % (fstr(pallid, digits))
            if max_pallid and not test.protsendita:
                buf += ' %s-st' % (fstr(max_pallid, digits))
                if self.tulemus_protsent is not None:
                    buf += ', %s%%' % (fstr(self.tulemus_protsent, digits))
        elif not test.protsendita:
            # palle pole, protsent on
            if self.tulemus_protsent is not None:
                buf = '%s%%' % (fstr(self.tulemus_protsent, digits))                
        if self.hinne:
            if nl:
                buf += '<br/>'
            buf += ' hinne "%s"' % (self.hinne)
        return buf
    
    def get_yhisosa_tulemus(self, digits=3):
        """Leitakse testi ühisosa lõplikud pallid koos max pallide ja protsentidega
        """
        pallid = self.yhisosa_pallid
        if pallid is not None:
            max_pallid = self.test.yhisosa_max_pallid
            if not max_pallid:
                return fstr(pallid, digits)
            return '%sp %s-st, %s%%' % (fstr(pallid, digits), 
                                        fstr(max_pallid, digits), 
                                        fstr(pallid*100/max_pallid, digits))

    def update_staatus(self):
        """Sooritaja staatuse uuendamine vastavalt soorituste staatustele.
        """
        staatus = None
        pallid = yhisosa_pallid = None
        on_tegemata = on_alustanud = on_alustamata = False
        on_mitu_osa = False
        for rcd in self.sooritused:
            if staatus:
                on_mitu_osa = True
                staatus = min(staatus, rcd.staatus)
            else:
                staatus = rcd.staatus

            if rcd.staatus >= const.S_STAATUS_POOLELI and \
               rcd.staatus != const.S_STAATUS_VABASTATUD:
                on_alustanud = True
            elif rcd.staatus == const.S_STAATUS_ALUSTAMATA:
                on_alustamata = True
            if rcd.staatus < const.S_STAATUS_TEHTUD:
                on_tegemata = True

            if rcd.pallid is not None:
                if rcd.staatus == const.S_STAATUS_EEMALDATUD:
                    rcd.pallid = rcd.yhisosa_pallid = 0
                elif rcd.staatus == const.S_STAATUS_PUUDUS:
                    rcd.pallid = rcd.yhisosa_pallid = 0
                elif rcd.staatus == const.S_STAATUS_VABASTATUD:
                    rcd.pallid = rcd.yhisosa_pallid = None

            if rcd.pallid is not None:
                if pallid is None:
                    pallid = 0
                pallid += rcd.pallid

            if rcd.yhisosa_pallid is not None:
                if yhisosa_pallid is None:
                    yhisosa_pallid = 0
                yhisosa_pallid += rcd.yhisosa_pallid

        # yheosalise testi olek on testiosa sooritamise olek
        if on_mitu_osa and on_tegemata:
            # mitmeosalise testi olek on:
            # - madalaim tehtud soorituse olek, kui kõik osad tehtud;
            # - muidu pooleli, kui on mõnda osa alustanud;
            # - muidu alustamata, kui mõni osa on "alustamata"
            # - muidu madalaim osa olek
            if on_alustanud:
                staatus = const.S_STAATUS_POOLELI
            elif on_alustamata:
                staatus = const.S_STAATUS_ALUSTAMATA

        if staatus and staatus != self.staatus:
            self.staatus = staatus
        # pallide ja protsendi arvutamiseks on vaja
        # hiljem teha resultentry.update_sooritaja()

    def get_sooritus(self, testiosa_id=None, toimumisaeg_id=None):
        if testiosa_id:
            for rcd in self.sooritused:
                if rcd.testiosa_id == testiosa_id:
                    return rcd
        elif toimumisaeg_id:
            for rcd in self.sooritused:
                if rcd.toimumisaeg_id == toimumisaeg_id:
                    return rcd

    def give_sooritus(self, 
                      testiosa_id, 
                      staatus=const.S_STAATUS_REGATUD,
                      toimumisaeg=None):
        rcd = self.get_sooritus(testiosa_id)
        testiosa = Testiosa.get(testiosa_id)

        if not rcd:
            if not toimumisaeg:
                kord = self.testimiskord
                if not kord and self.testimiskord_id:
                    kord = Testimiskord.get(self.testimiskord_id)
                if kord:
                    toimumisaeg = kord.get_toimumisaeg(testiosa)

            rcd = Sooritus(sooritaja=self, 
                           toimumisaeg=toimumisaeg,
                           testiosa_id=testiosa.id,
                           staatus=staatus)
        if staatus > const.S_STAATUS_REGAMATA and\
                rcd.staatus < const.S_STAATUS_REGATUD:
            # registreering kinnitati
            rcd.staatus = staatus
        return rcd

    def give_sooritused(self, staatus=const.S_STAATUS_REGATUD):
        test = self.test or Test.get(self.test_id)
        kord = self.testimiskord
        if not kord and self.testimiskord_id:
            kord = Testimiskord.get(self.testimiskord_id)
        kool_koht_id = None
        if kord and kord.reg_voorad and staatus > const.S_STAATUS_REGAMATA \
           and self.esitaja_koht_id \
           and self.esitaja_koht_id != const.KOHT_EKK:
            # võõra esitanud kool
            kool_koht_id = self.esitaja_koht_id
        elif kord and kord.kool_testikohaks and staatus > const.S_STAATUS_REGAMATA:
            # õppimiskoht
            kool_koht_id = self.kool_koht_id or self.kool_koht and self.kool_koht.id
        else:
            # ei määrata kohe soorituskohta
            kool_koht_id = None

        for testiosa in test.testiosad:
            toimumisaeg = kord and kord.get_toimumisaeg(testiosa) or None
            rcd = self.give_sooritus(testiosa.id, 
                                     staatus=staatus,
                                     toimumisaeg=toimumisaeg)
            if self.vabastet_kirjalikust and testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_KP):
                rcd.on_erivajadused = True
                rcd.on_erivajadused_kinnitatud = True

            # hindamiskogumita hinnatakse testimiskorrata teste
            # ja eeltesti testimiskorraga teste (määratud eeltesti läbiviijale)
            rcd.hindamiskogumita = not toimumisaeg or test.avaldamistase == const.AVALIK_MAARATUD
            # olemasoleva soorituse kirje testikoht
            testikoht2 = rcd.testikoht
            if kool_koht_id and staatus != const.S_STAATUS_VABASTATUD and \
                   (not testikoht2 or testikoht2.koht_id != kool_koht_id):
                #.sooritaja õppeasutusest moodustame testikoha
                # ja vana testikoht puudub või ei sobi
                testikoht2 = Testikoht.give_testikoht(kool_koht_id,
                                                      testiosa.id,
                                                      toimumisaeg.id)
                testikoht2.gen_tahis()

            # olemasoleva soorituse testiruum
            old_testiruum = rcd.testiruum
            old_tpv = old_testiruum and old_testiruum.toimumispaev
            if testikoht2 and \
                (not old_testiruum or old_testiruum.testikoht_id != testikoht2.id or \
                 (self.valimis and old_tpv and old_tpv.valim == False) or \
                 (rcd.reg_toimumispaev_id and rcd.reg_toimumispaev_id != old_testiruum.toimumispaev_id)):
                # vana testiruum puudub või ei sobi
                # igaks juhuks kontrollime, kas testikohal on tähis (vana testikoht ES-2744)
                if not testikoht2.tahis:
                    testikoht2.gen_tahis()
                    Session.flush()
                testiruum2 = testikoht2.give_testiruum(toimumispaev_id=rcd.reg_toimumispaev_id, valimis=self.valimis)

                if rcd.testikoht != testikoht2 or rcd.testiruum != testiruum2:
                    # suunatud teise ruumi, tyhistame p-testi koguste arvutuse
                    if testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
                        if toimumisaeg.on_kogused:
                            toimumisaeg.on_kogused = 0
                        if toimumisaeg.on_hindamisprotokollid:
                            toimumisaeg.on_hindamisprotokollid = 0
                    if toimumisaeg.on_ymbrikud:
                        toimumisaeg.on_ymbrikud = 0 
                    rcd.suuna(testikoht2, testiruum2)
                    Session.flush()
                    testiruum2.set_sooritajate_arv()
                    testiruum2.give_labiviijad()
                    if old_testiruum:
                        old_testiruum.set_sooritajate_arv()
        return self.sooritused

    def set_vabastet(self, vabastet, force=False):
        # 65-aastane ja vanema kodakondsuse taotleja võib vabastada tasemeeksami
        # kirjutamise alatestist, sooritada tuleb kuulamise, lugemise ja rääkimisi alatestid
        if vabastet != self.vabastet_kirjalikust or force:
            self.vabastet_kirjalikust = vabastet
            self.on_erivajadused = vabastet
            for tos in self.sooritused:
                if tos.staatus == const.S_STAATUS_REGATUD:
                    if tos.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_KP):
                        tos.on_erivajadused = vabastet
                        tos.on_erivajadused_kinnitatud = vabastet and True or False
                        for alatest in tos.alatestid:
                            if alatest.alatest_kood == const.ALATEST_RK_KIRJUTAMINE:
                                # kui alatest.sooritus on juba olemas, siis märgime õige oleku
                                # kui ei ole olemas, siis märgib vabastuse give_alatestisooritus()
                                atos = tos.get_alatestisooritus(alatest.id)
                                if atos:
                                    atos.staatus = vabastet and const.S_STAATUS_VABASTATUD or const.S_STAATUS_REGATUD
                                break

    def delete_subitems(self):    
        self.delete_subrecords(['sooritused',
                                'oppekohad',
                                'sooritajalogid',
                                'kandideerimiskohad',
                                'sooritajakirjad',
                                'testiopetajad',
                                'testiparoolilogid',
                                ])

    @classmethod
    def get_by_kasutaja(cls, kasutaja_id, testimiskord_id):
        if kasutaja_id:
            q = cls.query.\
                filter_by(testimiskord_id=testimiskord_id).\
                filter(Sooritaja.kasutaja_id==kasutaja_id)
            return q.first()

    @property
    def vaie_ettepandud(self):
        """Kui on vaie, siis kas vaie on olekus, kus ettepanek/otsus on koostatud,
        kuid menetlust pole veel lõpetatud - siis ei ole tulemus veel avalik
        """
        vaie = self.vaie
        return vaie and vaie.staatus == const.V_STAATUS_ETTEPANDUD

    @property
    def vaie_esitatud(self):
        """Kas on olemas vaie (ei arvesta veel esitamata vaideid)
        """
        vaie = self.vaie
        return vaie and vaie.staatus > const.V_STAATUS_ESITAMATA

    def give_vaie(self):
        if not self.vaie:
            self.vaie = Vaie(sooritaja=self, 
                             pallid_enne=self.pallid or 0,
                             staatus=const.V_STAATUS_ESITAMATA)

            # jätame meelde pallid enne vaidlustamist
            for sooritus in self.sooritused:
                sooritus.pallid_enne_vaiet = sooritus.pallid
                for yv in sooritus.ylesandevastused:
                    yv.pallid_enne_vaiet = yv.pallid or 0
                    yv.toorpunktid_enne_vaiet = yv.toorpunktid
                    for va in yv.vastusaspektid:
                        va.pallid_enne_vaiet = va.pallid or 0
                        va.toorpunktid_enne_vaiet = va.toorpunktid

                for atos in sooritus.alatestisooritused:
                    atos.pallid_enne_vaiet = atos.pallid or 0

        return self.vaie
            
    @property
    def millal(self):
        alates = kuni = None
        for tos in self.sooritused:
            aeg = tos.algus or tos.kavaaeg
            if aeg:
                aeg = aeg.date()
                if not alates or alates > aeg:
                    alates = aeg
                if not kuni or kuni < aeg:
                    kuni = aeg
        if not alates:
            #.sooritaja pole veel kohale määratud
            if self.testimiskord:
                return self.testimiskord.millal
            return None
        if alates != kuni:
            return '%s - %s' % (alates.strftime('%d.%m.%Y'), kuni.strftime('%d.%m.%Y'))
        else:
            return alates.strftime('%d.%m.%Y')

    @classmethod
    def registreeri(cls, 
                    kasutaja, 
                    test_id, 
                    kord, 
                    lang, 
                    piirkond_id, 
                    regviis_kood, 
                    esitaja_kasutaja_id, 
                    esitaja_koht_id,
                    nimekiri=None, 
                    kinnitatud=False,
                    alustamata=False,
                    mittekorduv=True):

        """Eksaminandi registreerimine,.sooritaja lisamine
        """
        added = False # kas lisame uue.sooritaja kirje või mitte
        if not kasutaja.id:
           Session.flush()

        test = Test.get(test_id)
        if kord:
            kord_id = kord.id
        else:
            kord_id = None

        # kontrollime, kas on juba registreeritud (topelt ei või olla)
        def _get_by_k(kasutaja, kord_id, test_id):
            q = (Session.query(Sooritaja)
                 .filter_by(kasutaja_id=kasutaja.id)
                 .filter_by(test_id=test_id)
                 .filter_by(testimiskord_id=kord_id)) # kord_id võib ka NULL olla
            if not kord_id and test.korduv_sooritamine and nimekiri and \
                   test.avaldamistase in (const.AVALIK_SOORITAJAD,
                                          const.AVALIK_OPETAJAD,
                                          const.AVALIK_MAARATUD):
                # kui lubatud on korduv sooritamine,
                # siis võib mitu korda samale sooritajale suunata,
                # aga mitte samas nimekirjas
                q = q.filter_by(nimekiri_id=nimekiri.id)
            sooritaja = q.first()
            return sooritaja

        if (kord_id or mittekorduv) and (regviis_kood != const.REGVIIS_EELVAADE):
           sooritaja = _get_by_k(kasutaja, kord_id, test_id)
        else:
           sooritaja = None

        if kord:
            keeled = kord.get_keeled()
            if not lang or lang not in keeled:
                lang = keeled[0]

        if sooritaja:
            # on juba registreeritud, võib-olla ka tyhistatud
            if sooritaja.staatus == const.S_STAATUS_TYHISTATUD:
                if kinnitatud or alustamata:
                    staatus = sooritaja.tasutud == False and const.S_STAATUS_TASUMATA or const.S_STAATUS_REGATUD
                else:
                    staatus = const.S_STAATUS_REGAMATA
                for tos in sooritaja.sooritused:
                    tos.staatus = staatus
                sooritaja.logi_pohjus = 'registreerimine'
            elif sooritaja.staatus >= const.S_STAATUS_POOLELI:
                # ei saa enam ymber registreerida, sest ta on juba hakanud seda testi sooritama
                return False, None
            # uuendame nime
            sooritaja.eesnimi = kasutaja.eesnimi
            sooritaja.perenimi = kasutaja.perenimi
        else:
            # pole veel registreeritud

            if kord and kord.korduv_reg_keelatud:
                # sellele testimiskorrale ei või regada sama testi teistele testimiskordadele regatuid
                q = (Session.query(Sooritaja)
                     .filter_by(kasutaja_id=kasutaja.id)
                     .filter_by(test_id=test_id)
                     .filter(Sooritaja.testimiskord_id!=None)
                     .filter(Sooritaja.testimiskord_id!=kord.id)
                     )
                if q.count():
                    return False, None
                
            added = True

            # kas on tasuline test ja kui on, kas rakendada esma- või kordusosalemise tasu
            tasutud = tasu = None
            opilane = kasutaja.opilane_keskh
            if kord and (kord.osalemistasu or kord.kordusosalemistasu) and not opilane:
                # kordusosalemine on siis, kui isik ei ole praegu õppur
                # üldhariduskoolis ega kutsekoolis põhihariduse baasil
                # ja ta on samas aines mõne sama liiki testi varem teinud
                # ehk tal on selle kohta tulemus kirjas
                # otsime varasemaid sooritatud olekus registreerimisi
                esmane_staatus = (const.S_STAATUS_TEHTUD,
                                  const.S_STAATUS_EEMALDATUD,
                                  const.S_STAATUS_KATKESTATUD, 
                                  const.S_STAATUS_KATKESPROT)                
                q_kordus = (Sooritaja.query
                            .filter_by(kasutaja_id=kasutaja.id)
                            .filter(Sooritaja.staatus.in_(esmane_staatus))
                            .join(Sooritaja.test)
                            .filter(Test.aine_kood==test.aine_kood)
                            )
                if test.testiliik_kood in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
                    # rahvusvahelisi eksameid ja riigieksameid vaatleme koos
                    q_kordus = q_kordus.filter(Test.testiliik_kood.in_((const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV)))
                else:
                    q_kordus = q_kordus.filter(Test.testiliik_kood==test.testiliik_kood)
                kordus = q_kordus.count()
                if kordus:
                    tasu = kord.kordusosalemistasu
                else:
                    tasu = kord.osalemistasu
                if tasu:
                    tasutud = False

            # lisame uue kirje
            sooritaja = Sooritaja(kasutaja_id=kasutaja.id,
                                  eesnimi=kasutaja.eesnimi,
                                  perenimi=kasutaja.perenimi,
                                  test_id=test_id,
                                  testimiskord_id=kord_id,
                                  tasu=tasu,
                                  tasutud=tasutud,
                                  esitaja_kasutaja_id=esitaja_kasutaja_id,
                                  esitaja_koht_id=esitaja_koht_id,
                                  reg_aeg=datetime.now(),
                                  regviis_kood=regviis_kood,
                                  lang=lang,
                                  staatus=const.S_STAATUS_REGAMATA)
            try:
                Session.flush()
            except sa.exc.IntegrityError as e:
                sooritaja = _get_by_k(kasutaja, kord_id, test_id)
                log.info('uuesti sooritaja:%s' % str(sooritaja))
                if not sooritaja:
                    raise
            sooritaja.set_ehis_data()
            sooritaja.kodakond_kood = kasutaja.kodakond_kood

        sooritaja.lang = lang
        sooritaja.set_ehis_data()
        if nimekiri:
            sooritaja.nimekiri = nimekiri
        if piirkond_id:
            sooritaja.piirkond_id=piirkond_id

        if test.on_jagatudtoo:
            # jagatud töö korral võib alati kohe alustada
            alustamata = True
        if alustamata:
            kinnitatud = True

        if not kinnitatud and not alustamata:
            # regamine pole kinnitatud
            staatus = sooritaja.staatus
        elif sooritaja.tasutud == False:
            staatus = const.S_STAATUS_TASUMATA
        elif alustamata:
            staatus = const.S_STAATUS_ALUSTAMATA
        elif kinnitatud:
            staatus = const.S_STAATUS_REGATUD

        # loome testiosasoorituste kirjed
        sooritaja.give_sooritused(staatus=staatus)
        sooritaja.update_staatus()

        return added, sooritaja

    def kinnita_reg(self, reg_auto=False):
        "Registreeringu kinnitamine"
        self.reg_auto = reg_auto
        if self.tasutud == False:
            staatus = const.S_STAATUS_TASUMATA
        else:
            staatus = const.S_STAATUS_REGATUD

        # uuendame nime
        self.eesnimi = self.kasutaja.eesnimi
        self.perenimi = self.kasutaja.perenimi

        self.give_sooritused(staatus=staatus)
        self.update_staatus()

    def tyhista(self):
        self.staatus = const.S_STAATUS_TYHISTATUD
        for tos in list(self.sooritused):
            tos.staatus = const.S_STAATUS_TYHISTATUD
            # kui on määratud soorituskoht, siis see määramine kaotatakse
            if tos.testiprotokoll_id:
                tos.testiprotokoll_id = None
            if tos.testikoht_id:
                tos.testikoht_id = None
                tos.piirkond_id = None
            for r in tos.erivajadused:
                r.delete()
            tos.on_erivajadused = False
            if tos.testiruum_id:
                testiruum = tos.testiruum
                tos.testiruum = None
                tos.tahis = None
                tos.tahised = None
                Session.flush()
                testiruum.set_sooritajate_arv()
        self.on_erivajadused = False
        self.regteateaeg = None

    @classmethod
    def reg_tky_opetaja(cls, kasutaja, opilase_test, nimekiri):
        "Taustaküsitluse suunamine õpetajale"
        tky = opilase_test.opilase_taustakysitlus
        if tky:
            op_test = tky.opetaja_test
            esitaja_id = nimekiri.esitaja_kasutaja_id
            koht_id = nimekiri.esitaja_koht_id
            keeled = op_test.keeled
            lang = const.LANG_ET in keeled and const.LANG_ET or keeled[0]
            added, sooritaja = Sooritaja.registreeri(kasutaja, op_test.id, None, lang,
                                                     None, const.REGVIIS_KOOL_EIS,
                                                     esitaja_id, koht_id,
                                                     nimekiri, alustamata=True)
            if sooritaja:
                sooritaja.opetajatest = True
                return sooritaja
            
    @classmethod
    def get_tky_opetaja(cls, nimekiri_id):
        "Leitakse taustaküsitluse õpetaja testisooritus"
        q = (Session.query(Sooritaja)
             .filter_by(nimekiri_id=nimekiri_id)
             .filter_by(opetajatest=True))
        return q.first()
            
    def voib_reg(self):
        "Kas sooritaja registreerimisaeg veel käib"
        if self.staatus >= const.S_STAATUS_POOLELI:
            # enam ei saa midagi muuta
            return False
        tk = self.testimiskord
        if tk:
            dt = date.today()
            if tk.reg_sooritaja and \
               tk.reg_sooritaja_alates <= dt <= tk.reg_sooritaja_kuni:
                return True
            return False

    def kool_voib_tyhistada(self, koht_id, testiliik):
        """Kas kool saab registreerimist tühistada
        Registreerimisperioodi siin ei kontrollita!
        """
        if self.staatus <= const.S_STAATUS_TYHISTATUD or self.staatus >= const.S_STAATUS_POOLELI:
            return False
        if testiliik == const.TESTILIIK_SISSE:
            # võib tyhistada siis, kui tulemuste vaatamise õigust
            # pole teistele koolidele antud
            q = (Session.query(Kandideerimiskoht.id)
                 .filter(Kandideerimiskoht.koht_id!=koht_id)
                 .filter_by(sooritaja_id=self.id)
                 .filter_by(automaatne=False))
            return q.limit(1).count() == 0
        return True
            
    def set_password(self, parool, userid):
        "Testiparooli määramine"
        self.testiparool = hash_pwd(parool, userid=userid)
        k = Testiparoolilogi(sooritaja=self,
                             testiparool=self.testiparool)
        self.testiparoolilogid.append(k)
                        
    def set_ehis_data(self):
        """EHISe puhvris olevad andmed kopeeritakse avaldusele.
        """
        kool = None
        kasutaja = self.kasutaja or Kasutaja.get(self.kasutaja_id)
        opilane = kasutaja.opilane
        if opilane:
            kasutaja.from_opilane(opilane)
        if opilane:
            # pooleli õppimise andmed statistika jaoks
            kool = opilane.koht
            self.kool_koht = kool
            self.set_kool_data(kool)
            self.klass = opilane.klass
            self.paralleel = opilane.paralleel
            self.oppekeel = opilane.oppekeel
            self.oppeaasta = opilane.get_oppeaasta()
            self.oppevorm_kood = opilane.oppevorm_kood
            self.oppekava_kood = opilane.oppekava_kood
            self.eesnimi = opilane.eesnimi
            self.perenimi = opilane.perenimi
        else:
            self.kool_koht = None
            self.set_kool_data(None)
            self.klass = None
            self.paralleel = None
            self.oppekeel = kasutaja.oppekeel
            self.oppevorm_kood = None
            self.oppekava_kood = None
            self.eesnimi = kasutaja.eesnimi
            self.perenimi = kasutaja.perenimi

    def set_kool_data(self, kool):
        """Kooli statistiliste andmete salvestamine avaldusele statistika jaoks.
        Üldjuhul on need õppimiskoha andmed,
        välja arvatud TE/SE korral, mil kasutatakse soorituskoha andmeid
        """
        koolinimi = kool and kool.kehtiv_koolinimi or None
        aadress = kool and kool.aadress
        self.koolinimi = koolinimi
        self.kool_aadress_kood1 = aadress and aadress.kood1 or None
        self.kool_aadress_kood2 = aadress and aadress.kood2 or None
        self.kool_piirkond_id = kool and kool.piirkond_id or None

    @property
    def nimi(self):
        return '%s %s' % (self.eesnimi, self.perenimi)

    def get_osasooritused(self):
        """Iga testiosa kohta leitakse kas kõigi alatestide sooritused või testiosa sooritus
        """
        data = []
        for sooritus in self.sooritused:
            testiosa = sooritus.testiosa
            if testiosa.on_alatestid:
                for alatest in sooritus.alatestid:
                    atos = sooritus.get_alatestisooritus(alatest.id)
                    data.append((atos, alatest, sooritus))
            else:
                data.append((sooritus, testiosa, None))
        return data
    
    def get_konsultatsiooniruumid(self):
        """Leitakse sooritamisega samas kohas toimuvad konsultatsioonid.
        Kui selliseid pole, siis leitakse soovitud piirkonnas toimuvad konsultatsioonid.
        Tagastatakse konsultatsioonide testikohad.
        """
        from .testikoht import Testikoht
        from .testiruum import Testiruum
        from .toimumisaeg import Toimumisaeg
        from .testikonsultatsioon import Testikonsultatsioon
        
        # selle testimiskorra konsultatsioonid
        Konsultatsioonikoht = sa.orm.aliased(Testikoht)
        Konsultatsiooniruum = sa.orm.aliased(Testiruum)
        q = (Session.query(Konsultatsiooniruum.algus, Koht, Ruum.tahis)
             .join((Konsultatsioonikoht,
                    Konsultatsiooniruum.testikoht_id==Konsultatsioonikoht.id))
             .join(Konsultatsioonikoht.toimumisaeg)
             .join(Toimumisaeg.testimiskord)
             .join(Testimiskord.eksamikorrad)
             .filter(Testikonsultatsioon.eksam_testimiskord_id==self.testimiskord_id)
             .join(Konsultatsioonikoht.koht)
             .outerjoin(Konsultatsiooniruum.ruum)
             )
        
        # kas leidub konsultatsiooni samas kohas, kus ta eksamit teeb?
        q_kohas = (q.filter(Sooritus.sooritaja_id==self.id)
                   .join(Sooritus.testikoht)
                   .filter(Konsultatsioonikoht.koht_id==Testikoht.koht_id)
                   )
        if q_kohas.count() == 0 and self.piirkond:
            # kui ei leidu, siis otsime.sooritaja soovitud piirkonnast
            piirkonnad_id = self.piirkond.get_alamad_id()
            q = q.filter(Koht.piirkond_id.in_(piirkonnad_id))
        else:
            q = q_kohas
        return q.order_by(Konsultatsiooniruum.algus,Koht.nimi,Ruum.tahis).all()

    def log_update(self):
        log_fields = ('staatus',
                      'kursus_kood',
                      'eesnimi',
                      'perenimi',
                      'lang',
                      'pallid',
                      'hinne',
                      'keeletase_kood',
                      'tulemus_aeg')
        old_values, new_values = self._get_changed_values()
        if new_values:
            fields = [r[0] for r in new_values]
            found = False
            for key in log_fields:
                if key in fields:
                    found = True
                    break
            if found:
                if 'pallid' in fields or 'keeletase_kood' in fields:
                    self.tulemus_aeg = datetime.now()
                self.add_sooritajalogi()
                
    def log_insert(self):
        if self.pallid is not None:
            self.tulemus_aeg = datetime.now()
        self.add_sooritajalogi()

    def add_sooritajalogi(self):
        request = usersession.get_request()
        if request:
            environ = request.environ
            remote_addr = request.remote_addr
        else:
            environ = {}
            remote_addr = None
        server_addr = environ.get('HOSTNAME') or environ.get('SERVER_ADDR')
        if self.pallid is not None and self.testimiskord_id:
            sig_status = const.G_STAATUS_UNSIGNED # vajab allkirja
        else:
            sig_status = const.G_STAATUS_NONE # ei vaja allkirja

        if self._logi:
            self._logi.staatus = self.staatus
            self._logi.kursus_kood = self.kursus_kood
            self._logi.eesnimi = self.eesnimi
            self._logi.perenimi = self.perenimi
            self._logi.lang = self.lang
            self._logi.pallid = self.pallid
            self._logi.hinne = self.hinne
            self._logi.keeletase_kood = self.keeletase_kood
            self._logi.tulemus_aeg = self.tulemus_aeg
            self._logi.pohjus = self.logi_pohjus
            self._logi.sig_status = sig_status
        else:
            self._logi = \
                Sooritajalogi(sooritaja=self,
                              staatus=self.staatus,
                              kursus_kood=self.kursus_kood,
                              eesnimi=self.eesnimi,
                              perenimi=self.perenimi,
                              lang=self.lang,
                              pallid=self.pallid,
                              hinne=self.hinne,
                              keeletase_kood=self.keeletase_kood,
                              tulemus_aeg=self.tulemus_aeg,
                              pohjus=self.logi_pohjus,
                              sig_status=sig_status,
                              url=request and request.url[:100] or None,
                              remote_addr=remote_addr,
                              server_addr=server_addr)

    def has_permission(self, permission, perm_bit, lang=None, user=None):
        """Kontrollitakse jooksva kasutaja õigust
        """
        if not user:
            user = usersession.get_user()
        if not user:
            return False
        if permission == 'toovaatamine':
            # õigus testitööd vaadata
            today = date.today()
            q = (SessionR.query(sa.func.count(Toovaataja.id))
                 .filter_by(kasutaja_id=user.id)
                 .filter_by(sooritaja_id=self.id)
                 .filter(Toovaataja.kehtib_kuni>=today)
                 )
            return q.scalar() > 0
        if permission.startswith('ts-'):
            # kooli õigus näha.sooritaja individuaalset tagasisidet
            ts, sooritaja_id, tk_id = permission.split('-')
            sooritaja_id = int(sooritaja_id)
            tk = Testimiskord.get(tk_id)
            return Sooritaja.has_permission_ts(sooritaja_id, tk)
        if permission == 'regikuitk':
            # õigus ligipääsule registreerimisinfole eeldusel,
            # et kasutajal on olemas testimiskorrale regamise õigus
            if self.kool_koht_id == user.koht_id:
                return True
            #if perm_bit == const.BT_SHOW:
            # kas võõras õpilane on andnud loa minu koolil tulemusi vaadata
            q = (SessionR.query(Kandideerimiskoht.id)
                 .filter_by(koht_id=user.koht_id)
                 .filter_by(sooritaja_id=self.id))
            if q.count() > 0:
                return True
            # kas on kooli poolt regatud võõras (testimiskord.reg_voorad=True)
            if self.esitaja_koht_id == user.koht_id:
                return True
            
        return False

    @classmethod
    def has_permission_ts(cls, sooritaja_id, tk):
        "Kooli õigus näha.sooritaja individuaalset tagasisidet"
        rc = False
        user = usersession.get_user()
        if user:
            if tk.tulemus_koolile:
                # kooli õigus vaadata.sooritaja tagasisidet
                if user.on_avalikadmin:
                    # kasutaja on soorituskoha admin
                    rc = True
                else:
                    # kas isik on.sooritaja aineõpetaja?
                    q = (SessionR.query(Testiopetaja.id)
                        .filter(Testiopetaja.sooritaja_id==sooritaja_id)
                        .filter(Testiopetaja.opetaja_kasutaja_id==user.id)
                        )
                    if q.count() > 0:
                        rc = True
            if not rc and tk.tulemus_admin:
                # testi admini õigus vaadata.sooritaja tagasisidet
                q = (SessionR.query(Labiviija.testiruum_id)
                    .filter(Labiviija.kasutaja_id==user.id)
                    .filter(Labiviija.kasutajagrupp_id==const.GRUPP_T_ADMIN)
                    .join((Sooritus, Sooritus.testiruum_id==Labiviija.testiruum_id))
                    .filter(Sooritus.sooritaja_id==sooritaja_id)
                    )
                if q.count() > 0:
                    rc = True
        return rc

    
