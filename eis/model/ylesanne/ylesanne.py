"Ülesande andmemudel"

import re
from lxml import etree
import urllib.request, urllib.parse, urllib.error

from eis.model.entityhelper import *
from eis.model.klassifikaator import Klrida
from eis.model.kasutaja import Kasutaja, Kasutajagrupp, Kasutajagrupp_oigus, Kasutajaroll
from eis.model.countchar import CountChar
from eis.recordwrapper.testwrapper import YlesanneWrapper

from .tulemus import Tulemus
from .lahendusjuhis import Lahendusjuhis
from .tulemusmall import Tulemusmall
from .ylesandeisik import Ylesandeisik
from .salaylesanne import Salaylesanne
from .salaylesandeisik import Salaylesandeisik
from .sisuplokk import Sisuplokk
from .ylesandefail import Ylesandefail, Ylesandeobjekt, Lahendusobjekt, Lahteobjekt
from .tulemus import Tulemus
from .ylesandelogi import Ylesandelogi
from .hindamiskysimus import Hindamiskysimus
from .hindamismaatriks import Hindamismaatriks
from .t_ylesanne import T_Ylesanne, T_Lahendusjuhis, T_Hindamisaspekt, T_Sisuplokk, T_Sisuobjekt, T_Ylesandefail, T_Kysimus, T_Valik, T_Hindamismaatriks
from .sisuobjekt import Sisuobjekt, Taustobjekt, Meediaobjekt, Piltobjekt
from .kysimus import Kysimus
from .valik import Valik
_ = usersession._
log = logging.getLogger(__name__)

