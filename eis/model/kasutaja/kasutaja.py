import hashlib
import argon2
from unidecode import unidecode
from eis.model.entityhelper import *
from eis.model.koht import Koht, Aadress
from eis.model.klassifikaator import Klrida, Klvastavus

from .pedagoog import Pedagoog
from .kasutajaroll import Kasutajaroll
from .volitus import Volitus
from .kasutajagrupp import Kasutajagrupp
from .kasutajagrupp_oigus import Kasutajagrupp_oigus
from .aineprofiil import Aineprofiil
from .profiil import Profiil
from .kasutajaajalugu import Kasutajaajalugu

log = logging.getLogger(__name__)
_ = usersession._

class Kasutaja(EntityHelper, Base):
    """Kasutajakontod
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    isikukood = Column(String(50), unique=True) # isikukood (Eesti isikukood ilma riigi koodita, teiste riikide korral ees riigi ISO2 kood)
    synnikpv = Column(Date) # sünnikuupäev
    eesnimi = Column(String(50), nullable=False) # eesnimi
    perenimi = Column(String(50), nullable=False) # perekonnanimi
    nimi = Column(String(75), nullable=False) # ees- ja perekonnanimi (otsingute lihtsustamiseks)
    parool = Column(String(97)) # püsiparooli räsi
    muuda_parool = Column(Boolean) # pannakse True siis, kui parooli seab ametnik (mitte kasutaja ise); kui on True, siis sisselogimisel soovitatakse parooli muutma ja pannakse False (ka siis, kui kasutaja parooli ei muutnud)
    epost = Column(String(255)) # e-posti aadress
    epost_seisuga = Column(DateTime) # millal viimati kasutajalt e-posti aadress üle küsiti
    aadress_id = Column(Integer, ForeignKey('aadress.id'), index=True) # viide aadressile
    aadress = relationship('Aadress', foreign_keys=aadress_id)
    postiindeks = Column(String(5)) # postiindeks
    normimata = Column(String(200)) # normaliseerimata aadress - vabatekstiliselt sisestatud aadressi lõpp, mida ei olnud võimalik sisestada ADSi komponentide klassifikaatori abil
    telefon = Column(String(20)) # telefon
    sugu = Column(String(1)) # sugu (M,N) statistika jaoks, võetakse isikukoodist
    staatus = Column(Integer, nullable=False) # olek: 1 - aktiivne, 0 - kehtetu
    on_ametnik = Column(Boolean) # kas kasutaja on eksamikeskuse vaate kasutaja (kaasneb EKK vaate kasutaja roll, kehtivuse kuupäev on rolli juures)
    on_labiviija = Column(Boolean) # kas kasutaja on testide läbiviimisega seotud isik
    uiroll = Column(String(1)) # vaikimisi roll avalikus vaates: S=const.UIROLL_S - testisooritaja; K=const.UIROLL_K - kool (õpetaja või admin); P=const.UIROLL_P - koolipsühholoog
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True) # vaikimisi koht avalikus vaates (0 - sooritaja)
    koht = relationship('Koht', foreign_keys=koht_id) 
    kasutajarollid = relationship('Kasutajaroll', back_populates='kasutaja')
    kasutajaajalood = relationship('Kasutajaajalugu', order_by=sa.desc(Kasutajaajalugu.id), back_populates='kasutaja') # kasutaja paroolimuudatused
    esitaja_nimekirjad = relationship('Nimekiri', foreign_keys='Nimekiri.esitaja_kasutaja_id', back_populates='esitaja_kasutaja')
    ylesandegrupid = [] # jooksva ylesande jaoks kehtivad grupid
    testigrupid = [] # jooksva testi jaoks kehtivad grupid
    teavitustellimused = relationship('Teavitustellimus', back_populates='kasutaja')
    ametikoht_seisuga = Column(DateTime) # aeg, millal viimati uuendati EHISest pedagoogi ametikohti (juhul, kui EHISe päring õnnestus)
    ametikoht_proovitud = Column(DateTime) # aeg, millal viimati prooviti uuendada EHISest pedagoogi ametikohti (ka siis, kui päringu sooritamine ebaõnnestus)    
    opilane_seisuga = Column(DateTime) # aeg, millal viimati uuendati EHISest õpilase andmeid (erineb tabeli Opilane seisust selle poolest, et mitte-õpilastel ei ole tabeli Opilane kirjet)
    isikukaart_seisuga = Column(DateTime) # aeg, millal viimati uuendati EHISest töötamise andmeid
    isikukaart_id = Column(Integer, ForeignKey('isikukaart.id'), index=True) # viide viimasele isikukaardile
    rr_seisuga = Column(DateTime) # aeg, millal viimati uuendati isikuandmed Rahvastikuregistrist
    session_id = Column(String(255)) # viimase Innove vaate seansi id (beaker_cache.namespace, request.session.id)
    viimati_ekk = Column(DateTime) # millal viimati Innove vaatesse logis
    tunnistus_nr = Column(String(25)) # keskharidust tõendava tunnistuse nr
    tunnistus_kp = Column(Date) # keskharidust tõendava dokumendi väljastamise kuupäev
    lopetanud = Column(Boolean) # kas on täidetud lõpetamise tingimused (EISi kontrollitud)
    lopetanud_kasitsi = Column(Boolean) # kas on täidetud lõpetamise tingimused (käsitsi märgitud)
    lopetanud_pohjus = Column(String(100)) # lõpetamise tingimuste täidetuse käsitsi märkimise põhjus
    lopetamisaasta = Column(Integer) # eeldatav keskhariduse lõpetamise aasta (lõpetamise tingimuste täidetuse kontrolli jaoks)
    kool_koht_id = Column(Integer, ForeignKey('koht.id'), index=True) # keskhariduse omandamise kool
    kool_koht = relationship('Koht', foreign_keys=kool_koht_id)
    kool_nimi = Column(String(100)) # lõpetatud keskhariduse kooli nimi
    oppekeel = Column(String(25)) # õppekeele kood EHISe klassifikaatoris: E - eesti; I - inglise; D - saksa; S - soome; V - vene
    kodakond_kood = Column(String(3)) # sooritaja kodakondsus, klassifikaator KODAKOND (Statistikaameti riikide ja territooriumide klassifikaator RTK)
    synnikoht = Column(String(100)) # sünnikoht RRis (rahvusvahelise DELF prantsuse keele eksami jaoks, saadakse RRist, ise ei sisestata)
    lisatingimused = Column(String(200)) # sooritaja lisatingimused
    markus = Column(Text) # märkused kasutaja kohta
    bgcolor = Column(String(7)) # kasutajaliidese värv
    profiil = relationship('Profiil', uselist=False, back_populates='kasutaja')
    labiviijalepingud = relationship('Labiviijaleping', order_by='Labiviijaleping.testsessioon_id, Labiviijaleping.id', back_populates='kasutaja')
    aineprofiilid = relationship('Aineprofiil', order_by='Aineprofiil.id', back_populates='kasutaja')
    kasutajapiirkonnad = relationship('Kasutajapiirkond', back_populates='kasutaja')
    kasutajakohad = relationship('Kasutajakoht', back_populates='kasutaja')
    volitatu_volitused = relationship('Volitus', foreign_keys='Volitus.volitatu_kasutaja_id', order_by='Volitus.kehtib_alates', back_populates='volitatu_kasutaja')
    opilane_volitused = relationship('Volitus', foreign_keys='Volitus.opilane_kasutaja_id', order_by='Volitus.kehtib_alates', back_populates='opilane_kasutaja')
    nousolekud = relationship('Nousolek', back_populates='kasutaja')
    labiviijad = relationship('Labiviija', back_populates='kasutaja')
    tunnistused = relationship('Tunnistus', order_by='Tunnistus.id', back_populates='kasutaja')
    sooritajad = relationship('Sooritaja', foreign_keys='Sooritaja.kasutaja_id', order_by='Sooritaja.id', back_populates='kasutaja')
    esitatud_sooritajad = relationship('Sooritaja', foreign_keys='Sooritaja.esitaja_kasutaja_id', order_by='Sooritaja.id', back_populates='esitaja_kasutaja')
    pedagoogid = relationship('Pedagoog', back_populates='kasutaja') # kasutaja ametikohad õpetajana
    opilased = relationship('Opilane', back_populates='kasutaja', order_by=sa.desc(sa.text('Opilane.prioriteet'))) # kasutaja kirjed õpilasena
    hindamised = relationship('Hindamine', foreign_keys='Hindamine.hindaja_kasutaja_id', back_populates='hindaja_kasutaja') # hindajana hindamised
    kirjasaajad = relationship('Kirjasaaja', order_by='Kirjasaaja.id', back_populates='kasutaja') # kasutajale e-postiga saadetud teated
    tkvaatajad = relationship('Tkvaataja', order_by=sa.desc(sa.text('Tkvaataja.created')), back_populates='kasutaja')
    opperyhmaliikmed = relationship('Opperyhmaliige', back_populates='kasutaja') # õpilase kuulumine rühmadesse
    opperyhmad = relationship('Opperyhm', back_populates='kasutaja') # õpetaja õpilaste rühmad
    kasutajaprotsessid = relationship('Kasutajaprotsess', back_populates='kasutaja')

    @property
    def vanus(self):
        aastad, kuud = self.get_vanus()
        return aastad

    @property
    def tais_aadress(self):
        buf = ''
        a = self.aadress
        if a:
            buf = a.tais_aadress
        if self.normimata:
            buf += ' ' + self.normimata
        return buf

    @property
    def aadress_korras(self):
        "Kas postiaadress on piisavalt täpne, et sellele kirju saata"
        if self.postiindeks:
            aadress = self.aadress
            if aadress:
                if aadress.kood4 or aadress.kood5 or aadress.kood6 or aadress.kood7:
                    return True
                if self.normimata and (aadress.kood2 or aadress.kood3):
                    return True
        return False

    @property
    def opilane(self):
        "Poolelioleva õppimise kirje"
        li = [op for op in self.opilased if not op.on_lopetanud]
        if not li:
            # isik ei õpi praegu kuskil
            return
        if len(li) > 1:
            # isik õpib samaaegselt mitmes koolis, järjestame prioriteedi järgi,
            # et eespool oleks yldhariduskoolid ja kõige ees käsitsi antud prioriteet
            li.sort(reverse=True, key=lambda op: (op.prioriteet or 0, op.seisuga, op.kool_id))
        return li[0]

    @property
    def opilane_keskh(self):
        """Poolelioleva keskhariduseta õppimise kirje
        (üldhariduskoolis või põhikooli baasil kutsekoolis)
        """
        # yldhariduse õppekavad EHISe klassifikaatoris
        yldharidus = ('1010101','1010102','1010103','1010104','1010107','1010109','2010101','3010101')
        # kutsekooli õppekavad KAVATASE klassifikaatoris, mis on põhikooli baasil
        pohikooli_baasil_kutse = ('215','216','233','315','323','408','409','410','411','421','431','441','442','443')
        li = []
        for op in self.opilased:
            if not op.on_lopetanud:
                oppekava = op.oppekava_kood
                if oppekava in yldharidus or oppekava in pohikooli_baasil_kutse:
                    li.append(op)

        if not li:
            # isik ei õpi praegu kuskil
            return
        if len(li) > 1:
            # isik õpib samaaegselt mitmes koolis, järjestame prioriteedi järgi,
            # et eespool oleks yldhariduskoolid ja kõige ees käsitsi antud prioriteet
            li.sort(reverse=True, key=lambda op: (op.prioriteet or 0, op.seisuga, op.kool_id))
        return li[0]

    @property
    def any_opilane(self):
        "Väljastatakse pooleli õppimise kirje või kui sellist pole, siis mõni lõpetatud õppimise kirje"
        opilane = self.opilane
        if not opilane:
            for opilane in self.opilased:
                break
        return opilane
    
    @property
    def te_data(self):
        "Leitakse värskeimad isikuandmed tasemeeksami lisandmete seast"
        class TeData(object):
            amet_kood = None
            amet_muu = None
            tvaldkond_kood = None
            tvaldkond_muu = None
            haridus_kood = None

        obj = TeData()
        from eis.model.testimine.sooritaja import Sooritaja
        q = (SessionR.query(Sooritaja.amet_kood,
                           Sooritaja.amet_muu,
                           Sooritaja.tvaldkond_kood,
                           Sooritaja.tvaldkond_muu,
                           Sooritaja.haridus_kood)
             .filter(Sooritaja.kasutaja_id==self.id)
             .filter(Sooritaja.tvaldkond_kood!=None)
             .order_by(sa.desc(Sooritaja.reg_aeg))
             )

        r = q.first()
        if r:
            obj.amet_kood, obj.amet_muu, obj.tvaldkond_kood, obj.tvaldkond_muu, obj.haridus_kood = r
        return obj
    
    def get_vanus(self, d=None):
        aastad = kuud = None
        synnikpv = self.synnikpv
        if synnikpv:
            if not d:
                d = date.today()
            vanus = d.year - synnikpv.year
            if d.month*100 + d.day < synnikpv.month*100 + synnikpv.day:
                vanus -= 1
            aastad = max(vanus, 0)
            kuud = d.month - synnikpv.month
            if kuud < 0:
                kuud += 12
            if d.day < synnikpv.day:
                kuud -= 1
        return aastad, kuud

    @classmethod
    def is_isikukood_ee(cls, value):
        "Kontroll, et pole välismaa isikukood"
        if not re.match(r'[A-Z]{2}', value):
            return value
        
    @property
    def isikukood_ee(self):
        if self.isikukood:
            return Kasutaja.is_isikukood_ee(self.isikukood)
    
    def ametikoht_uuendada(self, settings, ei_uuenda_opilasi=False):
        """Kas on vaja uuendada ametikoha andmeid EHISest
        """
        rc = True
        if not self.isikukood_ee:
            # ei saa uuendada
            return False
        cache_hours = float(settings.get('ehis.cache.ametikoht',24))
        cache_err_hours = float(settings.get('ehis.cache.error.ametikoht',0.1))
        if cache_hours == -1:
            # ei soovita üldse EHISest pärida
            rc = False
        if self.ametikoht_seisuga and \
               self.ametikoht_seisuga > datetime.now() - timedelta(hours=cache_hours):
            # viimati tehti EHISest päring alles piisavalt hiljuti
            rc = False
        elif self.ametikoht_proovitud and \
                self.ametikoht_proovitud > datetime.now() - timedelta(hours=cache_err_hours):
            # viimati prooviti EHISest päringut teha alles piisavalt hiljuti
            rc = False
        if rc:
            if ei_uuenda_opilasi:
                # pole mõtet teha ametikoha päringut siis,
                # kui isik on viimase 90 päeva jooksul olnud õpilane,
                # sest õpilane pole ilmselt veel õpetajaks saanud
                opilane = self.opilane
                if opilane and not opilane.on_lopetanud and \
                       opilane.seisuga and opilane.seisuga > datetime.now() - timedelta(days=90):
                    rc = False

        return rc

    @classmethod
    def opilane_uuendada(cls, settings, kasutaja):
        """Kas on vaja uuendada õppimise andmeid EHISest
        """
        rc = True
        if kasutaja and not kasutaja.isikukood_ee:
            # ei saa uuendada
            return False
        
        seisuga = kasutaja and kasutaja.opilane_seisuga
        # mittekriitilise info puhver (teadete kuvamiseks)
        cache_hours = float(settings.get('ehis.cache.opilane.lazy',1440))
        if cache_hours == -1:
            # ei soovita üldse EHISest pärida
            rc = False
        elif seisuga:
            if seisuga > datetime.now() - timedelta(hours=cache_hours):
                rc = False
        return rc

    def from_opilane(self, opilane):
        """Õpilase kirjest andmete võtmine.
        Kasutada ainult kõige prioriteetsema õpilaskirjega.
        """
        if opilane.on_lopetanud:
            self.lopetamisaasta = opilane.lopetamisaasta
            # lõpetatud kooli andmed
            self.kool_koht_id = opilane.koht_id
            if opilane.koht:
                self.kool_nimi = opilane.koht.nimi
            self.tunnistus_nr = opilane.tunnistus_nr
            self.tunnistus_kp = opilane.tunnistus_kp
        else:
            self.set_kehtiv_nimi(opilane.eesnimi, opilane.perenimi)
            
    def get_opilased(self):
        """Kelle andmeid saab kasutaja vaadata
        """
        dt = datetime.now()
        return Kasutaja.query.filter(\
            Kasutaja.opilane_volitused.any(sa.and_(\
                    Volitus.volitatu_kasutaja_id==self.id,
                    Volitus.kehtib_kuni >= dt,
                    Volitus.tyhistatud == None))).\
                    order_by(Kasutaja.nimi).all()
    
    def get_volitatud(self):
        """Kes saavad kasutaja andmeid vaadata
        """
        dt = datetime.now()
        return Kasutaja.query.filter(\
            Kasutaja.volitatu_volitused.any(sa.and_(\
                    Volitus.opilane_kasutaja_id==self.id,
                    Volitus.kehtib_kuni >= dt,
                    Volitus.tyhistatud == None))).\
                    order_by(Kasutaja.nimi).all()

    def on_volitatud(self, opilane_kasutaja_id):
        """Kes saavad kasutaja andmeid vaadata
        """
        if self.id == opilane_kasutaja_id:
            return True
        dt = datetime.now()
        q = Volitus.query.\
            filter(Volitus.opilane_kasutaja_id==opilane_kasutaja_id).\
            filter(Volitus.volitatu_kasutaja_id==self.id).\
            filter(Volitus.kehtib_kuni > dt).\
            filter(Volitus.tyhistatud == None)
        return q.count() > 0

    def default(self):
        if not self.staatus:
            self.staatus = const.B_STAATUS_KEHTIV

    @property
    def isikukood_riik(self):
        # riigi prefiks isikukoodi ees
        if self.isikukood:
            if re.match(r'[A-Z]{2}', self.isikukood):
                return self.isikukood[:2]
            else:
                # Eesti isikukood, ilma riigi prefiksita                
                return const.RIIK_EE
    @property
    def isikukood_kood(self):
        if self.isikukood:
            if re.match(r'[A-Z]{2}', self.isikukood):
                return self.isikukood[2:]
            else:
                # Eesti isikukood, ilma riigi prefiksita
                return self.isikukood
        
    @property
    def isikukood_hide(self):
        "Isikukoodi kuvamine kohtades, kus ei soovi kogu isikukoodi paljastada"
        if self.isikukood:
            return self.isikukood[:7] + '****'

    @property
    def staatus_nimi(self):
        if self.staatus == const.B_STAATUS_KEHTIV:
            return usersession.get_opt().STR_KEHTIV
        elif self.staatus == const.B_STAATUS_KEHTETU:
            return usersession.get_opt().STR_KEHTETU
  
    @property
    def kehtiv(self):
        for r in self.kasutajarollid:
            if r.kehtiv:
                return True
        return False

    @property
    def kehtiv_str(self):
        if self.kehtiv:
            return usersession.get_opt().STR_KEHTIV
        else:
            return usersession.get_opt().STR_KEHTETU

    @classmethod
    def get_by_ik(cls, ik):
        if ik:
            return cls.query.filter_by(isikukood=ik).first()

    @classmethod
    def get_by_ikR(cls, ik):
        if ik:
            return cls.queryR.filter_by(isikukood=ik).first()

    @classmethod
    def get_name_by_creator(cls, creator):
        if creator and creator != const.USER_NOT_AUTHENTICATED:
            if len(creator) == 11:
                rcd = SessionR.query(cls.nimi).filter_by(isikukood=creator).first()
            else:
                try:
                    userid = int(creator)
                except ValueError:
                    return
                rcd = SessionR.query(cls.nimi).filter_by(id=userid).first()                
            if rcd:
                return rcd[0]

    @classmethod
    def add_kasutaja(cls, ik, eesnimi, perenimi, synnikpv=None):
        rcd = Kasutaja(isikukood=ik,
                       eesnimi=eesnimi,
                       perenimi=perenimi,
                       synnikpv=synnikpv)
        rcd.add_pedagoogid()
        return rcd
        
    def check_password(self, value):
        if self.parool:
            try:
                if argon2.PasswordHasher().verify(self.parool, value):
                    return True
            except Exception:
                pass
        return False

    def check_password_old(self, value):
        if self.parool:
            # vana SHA1
            if isinstance(value, str):
                value = value.encode('utf-8')
            if hashlib.sha1(value).hexdigest() == self.parool:
                return True
        return False

    def set_password(self, parool, muuda):
        self.parool = hash_pwd(parool)
        self.muuda_parool = muuda
        k = Kasutajaajalugu(kasutaja_id=self.id)
        self.kasutajaajalood.append(k)

    def set_modifier(self):
        EntityHelper.set_modifier(self)
        self.set_nimi()
        
    def set_nimi(self):
        self.nimi = '%s %s' % (self.eesnimi or '', self.perenimi or '')
        if self.isikukood:
            try:
                self.sugu = int(self.isikukood[0]) % 2 and const.SUGU_M or const.SUGU_N
                sajand = int(self.isikukood[0])
                aasta = int(self.isikukood[1:3])
                kuu = int(self.isikukood[3:5])
                paev = int(self.isikukood[5:7])
                aasta += 1800 + int((sajand - 1)/2)*100
                self.synnikpv = date(aasta, kuu, paev)
            except:
                # isikukoodi asemel on kasutajatunnus
                pass
        
    def set_kehtiv_nimi(self, eesnimi, perenimi):
        if eesnimi and perenimi:
            if self.eesnimi != eesnimi or self.perenimi != perenimi:
                self.eesnimi = eesnimi
                self.perenimi = perenimi
                self.nimi = '%s %s' % (eesnimi or '', perenimi or '')                
                for sooritaja in self.get_reg_sooritajad():
                    sooritaja.eesnimi = eesnimi
                    sooritaja.perenimi = perenimi
                return True
        return False

    @classmethod
    def gen_userid(cls, eesnimi, perenimi):
        nimi = ('%s.%s' % (eesnimi, perenimi)).lower()
        nimi = unidecode(nimi)
        nimi = re.sub(r"[^\w\s]", '', nimi)
        nimi = re.sub(r"\s+", '', nimi)
        userid = nimi = nimi[:20]
        for ind in range(1,10000):
            item2 = cls.get_by_ik(userid)
            if not item2:
                return userid
            userid = '%s%d' % (nimi, ind)

    @property
    def on_kehtiv_ametnik(self):
        if self.on_ametnik and self.ametnik_kuni:
            return True
        else:
            return False

    @property
    def ametnik_kuni(self):
        "Millise kuupäevani kehtib EKK vaate roll"
        tyybid = (const.USER_TYPE_EKK, const.USER_TYPE_AV)
        today = date.today()
        q = (Session.query(sa.func.max(Kasutajaroll.kehtib_kuni))
             .filter(Kasutajaroll.kasutaja_id==self.id)
             .join(Kasutajaroll.kasutajagrupp)
             .filter(Kasutajagrupp.tyyp.in_(tyybid))
             .filter(Kasutajaroll.kehtib_alates<=today)
             .filter(Kasutajaroll.kehtib_kuni>=today)
             )
        kuni = q.scalar()
        return kuni

    @property
    def on_kehtiv_tookogumikud(self):
        "Kas kasutajal on avalikus vaates töökogumike õigus"
        today = date.today()
        q = (SessionR.query(Pedagoog.id)
             .filter(Pedagoog.kasutaja_id==self.id)
             .filter(sa.or_(Pedagoog.kehtib_kuni==None,
                            Pedagoog.kehtib_kuni>=today))
             )
        if q.count() > 0:
            return True
        return self.has_permission('tookogumikud', const.BT_UPDATE)

    @property
    def on_kehtiv_klass(self):
        "Kas kasutajal on mõnes koolis pedagoogi roll"
        today = date.today()

        q = (SessionR.query(sa.func.count(Pedagoog.id))
             .filter(Pedagoog.kasutaja_id==self.id)
             .filter(sa.or_(Pedagoog.kehtib_kuni==None,
                            Pedagoog.kehtib_kuni>=today))
             )
        if q.scalar() > 0:
            return True

        q = (SessionR.query(Kasutajaroll.id)
             .join((Kasutajagrupp_oigus,
                    Kasutajaroll.kasutajagrupp_id==Kasutajagrupp_oigus.kasutajagrupp_id))
             .filter(Kasutajagrupp_oigus.nimi=='klass')
             .filter(Kasutajaroll.kasutaja_id==self.id)
             .filter(Kasutajaroll.kehtib_alates<=today)
             .filter(Kasutajaroll.kehtib_kuni>=today)
             )
        for r in q.all():
            return True
        return False
    
    def on_kehtiv_roll(self, kasutajagrupp_id):
        for r in self.kasutajarollid:
            if r.kasutajagrupp_id == kasutajagrupp_id:
                if r.kehtiv:
                    return True

    def get_permissions(self, koht_id):
        """Leitakse kasutaja õigused antud soorituskohas
        """
        today = date.today()
        # koolipsyhholoogid, logopeedid ja nende litsentside haldajad ei ole seotud kooliga        
        # GRUPP_PLANK - EKK plankide halduril on õigus kõigil kohtadel planke hallata            
        kohaylesed_grupid_id = (const.GRUPP_A_PSYH,
                                const.GRUPP_A_PSYHADMIN,
                                const.GRUPP_A_LOGOPEED,
                                const.GRUPP_A_LOGOPEEDADMIN,
                                const.GRUPP_TOOVAATAJA,
                                const.GRUPP_PLANK)
        cond = Kasutajaroll.kasutajagrupp_id.in_(kohaylesed_grupid_id)
        if koht_id:
            cond = sa.or_(cond, Kasutajaroll.koht_id==koht_id)

        # leiame kasutajal olevad grupid    
        q = (SessionR.query(Kasutajaroll.kasutajagrupp_id)
             .filter(Kasutajaroll.kasutaja_id==self.id)
             .filter(Kasutajaroll.kehtib_alates<=today)
             .filter(Kasutajaroll.kehtib_kuni>=today)
             .filter(cond)
             )
        grupid_id = set([g_id for g_id, in q.all()])

        # adminil on plankide haldamise õigus kõigis kohtades
        if koht_id == const.KOHT_EKK and const.GRUPP_ADMIN in grupid_id:
            grupid_id.add(const.GRUPP_PLANK)

        # läbiviija õigused
        if self.on_labiviija:
            grupid_id.add(const.GRUPP_LABIVIIJA)

        # leiame pedagoogigrupid
        if koht_id:
            q = (SessionR.query(Pedagoog.kasutajagrupp_id)
                .filter(Pedagoog.kasutaja_id==self.id)
                .filter(Pedagoog.koht_id==koht_id)
                .filter(sa.or_(Pedagoog.kehtib_kuni==None,
                               Pedagoog.kehtib_kuni>=today))
                )
            for g_id, in q.all():
                grupid_id.add(g_id)

        oigused = dict()
        if grupid_id:
            # leiame kasutajal olevatele gruppidele antud õigused
            q = (SessionR.query(Kasutajagrupp_oigus.nimi,
                               Kasutajagrupp_oigus.bitimask)
                .filter(Kasutajagrupp_oigus.kasutajagrupp_id.in_(grupid_id))
                )
            for nimi, bitimask in q.all():
                if nimi not in oigused:
                    oigused[nimi] = bitimask
                else:
                    oigused[nimi] |= bitimask

        if koht_id == const.KOHT_EKK:
            # kontrollime, kas isik on kuskil pedagoog
            if 'klass' not in oigused and self.on_kehtiv_klass:
                oigused['klass'] = const.BT_SHOW

        if koht_id != const.KOHT_EKK:
            # EKK vaates antud õigused, mis kehtivad avalikus vaates
            over_perms = ('abi','avtugi')
            q = (SessionR.query(Kasutajagrupp_oigus.nimi,
                               Kasutajagrupp_oigus.bitimask)
                 .filter(Kasutajagrupp_oigus.nimi.in_(over_perms))
                 .join((Kasutajaroll,
                        sa.and_(Kasutajaroll.kasutajagrupp_id==Kasutajagrupp_oigus.kasutajagrupp_id,
                                Kasutajaroll.kasutaja_id==self.id)))
                 .filter(Kasutajaroll.kehtib_alates<=today)
                 .filter(Kasutajaroll.kehtib_kuni>=today)
                 )
            for nimi, bitimask in q.all():
                if nimi not in oigused:
                    oigused[nimi] = bitimask
                else:
                    oigused[nimi] |= bitimask

        #log.debug(f' oigused kasutaja={self.id} koht={koht_id}: {oigused}')
        return oigused

    def has_permission(self, permission, perm_bit, koht_id=None, aine_kood=None, oskus_kood=None, piirkond_id=None, testiliigid=[], grupp_id=None, ained=[], oskused=[], gtyyp=None):
        """Kas kasutajal on õigus?
        Konkreetse ülesande või testiga seotud õigusi siin ei arvestata.
        """
        from eis.model.koht.piirkond import Piirkond
        # mõni argument peab olema antud
        assert permission and perm_bit or koht_id or aine_kood or ained or oskus_kood or oskused or testiliigid or grupp_id, 'Midagi on siit puudu'
        
        if koht_id:
            for p in self.pedagoogid:
                if p.koht_id == koht_id and p.has_permission(permission, perm_bit):
                    return True

        if permission == 'abi' and koht_id:
            # abi sisestamisel kehtib Innove vaate õigus
            koht_id = None

        today = date.today()
        q = (SessionR.query(sa.func.count(Kasutajaroll.id))
             .filter(Kasutajaroll.kasutaja_id==self.id)
             .filter(Kasutajaroll.kehtib_alates<=today)
             .filter(Kasutajaroll.kehtib_kuni>=today)
             )
        if grupp_id:
            if isinstance(grupp_id, (tuple, list)):
                q = q.filter(Kasutajaroll.kasutajagrupp_id.in_(grupp_id))
            else:
                q = q.filter(Kasutajaroll.kasutajagrupp_id==grupp_id)

        if permission:
            q = (q.join((Kasutajagrupp_oigus,
                         Kasutajaroll.kasutajagrupp_id==Kasutajagrupp_oigus.kasutajagrupp_id))
                 .filter(sa.literal(permission).startswith(Kasutajagrupp_oigus.nimi))
                 .filter(Kasutajagrupp_oigus.bitimask.op('&')(perm_bit) == perm_bit)
                 )
            if gtyyp:
                q = q.filter(Kasutajagrupp_oigus.grupp_tyyp==gtyyp)
            elif koht_id == const.KOHT_EKK:
                tyybid = (const.USER_TYPE_EKK, const.USER_TYPE_AV)
                q = q.filter(Kasutajagrupp_oigus.grupp_tyyp.in_(tyybid))
            elif koht_id:
                gtyyp = const.USER_TYPE_KOOL
                q = q.filter(Kasutajagrupp_oigus.grupp_tyyp==gtyyp)

        if koht_id:
            q = q.filter(Kasutajaroll.koht_id==koht_id)

        #if not aine_kood and not ained:
        #    q = q.filter(Kasutajaroll.aine_kood==None)
        if ained:
            if len(ained) == 1:
                aine_kood = ained[0]
            else:
                q = q.filter(sa.or_(Kasutajaroll.aine_kood==None,
                                    Kasutajaroll.aine_kood.in_(ained)))

        if aine_kood:
            q = q.filter(sa.or_(Kasutajaroll.aine_kood==None,
                                Kasutajaroll.aine_kood==aine_kood))

        if oskused:
            if len(oskused) == 1:
                oskus_kood = oskused[0]
            else:
                q = q.filter(sa.or_(Kasutajaroll.oskus_kood==None,
                                    Kasutajaroll.oskus_kood.in_(oskused)))
        if oskus_kood:
            q = q.filter(sa.or_(Kasutajaroll.oskus_kood==None,
                                Kasutajaroll.oskus_kood==oskus_kood))

        if piirkond_id:
            # kontrollime, et antud piirkond on lubatud või lubatu all
            piirkonnad_id = Piirkond.get(piirkond_id).get_ylemad_id()
            q = q.filter(sa.or_(Kasutajaroll.piirkond_id==None,
                                Kasutajaroll.piirkond_id.in_(piirkonnad_id)))

        if testiliigid:
            if len(testiliigid) == 1:
                q = q.filter(sa.or_(Kasutajaroll.testiliik_kood==None,
                                    Kasutajaroll.testiliik_kood==testiliigid[0]))
            elif len(testiliigid) > 1:
                q = q.filter(sa.or_(Kasutajaroll.testiliik_kood==None,
                                    Kasutajaroll.testiliik_kood.in_(testiliigid)))
        cnt = q.scalar()
        return bool(cnt)

    def get_kohad(self):
        today = date.today()
        li = [p.koht_id for p in self.pedagoogid if p.koht_id and \
              (not p.kehtib_kuni or p.kehtib_kuni >= today)]
        for r in self.kasutajarollid:
            if r.kehtiv and r.koht_id and r.koht_id not in li and r.koht_id != const.KOHT_EKK:
                li.append(r.koht_id)
        li2 = []
        for koht_id in li:
            koht = Koht.get(koht_id)
            if koht.staatus == const.B_STAATUS_KEHTIV:
                li2.append(koht)
        return li2

    def get_piirkonnad_id(self, permission, perm_bit, testiliik=None):
        """Leiame piirkonnad, kus kasutajal on antud õigus
        """
        from eis.model.koht.piirkond import Piirkond
        if testiliik == const.TESTILIIK_AVALIK:
            # avaliku vaate testi korraldajat ei piirata piirkonniti
            return [None]
        today = date.today()
        q = (SessionR.query(Kasutajaroll.piirkond_id).distinct()
             .filter(Kasutajaroll.kasutaja_id==self.id)
             .filter(Kasutajaroll.kehtib_alates<=today)
             .filter(Kasutajaroll.kehtib_kuni>=today)
             )
        if permission:
            q = (q.join((Kasutajagrupp_oigus,
                        Kasutajagrupp_oigus.kasutajagrupp_id==Kasutajaroll.kasutajagrupp_id))
                 .filter(sa.literal(permission).startswith(Kasutajagrupp_oigus.nimi))
                 .filter(Kasutajagrupp_oigus.bitimask.op('&')(perm_bit) == perm_bit)
                 )

        if testiliik:
            q = q.filter(sa.or_(Kasutajaroll.testiliik_kood==None,
                                Kasutajaroll.testiliik_kood==testiliik))

        lubatud_id = [prk_id for prk_id, in q.all()]
        if None in lubatud_id:
            # kõik piirkonnad on lubatud
            piirkonnad_id = [None]
        else:
            # ei ole kõik piirkonnad lubatud,
            # leiame lubatud piirkondade alampiirkonnad
            piirkonnad_id = []
            for prk_id in lubatud_id:
                piirkonnad_id += Piirkond.get(prk_id).get_alamad_id()
            
        return list(set(piirkonnad_id))

    def get_kasutaja_piirkonnad_id(self):
        """Leiame piirkonnad, kus isikut saab testimisel kasutada
        """
        return [r.piirkond_id for r in self.kasutajapiirkonnad]

    def get_testiliigid(self, permission, perm_bit):
        """Leiame testiliigid, mille kohta kasutajal on antud õigus
        """
        today = date.today()
        q = (SessionR.query(Kasutajaroll.testiliik_kood).distinct()
             .filter(Kasutajaroll.kasutaja_id==self.id)
             .filter(Kasutajaroll.kehtib_alates<=today)
             .filter(Kasutajaroll.kehtib_kuni>=today)
             )
        if permission:
            q = (q.join((Kasutajagrupp_oigus,
                        Kasutajagrupp_oigus.kasutajagrupp_id==Kasutajaroll.kasutajagrupp_id))
                 .filter(sa.literal(permission).startswith(Kasutajagrupp_oigus.nimi))
                 .filter(Kasutajagrupp_oigus.bitimask.op('&')(perm_bit) == perm_bit)
                 )

        lubatud_id = [liik or None for liik, in q.all()]
        #log.debug('lubatud liigid:%s' % str(lubatud_id))
        return list(set(lubatud_id))

    def get_ained(self, permission, perm_bit):
        """Leiame ained, kus kasutajal on antud õigus
        """
        today = date.today()
        q = (SessionR.query(Kasutajaroll.aine_kood).distinct()
             .filter(Kasutajaroll.kasutaja_id==self.id)
             .filter(Kasutajaroll.kehtib_alates<=today)
             .filter(Kasutajaroll.kehtib_kuni>=today)
             )
        if permission:
            q = (q.join((Kasutajagrupp_oigus,
                        Kasutajagrupp_oigus.kasutajagrupp_id==Kasutajaroll.kasutajagrupp_id))
                 .filter(sa.literal(permission).startswith(Kasutajagrupp_oigus.nimi))
                 .filter(Kasutajagrupp_oigus.bitimask.op('&')(perm_bit) == perm_bit)
                 )

        lubatud_ained = [aine for aine, in q.all()]
        return list(set(lubatud_ained))

    def get_opetaja_ained(self):
        """Leiame ained, mida kasutaja õpetab
        """
        from .ainepedagoog import Ainepedagoog
        ained = []

        # EHISe pedagoogiroll
        q = (SessionR.query(Ainepedagoog.ehis_aine_kood)
             .join(Ainepedagoog.pedagoog)
             .filter(Pedagoog.kasutaja_id==self.id))
        ehis_ained = [aine for aine, in q.all()]
        if ehis_ained:
            EHISKlrida = sa.orm.aliased(Klrida)
            q = (SessionR.query(Klrida.kood).distinct()
                .join(Klrida.eis_klvastavused)
                .join((EHISKlrida, EHISKlrida.id==Klvastavus.ehis_klrida_id))
                .filter(EHISKlrida.kood.in_(ehis_ained)))
            ained = [aine for aine, in q.all()]

        # EISis aineõpetaja roll
        q = (SessionR.query(Kasutajaroll.aine_kood)
             .filter(Kasutajaroll.kasutaja_id==self.id)
             .filter(Kasutajaroll.kasutajagrupp_id==const.GRUPP_AINEOPETAJA))
        ained.extend([r for r, in q.all()])
        return set(ained)
    
    def get_keeled(self, permission, perm_bit):
        """Leiame keeled, kus kasutajal on antud õigus
        """
        today = date.today()
        q = (SessionR.query(Kasutajaroll.lang).distinct()
             .filter(Kasutajaroll.kasutaja_id==self.id)
             .filter(Kasutajaroll.kehtib_alates<today)
             .filter(Kasutajaroll.kehtib_kuni>today)
             )
        if permission:
            q = (q.join((Kasutajagrupp_oigus,
                        Kasutajagrupp_oigus.kasutajagrupp_id==Kasutajaroll.kasutajagrupp_id))
                 .filter(sa.literal(permission).startswith(Kasutajagrupp_oigus.nimi))
                 .filter(Kasutajagrupp_oigus.bitimask.op('&')(perm_bit) == perm_bit)
                 )
        lubatud_keeled = [l for l, in q.all()]
        return list(set(lubatud_keeled))

    def get_kohad_nimi(self, app_name):
        from eis.model.testimine import Labiviija
        from eis.model.testimine import Testikoht
        from eis.model.testimine import Testiruum

        # edasi antud soorituskoha administraatorite õigused
        today = date.today()
        q = (SessionR.query(Koht.id, Koht.nimi)
             .join(Koht.kasutajarollid)
             .filter(Kasutajaroll.kasutaja_id==self.id)
             .filter(Kasutajaroll.kehtib_alates<=today)
             .filter(Kasutajaroll.kehtib_kuni>=today)
             .filter(Koht.staatus==const.B_STAATUS_KEHTIV))
        if app_name == const.APP_PLANK:
            grupid = (const.GRUPP_K_PLANK,
                      const.GRUPP_K_ADMIN,
                      const.GRUPP_K_JUHT,
                      const.GRUPP_PLANK)
        else:
            # EISi avalik vaade
            q = q.filter(Kasutajaroll.koht_id!=const.KOHT_EKK)
            grupid = (const.GRUPP_K_JUHT, 
                      const.GRUPP_K_ADMIN,
                      const.GRUPP_K_PROTOKOLL, 
                      const.GRUPP_K_FAILID,
                      const.GRUPP_AINEOPETAJA)
        q = q.filter(Kasutajaroll.kasutajagrupp_id.in_(grupid))
        q = q.order_by(Koht.nimi)
        kohad1 = [(rcd[0], rcd[1]) for rcd in q.all()]

        today = date.today()
        kohad2 = []
        if app_name == const.APP_EIS:
            # pedagoogide ametikohad EHISe puhvrist
            q = (SessionR.query(Koht.id, Koht.nimi)
                 .join(Koht.pedagoogid)
                 .filter(Pedagoog.kasutaja_id==self.id)
                 .filter(sa.or_(Pedagoog.kehtib_kuni==None,
                                Pedagoog.kehtib_kuni>=today))
                 .filter(Koht.staatus==const.B_STAATUS_KEHTIV)
                 .order_by(Koht.nimi))
            kohad2 = [(rcd[0], rcd[1]) for rcd in q.all()]

        # ajutine!
        if app_name == const.APP_PLANK:
            # pedagoogide ametikohad EHISe puhvrist
            q = (SessionR.query(Koht.id, Koht.nimi)
                 .join(Koht.pedagoogid)
                 .filter(Pedagoog.kasutaja_id==self.id)
                 .filter(Pedagoog.kasutajagrupp_id.in_((const.GRUPP_K_ADMIN, const.GRUPP_K_JUHT)))
                 .filter(sa.or_(Pedagoog.kehtib_kuni==None,
                                Pedagoog.kehtib_kuni>=today))
                 .filter(Koht.staatus==const.B_STAATUS_KEHTIV)                 
                 .order_by(Koht.nimi))
            kohad2 = [(rcd[0], rcd[1]) for rcd in q.all()]
        kohad3 = []
        kohad5 = []
        if app_name == const.APP_EIS:
            # testide läbiviimise kohad
            today = date.today()
            tomorrow = today + timedelta(days=1)

            grupid_id = (const.GRUPP_HINDAJA_S,
                         const.GRUPP_HINDAJA_S2,
                         const.GRUPP_HINDAJA_K,
                         const.GRUPP_INTERVJUU,
                         const.GRUPP_HIND_INT,
                         const.GRUPP_T_ADMIN)
            q = (SessionR.query(Koht.id, Koht.nimi)
                 .join(Koht.testikohad)
                 .filter(Koht.staatus==const.B_STAATUS_KEHTIV)                                  
                 .join(Testikoht.labiviijad)
                 .filter(Labiviija.kasutaja_id==self.id)
                 .filter(Labiviija.kasutajagrupp_id.in_(grupid_id))
                 .filter(Labiviija.staatus.in_(
                     (const.L_STAATUS_MAARATUD, const.L_STAATUS_OSALENUD)
                     ))
                 .join(Labiviija.testiruum)
                 .filter(
                     sa.and_(Testiruum.algus>=today,
                             Testiruum.algus<tomorrow))
                 )
            kohad3 = [(rcd[0], rcd[1]) for rcd in q.all()]

            grupid_id = (const.GRUPP_KOMISJON,
                         const.GRUPP_KOMISJON_ESIMEES)
            q = (SessionR.query(Koht.id, Koht.nimi)
                 .join(Koht.testikohad)
                 .filter(Koht.staatus==const.B_STAATUS_KEHTIV)                                  
                 .join(Testikoht.labiviijad)
                 .filter(Labiviija.kasutaja_id==self.id)
                 .filter(Labiviija.kasutajagrupp_id.in_(grupid_id))
                 .filter(Labiviija.staatus.in_(
                     (const.L_STAATUS_MAARATUD, const.L_STAATUS_OSALENUD)
                     ))
                 .filter(Testikoht.testiruumid.any(
                     sa.and_(Testiruum.algus>=today,
                             Testiruum.algus<tomorrow))
                         )
                 )
            kohad5 = [(rcd[0], rcd[1]) for rcd in q.all()]

        kohad = list(set(kohad1+kohad2+kohad3+kohad5))
        return kohad

    def add_pedagoogid(self):
        """Peale uue kasutaja kirje loomist seotakse sellega sama isiku pedagoogikirjed
        """
        if self.isikukood:
            # otsime pedagoogi kirjeid, mis pole kasutajaga veel seotud
            q = (Session.query(Pedagoog)
                 .filter(Pedagoog.isikukood==self.isikukood)
                 .filter(Pedagoog.kasutaja_id==None)
                 )
            found = False
            for r in q.all():
                found = True
                self.pedagoogid.append(r)
            if found:
                Session.flush()
    
    def update_pedagoogid(self, ametikohad):
        """Pedagoogi ametikohad uuendatakse EHISest küsitud andmetega.
        """
        if not self.isikukood_ee:
            # ei saa uuendada
            return False
        # lisame pedagoogi kirjed, mis veel pole kasutaja kirjega seotud
        self.add_pedagoogid()
        
        now = datetime.now()
        self.ametikoht_seisuga = now
        
        # olemasolevad andmed
        pedagoogid = self.pedagoogid
        removed = list(pedagoogid)

        # EHISes on viga, mille tõttu samas koolis mitut ametikohta pidava isiku
        # korral tuleb iga ametikoha kohta eraldi kirje ja koolijuhi väli
        # ei käi isiku kohta, vaid ainult kirje tekitanud ametikoha kohta;
        # teeme vastuse ymber nii, et iga kooli kohta oleks yks kirje
        # ja selles oleks koolijuhi väljal õige väärtus
        di_ametikohad = {}
        for rcd in ametikohad or []:
            kool_id = int(rcd.koolId)
            rcd2 = di_ametikohad.get(kool_id)
            if rcd2:
                # kui kirje on juba eespool olemas ja praegune kirje on koolijuhi kirje,
                # siis muudame vanas kirjes koolijuhi väärtuse õigeks
                if _xbool(rcd.koolijuht):
                    rcd2.koolijuht = True
            else:
                # kui selle kooli kirjet eespool pole olnud, siis saab praegune kirje
                # selle kooli kirjeks
                di_ametikohad[kool_id] = rcd

        eesnimi = perenimi = None
        
        # tsykkel yle isiku koolide
        for rcd in list(di_ametikohad.values()):
            # rcd on x-tee päringu tulemuse kirje
            kool_id = int(rcd.koolId)

            # otsime olemasolevate kirjete seast seda kooli
            pedagoog = None
            for item in self.pedagoogid:
                if item.kool_id == kool_id:
                    if item in removed:
                        removed.remove(item)
                    pedagoog = item
                    break
            
            # kui ei ole olemas, siis teeme uue kirje
            if not pedagoog:
                pedagoog = Pedagoog(kasutaja=self, kool_id=kool_id, isikukood=self.isikukood)

            pedagoog.update_from_ehis(rcd, True)
            pedagoog.seisuga = now
            eesnimi = pedagoog.eesnimi
            perenimi = pedagoog.perenimi
            
        # kustutame kasutaja ametikohad, mida enam pole
        for item in removed:
            if item.on_ehisest:
                item.delete()

        if eesnimi and perenimi and \
               (self.eesnimi.lower() != eesnimi.lower() or self.perenimi.lower() != perenimi.lower()):
            # nimi erineb, peab õiget nime kontrollima RRist
            return True
        else:
            return False

    def lisagrupid(self, grupid_id):
        for grupp_id in grupid_id:
            self.lisaroll(grupp_id)
        return self

    def lisaroll(self, grupp_id, **roll_kw):
        grupp = Kasutajagrupp.get(grupp_id)
        roll = Kasutajaroll(kasutajagrupp=grupp, kasutaja=self, **roll_kw)
        self.kasutajarollid.append(roll)
        return roll

    def give_profiil(self):
        if not self.profiil:
            self.profiil = Profiil(kasutaja=self)
        return self.profiil
 
    def get_aineprofiil(self, aine_kood, kasutajagrupp_id, keeletase_kood):
        for r in self.aineprofiilid:
            if r.aine_kood == aine_kood and \
               r.kasutajagrupp_id == kasutajagrupp_id and \
               (r.keeletase_kood or '') == (keeletase_kood  or ''):
                return r

    def give_aineprofiil(self, aine_kood, kasutajagrupp_id, keeletase_kood):
        r = self.get_aineprofiil(aine_kood, kasutajagrupp_id, keeletase_kood)
        if r:
            return r
        r = Aineprofiil(aine_kood=aine_kood,
                        keeletase_kood=keeletase_kood,
                        kasutajagrupp_id=kasutajagrupp_id)
        self.aineprofiilid.append(r)
        return r

    def get_labiviijaleping(self, leping_id, sessioon_id):
        from .labiviijaleping import Labiviijaleping
        q  = Labiviijaleping.query.\
             filter(Labiviijaleping.kasutaja_id==self.id).\
             filter(Labiviijaleping.leping_id==leping_id)
        if sessioon_id:
            q = q.filter(Labiviijaleping.testsessioon_id==sessioon_id)
        return q.first()

    def get_reg_sooritajad(self, testiliik=None, is_B1=None, peitmata=False, regamine=False, kinnitamata=False):
        "Kasutaja nende registreeringute nimekiri, mida pole veel toimunud"
        from eis.model.test.test import Test
        from eis.model.test.testitase import Testitase
        from eis.model.testimine.testimiskord import Testimiskord        
        from eis.model.testimine.sooritaja import Sooritaja
        q = (Sooritaja.query
             .filter(Sooritaja.kasutaja_id==self.id)
             .join(Sooritaja.testimiskord)
             )
        if kinnitamata:
            # ainult kinnitamata registreeringud
            q = q.filter(Sooritaja.staatus==const.S_STAATUS_REGAMATA)
        else:
            # kõik registreeringud
            q = q.filter(Sooritaja.staatus.in_((const.S_STAATUS_REGAMATA,
                                                const.S_STAATUS_TASUMATA,
                                                const.S_STAATUS_REGATUD)))
        if testiliik:
            if testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
                # rahvusvahelistele eksamitele ja riigieksamitele registreeritakse koos
                q = q.join(Sooritaja.test).filter(Test.testiliik_kood.in_((const.TESTILIIK_RIIGIEKSAM,
                                                                           const.TESTILIIK_RV)))
            else:
                q = q.join(Sooritaja.test).filter_by(testiliik_kood=testiliik)
                if testiliik == const.TESTILIIK_TASE and is_B1:
                    q = q.filter(Test.testitasemed.any(Testitase.keeletase_kood==const.KEELETASE_B1))
        if peitmata:
            # leida ainult need sooritajad, kes pole peidetud
            dt = datetime.now()
            q = q.filter(sa.or_(Testimiskord.sooritajad_peidus_kuni == None,
                                Testimiskord.sooritajad_peidus_kuni <= dt))
        if regamine:
            # jätta välja kinnitamata registreeringud testidele, millele enam ei saa registreerida
            # (kui on tasumata, siis kuvatakse, sest Harno lubab ka hiljem tasuda)
            dt = date.today()
            q = q.filter(sa.or_(sa.and_(Testimiskord.reg_sooritaja == True,
                                        Testimiskord.reg_sooritaja_alates <= dt,
                                        Testimiskord.reg_sooritaja_kuni >= dt),
                                sa.and_(sa.or_(Testimiskord.kuni>=dt,
                                               Testimiskord.kuni==None),
                                        Sooritaja.staatus!=const.S_STAATUS_REGAMATA)
                                ))

        q = q.order_by(sa.desc(Sooritaja.id))
        return q.all()

def hash_pwd_old(value):
    "Vana parooli räsimine"
    if value:
        if isinstance(value, str):
            value = value.encode('utf-8')
        return hashlib.sha1(value).hexdigest()
    
def hash_pwd(value, userid=None):
    "Parooli räsimine"
    if value:
        if userid:
            # testiparooli sool: pikkus vähemalt 8, mahub kuni 14
            salt = userid.upper().zfill(8).encode('utf-8')[-14:]
        else:
            # sool genereeritakse
            salt = None
        return argon2.PasswordHasher().hash(value, salt=salt)

def _xbool(node):
    """X-tee päringu vastuses oleva boolean välja dekodeerimine
    """
    value = str(node)
    if value in ('true','1','t'):
        return True
    elif value in ('false','0','f'):
        return False
    else:
        return None
