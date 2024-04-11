import hashlib

import formencode
from eis.forms import validators

from eis.model.entityhelper import *
from eis.model.koht import Koht
from eis.model.klassifikaator import Klrida

from .klass import Klass
from .kasutaja import Kasutaja

log = logging.getLogger(__name__)
  
class Opilane(EntityHelper, Base):
    """Õppurite andmed, kopeeritakse EHISest
    """
    PRIORITEET_KASITSI = 2 # käsitsi antud prioriteet, kõige prioriteetsem
    PRIORITEET_YLD = 1 # põhikool või gümnaasium, kus õppimine pooleli
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    isikukood = Column(String(50)) # isikukood
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide kasutaja kirjele
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='opilased')
    eesnimi = Column(String(50), nullable=False) # eesnimi
    perenimi = Column(String(50), nullable=False) # perekonnanimi
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True) # õppeasutus
    koht = relationship('Koht', foreign_keys=koht_id)
    kool_id = Column(Integer, nullable=True) # EHISe kooli id
    klass = Column(String(10)) # klass 
    paralleel = Column(String(40)) # paralleel
    ryhm_id = Column(Integer, ForeignKey('ryhm.id'), index=True) # viide lasteaiarühmale
    ryhm = relationship('Ryhm', foreign_keys=ryhm_id, back_populates='opilased')
    oppekeel = Column(String(25)) # õppekeele kood EHISe klassifikaatoris: E - eesti; I - inglise; D - saksa; S - soome; V - vene
    lang = Column(String(2)) # õppekeelele vastav EISi soorituskeel 
    sugu = Column(String(1)) # sugu (M,N) 
    synnikpv = Column(Date) # sünnikuupäev
    oppevorm_kood = Column(String(10)) # õppevorm, klassifikaator OPPEVORM

    # üldhariduse õppekavad EHISes:
    # 1010101 - põhikooli, gümnaasiumi riiklik õppekava (RÕK)
    # 1010102 - põhikooli lihtsustatud riiklik õppekava lihtsustatud õpe
    # 1010103 - Rahvusvahelise bakalaureuseõppe õppekava (IB)
    # 1010104 - European Baccalaureate curriculum
    # 1010107 - põhikooli lihtsustatud riiklik õppekava hooldusõpe
    # 1010109 - põhikooli lihtsustatud riiklik õppekava toimetulekuõpe
    # 2010101 - põhikooli, gümnaasiumi riiklik õppekava, põhik. 1.-9. klass
    # 3010101 - põhikooli, gümnaasiumi riiklik õppekava, gümn. 10.-12. klass
    oppekava_kood = Column(String(25)) # õppekava EHISe klassifikaatoris (kutseharidus nagu meie klassifikaator KAVATASE, üldharidus erineb)
    on_lopetanud = Column(Boolean, nullable=False) # kas on keskhariduse omandanud
    lopetamisaasta = Column(Integer) # keskhariduse omandamise aasta
    tunnistus_nr = Column(String(25)) # keskharidust tõendava tunnistuse nr
    tunnistus_kp = Column(DateTime) # keskharidust tõendava tunnistuse kuupäev
    seisuga = Column(DateTime, nullable=False) # viimane EHISest andmete kontrollimise aeg
    on_ehisest = Column(Boolean, sa.DefaultClause('1')) # kas andmed on pärit EHISest (kui pole, siis seda kirjet EHISe päringu tulemuse põhjal ei kustutata)
    prioriteet = Column(Integer) # kui EHISe andmetel õpib isik korraga mitmes koolis, siis registreeringute juurde märgitakse kõrgema prioriteediga kool (vaikimisi NULL, üldhariduskooli korral 1, käsitsi saab panna 2)
    
    @classmethod
    def update_klass(cls, oppimised, kool_id, klass, paralleel, ftrace=None):
        "Salvestame klassi õpilaste andmed (EHISest saadud)"
        total = 0
        if paralleel:
            paralleel = paralleel.upper()
        now = datetime.now()
        Klass.give(kool_id, klass, paralleel).seisuga = now

        for rcd in oppimised or []:
            item = cls.update_opilane(rcd, False, ftrace=ftrace)
            if item and item.klass == klass:
                total += 1
        Session.flush()

        # eemaldame need, keda enam pole klassis
        q = (Session.query(Opilane)
             .filter_by(kool_id=kool_id)
             .filter_by(klass=klass)
             .filter(Opilane.seisuga<now))
        if paralleel:
            q = q.filter_by(paralleel=paralleel)
        for item in q.all():
            # eemaldame klassi nendelt, kes enam ei ole klassis
            item.klass = None
            item.paralleel = None
                
        # eemaldame selle klassi õpilaste varasemad kirjed,
        # kuna eeldatavasti need enam ei kehti
        Opilane1 = sa.orm.aliased(Opilane)
        q1 = (Session.query(Opilane1.isikukood)
              .filter(Opilane1.kool_id==kool_id)
              .filter(Opilane1.klass==klass))
        if paralleel:
            q1 = q1.filter_by(paralleel=paralleel)
            
        q = (Session.query(Opilane)
             .filter(Opilane.seisuga < now - timedelta(days=2))
             .filter(Opilane.isikukood == q1.subquery().c.isikukood)
             )
        for item in list(q.all()):
            k = item.kasutaja or Kasutaja.get_by_ik(item.isikukood)
            if k and k.opilane_seisuga:
                k.opilane_seisuga = None
            item.delete()
        return total    
                
    @classmethod
    def update_opilased(cls, oppimised, isikukoodid):
        """Õpilaste andmete uuendamine EHISest saadud andmetega.
        EHISest on eelnevalt tehtud päring isikukoodide järgi, mitte klassi järgi
        """
        log.info('update_opilased %s' % (len(isikukoodid) > 5 and 'mitu' or isikukoodid))
        # salvestame saadud andmed
        qtime = datetime.now()
        for rcd in oppimised:
            cls.update_opilane(rcd, True, qtime)
        Session.flush()
        
        # märgime seisu neile isikutele, kelle kohta andmeid ei saadud
        q = (Session.query(Kasutaja)
             .filter(Kasutaja.isikukood.in_(isikukoodid))
             .filter(~ sa.exists().where(
                 sa.and_(Opilane.isikukood==Kasutaja.isikukood,
                         Opilane.seisuga>=qtime)))
             )
        for k in q.all():
            log.info('update_opilased: ei tulnud andmeid %s' % (k.isikukood))
            k.opilane_seisuga = qtime

        # kustutame need kirjed, mida enam ei tulnud
        q = (Session.query(Opilane)
             .filter(Opilane.isikukood.in_(isikukoodid))
             .filter(Opilane.on_ehisest==True)
             .filter(Opilane.seisuga < qtime))
        for opilane in q.all():
            log.info('update_opilased: kustutab %s' % opilane.isikukood)
            opilane.delete()
            
    @classmethod
    def update_opilane(cls, rcd, isikuparing, qtime=None, ftrace=None):

        def _ik_kpv(ehis_ik):
            "Leitakse, kas EHIS hoiab isikukoodi väljal isikukoodi või synnikuupäeva"
            check_digit = False
            try:
                # kas on isikukood
                validators.Isikukood(check_digit=check_digit).to_python(ehis_ik)
                return ehis_ik, None
            except formencode.api.Invalid as ex:
                try:
                    # kas on synnikpv dd.mm.yyyy
                    dd, mm, yyyy = list(map(int, ehis_ik.split('.')))
                    synnikpv = date(yyyy, mm, dd)
                    return None, synnikpv
                except Exception as ex:
                    # vigane isikukood
                    log.error('Vigane isikukood %s: %s' % (ehis_ik, ex))
                    return None, None

        item = None
        if not qtime:
            qtime = datetime.now()
        ehis_ik = rcd.isikukood.strip()
        isikukood, synnikpv = _ik_kpv(ehis_ik)
        kool_id = int(rcd.koolId)
        klass = rcd.klassKursus
        paralleel = rcd.paralleeliTunnus
        oppekava = rcd.oppekava
        log.info('update_opilane: %s kool %s' % (ehis_ik, kool_id))

        q = (Session.query(Opilane)
             .filter_by(kool_id=kool_id)
             .filter(Opilane.oppekava_kood==oppekava)
             .filter(Opilane.seisuga < qtime)
             )
        if isikukood:
            q = q.filter_by(isikukood=isikukood)
        elif synnikpv:
            q = (q.filter_by(synnikpv=synnikpv)
                 .filter_by(klass=klass)
                 )
        else:
            log.error('EHIS vastuses puudub isikukood ja synnikpv')
            if ftrace:
                ftrace(f' update_opilane:EHIS vastuses puudub isikukood ja synnikpv {kool_id},{klass},{paralleel}')
            return
        item = q.first()
        if not item:
            # meie puhvris kirjet pole, aga EHISes on
            # lisame uue kirje oma puhvrisse
            if isikukood:
                item = Opilane(isikukood=isikukood)
                item.set_ik()                
            else:
                # isik tuli EHISest ilma isikukoodita
                item = Opilane(synnikpv=synnikpv)

        #if ftrace:
        #    ftrace(f' update_opilane,{item.id},{isikukood},{kool_id},{klass},{paralleel}')

        # uuendame andmeid
        item.kool_id = kool_id
        item.oppekava_kood = oppekava
        item.on_lopetanud = _xbool(rcd.onLopetanud)
        item.eesnimi = rcd.eesnimi
        item.perenimi = rcd.perenimi
        item.oppekeel = rcd.oppekeel
        item.lang = const.EHIS_LANG.get(item.oppekeel) # kui keele kood tuleb EHISest vigaselt, siis lang=None
        item.oppevorm_kood = rcd.oppevorm

        try:
            item.lopetamisaasta = int(rcd.lopetAasta)
        except:
            # ei tohi yle kirjutada item.lopetamisaasta = None ????
            # kuna EHIS ei anna aastat, kui see ka olemas on
            item.lopetamisaasta = None

        if item.on_lopetanud:
            item.klass = item.paralleel = None
            try:
                item.tunnistus_nr = rcd.tunnistusNr
                item.tunnistus_kp = date_from_iso(rcd.tunnistusKp)
            except:
                item.tunnistus_nr = None
                item.tunnistus_kp = None
        else:
            item.klass = klass
            if paralleel:
                item.paralleel = paralleel.upper()
                if item.paralleel == 'FALSE':
                    item.paralleel = None
            else:
                item.paralleel = None
            item.tunnistus_nr = None
            item.tunnistus_kp = None

        item.seisuga = qtime
        koht = (SessionR.query(Koht)
                .filter_by(kool_id=item.kool_id)
                .filter_by(on_soorituskoht=True)
                .first())
        item.koht_id = koht and koht.id or None

        # lasteaia andmed ES-2739
        #item.set_ryhm(koht, rcd)

        if item.prioriteet != Opilane.PRIORITEET_KASITSI:
            item.set_prioriteet(koht)

        if not koht:
            log.error('EHISe õppurite päringu vastuses on kool %d, mida meile tuntud kehtivate koolide hulgas pole' % item.kool_id)

        if isikukood:
            if not item.kasutaja_id:
                kasutaja = Kasutaja.get_by_ik(isikukood)
                if kasutaja:
                    kasutaja.opilased.append(item)
                    item.kasutaja = kasutaja
            kasutaja = item.kasutaja
            if kasutaja:
                opilane = kasutaja.opilane
                if opilane == item:
                    # kui see kirje ongi kasutaja peamine kirje
                    kasutaja.from_opilane(item)
                if isikuparing:
                    kasutaja.opilane_seisuga = item.seisuga
                    
        return item

    def set_ryhm(self, koht, rcd):
        "Lasteaiarühma andmed"
        # rcd.oppurIsikId (string)
        from eis.model.koht.ryhm import Ryhm
        ryhm_id = rcd.ryhmId and int(rcd.ryhmId) or None
        if ryhm_id and koht:
            ryhm = Ryhm.get(ryhm_id)
            nimi = rcd.ryhmNimetus
            liik = rcd.ryhmLiik
            if not ryhm:
                ryhm = Ryhm(id=ryhm_id,
                            koht=koht,
                            nimi=nimi,
                            liik=liik)
                Session.flush()
            else:
                assert ryhm.koht_id == koht.id, 'ryhm_id pole unikaalne'
                if ryhm.nimi != nimi:
                    ryhm.nimi = nimi
            self.ryhm_id = ryhm_id
        else:
            self.ryhm_id = None

    def set_prioriteet(self, koht):
        # kui ei ole käsitsi prioriteet antud, siis eelistame koole, mille tyyp on POHIKOOL
        if koht and koht.koolityyp_kood == const.KOOLITYYP_POHIKOOL and not self.on_lopetanud:
            # põhikool või gümnaasium
            self.prioriteet = Opilane.PRIORITEET_YLD
        else:
            self.prioriteet = 0

    @property
    def nimi(self):
        return ('%s %s' % (self.eesnimi or '', self.perenimi or '')).strip()

    @classmethod
    def get_by_ik(cls, ik):
        if ik:
            return (Opilane.query
                    .filter_by(isikukood=ik)
                    .order_by(Opilane.on_lopetanud,
                              sa.desc(Opilane.prioriteet))
                    .first())

    def set_ik(self):
        try:
            self.sugu = int(self.isikukood[0]) % 2 and const.SUGU_M or const.SUGU_N
            sajand = int(self.isikukood[0])
            aasta = int(self.isikukood[1:3])
            kuu = int(self.isikukood[3:5])
            paev = int(self.isikukood[5:7])
            aasta += 1800 + int((sajand - 1)/2)*100
            self.synnikpv = date(aasta, kuu, paev)
        except:
            # pole Eesti isikukood
            pass

    def give_kasutaja(self):
        if not self.kasutaja:
            if self.isikukood:
                self.kasutaja = Kasutaja.get_by_ik(self.isikukood)
            if not self.kasutaja:
                kasutaja = Kasutaja.add_kasutaja(self.isikukood,self.eesnimi,self.perenimi,self.synnikpv)
                kasutaja.staatus = 1
                kasutaja.opilane_seisuga = self.seisuga
                kasutaja.on_ametnik = False
                kasutaja.on_labiviija = False
                kasutaja.lopetamisaasta = self.lopetamisaasta
                kasutaja.sugu = self.sugu
                kasutaja.synnikpv = self.synnikpv
                kasutaja.tunnistus_nr = self.tunnistus_nr
                kasutaja.tunnistus_kp = self.tunnistus_kp
                Session.flush()
                kasutaja.opilased.append(self)
                self.kasutaja = kasutaja
        return self.kasutaja

    def get_oppeaasta(self):
        """Tuletame kehtiva õppeaasta kevade.
        """
        d = date.today()
        if d.month < 8:
            return d.year
        else:
            return d.year + 1

    def get_kooliaste(self):
        """Tuletame kooliastme.
        """
        for aste, klassid in const.EHIS_KLASS_ASTE.items():
            if self.klass in klassid:
                return aste

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