class Ylesanne(EntityHelper, Base, YlesanneWrapper):
    """Ülesanne
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_valid = Column(DateTime) # hetk, millest varem puhverdatud õigus vajab uuendamist (muudetakse ligipääsuõiguste muutmisel)
    nimi = Column(String(256)) # ülesande pealkiri
    kood = Column(String(100)) # ülesande kood, väline ID (QTI ja CSV import-eksport)
    staatus = Column(Integer) # olek: 1 - koostamisel; 2 - peatatud; 3 - eeltest; 4 - test; 5 - ankur; 6 - avalik; 7 - pedagoogidele; 8 - arhiveeritud; 9 - üleandmiseks; 10 - valmis kasutamiseks; 20 - ülesannete mall; 30 - ülesannete mall avalikus vaates kasutamiseks; 31 - avalikus vaates koostatud ülesanne koostamisel; 34 - avalikus vaates koostatud ülesanne valmis; 38 - avalikus vaates koostatud ülesanne arhiveeritud
    salastatud = Column(Integer, sa.DefaultClause('0'), nullable=False) # 0 - pole salastatud; 2 - loogiline salastatus; 3 - krüptitud (enam ei saa)
    lukus = Column(Integer) # muutmise lukustus: NULL - ülesanne pole lukus; 1=const.LUKUS_KINNITATUD - ülesanne on kinnitatud komplektis ja muuta võib ainult ülesannete hindamise osa; 2=const.LUKUS_KATSE_SOORITATUD - ülesannet on sooritatud KATSE testimiskorral, ei ole hinnatud, muuta võib ainult hindamise osa, muutja saab lukust lahti võtta; 3=const.LUKUS_KATSE_HINNATUD - ülesannet on sooritatud ja hinnatud ainult KATSE testimiskorral, midagi ei või muuta, muutja saab lukust lahti võtta; 4=const.LUKUS_SOORITATUD - ülesannet on kasutatud mitte-KATSE testimiskorral või testimiskorrata, hinnatud ei ole, muuta võib ainult hindamise osa, lukust lahti võtmiseks vaja eriõigusi; 5=const.LUKUS_HINNATUD - ülesannet on kasutatud mitte-KATSE testimiskorral või testimiskorrata, on hinnatud, muuta ei või midagi, lukust lahti võtmiseks on vaja eriõigusi
    logitase = Column(Integer) # logitase: 1 - logida õiguste andmine; 2 - logida kõigi andmete muutmine
    max_pallid = Column(Float, sa.DefaultClause('0')) # ülesande maksimaalne võimalik toorpunktide arv: aspektideta ülesande korral küsimuste toorpunktide summa; aspektidega ülesande korral aspektide toorpunktide ja kaalude korrutiste summa
    #yhisosa_max_punktid = Column(Float) # ühisosaküsimuste punktide summa
    ymardamine = Column(Boolean) # kas tulemuseks arvutatud pallid ümardada
    raskus = Column(Float) # ülesande raskus, vaikimisi NULL, saab kopeerida ülesannete statistikast ülesande kasutamise ajaloo vormil
    raskus_kood = Column(Integer, sa.DefaultClause('0'), nullable=False) # koostaja ette antud raskus: -1=const.RASKUS_KERGE - kerge; 0=const.RASKUS_KESKMINE - keskmine (vaikimisi); 1=const.RASKUS_RASKE - raske
    eristusindeks = Column(Float) # eristusindeks, -1..1
    arvamisindeks = Column(Float) # äraarvamisindeks, 0..1 (vastuse juhusliku äraarvamise tõenäosus)
    lahendatavus = Column(Float) # keskmine lahendusprotsent, 0..100, (keskmine pallide arv / max pallide arv)*100%
    keeletase_kood = Column(String(10)) # keeleoskuse tase, klassifikaator KEELETASE
    aste_kood = Column(String(10)) # peamine kooliaste, klassifikaator ASTE
    aste_mask = Column(Integer) # kooliastmed/erialad kodeeritud bittide summana; peamiste kooliastmete korral on biti jrk nr: 0 - I aste; 1 - II aste; 2 - III aste; 3 - gümnaasium; 4 - ülikool; muudel juhtudel on klassifikaatori kood biti järjekorranumbriks
    vastvorm_kood = Column(String(10)) # vastamise vorm, klassifikaator VASTVORM
    hindamine_kood = Column(String(10)) # hindamise meetod, klassifikaator HINDAMINE
    arvutihinnatav = Column(Boolean) # kas ülesanne on üleni arvutiga hinnatav (arvutihinnatava ülesande kõik küsimused peavad olema arvutihinnatavad; mitte-arvutihinnatav ülesanne võib sisaldada ka arvutihinnatavaid küsimusi)
    adaptiivne = Column(Boolean, sa.DefaultClause('0'), nullable=False) # diagnoosiva testi ülesanne
    #ajaline = Column(Boolean) 
    ptest = Column(Boolean) # sobivus p-testiks (paber-pliiats-testiks)
    etest = Column(Boolean) # sobivus e-testiks
    nutiseade = Column(Boolean) # sobivus nutiseadmele
    pallemaara = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas avaliku vaate testi koostaja saab ise ülesande palle määrata
    kvaliteet_kood = Column(String(10), index=True) # ülesande kvaliteedimärk
    markus = Column(Text) # märkused
    marksonad = Column(String(256)) # otsingu märksõnad  
    autor = Column(String(128)) # ülesande autor (informatiivne)
    konesyntees = Column(Boolean) # kas võimaldada kõnesünteesi
    rp_reeglid = Column(Text) # ResultProcessing XML-kujul, QTI import-eksport
    tulemusmall_id = Column(Integer, ForeignKey('tulemusmall.id'), index=True) # viide QTI tulemusmalli kirjele
    tulemusmall = relationship('Tulemusmall', foreign_keys=tulemusmall_id, back_populates='ylesanne_list')
    kuva_tulemus = Column(Boolean, sa.DefaultClause('1'), nullable=False) # kas kuvada lahendajale tema tulemus (tagasisidega ülesande korral)
    on_tagasiside = Column(Boolean) # kas ülesande tulemus esitada tagasisidena
    on_pallid = Column(Boolean) # kas tulemused kuvada pallides või protsentides (tagasiside korral); kui on NULL, siis tehakse nii, nagu vormil vaikimisi
    yl_tagasiside = Column(Text) # tagasiside terve ülesande kohta sõltumata tulemusest
    ylesandeained = relationship('Ylesandeaine', order_by='Ylesandeaine.seq', back_populates='ylesanne') # ülesande õppeained
    sisuplokid = relationship('Sisuplokk', order_by='Sisuplokk.seq', back_populates='ylesanne') 
    tulemused = relationship('Tulemus', back_populates='ylesanne')
    valjundid = relationship('Valjund', back_populates='ylesanne')
    ylesandefailid = relationship('Ylesandefail', back_populates='ylesanne')
    testiliigid = relationship('Testiliik', back_populates='ylesanne')
    kasutliigid = relationship('Kasutliik', back_populates='ylesanne')    
    vahendid = relationship('Vahend', order_by='Vahend.vahend_kood', back_populates='ylesanne')
    motlemistasandid = relationship('Motlemistasand', back_populates='ylesanne')
    normipunktid = relationship('Normipunkt', back_populates='ylesanne')
    lang = Column(String(2), sa.DefaultClause(const.LANG_ET), nullable=False) # põhikeel, keelte 2-kohaline klassifikaator
    skeeled = Column(String(60)) # ülesande keelte koodid eraldatuna tühikuga
    disain_ver = Column(Integer, sa.DefaultClause('2'), nullable=False) # CSS disaini versioon: 1=const.DISAIN_EIS1 - EIS 1 disain (kuni 2020); 2=const.DISAIN_HDS - HITSA disain (alates 2020)
    fixkoord = Column(Boolean) # fikseeritud koordinaatidega kujundus (hindamise välju ei või paigutada ülesande sisse, sest need võivad midagi kinni katta)
    alus_id = Column(Integer, ForeignKey('ylesanne.id'), index=True) # viide alusülesandele (kui antud ülesanne on loodud alusülesande koopiana)
    alus = relationship('Ylesanne', foreign_keys=alus_id, remote_side=id, back_populates='koopiad') 
    koopiad = relationship('Ylesanne', back_populates='alus')
    paanide_arv = Column(Integer) # paanide (ekraanipoolte) arv sisuplokkide kuvamisel
    paan1_laius = Column(Integer) # vasaku paani (ekraanipoole) laius protsentides
    segamini = Column(Boolean) # kas sisuplokid kuvatakse juhuslikus järjekorras (välja arvatud need, millel on sisuplokk.fikseeritud=true)
    tahemargid = Column(Integer) # ülesande tähemärkide arv (originaalkeeles)
    spellcheck = Column(Boolean) # kas lahendajale lubada sisestusväljades brauseri speller
    on_juhuarv = Column(Boolean) # kas ülesandes esineb juhuarvu sisuplokk või segatavate valikutega küsimus
    ylesandeisikud = relationship('Ylesandeisik', back_populates='ylesanne')
    ylesandelogid = relationship('Ylesandelogi', order_by=sa.desc(sa.text('Ylesandelogi.id')), back_populates='ylesanne')
    hindamisaspektid = relationship('Hindamisaspekt', order_by='Hindamisaspekt.seq', back_populates='ylesanne')
    hindamiskysimused = relationship('Hindamiskysimus', back_populates='ylesanne')
    salaylesanne = relationship('Salaylesanne', uselist=False, back_populates='ylesanne')
    lahendusjuhis = relationship('Lahendusjuhis', uselist=False, back_populates='ylesanne')
    trans = relationship('T_Ylesanne', cascade='all', back_populates='orig') # kui cascade puudub, siis antakse kustutamisel viga
    valitudylesanded = relationship('Valitudylesanne', back_populates='ylesanne')
    kasutusmaar = Column(Integer, sa.DefaultClause('0')) # mitmes testis on ülesanne kasutusel
    lahendada_lopuni = Column(Boolean) # kas üksikülesannet lahendades on vajalik kõik väljad täita ja ülesanne lõpuni lahendada
    valimata_vastused = Column(Boolean) # kas arvestada valede ja õigete vastuste arvus ka valimata õigeid ja valesid hindamismaatriksi kirjeid (psühholoogilise testi jaoks)
    ylesandeversioonid = relationship('Ylesandeversioon', back_populates='ylesanne')
    dlgop_aeg = Column(Integer) # mitu sekundit oodata enne dialoogiakna avamist (õpipädevuse ülesannetes)
    dlgop_tekst = Column(String(256)) # dialoogiakna tekst, kui vastamist ei alustata ooteaja jooksul (õpipädevuse ülesannetes)
    dlgop_ei_edasi = Column(Integer) # mitme ülesande võrra edasi liikuda, kui dialoogiaknas vastatakse eitavalt (õpipädevuse ülesannetes)
    evast_edasi = Column(Boolean) # kas kanda selle ülesande vastuseid edasi järgmistesse ülesannetesse
    evast_kasuta = Column(Boolean) # kas kasutada varasemast edasi kantud vastuseid vaikimisi algseisuna    
    koguylesanded = relationship('Koguylesanne', order_by='Koguylesanne.id', back_populates='ylesanne')
    
    @property
    def kooliastmed(self):
        "Leiame astmete koodid"
        astmed = []
        mask = self.aste_mask or 0
        opt = usersession.get_opt()
        for r in opt.astmed():
            aste_kood = r[0]
            bit = opt.aste_bit(aste_kood)
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
    def lukus_nimi(self):
        if self.lukus:
            di = {const.LUKUS_KINNITATUD: _("Ülesande sisu on lukus (ülesanne on kasutusel testis)"),
                  const.LUKUS_KATSE_SOORITATUD: _("Ülesande sisu on lukus (ülesannet on sooritatud katsetamisel)"),
                  #const.LUKUS_KATSE_SOORITATUD: _("Ülesande sisu on lukus (ülesannet on sooritatud KATSE testimiskorral)"),
                  const.LUKUS_KATSE_HINNATUD: _("Ülesanne on lukus (ülesannet on hinnatud katsetamisel)"),
                  #const.LUKUS_KATSE_HINNATUD: _("Ülesanne on lukus (ülesannet on hinnatud KATSE testimiskorral)"),
                  const.LUKUS_SOORITATUD: _("Ülesande sisu on lukus (ülesannet on sooritatud testis)"),
                  const.LUKUS_HINNATUD: _("Ülesanne on lukus (ülesannet on hinnatud testis)"),
                  }
            return di.get(self.lukus)
        else:
            return _("Ülesanne pole lukus")

    @property
    def lukus_hm_muudetav(self):
        "Kas lukustus lubab ülesande hindamist muuta"
        return not self.lukus or self.lukus not in (const.LUKUS_KATSE_HINNATUD, const.LUKUS_HINNATUD)

    def get_lukustusvajadus(self):
        """Kontrollitakse, kas ülesanne peaks olema lukus.
        """
        from eis.model.test.komplekt import Komplekt
        from eis.model.test.valitudylesanne import Valitudylesanne

        q = (SessionR.query(sa.func.max(Komplekt.lukus))
             .join(Komplekt.valitudylesanded)
             .filter(Valitudylesanne.ylesanne_id==self.id))
        return q.scalar()

    @property
    def is_encrypted(self):
        return self.salastatud in (const.SALASTATUD_KRYPTITUD, const.SALASTATUD_T_KRYPTITUD)

    def set_cache_valid(self):
        "Kutsutakse õiguste muutmisel"
        self.cache_valid = datetime.now()

    def set_salastatud(self, salastatud):
        self.set_cache_valid()
        self.salastatud = salastatud
        if salastatud and self.staatus in (const.Y_STAATUS_AVALIK, const.Y_STAATUS_PEDAGOOG):
            self.staatus = const.Y_STAATUS_TEST
            
    def default(self):
        if not self.logitase:
            self.logitase = const.LOG_LEVEL_CHANGE
        if not self.salastatud:
            self.salastatud = const.SALASTATUD_POLE

    def logitase_nimi(self, logitase=None):
        if logitase is None:
            logitase = self.logitase
        if logitase == const.LOG_LEVEL_GRANT:
            return 'Tavaline logimine'
        if logitase == const.LOG_LEVEL_CHANGE:
            return 'Muudatuste logimine'

    def salastatud_nimi(self, salastatud=None):
        if salastatud is None:
            salastatud = self.salastatud
        if salastatud == const.SALASTATUD_SOORITATAV:
            return _("Salastatud (sooritatav)")        
        elif salastatud == const.SALASTATUD_LOOGILINE:
            return _("Salastatud")
        elif salastatud == const.SALASTATUD_KRYPTITUD:
            return _("Krüptitud")
        elif salastatud == const.SALASTATUD_T_KRYPTITUD:
            return _("Test krüptitud")
        elif salastatud == const.SALASTATUD_POLE:
            return _("Pole salastatud")

    def has_permission(self, permission, perm_bit, lang=None, user=None, salastatud=None):
        """Kontrollitakse jooksva kasutaja õigust 
        antud tegevusele antud ülesandes.
        """
        staatus = self.staatus
        if salastatud is None:
            salastatud = self.salastatud
        elif salastatud:
            # kui parameeter salastatud on antud, siis kontrollitakse õiguste olemasolu juhul,
            # kui ylesanne oleks salastatud, isegi kui see praegu veel ei ole
            # arvestame ka seda, et salastamisel muudetakse avalik olek testi kandidaadi olekuks
            if staatus in (const.Y_STAATUS_AVALIK, const.Y_STAATUS_PEDAGOOG):
                staatus = const.Y_STAATUS_TEST

        if not salastatud and permission.startswith('lahendamine'):
            if self.staatus == const.Y_STAATUS_AVALIK:
                # kui soovitakse lahendada ja on avalik ylesanne, siis on õigus olemas
                return True

        if not user:
            user = usersession.get_user()
        if not user:
            return False
        kasutaja = user.get_kasutaja()
        if not kasutaja:
            return False

        if not salastatud and permission.startswith('lahendamine'):
            if self.staatus == const.Y_STAATUS_PEDAGOOG:
                if user.on_pedagoog:
                    return True

        if user.handler.c.app_ekk:
            if staatus in const.Y_ST_AV:
                # lubame adminil vaadata kõiki ylesandeid
                if perm_bit in (const.BT_SHOW, const.BT_INDEX) and user.on_admin:
                    return True
                # avalikus vaates koostamise olekuga ylesannet saab EKK vaates kasutada ainult
                # individuaalse õigusega kasutaja, kui tal on avalik õigus
                if not user.has_permission('ylesanded', perm_bit, gtyyp=const.USER_TYPE_AV):
                    return False
                if Ylesandeisik.has_role(const.GRUPP_Y_KOOSTAJA, user.id, self.id):
                    # avaliku ylesande kõik õigused on koostajal olemas
                    return True
                if not Ylesandeisik.has_role(None, user.id, self.id):
                    # isiklik õigus puudub
                    return False
                
            elif permission != 'lahendamine':
                # ekk vaate ylesande vaatamiseks EKK vaates peab oma ametniku roll
                if not user.has_permission('ylesanded', const.BT_INDEX, gtyyp=const.USER_TYPE_EKK):
                    return False
                
        if staatus not in const.Y_ST_AV and permission == 'avylesanded':
            # ylesande olek ei võimalda avalikus vaates koostamist
            return False

        if staatus in (const.Y_STAATUS_MALL, const.Y_STAATUS_AV_MALL) and perm_bit != const.BT_SHOW:
            if not kasutaja.has_permission('ylesandemall', perm_bit):
                # ylesandemalle saab muuta ainult eriõigusega kasutaja
                return False

        if salastatud:
            if staatus in (const.Y_STAATUS_ANKUR, const.Y_STAATUS_TEST, const.Y_STAATUS_EELTEST):
                # kui on salastatud ning olek on ankur, testi kandidaat või eeltesti kandidaat,
                # siis saavad ligi need, kes on korraga individuaalselt koostajad ning
                # rolli poolest ainespetsialist, eksamikorralduse ametnik või admin
                if not (self._has_use_rol_permission(kasutaja) and 
                        Ylesandeisik.has_role(const.GRUPP_Y_KOOSTAJA, user.id, self.id)):
                    return False
            else:
                # salastatud ülesannet saavad vaadata ainult individuaalse õigusega kasutajad
                if not Ylesandeisik.has_role(None, user.id, self.id):
                    return False
        else:
            if perm_bit == const.BT_SHOW:
                if permission == 'ylesanded' and staatus == const.Y_STAATUS_AVALIK:
                    # kui soovitakse vaadata avalikku ylesannet, siis on õigus alati olemas
                    return True
                if (permission == 'ylesanded' or permission.startswith('lahendamine')) and staatus == const.Y_STAATUS_PEDAGOOG:
                    # pedagoogidele lubatud ylesanne
                    if user.on_pedagoog:
                        return True

            if permission.startswith('lahendamine'):
                # kui soovitakse lahendada, aga pole avalik ylesanne, siis on vaja vaatamisõigust
                permission = 'ylesanded'
                perm_bit = const.BT_SHOW

        if permission == 'suunamine':
            # seda õigust ei anna otseselt ykski grupp
            return self._has_permission_suunamine(user)
                
        rc = self._has_rol_permission(permission, perm_bit, kasutaja)
        if not rc:
            rc = self._has_ind_permission(permission, perm_bit, lang, kasutaja, salastatud, staatus)
        if not rc:
            rc = self._has_test_permission(permission, perm_bit, lang, kasutaja)
        return rc

    def _has_rol_permission(self, permission, perm_bit, kasutaja, grupp_id=None):
        """Kontrollime ainespetsialisti või administraatori rolli olemasolu,
        aga see ei taga veel ligipääsu, kuna siin ei kontrollita salastatust
        """
        testiliigikoodid = [tl.kood for tl in self.testiliigid]
        ained = []
        oskused = []
        for r in self.ylesandeained:
            ained.append(r.aine_kood)
            if r.oskus_kood:
                oskused.append(r.oskus_kood)

        if kasutaja.has_permission(permission, 
                                   perm_bit,
                                   const.KOHT_EKK, 
                                   ained=ained,
                                   oskused=oskused,
                                   testiliigid=testiliigikoodid,
                                   grupp_id=grupp_id):
            return True
        return False

    def _has_ind_permission(self, permission, perm_bit, lang, kasutaja, salastatud, staatus):
        """Kontrollime, kas kasutajal on antud ülesandele eraldi õigus antud
        """
        rc = None
        if not kasutaja:
            return False

        now = datetime.now()
        q = (SessionR.query(sa.func.count(Ylesandeisik.id))
             .filter(Ylesandeisik.kasutaja_id==kasutaja.id)
             .filter(Ylesandeisik.ylesanne_id==self.id)
             .filter(Ylesandeisik.kehtib_alates<now)
             .filter(Ylesandeisik.kehtib_kuni>now)
             .join((Kasutajagrupp_oigus,
                    Kasutajagrupp_oigus.kasutajagrupp_id==Ylesandeisik.kasutajagrupp_id))
             .filter(sa.literal(permission).startswith(Kasutajagrupp_oigus.nimi))
             .filter(Kasutajagrupp_oigus.bitimask.op('&')(perm_bit) == perm_bit)
             )
            
        if salastatud:
            if staatus in (const.Y_STAATUS_ANKUR, const.Y_STAATUS_TEST, const.Y_STAATUS_EELTEST):
                # kui on salastatud ning olek on ankur, testi kandidaat või eeltesti kandidaat,
                # siis saavad ligi need, kes on korraga individuaalselt koostajad ning
                # rolli poolest ainespetsialist, eksamikorralduse ametnik või admin
                if self._has_use_rol_permission(kasutaja):
                    q = q.filter(Ylesandeisik.kasutajagrupp_id==const.GRUPP_Y_KOOSTAJA)
                else:
                    rc = False
                   
            elif staatus != const.Y_STAATUS_KOOSTAMISEL:
                # kui on salastatud ja olek ei ole koostamisel,
                # siis koostaja õigus ei kehti
                rc = False

            # kui ülesanne on salastatud ning olek on koostamisel,
            # siis saavad ligi kõik ülesandega seotud isikud
            # (koostaja, kujundaja, toimetaja, tõlkija, vaataja)
            
        elif staatus != const.Y_STAATUS_KOOSTAMISEL and staatus not in const.Y_ST_AV:
            # koostaja õigus kehtib Innove vaates seni, kui ylesanne on koostamisel (EH-201)
            # avalikus vaates loodud ylesandel jääb õigus ka edaspidi kehtima
            rc = False

        if rc is None:
            # kontrollime mingi õiguse olemasolu
            cnt = q.scalar()
            rc = bool(cnt)
            #log_query(q)
        log.debug('Y: Kasutajal %s %s ylesandes %s roll %s' % \
                  (kasutaja.nimi, rc and 'on' or 'pole', self.id, permission))
        return rc

    def _has_use_permission(self, kasutaja):
        """Kas kasutaja võib ülesannet lisada testi, kui see on salastatud"""
        # salastatud ylesannet saab testile lisada ainult ülesande koostaja, kellel on
        # ainespetsialisti, eksamikorralduse ametniku või administraatori roll
        permission = 'ylesanded'
        rc = self._has_ind_permission(permission, const.BT_VIEW, None, kasutaja, self.salastatud, self.staatus) 
        if rc:
            rc = self._has_use_rol_permission(kasutaja)
        return rc

    def _has_use_rol_permission(self, kasutaja):
        return self._has_rol_permission('ylesanded', const.BT_VIEW, kasutaja,
                                        grupp_id=(const.GRUPP_ADMIN, const.GRUPP_AINESPETS)) or \
                self._has_rol_permission('korraldamine', const.BT_VIEW, kasutaja,
                                         grupp_id=(const.GRUPP_KORRALDUS,))
            

    def _has_test_permission(self, permission, perm_bit, lang, kasutaja):
        """Kontrollime, kas kasutajal on antud ülesannet sisaldavale testile eraldi õigus antud
        """
        from eis.model.test import Testiisik, Valitudylesanne
        now = datetime.now()
        q = (SessionR.query(sa.func.count(Testiisik.id))
             .filter(Testiisik.kasutaja_id==kasutaja.id)
             .filter(Testiisik.kehtib_alates<now)
             .filter(Testiisik.kehtib_kuni>now)
             .join((Valitudylesanne, Valitudylesanne.test_id==Testiisik.test_id))
             .filter(Valitudylesanne.ylesanne_id==self.id)
             .join((Kasutajagrupp_oigus,
                    Kasutajagrupp_oigus.kasutajagrupp_id==Testiisik.kasutajagrupp_id))
             .filter(sa.literal(permission).startswith(Kasutajagrupp_oigus.nimi))
             .filter(Kasutajagrupp_oigus.bitimask.op('&')(perm_bit) == perm_bit)
             )
        cnt = q.scalar()
        rc = bool(cnt)
        log.debug('Y: Kasutajal %s %s ylesandes %s testi kaudu roll %s' % \
                  (kasutaja.nimi, cnt and 'on' or 'pole', self.id, permission))
        return rc

    def _has_permission_suunamine(self, user):
        "Kas kasutajal on õigus ülesannet testis kasutada"
        if self.staatus in const.Y_ST_AV:
            # minu koostatud staatuse järgi otsimine
            today = date.today()
            q = (SessionR.query(sa.func.count(Ylesandeisik.id))
                 .filter(Ylesandeisik.ylesanne_id==self.id)
                 .filter(Ylesandeisik.kasutaja_id==user.id)
                 .filter(Ylesandeisik.kasutajagrupp_id==const.GRUPP_Y_KOOSTAJA)
                 .filter(Ylesandeisik.kehtib_alates<=today)
                 .filter(Ylesandeisik.kehtib_kuni>=today)
                 )
            rc = q.scalar() > 0
        elif self.staatus == const.Y_STAATUS_PEDAGOOG:
            rc = user.on_pedagoog
        elif self.staatus == const.Y_STAATUS_AVALIK:
            rc = True
        else:
            # kõigi lubatud staatuste otsimine
            rc = False
        return rc
    
    def get_rollitegelejad(self):
        """Ametnikud, kellel on rolli järgi õigus selliste ülesannetega tegeleda.
        """
        ained = []
        oskused = []
        for r in self.ylesandeained:
            ained.append(r.aine_kood)
            if r.oskus_kood:
                oskused.append(r.oskus_kood)
        testiliigikoodid = [tl.kood for tl in self.testiliigid]

        d = date.today()
        q = (Kasutajaroll.query
             .filter(Kasutajaroll.kasutajagrupp_id.in_(Kasutajagrupp.ainegrupid))
             .filter(Kasutajaroll.kehtib_alates<=d)
             .filter(Kasutajaroll.kehtib_kuni>=d))

        if ained:
            # kui ylesande ainet pole sisestatud, siis lubame kõiki ligi 
            if len(ained) == 1:
                q = q.filter(Kasutajaroll.aine_kood==ained[0])
            else:
                q = q.filter(Kasutajaroll.aine_kood.in_(ained))
        q = q.join(Kasutajaroll.kasutaja).\
            options(sa.orm.contains_eager(Kasutajaroll.kasutaja))
        q = q.join(Kasutajaroll.kasutajagrupp).\
            options(sa.orm.contains_eager(Kasutajaroll.kasutajagrupp))

        li = []
        for r in q.all():
            if r.kasutajagrupp.id == const.GRUPP_OSASPETS:
                # tuleb kontrollida ka osaoskust ja testiliiki
                if r.oskus_kood not in oskused:
                    continue
                if r.testiliik_kood not in testiliigikoodid:
                    continue
            li.append(r)

        return li

    def get_kasutajad(self):
        """Leitakse loetelu kasutajatest, kellel on sellele ülesandele õiguseid.
        Iga kasutaja esineb loetelus üheainsa korra.
        Igale kasutajale tehakse atribuut "ylesandegrupid", mis
        sisaldab tema kasutajagruppe selle ülesande suhtes.
        """
        s = set()
        for isik in self.ylesandeisikud:
            kasutaja = isik.kasutaja
            grupp = isik.kasutajagrupp
            s.add((kasutaja, grupp))

        for k_id, g_id in self.get_testitegelejad():
            kasutaja = Kasutaja.get(k_id)
            grupp = Kasutajagrupp.get(g_id)
            s.add((kasutaja, grupp))

        for roll in self.get_rollitegelejad():
            kasutaja = roll.kasutaja
            grupp = roll.kasutajagrupp
            s.add((kasutaja, grupp))

        li = []
        for kasutaja, grupp in s:
            if kasutaja not in li:
                kasutaja.ylesandegrupid = []
                li.append(kasutaja)
            if grupp not in kasutaja.ylesandegrupid:
                kasutaja.ylesandegrupid.append(grupp)
        return li

    def get_testitegelejad(self):
         """Ametnikud, kellele on antud õigus tegeleda mõne testiga,
         kus seda ülesannet kasutatakse.
         """
         from eis.model.test import Testiisik, Valitudylesanne
         q = (SessionR.query(Testiisik.kasutaja_id,
                            Testiisik.kasutajagrupp_id)
              .distinct()
              .join((Valitudylesanne,
                     Valitudylesanne.test_id==Testiisik.test_id))
              .filter(Valitudylesanne.ylesanne_id==self.id)
              .filter(Testiisik.kehtib_kuni>=date.today())
              )
         li = [(r_id, g_id) for (r_id, g_id) in q.all()]
         return li

    def get_max_pallid(self):
        return self.max_pallid

    def calc_max_pallid(self):
        """Arvutatakse ülesande maksimaalne võimalik pallide arv.
        Kui on aspektid, siis arvutatakse nende põhjal.
        Kui pole aspekte, siis küsimuste põhjal.
        """
        pallid = 0
        arvutihinnatav = None
        evast_edasi = evast_kasuta = False
        on_aspektid = False
        on_juhuarv = False
        for ha in self.hindamisaspektid:
            if ha.max_pallid and ha.kaal:
                pallid += ha.max_pallid * ha.kaal
                arvutihinnatav = False
                on_aspektid = True
        log.debug('ha pallid=%s' % pallid)
        for sp in self.sisuplokid:
            sp_pallid = sp_ah_pallid = 0
            if sp.tyyp == const.BLOCK_RANDOM:
                # juhuarvu sisuplokk
                on_juhuarv = True
            for k in list(sp.kysimused):
                evast_edasi |= k.evast_edasi or False
                evast_kasuta |= k.evast_kasuta or False
                if k.segamini:
                    # segatavate valikutega kysimus
                    on_juhuarv = True
                t = k.tulemus
                if t:
                    if t in Session.deleted:
                        continue
                    if len(t.kysimused) == 0:
                        Session.refresh(t)
                        #log.debug('kysimusi pole')
                        #continue
                    if t.max_pallid is not None:
                        t_pallid = t.max_pallid
                    else:
                        try:
                            t_pallid = t.calc_max_pallid() or 0
                        except sa.orm.exc.ObjectDeletedError:
                            log.debug('ObjectDeletedError')
                            continue
                    t_arvutihinnatav = bool(t.arvutihinnatav)
                    if arvutihinnatav is None:
                        arvutihinnatav = t_arvutihinnatav
                    else:
                        arvutihinnatav &= t_arvutihinnatav

                    log.debug('%s pallid=%s, arvutihinnatav=%s' % (t.kood, t_pallid, t.arvutihinnatav))
                    if not k.ei_arvesta:
                        sp_pallid += t_pallid
                        if t_arvutihinnatav:
                            sp_ah_pallid += t_pallid
            if on_aspektid:
                # aspektidega ylesandes lisanduvad aspektide pallidele ainult arvutihinnatavate kysimuste pallid
                sp_pallid = sp_ah_pallid
            if sp.max_pallid is not None and sp_pallid > sp.max_pallid:
                sp_pallid = sp.max_pallid
            if sp.ymardamine:
                sp_pallid = round(sp_pallid + .0001)
            log.debug('sp pallid=%s' % sp_pallid)
            pallid += sp_pallid

        if self.ymardamine:
            pallid = round(pallid+.000001)

        #if arvutihinnatav is None and pallid == 0:
        if pallid == 0:
            # pole midagi hinnata
            arvutihinnatav = True

        log.debug('kokku=%s' % pallid)
        if self.max_pallid != pallid:
            self.max_pallid = pallid
            # kui palle muudeti, siis tuleb kõigis testides koefitsiendid muuta
            for vy in self.valitudylesanded:
                vy.update_koefitsient(vy.testiylesanne)
                
        if self.arvutihinnatav != arvutihinnatav:
            self.arvutihinnatav = arvutihinnatav
            if arvutihinnatav:
                self.hindamine_kood = const.HINDAMINE_OBJ
            else:
                self.adaptiivne = False

        if self.evast_edasi != evast_edasi:
            self.evast_edasi = evast_edasi
        if self.evast_kasuta != evast_kasuta:
            self.evast_kasuta = evast_kasuta            
        if self.on_juhuarv != on_juhuarv:
            self.on_juhuarv = on_juhuarv
        return pallid

    def remove_unused(self, handler=None):
        seq = 0
        to_delete = []
        for plokk in self.sisuplokid:
            seq += 1
            if plokk.seq != seq:
                plokk.seq = seq
            if plokk.tyyp in (const.INTER_INL_TEXT, const.INTER_INL_CHOICE, const.INTER_GAP):
                koodid = [sv.kood for sv in plokk.sisukysimused]
                for kysimus in plokk.kysimused:
                    if plokk.tyyp == const.INTER_GAP and kysimus.seq == 0:
                        # valikute baaskysimus
                        continue
                    if kysimus.kood not in koodid:
                        log.debug('%s NOT IN %s, DELETE KYSIMUS' % (kysimus.kood, koodid))
                        kysimus.delete_eelvaade()
                        to_delete.append(kysimus)
        if to_delete:
            Session.flush()
            for kysimus in to_delete:
                # if kysimus.on_vastatud():
                #     msg = _('Liigset küsimust {s} ei saa kustutada, sest seda on vastatud').format(s=kysimus.kood)
                #     log.error(msg)
                #     if handler:
                #         handler.error(msg)
                # else:
                msg = _('Kustutatud liigne küsimus {s}').format(s=kysimus.kood)
                kysimus.delete()
                log.debug(msg)
                if handler:
                    handler.notice(msg)
        for t in list(self.tulemused):
            if len(t.kysimused) == 0:
                Session.refresh(t)
                if len(t.kysimused) == 0:
                    t.delete()
            
    def check(self, handler):
        self.flush()
        self.remove_unused(handler)
        self.flush()
        self.calc_max_pallid()
        self.count_tahemargid()

    def gen_ette_esitlused(self, ctrl):
        return # ettetehtud esitlusi ei kasuta
        
    def get_tulemus(self, kood):
        """Tulemuse kirje leidmine koodi järgi.
        Seda on vaja siis, kui inline teksti sisuploki salvestamisel esmalt salvestatakse
        hindamismaatriks ja hiljem küsimus.
        """
        if kood is not None:
            for t in self.tulemused:
                if t.kood == kood:
                    return t

    def give_tulemus(self, kood):
        t = self.get_tulemus(kood)
        if t is None:
            t = Tulemus(kood=kood)
            t.ylesanne = self
            self.tulemused.append(t)
        return t

    def get_kysimus(self, kood=None, kysimus_id=None):
        # leiame kiiresti kysimuse
        if kysimus_id:
            k = Kysimus.get(kysimus_id)
        else:
            k = Kysimus.query.join(Kysimus.sisuplokk).\
                filter(Sisuplokk.ylesanne_id==self.id).\
                filter(Kysimus.kood==kood).\
                first()
        if k:
            return k

        # kui ei leidnud, siis ehk pole veel andmebaasis
        for sp in self.sisuplokid:
            for k in sp.kysimused:
                if kood is not None and k.kood == kood:
                    return k
                elif kysimus_id is not None and k.id == kysimus_id:
                    return k

    def opt_kysimused(self, ignore_k_id):
        if not self.id:
            return []
        else:
            q = (SessionR.query(Kysimus.id, Kysimus.kood)
                 .filter(Kysimus.kood!=None)
                 .filter(Kysimus.tulemus_id!=None)
                 .join(Kysimus.sisuplokk)
                 .filter(Sisuplokk.ylesanne_id==self.id)
                 #.filter(Sisuplokk.tyyp==const.BLOCK_FORMULA)
                 )
            if ignore_k_id:
                q = q.filter(Kysimus.id!=ignore_k_id)
            return [(k_id, k_kood) for (k_id, k_kood) in q.order_by(Kysimus.kood).all()]

    def get_juhis(self, lang=None):
        if self.lahendusjuhis:
            return self.lahendusjuhis.tran(lang).juhis
        else:
            return ''

    def give_lahendusjuhis(self):
        if not self.lahendusjuhis:
            self.lahendusjuhis = Lahendusjuhis(ylesanne=self)
        return self.lahendusjuhis

    @property 
    def staatus_nimi(self):
        return Klrida.get_str('Y_STAATUS', str(self.staatus))

    @property 
    def lang_nimi(self):
        return Klrida.get_str('SOORKEEL', self.lang)

    @property
    def has_solution(self):
        for t in self.tulemused:
            if len(t.hindamismaatriksid) > 0:
                return True
            if t.naidisvastus and t.naidis_naha:
                return True
        for p in self.sisuplokid:
            if p.has_solution:
                return True
        return False

    @property
    def is_interaction(self):
        for p in self.sisuplokid:
            if p.is_interaction:
                return True
        return False

    def set_tulemusmall(self):
        is_correct = False
        is_mapEntry = False
        is_areaMapEntry = False
        for t in self.tulemused:
            for e in t.hindamismaatriksid:
                if e.is_correct:
                    is_correct = True
                if e.is_mapEntry:
                    is_mapEntry = True
                if e.is_areaMapEntry:
                    is_areaMapEntry = True
        ns = None
        if is_areaMapEntry:
            ns = const.RPT_MAP_RESPONSE_POINT
        elif is_mapEntry:
            ns = const.RPT_MAP_RESPONSE
        elif is_correct:
            ns = const.RPT_MATCH_CORRECT
        if not ns:
            self.tulemusmall = None
        else:
            self.tulemusmall = Tulemusmall.query.filter_by(rp_uri=ns).first()

    def post_create(self):
        if self.staatus is None:
            self.staatus = const.Y_STAATUS_KOOSTAMISEL

        user = usersession.get_user()
        if user.id:
            # ülesande looja saab kohe ülesandega seotud isikuks koostaja rollis
            g = Kasutajagrupp.get(const.GRUPP_Y_KOOSTAJA)
            isik = Ylesandeisik(kasutaja_id=user.id,
                                kasutajagrupp=g,
                                kehtib_alates=datetime.now())
            self.ylesandeisikud.append(isik)

    @property
    def koostaja_nimed(self):
        return [r.kasutaja.nimi for r in self.ylesandeisikud \
                if r.kasutajagrupp_id == const.GRUPP_Y_KOOSTAJA]

    def copy(self):
        map_ok = self._map_oigsus()
        cp = EntityHelper.copy(self)
        Session.autoflush = False # integrity errori pärast
        cp.alus = self
        cp.staatus = const.Y_STAATUS_KOOSTAMISEL
        cp.lukus = None
        if cp.salastatud == const.SALASTATUD_SOORITATAV:
            cp.salastatud = const.SALASTATUD_LOOGILINE
        cp.nimi = 'Koopia ' + (cp.nimi or '')
        self.copy_subrecords(cp, ['sisuplokid',
                                  'ylesandeained',
                                  'valjundid',
                                  'ylesandefailid',
                                  'testiliigid',
                                  'kasutliigid',
                                  'vahendid',
                                  'hindamisaspektid',
                                  'trans',
                                  ])
        for normipunkt in self.normipunktid:
            cp_normipunkt = normipunkt.copy()
            cp.normipunktid.append(cp_normipunkt)

        if self.lahendusjuhis:
            rcd_cp = self.lahendusjuhis.copy()
            rcd_cp.ylesanne = cp
            cp.lahendusjuhis = rcd_cp
            
        cp._copy_oigsus(map_ok)
        user = usersession.get_user()
        if user.id:
            # koopia looja saab kohe ülesandega seotud isikuks koostaja rollis
            g = Kasutajagrupp.get(const.GRUPP_Y_KOOSTAJA)
            isik = Ylesandeisik(kasutaja_id=user.id,
                                kasutajagrupp=g)
            cp.ylesandeisikud.append(isik)
                    
        Session.autoflush = True    

        Session.flush()
        # väljakutsuja peab tegema BlockController.after_copy_task()
        return cp

    def _map_oigsus(self):
        # enne sisuplokkide teise ylesandesse kopeerimist 
        map_ok = {}
        for t in self.tulemused:
            ok = t.oigsus_kysimus
            if ok:
                map_ok[t.kood] = ok.kood
        return map_ok

    def _copy_oigsus(self, map_ok):
        # peale sisuplokkide teisest ylesandest kopeerimist
        # panna paika viited oma ylesande kysimustele
        map_k = {}
        for sp in self.sisuplokid:
            for k in sp.kysimused:
                map_k[k.kood] = k
                
        for sp in self.sisuplokid:
            for k in sp.kysimused:
                t = k.tulemus
                if t:
                    t.ylesanne = self
                    ok_kood = map_ok.get(t.kood)
                    t.oigsus_kysimus = ok_kood and map_k.get(ok_kood) or None

    def log_delete(self):
        # logimist ei toimu
        pass

    def delete_subitems(self):    
        Session.autoflush = False # integrity errori pärast
        self.logitase = -1
        self.delete_subrecords(['tulemused',
                                #'esitlused',
                                'ylesandeained',
                                'sisuplokid',
                                'ylesandefailid',
                                'testiliigid',
                                'kasutliigid',
                                'vahendid',
                                'motlemistasandid',
                                'ylesandeisikud',
                                'ylesandelogid',
                                'hindamisaspektid',
                                'hindamiskysimused',
                                'valjundid',
                                'ylesandeversioonid',
                                'normipunktid',
                                'koguylesanded',
                                ])
        n=len(self.testiliigid)
        if self.lahendusjuhis:
            self.lahendusjuhis.delete()
        if self.salaylesanne:
            self.salaylesanne.delete()
        Session.autoflush = True # integrity errori pärast

    def save_encrypted(self, encrypted_password, encrypted_data, isikukoodid):
        if not self.salaylesanne:
            self.salaylesanne = Salaylesanne(ylesanne=self)

        self.salaylesanne.parool = encrypted_password
        self.salaylesanne.data = encrypted_data

        li = [rcd.kasutaja_id for rcd in self.salaylesanne.salaylesandeisikud]
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
                rcd = Salaylesandeisik(salaylesanne=self.salaylesanne,
                                       kasutaja=kasutaja)
                self.salaylesanne.salaylesandeisikud.append(rcd)

        # eemaldame vanast ajast jäänud ülearused
        for kasutaja_id in li:
            for rcd in self.salaylesanne.salaylesandeisikud:
                if rcd.id == kasutaja_id:
                    rcd.delete()
                    break
        
    def pack_crypt(self):
        Session.autoflush = False 
        li = self.pack(True, None)
        Session.autoflush = True
        return li

    def pack_subrecords(self, delete=True, modified=None):
        li = []
        for rcd in self.ylesandeversioonid:
            li.extend(rcd.pack(delete, modified))
        for rcd in self.ylesandefailid:
            li.extend(rcd.pack(delete, modified))
        for rcd in self.ylesandeained:
            li.extend(rcd.pack(delete, modified))            
        for rcd in self.tulemused:
            li.extend(rcd.pack(delete, modified))
        for rcd in self.sisuplokid:
            li.extend(rcd.pack(delete, modified, ignore_keys=['tiitel']))
        if self.lahendusjuhis:
            li.extend(self.lahendusjuhis.pack(delete, modified))
        for rcd in self.normipunktid:
            li.extend(rcd.pack(delete, modified))
        for rcd in self.valjundid:
            li.extend(rcd.pack(delete, modified))
        for rcd in self.testiliigid:
            li.extend(rcd.pack(delete, modified))
        for rcd in self.kasutliigid:
            li.extend(rcd.pack(delete, modified))
        for rcd in self.vahendid:
            li.extend(rcd.pack(delete, modified))
        for rcd in self.hindamisaspektid:
            li.extend(rcd.pack(delete, modified))            
        for rcd in self.trans:
            li.extend(rcd.pack(delete, modified))
        return li

    def depack_crypt(self, li):
        """Pakitud andmed on list dictidest. 
        Iga dict sisaldab üht tabelikirjet. 
        Tabelile vastava klassi nimi on dicti väljal 'class'. 
        Ülejäänud väljade nimed vastavad tabeli veerule.
        """
        for di in li:
            cls = eval(di.pop('class'))
            if cls in (Sisuplokk, Ylesandefail, Tulemus, Lahendusjuhis):
                if di['ylesanne_id'] != self.id:
                    raise Exception('Valed andmed')
            item = cls.unpack(**di)
            item.logging = False
            item.flush()

    def _on_ylesandeisik(self, kasutaja_id, kasutajagrupp_id):
        """Kontrollitakse, kas isik on juba antud rollis ülesandeisik.
        """
        for isik in self.ylesandeisikud:
            if isik.kasutaja_id == kasutaja_id \
                    and isik.kasutajagrupp_id == kasutajagrupp_id:
                return True
        return False

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        if self.logitase >= logitase:
            if liik and len(liik) > 256:
                liik = liik[:256]
            if not self.id:
                return
            logi = Ylesandelogi(ylesanne_id=self.id,
                                kasutaja_id=usersession.get_user().id or None,
                                liik=liik,
                                vanad_andmed=vanad_andmed,
                                uued_andmed=uued_andmed)

    def set_lang(self):
        if self.skeeled is None:
            self.skeeled = self.lang + ' '
        elif self.lang not in self.skeeled:
            self.skeeled = self.lang + ' ' + self.skeeled

    def has_lang(self, lang):
        return self.skeeled and (lang in self.skeeled)

    @property
    def keeled(self):
        if not self.skeeled:
            return []
        return self.skeeled.split()

    def gen_kysimus_kood(self, default_kood=None, koodid=None):
        """Genereeritakse ülesande piires unikaalne kood uuele küsimusele
        """
        if koodid is None:
            # leitakse kõik olemasolevad koodid
            koodid = self.get_kysimus_koodid()

        if default_kood:
            if default_kood not in koodid:
                return default_kood
            elif default_kood[-1].isdigit():
                prefix = default_kood + '_'
            else:
                prefix = default_kood
        else:
            prefix = const.RESPONSE_PREFIX
        if default_kood == 'A':
            for kood in map(chr,range(65,91)):
                if kood not in koodid:
                    return kood
        for n in range(1,1000):
            kood = '%s%02d' % (prefix, n)
            if kood not in koodid:
                return kood

    def get_kysimus_koodid(self, except_sp=None, query=False):
        "Leitakse ylesande kõigi kysimuste koodid (välja arvatud parameetriks antud sisuploki kysimused)"
        if query:
            q = (SessionR.query(Kysimus.kood)
                 .join(Kysimus.sisuplokk)
                 .filter(Sisuplokk.ylesanne_id==self.id))
            if except_sp:
                q = q.filter(Kysimus.sisuplokk_id!=except_sp.id)
            koodid = [kood for kood, in q.all()]
        else:
            koodid = []
            for sp in self.sisuplokid:
                if sp != except_sp:
                    for k in sp.kysimused:
                        if k.kood:
                            koodid.append(k.kood)
        return koodid
    
    def hindamisjuhist_muudetud(self):
        """Kas viimase 24 tunni jooksul on hindamisjuhist muudetud
        """
        from .hindamisaspekt import Hindamisaspekt
        dt = datetime.now() - timedelta(1)
        q = (Hindamisaspekt.query
             .filter(Hindamisaspekt.ylesanne_id==self.id)
             .filter(Hindamisaspekt.modified>=dt))
        if q.count() > 0:
            return True

        q = (Hindamiskysimus.query
             .filter(Hindamiskysimus.ylesanne_id==self.id)
             .filter(Hindamiskysimus.vastamisaeg>=dt)
             .filter(sa.or_(Hindamiskysimus.avalik==True, 
                            Hindamiskysimus.kysija_kasutaja_id==usersession.get_user().id))
             )
        if q.count() > 0:
            return True
             
        return False

    @property
    def on_hindamisjuhend(self):
        # kas on midagi kuvada hindamisel hindamisjuhendi vormil 
        from .hindamisaspekt import Hindamisaspekt       
        q = (SessionR.query(Hindamisaspekt.id)
             .filter_by(ylesanne_id=self.id))
        if q.count():
            return True
        q = (SessionR.query(Tulemus.id)
             .filter(Tulemus.naidisvastus != None)
             .filter(Tulemus.naidisvastus != '')
             .filter_by(ylesanne_id=self.id))
        if q.count():
            return True
        return False

    def correct_responses(self, yv, lang=None, naide_only=False, hindaja=False, naidistega=True, as_tip=False, e_locals=None):
        "Õiged vastused"
        responses = dict()
        if not e_locals:
            e_locals = dict()
        yv_responses = None
        for plokk in self.sisuplokid:
            if plokk.naide or not naide_only or plokk.tyyp == const.BLOCK_RANDOM:
                plokk.correct_responses(yv, lang=lang, e_locals=e_locals, responses=responses, hindaja=hindaja, naidistega=naidistega, as_tip=as_tip)
        return responses

    def naide_responses(self, lang=None):
        "Näidisplokkide vastused"
        return self.correct_responses(None, lang=lang, naide_only=True)

    def count_tahemargid(self):
        "Arvutatakse sisuplokkide tähemärgid"
        for sp in self.sisuplokid + [self.lahendusjuhis]:
            if sp: # and sp.on_tahemargid:
                for lang in self.keeled:
                    if lang == self.lang:
                        lang = None
                    sp.count_tahemargid(lang)
        self.sum_tahemargid()

    def sum_tahemargid(self):
        "Sisuplokkide tähemärgid liidetakse kokku"
        for lang in self.keeled:
            self.sum_tahemargid_lang(lang)
            
    def sum_tahemargid_lang(self, lang):
        "Sisuplokkide tähemärgid liidetakse kokku"
        cch = CountChar(self.lang, lang)

        total = 0
        tr = cch.tran(self, lang)
        if tr:
            total += cch.count(tr.nimi, False) + \
                     cch.count(tr.marksonad, False)
            
        for sp in self.sisuplokid + [self.lahendusjuhis]:
            if sp: # and sp.on_tahemargid:
                if lang == self.lang:
                    tran_sp = sp
                else:
                    tran_sp = sp.tran(lang, False)
                if tran_sp:
                    total += tran_sp.tahemargid or 0

        for np in self.normipunktid:
            if lang == self.lang:
                tr2 = np
            else:
                tr2 = np.tran(lang, False)
            if tr2:
                total += cch.count(tr2.nimi, False)
            for ns in np.nptagasisided:
                if lang == self.lang:
                    tr2 = ns
                else:
                    tr2 = ns.tran(lang, False)
                if tr2:
                    total += cch.count(tr2.tagasiside, True) + \
                             cch.count(tr2.op_tagasiside, True)

        if lang == self.lang:
            tran_y = self
        else:
            tran_y = self.give_tran(lang)
        tran_y.tahemargid = total
