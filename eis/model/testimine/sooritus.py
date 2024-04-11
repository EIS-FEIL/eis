"Testikorralduse andmemudel"

import random

from eis.model.entityhelper import *
from eis.model.test import Testiosa, Testiylesanne, Valitudylesanne, Alatest, Hindamiskriteerium, Normipunkt, Nptagasiside, Komplekt
from eis.model.koht import Koht

from .testikoht import Testikoht
from .hindamisolek import Hindamisolek
from .sisestusolek import Sisestusolek
from .testiprotokoll import Testiprotokoll
from .skannfail import Skannfail
from .soorituslogi import Soorituslogi
from .kriteeriumivastus import Kriteeriumivastus

_ = usersession._

class Sooritus(EntityHelper, Base):
    """Testiosasooritus
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sooritaja_id = Column(Integer, ForeignKey('sooritaja.id'), index=True, nullable=False) # viide sooritaja kirjele
    sooritaja = relationship('Sooritaja', foreign_keys=sooritaja_id, back_populates='sooritused')
    testiosa_id = Column(Integer, ForeignKey('testiosa.id'), index=True, nullable=False) # viide testiosale
    testiosa = relationship('Testiosa', foreign_keys=testiosa_id)
    toimumisaeg_id = Column(Integer, ForeignKey('toimumisaeg.id'), index=True) # viide toimumisajale, puudub avaliku vaate testi korral
    toimumisaeg = relationship('Toimumisaeg', foreign_keys=toimumisaeg_id, back_populates='sooritused')
    tahis = Column(String(5)) # testiosasoorituse tähis (kui testikoht on määratud, unikaalne testikoha piires), selle järgi sorditakse sooritajaid protokollis või ruumis; pikkus üldjuhul 3, vajadusel 4
    tahised = Column(String(20)) # soorituskoha ja soorituse tähised, kriips vahel
    reg_toimumispaev_id = Column(Integer, ForeignKey('toimumispaev.id'), index=True) # registreerimisel määratud toimumispäev (kui on antud, siis sooritajat saab suunata ainult selle toimumispäeva testiruumi)
    reg_toimumispaev = relationship('Toimumispaev', foreign_keys=reg_toimumispaev_id, back_populates='sooritused')
    kavaaeg = Column(DateTime) # sooritajale kavandatud alguse aeg
    algus = Column(DateTime) # testiosasoorituse esimese seansi tegelik algus
    lopp = Column(DateTime) # testiosasoorituse viimase seansi lõpp
    seansi_algus = Column(DateTime) # testiosasoorituse viimase seansi algus
    lisaaeg = Column(Integer) # sooritajale antud lisaaeg, lisandub testiosa piirajale
    ajakulu = Column(Integer) # kulutatud sekundite arv kõigi lõpetatud seansside peale kokku
    peatus_algus = Column(DateTime) # kui sooritamine on katkestatud, siis viimase katkestamise aeg (nullitakse sooritamise jätkamisel)
    peatatud_aeg = Column(Integer) # sekundite arv, millal sooritamine oli katkestatud (arvutatakse sooritamise jätkamisel)
    piiraeg_muutus = Column(Integer) # märge, et testi sooritamise ajal on muudetud testiosa või alatesti piiraega ja peab brauseris piiraja arvestust muutma (peale brauseris taimeri muutmist nullitakse); 
    markus = Column(String(1024)) # läbiviija märkus sooritaja kohta
    staatus = Column(Integer, nullable=False) # sooritamise olek: 0=const.S_STAATUS_TYHISTATUD - tühistatud; 1=const.S_STAATUS_REGAMATA - registreerimata; 2=const.S_STAATUS_TASUMATA - tasumata; 3=const.S_STAATUS_REGATUD - registreeritud; 5=const.S_STAATUS_ALUSTAMATA - alustamata; 6=const.S_STAATUS_POOLELI - pooleli; 7=const.S_STAATUS_KATKESTATUD - ise katkestanud; 8=const.S_STAATUS_TEHTUD - tehtud; 9=const.S_STAATUS_EEMALDATUD - eemaldatud; 10=const.S_STAATUS_PUUDUS - puudus; 11=const.S_STAATUS_VABASTATUD - vabastatud; 12=const.S_STAATUS_KATKESPROT - protokollil katkestanuks märgitud
    stpohjus = Column(String(100)) # viimase oleku muutmise põhjus
    luba_veriff = Column(Boolean) # true - luba sooritada ilma isikut tõendamata (kui toimumisaeg.verif või toimumisaeg.verif_seb on seatud, st kasutusel on Veriff või Proctorio või SEB)
    puudumise_pohjus = Column(Integer) # puudumise põhjus, kui staatus on 10: 12=const.S_STAATUS_PUUDUS_VANEM - puudus lapsevanema keeldumise tõttu; 13=const.S_STAATUS_PUUDUS_HEV - puudus erievajduste tõttu
    hindamine_staatus = Column(Integer, sa.DefaultClause('0'), nullable=False) # hindamise olek: 0=const.H_STAATUS_HINDAMATA - kõik hindamiskogumid hindamata; 1=const.H_STAATUS_POOLELI - mõni hindamiskogum hindamisel; 6=const.H_STAATUS_HINNATUD - kõik hindamiskogumid hinnatud; 10=const.H_STAATUS_TOOPUUDU - töö puudub
    pallid = Column(Float) # saadud hindepallid
    pallid_arvuti = Column(Float) # (esialgne) arvutihinnatav osa hindepallidest
    pallid_kasitsi = Column(Float) # mitte-arvutihinnatav osa hindepallidest
    pallid_enne_vaiet = Column(Float) # hindepallid enne vaidlustamist
    pallid_peale_vaiet = Column(Float) # ettepanek, millised võiksid olla pallid peale vaiet
    yhisosa_pallid = Column(Float) # testimiskordade ühisossa kuuluvate küsimuste eest saadud hindepallid
    tulemus_protsent = Column(Float) # saadud hindepallid protsentides suurimast võimalikust tulemusest
    max_pallid = Column(Float) # võimalikud max pallid (sõltub alatestidest vabastusest ja lõdva struktuuri korral komplektist)
    ylesanneteta_tulemus = Column(Boolean) # kas testiosa tulemus on sisestatud toimumise protokollile või tuleb rv tunnistuselt (siis ülesannete kaupa tulemusi EISis ei ole)
    on_rikkumine = Column(Boolean) # VI hindamise korral märge, kui tuvastati rikkumine ja testitöö tuleb hinnata 0 punktiga (ülesannete tulemusi ei muudeta)
    rikkumiskirjeldus = Column(Text) # rikkumise märkimise põhjendus
    helivastused = relationship('Helivastus', back_populates='sooritus')
    hindamiskogumita = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas hinnatakse hindamiskogumita (jah, kui on testimiskorrata test või eeltesti testimiskorraga test)
    testikoht_id = Column(Integer, ForeignKey('testikoht.id'), index=True) # viide testi sooritamise kohale
    testikoht = relationship('Testikoht', foreign_keys=testikoht_id, back_populates='sooritused')
    testiruum_id = Column(Integer, ForeignKey('testiruum.id'), index=True) # viide testi sooritamise ruumile
    testiruum = relationship('Testiruum', foreign_keys=testiruum_id, back_populates='sooritused')
    testiarvuti_id = Column(Integer, ForeignKey('testiarvuti.id'), index=True) # viide testi sooritamiseks kasutatud arvutile
    testiarvuti = relationship('Testiarvuti', foreign_keys=testiarvuti_id, back_populates='sooritused')
    remote_addr = Column(String(36)) #sooritaja (või tulemüüri) IP
    autentimine = Column(String(2)) #sooritaja autentimisviis: p - püsiparooliga; tp - testiparooliga; i - id-kaardiga; i2 - digitaalse isikutunnistusega
    verifflog_id = Column(Integer, index=True) # viide viimasele verifitseerimisele
    isikudok_nr = Column(String(25)) #sooritaja esitatud isikut tõendava dokumendi number
    on_erivajadused = Column(Boolean) # kas sooritaja on taotlenud eritingimusi
    on_erivajadused_kinnitatud = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas sooritaja eritingimused on Harnos kinnitatud 
    on_erivajadused_vaadatud = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas sooritaja eritingimused on Harnos üle vaadatud (kui kinnitamist ei toimu)
    on_erivajadused_tagasilykatud = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas kõik sooritaja eritingimused on Harnos tagasi lükatud
    erivajadused_teavitatud = Column(DateTime) # eritingimuste teate saatmise aeg
    tugiisik_kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide tugiisikule
    tugiisik_kasutaja = relationship('Kasutaja', foreign_keys=tugiisik_kasutaja_id)
    intervjuu_labiviija_id = Column(Integer, ForeignKey('labiviija.id'), index=True) # viide intervjueerijale suulise (hindajaga) vastamise vormi korral
    intervjuu_labiviija = relationship('Labiviija', foreign_keys=intervjuu_labiviija_id)
    piirkond_id = Column(Integer, ForeignKey('piirkond.id'), index=True) # testikoha piirkond, dubleeritud päringute kiirendamiseks
    piirkond = relationship('Piirkond', foreign_keys=piirkond_id)
    erikomplektid = relationship('Erikomplekt', back_populates='sooritus')
    erivajadused = relationship('Erivajadus', order_by='Erivajadus.erivajadus_kood', back_populates='sooritus') 
    testiprotokoll_id = Column(Integer, ForeignKey('testiprotokoll.id'), index=True) # viide testiprotokollile; p-testitöö on jaotatud vastava testiprotokolli kõigi tagastusümbrike vahel
    testiprotokoll = relationship('Testiprotokoll', foreign_keys=testiprotokoll_id, back_populates='sooritused')
    toimumisprotokoll_id = Column(Integer, index=True) # viide toimumisprotokollile, tekib protokolli salvestamisel ja on kasutusel protokolli kinnituse kontrollimiseks; valimi korral viitab mittevalimi protokollile, mille kaudu soorituse olek märgiti
    viimane_valitudylesanne_id = Column(Integer) # viimane vaadatud valitudylesanne
    viimane_testiylesanne_id = Column(Integer) # viimane vaadatud testiylesanne
    tutv_esit_aeg = Column(DateTime, index=True) # tööga tutvumise soovi esitamise aeg
    soovib_skanni = Column(Boolean, index=True) # kas soovib saada oma töö skannitud koopiat
    valjaotsitud = Column(Boolean) # kas töö on välja otsitud (tööga tutvumise soovi korral): true - välja otsitud; false - välja otsimata
    valikujrk = Column(ARRAY(Integer)) # ülesannete järjekord antud soorituses (kui on juhusliku järjekorraga testiosa)
    klastrist_seisuga = Column(DateTime) # aeg, mil viimati soorituse andmed klastrist võeti
    klastrist_toomata = Column(Boolean) # true - olek on tehtud, aga andmed veel klastris
    hindamisolekud = relationship('Hindamisolek', back_populates='sooritus')
    sisestusolekud = relationship('Sisestusolek', back_populates='sooritus')
    soorituslogid = relationship('Soorituslogi', order_by='Soorituslogi.created', back_populates='sooritus')
    _parent_key = 'sooritaja_id'
    _logi = None # jooksva tegevuse logikirje
    __table_args__ = (
        sa.UniqueConstraint('toimumisaeg_id','tahised','tahis'),
        )

    @property
    def skannfail(self):
        q = (Session.query(Skannfail)
             .filter_by(sooritus_id=self.id)
             )
        return q.first()
    
    @property
    def autentimine_nimi(self):
        if self.autentimine:
            return usersession.get_opt().AUTENTIMINE.get(self.autentimine)

    @property
    def alatestid(self):
        kursus = self.sooritaja.kursus_kood
        return [r for r in self.testiosa.alatestid if r.kursus_kood==kursus]

    @property
    def testikoht_koht(self):
        testikoht = self.testikoht or Testikoht.get(self.testikoht_id)
        return testikoht and testikoht.koht or None

    @property
    def alatestisooritused(self):
        from eis.model.eksam.alatestisooritus import Alatestisooritus
        q = (Session.query(Alatestisooritus)
             .filter_by(sooritus_id=self.id)
             .order_by(Alatestisooritus.id))
        return q.all()

    @property
    def ylesandevastused(self):
        from eis.model.eksam.ylesandevastus import Ylesandevastus
        q = (Session.query(Ylesandevastus)
             .filter_by(sooritus_id=self.id)
             .order_by(Ylesandevastus.id))
        return q.all()

    @property
    def npvastused(self):
        from eis.model.eksam.npvastus import Npvastus
        q = (Session.query(Npvastus)
             .filter_by(sooritus_id=self.id)
             .order_by(Npvastus.id))
        return q.all()
    
    def get_alatestisooritus(self, alatest_id):
        from eis.model.eksam.alatestisooritus import Alatestisooritus
        q = (Session.query(Alatestisooritus)
             .filter_by(alatest_id=alatest_id)
             .filter_by(sooritus_id=self.id))
        return q.first()

    def getq_alatestisooritus(self, alatest_id):
        return self.get_alatestisooritus(alatest_id)
    
    def give_alatestisooritus(self, alatest_id, sooritaja=None, alatest_kood=None):
        from eis.model.eksam.alatestisooritus import Alatestisooritus
        rcd = self.get_alatestisooritus(alatest_id)
        if not rcd:
            staatus = const.S_STAATUS_ALUSTAMATA
            if not sooritaja or sooritaja.vabastet_kirjalikust:
                 # tasemeeksami kirjutamise alatest
                 # kontrollime, kas on yle 65a tasemeeksami sooritajana vabastatud
                 if alatest_kood == const.ALATEST_RK_KIRJUTAMINE:
                     if not sooritaja:
                         sooritaja = self.sooritaja
                     if sooritaja.vabastet_kirjalikust:
                         staatus = const.S_STAATUS_VABASTATUD
                        
            rcd = Alatestisooritus(sooritus_id=self.id,
                                   alatest_id=alatest_id,
                                   staatus=staatus)
        return rcd
    
    def calc_max_pallid(self):
        "Arvutame soorituse ja alatestisoorituste max pallid"
        max_pallid = 0
        testiosa = self.testiosa
        on_alatestid = False
        kursus = self.sooritaja.kursus_kood

        # kriteeriumitega hinnatavad hindamiskogumid
        krit_hk = {hk.id: hk.max_pallid for hk in testiosa.hindamiskogumid if hk.on_kriteeriumid}

        for alatest in testiosa.alatestid:
            # leiame alatestide pallid 
            on_alatestid = True
            if kursus and alatest.kursus_kood != kursus:
                continue
            a_krit_hk_id = set()
            atos = self.give_alatestisooritus(alatest.id)
            mp = None
            if atos.staatus == const.S_STAATUS_VABASTATUD:
                mp = 0
            elif alatest.max_pallid is not None:
                mp = alatest.max_pallid
            else:
                k = self.get_komplekt(alatest.id)
                if k:
                    # leiame komplekti pallid, sellest alatestist
                    mp = 0
                    for ty in alatest.testiylesanded:
                        vy = k.get_valitudylesanne(None, ty.id)
                        if vy and vy.ylesanne:
                            hk_id = vy.hindamiskogum_id or ty.hindamiskogum_id
                            if hk_id in krit_hk:
                                # ylesannet hinnatakse hindamiskogumi hindamiskriteeriumiga
                                if hk_id not in a_krit_hk_id:
                                    # selle hindamiskogumi palle pole veel arvesse võetud
                                    a_krit_hk_id.add(hk_id)
                                    mp += krit_hk[hk_id] or 0
                            else:
                                # ylesande oma pallid
                                mp += vy.ylesanne.max_pallid or 0

            if atos.max_pallid != mp:
                atos.max_pallid = mp
            if mp is None:
                max_pallid = None
                break
            else:
                max_pallid += mp

        if not on_alatestid:
            max_pallid = testiosa.max_pallid
            if max_pallid is None:
                max_pallid = 0
                for holek in self.hindamisolekud:
                    hk = holek.hindamiskogum
                    if hk:
                        mp = hk.max_pallid
                        if mp is None:
                            max_pallid = None
                            break
                        else:
                            max_pallid += mp

        if testiosa.skoorivalem:
            max_pallid = testiosa.max_pallid
        if self.max_pallid != max_pallid:
            self.max_pallid = max_pallid

    def calc_vastustearvud(self):
        "Arvutame iga ylesande õigete ja valede vastuste arvud"
        Session.flush()
        params = {'sooritus_id': self.id}

        sql = """UPDATE ylesandevastus SET valimata_oigete_arv=
        (SELECT count(hm.id) FROM hindamismaatriks hm 
        JOIN kysimus ON kysimus.tulemus_id=hm.tulemus_id 
        JOIN sisuplokk ON sisuplokk.id=kysimus.sisuplokk_id
        JOIN valitudylesanne vy ON vy.ylesanne_id=sisuplokk.ylesanne_id
         AND vy.id=ylesandevastus.valitudylesanne_id
        JOIN ylesanne ON ylesanne.id=vy.ylesanne_id AND ylesanne.valimata_vastused=true
        WHERE hm.pallid>0
        AND sisuplokk.ylesanne_id=vy.ylesanne_id
        AND sisuplokk.naide=false
        AND NOT EXISTS (
           SELECT * FROM kvsisu ks, kysimusevastus kv
           WHERE ks.kysimusevastus_id=kv.id
           AND kv.ylesandevastus_id=ylesandevastus.id
           AND ks.hindamismaatriks_id=hm.id))
        WHERE ylesandevastus.sooritus_id=:sooritus_id"""
        Session.execute(sa.text(sql), params)

        sql = """UPDATE ylesandevastus SET valimata_valede_arv=
        (SELECT count(hm.id) FROM hindamismaatriks hm 
        JOIN kysimus ON kysimus.tulemus_id=hm.tulemus_id 
        JOIN sisuplokk ON sisuplokk.id=kysimus.sisuplokk_id
        JOIN valitudylesanne vy ON vy.ylesanne_id=sisuplokk.ylesanne_id
         AND vy.id=ylesandevastus.valitudylesanne_id
        JOIN ylesanne ON ylesanne.id=vy.ylesanne_id AND ylesanne.valimata_vastused=true
        WHERE hm.pallid<=0
        AND sisuplokk.ylesanne_id=vy.ylesanne_id
        AND sisuplokk.naide=false
        AND NOT EXISTS (
           SELECT * FROM kvsisu ks, kysimusevastus kv
           WHERE ks.kysimusevastus_id=kv.id
           AND kv.ylesandevastus_id=ylesandevastus.id
           AND ks.hindamismaatriks_id=hm.id))
        WHERE ylesandevastus.sooritus_id=:sooritus_id"""
        Session.execute(sa.text(sql), params)

        # sql = """UPDATE ylesandevastus SET
        # oigete_arv = COALESCE(valimata_valede_arv, 0) +
        # (SELECT count(ks.id) FROM kvsisu ks, kysimusevastus kv
        # WHERE kv.ylesandevastus_id=ylesandevastus.id
        # AND kv.id=ks.kysimusevastus_id AND ks.oige=%s),
        # valede_arv=COALESCE(valimata_oigete_arv, 0) + 
        # (SELECT count(ks.id) FROM kvsisu ks, kysimusevastus kv 
        # WHERE kv.ylesandevastus_id=ylesandevastus.id 
        # AND kv.id=ks.kysimusevastus_id AND ks.oige=%s) 
        # WHERE sooritus_id=:sooritus_id
        # """ % (const.C_OIGE, const.C_VALE)
        # Session.execute(sa.text(sql), params)

        sql = """UPDATE ylesandevastus SET
        oigete_arv = COALESCE(valimata_valede_arv, 0) +
        (SELECT COALESCE(SUM(kv.oigete_arv), 0) FROM kysimusevastus kv
        WHERE kv.ylesandevastus_id=ylesandevastus.id),
        valede_arv=COALESCE(valimata_oigete_arv, 0) + 
        (SELECT COALESCE(SUM(kv.valede_arv), 0) FROM kysimusevastus kv 
        WHERE kv.ylesandevastus_id=ylesandevastus.id) 
        WHERE sooritus_id=:sooritus_id"""
        Session.execute(sa.text(sql), params)

        sql = """UPDATE ylesandevastus SET oigete_suhe=
        CASE WHEN oigete_arv IS NULL OR valede_arv is NULL OR oigete_arv=0 AND valede_arv=0 THEN NULL 
        ELSE CAST(oigete_arv AS DOUBLE PRECISION)/(oigete_arv + valede_arv) END 
        WHERE ylesandevastus.sooritus_id=:sooritus_id
        """
        Session.execute(sa.text(sql), params)       

        # sql = """UPDATE ylesandevastus SET
        # vastamata_arv = 
        # (SELECT COUNT(kvsisu.id) FROM kysimusevastus kv, kvsisu 
        # WHERE kv.ylesandevastus_id=ylesandevastus.id
        # AND kvsisu.kysimusevastus_id=kv.id
        # AND kvsisu.oige != %s AND kvsisu.oige != %s
        # WHERE sooritus_id=:sooritus_id""" % (const.C_OIGE, const.C_VALE)
        # Session.execute(sa.text(sql), params)
        
    def calc_alatestitulemus(self, pallid, is_delf):
        # tasemeeksamite korral alatestide pallid ymardatakse
        # riigieksamite korral ei ymardata
        from eis.model.eksam.ylesandevastus import Ylesandevastus
        testiosa = self.testiosa
        on_tseis = testiosa.test.on_tseis
        Session.flush()

        def roundhalf(pallid):
            """DELFScolaire eksamis kasutatav ymardamine poole punkti täpsusega
            """
            p = round(pallid)
            if pallid < p - .250001:
                p -= .5
            elif pallid > p + .2499999:
                p += + .5
            return p
        
        to_pallid = 0
        li_atos_id = list()
        for atos in self.alatestisooritused:
            # et topelt ei tuleks
            if atos.id in li_atos_id:
                continue
            li_atos_id.append(atos.id)
            
            alatest = atos.alatest
            max_pallid = alatest.max_pallid or atos.max_pallid
            if on_tseis and max_pallid:
                max_pallid = round(max_pallid)
            q = (Session.query(sa.func.sum(Ylesandevastus.oigete_arv),
                               sa.func.sum(Ylesandevastus.valede_arv),
                               sa.func.sum(Ylesandevastus.valimata_oigete_arv),
                               sa.func.sum(Ylesandevastus.valimata_valede_arv))
                 .join((Testiylesanne, Testiylesanne.id==Ylesandevastus.testiylesanne_id))
                 .filter(Ylesandevastus.sooritus_id==self.id)
                 .filter(Testiylesanne.alatest_id==alatest.id)
                 #.filter(Testiylesanne.liik==const.TY_LIIK_Y)
                 .filter(Ylesandevastus.loplik==True)                 
                 )
            atos.oigete_arv, atos.valede_arv, atos.valimata_oigete_arv, atos.valimata_valede_arv = q.first()

            if atos.oigete_arv is None or atos.valede_arv is None or \
               atos.oigete_arv == 0 and atos.valede_arv == 0:
                atos.oigete_suhe = None
            else:
                atos.oigete_suhe = float(atos.oigete_arv) / (atos.oigete_arv + atos.valede_arv)
                
            if alatest.skoorivalem:
                # arvutame valemiga
                # OIGED - alatesti ülesannete õigete vastuste arv kokku
                e_locals = {'OIGED': atos.oigete_arv or 0}
                value, err0, err, buf1 = eval_formula(alatest.skoorivalem, e_locals, divzero=0)
                #log.info('s_id=%s, atos_id=%s: %s' % (self.id, atos.id, buf1))
                if value and value > max_pallid:
                    log.error('testiosa %d.sooritus %d alatest %d arvutatud tulemus %s, lubatud max %s' % \
                              (self.testiosa_id, self.id, alatest.id, value, max_pallid))
                    value = max_pallid
            else:
                # alatesti pallideks on ylesandevastuste pallide summa + kriteeriumite pallide summa
                total_field = sa.func.sum(Ylesandevastus.pallid)
                if on_tseis:
                    total_field = sa.func.round(total_field + .000001)
                q = (Session.query(total_field)
                     .filter(Ylesandevastus.sooritus_id==self.id)
                     .join((Testiylesanne, Testiylesanne.id==Ylesandevastus.testiylesanne_id))
                     .filter(Testiylesanne.alatest_id==alatest.id)
                     .filter(Ylesandevastus.loplik==True)
                     )
                value = q.scalar()

                # kriteeriumite pallid
                total_field = sa.func.sum(Kriteeriumivastus.pallid)
                if on_tseis:
                    total_field = sa.func.round(total_field + .000001)
                q = (Session.query(total_field)
                     .filter(Kriteeriumivastus.sooritus_id==self.id)
                     .join(Kriteeriumivastus.hindamiskriteerium)
                     )
                # hindamiskogumi seos alatestiga
                if testiosa.lotv:
                    q = q.filter(sa.exists().where(
                        sa.and_(Hindamiskriteerium.hindamiskogum_id==Valitudylesanne.hindamiskogum_id,
                                Valitudylesanne.testiylesanne_id==Testiylesanne.id,
                                Testiylesanne.alatest_id==alatest.id)))
                else:
                    q = q.filter(sa.exists().where(
                        sa.and_(Hindamiskriteerium.hindamiskogum_id==Testiylesanne.hindamiskogum_id,
                                Testiylesanne.alatest_id==alatest.id)))
                value1 = q.scalar()
                if value1:
                    value = (value or 0) + value1

            if value and is_delf:
                # ymardamine poole punktini
                value = roundhalf(value)
            atos.pallid = value
            if atos.pallid is not None and max_pallid:
                atos.tulemus_protsent = atos.pallid * 100. / max_pallid
                assert atos.tulemus_protsent < 100.0001, '%s alatesti %s tulemus liiga suur: %s>%s' % (self.tahised, atos.alatest_id, atos.pallid, max_pallid)
                    
            else:
                atos.tulemus_protsent = None

            # tasemeeksami korral summeeritakse alatestide ymardatud pallid
            to_pallid += atos.pallid or 0    
        return to_pallid

    def gen_tahis(self):
        """Genereeritakse testikoha piires unikaalne tähis
        """
        testikoht = self.testikoht or Testikoht.get(self.testikoht_id)
        if not self.tahis and testikoht :
            testikoht.sooritused_seq += 1
            testiosa = testikoht.testiosa
            if testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
                self.tahis = '%03d' % testikoht.sooritused_seq
            else:
                self.tahis = '%04d' % testikoht.sooritused_seq
            self.tahised = '%s-%s' % (testikoht.tahis, self.tahis)

    def get_tulemus(self, digits=3, with_pr=True):
        #if self.hindamine_staatus == const.H_STAATUS_HINNATUD:
        return self.get_tulemus_pro(digits, with_pr)

    def get_tulemus_pro(self, digits=3, with_pr=True):
        pallid = self.pallid or 0
        max_pallid = self.max_pallid
        if pallid is None:
            return None
        osa = self.testiosa
        test = osa.test
        buf = ''
        if test.pallideta:
            if not test.protsendita and self.tulemus_protsent is not None:
                buf = _('{p3}%').format(p3=fstr(self.tulemus_protsent, digits))
        elif max_pallid and not test.protsendita and with_pr and (self.tulemus_protsent is not None):
            buf = _('{p1}p {p2}-st, {p3}%').format(
                p1=fstr(pallid, digits),
                p2=fstr(max_pallid, digits),
                p3=fstr(self.tulemus_protsent, digits))
        elif max_pallid and not test.protsendita:
            buf = _('{p1}p {p2}-st').format(
                p1=fstr(pallid, digits),
                p2=fstr(max_pallid, digits))
        else:
            buf = _('{p1}p').format(
                p1=fstr(pallid, digits))
        return buf

    def get_tulemus_eraldi(self):
        if self.pallid is not None:
            # yleni arvutihinnatav test
            return self.get_tulemus_pro()
        elif self.pallid_arvuti is not None:
            # osaliselt arvutihinnatav ylesanne
            return self.get_tulemus_eraldi_(self.pallid_arvuti,
                                            self.pallid_kasitsi,
                                            self.pallid)

    @classmethod
    def get_tulemus_eraldi_(cls, pallid_arvuti, pallid_kasitsi, pallid):
        buf = _("Esialgsed arvutihinnatavad punktid: {p}").format(p=fstr(pallid_arvuti) or '-')
        buf += '<br/>' + _("Subjektiivhinnatavad punktid: {p}").format(p=fstr(pallid_kasitsi) or '?')
        buf += '<br/>' + _("Tulemus kokku: {p}").format(p=fstr(pallid) or '?')
        return buf        

    def can_show(self, test, sooritaja, testimiskord, app_ekk):
        """Kas soorituse vastuste vaatamisel võib kuvada soorituse tulemust,
        alatestide tulemust, ylesannete tulemust
        """
        if not sooritaja:
           sooritaja = self.sooritaja
        show_sooritus_tulemus = show_alatestitulemus = show_ylesandetulemus = None
        
        if self.staatus != const.S_STAATUS_TEHTUD or test.diagnoosiv or not test.naita_p:
            show_sooritus_tulemus = False
            show_alatestitulemus = False
            show_ylesandetulemus = False
        elif app_ekk:
            show_sooritus_tulemus = True
            show_alatestitulemus = True
            show_ylesandetulemus = True
        elif testimiskord and sooritaja.vaie_ettepandud:
            show_sooritus_tulemus = False
            show_alatestitulemus = False
            show_ylesandetulemus = False
        elif testimiskord:
            show_sooritus_tulemus = testimiskord.koondtulemus_avaldet
            show_alatestitulemus = testimiskord.alatestitulemused_avaldet
            show_ylesandetulemus = testimiskord.ylesandetulemused_avaldet
        elif sooritaja: 
            nk = sooritaja.nimekiri
            show_sooritus_tulemus = not nk or nk.tulemus_nahtav
            show_alatestitulemus = not nk or nk.alatestitulemus_nahtav
            show_ylesandetulemus = show_alatestitulemus
        else:
            show_sooritus_tulemus = True
            show_alatestitulemus = True
            show_ylesandetulemus = True
        return show_sooritus_tulemus, show_alatestitulemus, show_ylesandetulemus
    
    def delete_subitems(self):    
        self.delete_subrecords(['hindamisolekud',
                                'erivajadused',
                                'erikomplektid',
                                'soorituslogid',
                                ])
        from eis.model.eksam import Alatestisooritus, Ylesandevastus, Npvastus, Soorituskomplekt, Seblog
        for tbl in (Ylesandevastus,
                    Npvastus,
                    Soorituskomplekt,
                    Alatestisooritus,
                    Seblog):
            q = tbl.query.filter_by(sooritus_id=self.id)
            for r in q.all():
                r.delete()
                
    def get_piiraeg(self, testiosa1):
        testiosa = self.testiosa
        piiraeg = testiosa.piiraeg
        if piiraeg:
            piiraeg += self.lisaaeg or 0
        if piiraeg:
            ajakulu = self.ajakulu or 0
            if self.staatus in (const.S_STAATUS_POOLELI, const.S_STAATUS_KATKESTATUD):
                ajakulu = (datetime.now() - self.algus).seconds
                if testiosa.aeg_peatub and self.peatatud_aeg:
                    ajakulu = max(0, ajakulu - self.peatatud_aeg)
            kasutamata = piiraeg - ajakulu
            
            testiruum = self.testiruum
            if testiruum:
                lopp = testiruum.lopp
                if lopp:
                    lopuni = (lopp - datetime.now()).seconds
                    if lopuni < kasutamata:
                        kasutamata = lopuni
            return piiraeg, ajakulu, kasutamata
        else:
            return None, None, None

    @property
    def piiraeg(self):
        testiosa = self.testiosa
        piiraeg = testiosa.piiraeg
        if piiraeg:
            piiraeg += self.lisaaeg or 0
            return piiraeg

    @property
    def kasutamata_aeg(self):
        piiraeg, ajakulu, kasutamata = self.get_piiraeg(self.testiosa)
        return kasutamata

    @classmethod
    def set_piiraeg_muutus(cls, testiosa_id, testiruum_id=None):
        """Leiame pooleliolevad sooritused ja teeme neile märke, et
        brauseris on vaja muuta piiraja taimerit.
        """
        q = (Session.query(Sooritus)
             .filter(Sooritus.testiosa_id==testiosa_id)
             .filter(Sooritus.staatus==const.S_STAATUS_POOLELI)
             .filter(Sooritus.seansi_algus > datetime.now() - timedelta(hours=6))
             )
        if testiruum_id:
            q = q.filter(Sooritus.testiruum_id==testiruum_id)
        now = int(datetime.now().timestamp())
        for tos in q.all():
            tos.piiraeg_muutus = now

    def set_piiraeg_muutus1(self):
        self.piiraeg_muutus = int(datetime.now().timestamp())
           
    @property
    def staatus_nimi(self):
        return usersession.get_opt().S_STAATUS.get(self.staatus)    

    @property
    def hindamine_staatus_nimi(self):
        return usersession.get_opt().H_STAATUS.get(self.hindamine_staatus)

    def saab_alustada(self, ta=None, testiruum=None):
        "Kas sooritaja võib lahendamist alustada?"
        if self.staatus == const.S_STAATUS_ALUSTAMATA:
            # alustamata olekus saab tavaliselt alustada
            ta = ta or self.toimumisaeg
            if ta:
                algusaja_kontroll = ta.algusaja_kontroll
            else:
                testiruum = testiruum or self.testiruum
                algusaja_kontroll = testiruum and testiruum.algusaja_kontroll
            if algusaja_kontroll:
                # enne alguse kellaaega ei ole lubatud alustada
                now = datetime.now()
                truum = testiruum or self.testiruum
                if not truum.algus or truum.algus > now:
                    # algus pole veel käes
                    return False
                if truum.lopp and truum.lopp < now:
                    # sooritamiseks antud aeg on läbi
                    return False
            return True
        
        if self.staatus == const.S_STAATUS_REGATUD:
            # regatud olekus saab alustada siis,
            # kui on suuline test
            if self.testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP, const.VASTVORM_I):
                return True
            # või kui on aja järgi alustamine ja praegu on alustamise aeg
            ta = ta or self.toimumisaeg
            truum = testiruum or self.testiruum
            aja_jargi_alustatav = False
            if ta:
                aja_jargi_alustatav = ta.aja_jargi_alustatav
            elif truum:
                aja_jargi_alustatav = truum.aja_jargi_alustatav

            if aja_jargi_alustatav:
                now = datetime.now()
                if truum and truum.algus:
                    # aja järgi alustatav määratud sooritus
                    if truum.algus <= now:
                        if not truum.alustamise_lopp or now <= truum.alustamise_lopp:
                            if not truum.lopp or now < truum.lopp:
                                return True
                elif ta:
                    # aja järgi alustatav toimumisaeg
                    tpaev = truum and truum.toimumispaev
                    if tpaev:
                        if tpaev.aeg <= now:
                            if not tpaev.alustamise_lopp or now <= tpaev.alustamise_lopp:
                                if not tpaev.lopp or now < tpaev.lopp:
                                    return True
        return False
    
    def set_staatus(self, staatus, stpohjus=None):
        if self.staatus == const.S_STAATUS_TEHTUD and staatus < const.S_STAATUS_TEHTUD:
            # avatakse test, mis on juba tehtud
            # leiame viimase alatesti, mida sooritaja on näinud
            testiosa = self.testiosa
            for ala in reversed(self.alatestisooritused):
                if ala.staatus == const.S_STAATUS_TEHTUD:
                    if not ala.seansi_algus:
                        # alatestid, mida sooritaja pole näinud, lähevad alustamata olekusse
                        ala.staatus = const.S_STAATUS_ALUSTAMATA
                    else:
                        # viimane alatest, mida sooritaja on näinud, läheb katkestatud olekusse
                        ala.staatus = const.S_STAATUS_KATKESTATUD
                        if testiosa.yhesuunaline:
                            # kui on yhesuunaline testiosa, siis eespool olevad tehtud alatestid jäävad tehtuks
                            break
                        
        if self.staatus != staatus or stpohjus:
            self.stpohjus = stpohjus
        if staatus in (const.S_STAATUS_PUUDUS_VANEM, const.S_STAATUS_PUUDUS_HEV):
            self.puudumise_pohjus = staatus
            self.staatus = const.S_STAATUS_PUUDUS
        else:
            self.puudumise_pohjus = None
            self.staatus = staatus

        if staatus == const.S_STAATUS_TEHTUD:
            # kui testiosa on tehtud, siis peavad kõik alatestid ka tehtud olema
            # (välja arvatud testiväline alatest)
            for atos in self.alatestisooritused:
                if atos.staatus not in (const.S_STAATUS_TEHTUD, const.S_STAATUS_VABASTATUD):
                    if not atos.alatest.testivaline:
                        atos.staatus = const.S_STAATUS_TEHTUD
                        atos.lopp = self.lopp

    def get_ylesandevastused(self, testiylesanne_id=None, komplekt_id=None, muudetav=None, kehtiv=True, ylesanne_id=None, vy=None, loplik=True):
        "Sooritusega seotud ylesandevastuste kirjed"
        from eis.model.eksam.ylesandevastus import Ylesandevastus
        li = []
        q = (Session.query(Ylesandevastus)
             .filter_by(sooritus_id=self.id)
             )
        if testiylesanne_id:
            q = q.filter_by(testiylesanne_id=testiylesanne_id)
        if kehtiv:
            q = q.filter(Ylesandevastus.kehtiv==True)
        if muudetav:
            q = q.filter(Ylesandevastus.muudetav==True)
        if ylesanne_id:
            q = q.join((Valitudylesanne, Valitudylesanne.ylesanne_id==ylesanne_id))
        for rcd in q.all():
            if komplekt_id:
                # otsitakse antud komplekti kuuluva ylesande vastust
                vy2 = Valitudylesanne.get(rcd.valitudylesanne_id)
                if vy2 and vy2.komplekt_id == komplekt_id:
                    if (not vy or vy.id == vy2.id):
                        li.append(rcd)
            elif not loplik or rcd.loplik:
                # otsitakse lõplikult valitud ylesande vastust
                li.append(rcd)
        return li

    def get_ylesandevastus(self, testiylesanne_id, komplekt_id=None, vy=None, muudetav=None, kehtiv=True, ylesanne_id=None):
        yv = None
        for rcd in self.get_ylesandevastused(testiylesanne_id,
                                         komplekt_id=komplekt_id,
                                         muudetav=muudetav,
                                         kehtiv=kehtiv,
                                         vy=vy,
                                         ylesanne_id=ylesanne_id):
            yv = rcd
            if yv.loplik:
                break
            # vaatame edasi, kas leidub ka lõplik (valikylesandes)
            continue
        return yv

    def getq_ylesandevastus(self, testiylesanne_id, komplekt_id=None, vy=None, muudetav=None, kehtiv=True, ylesanne_id=None):
        return self.get_ylesandevastus(testiylesanne_id, komplekt_id, vy, muudetav, kehtiv, ylesanne_id)

    def give_ylesandevastus(self, ty_id, vy_id=None, kehtiv=None, komplekt_id=None):
        return self.giveq_ylesandevastus(ty_id, vy_id, kehtiv, komplekt_id)

    def giveq_ylesandevastus(self, ty_id, vy_id, kehtiv=None, komplekt_id=None, muudetav=True):
        from eis.model.eksam.ylesandevastus import Ylesandevastus
        is_modified = False
        rcd = self.getq_ylesandevastus(ty_id, komplekt_id, vy_id, kehtiv=kehtiv, muudetav=muudetav)
        if not rcd:
            assert vy_id, 'vy_id puudu'
            rcd = Ylesandevastus(valitudylesanne_id=vy_id,
                                 testiylesanne_id=ty_id,
                                 muudetav=True,
                                 kehtiv=True,
                                 sooritus_id=self.id,
                                 vastuseta=True)
            is_modified = True
        if vy_id:
            if rcd.valitudylesanne_id != vy_id:
                rcd.valitudylesanne_id = vy_id
                is_modified = True

        q = (Session.query(Ylesandevastus)
             .filter_by(sooritus_id=self.id)
             .filter_by(testiylesanne_id=ty_id)
             .filter_by(loplik=True)
             .filter(Ylesandevastus.id!=rcd.id))
        for _yv in q.all():
            _yv.loplik = None
            is_modified = True
        if not rcd.loplik:
            rcd.loplik = True
            is_modified = True
        if is_modified:
            Session.flush()
        
        # uuendame vastatud ylesande max pallid
        rcd.calc_max_pallid(ty_id, vy_id)
        rcd.is_modified = is_modified
        return rcd

    def get_komplekt_id_by_kv(self, kv_id):
        "Leitakse sooritaja komplekt antud komplektivalikust"
        from eis.model.eksam import Soorituskomplekt
        q = (SessionR.query(Soorituskomplekt.komplekt_id)
             .filter_by(sooritus_id=self.id))
        if kv_id:
            q = q.filter_by(komplektivalik_id=kv_id)
        for kv_id, in q.all():
            return kv_id

    def get_komplekt(self, alatest_id):
        "Leitakse sooritatav komplekt"
        # leiame alatestis kasutatava komplektivaliku
        
        kv = self.testiosa.get_komplektivalik(alatest_id)
        if kv is not None:
            return self.get_komplekt_by_kv(kv.id)
 
    def get_toimumisaeg(self):
        return self.toimumisaeg

    def kas_on_erivajadused(self):
        "Kontrollitakse, kas on vaja märget eritingimuste olemasolu kohta"
        if self.tugiisik_kasutaja_id:
            return True
        if self.staatus == const.S_STAATUS_VABASTATUD:
            return True
        for atos in self.alatestisooritused:
            if atos.staatus == const.S_STAATUS_VABASTATUD:
                return True
        for r in self.erivajadused:
            return True
        if self.sooritaja.vabastet_kirjalikust:
            for alatest in self.testiosa.alatestid:
                if alatest.alatest_kood == const.ALATEST_RK_KIRJUTAMINE:
                    return True
        return False
    
    def set_erivajadused(self, on_erivajadused):
        "Märgitakse eritingimuste olemasolu"
        if on_erivajadused is None:
            on_erivajadused = self.kas_on_erivajadused()
        sooritaja = self.sooritaja
        if on_erivajadused:
            if not self.on_erivajadused:
                self.on_erivajadused = True
            if not sooritaja.on_erivajadused:
                sooritaja.on_erivajadused = True
        else:
            if self.on_erivajadused:
                self.on_erivajadused = False
            sooritaja_on_erivajadused = len([tos for tos in sooritaja.sooritused if tos.on_erivajadused]) > 0
            if sooritaja.on_erivajadused != sooritaja_on_erivajadused:
                sooritaja.on_erivajadused = sooritaja_on_erivajadused

    def get_erivajadus(self, kood):
        for rcd in self.erivajadused:
            if rcd.erivajadus_kood == kood:
                return rcd

    def give_erivajadus(self, kood):
        from .erivajadus import Erivajadus
        rcd = self.get_erivajadus(kood)
        if not rcd:
            rcd = Erivajadus(erivajadus_kood=kood,
                             sooritus_id=self.id)
            self.erivajadused.append(rcd)
        return rcd

    def get_str_erivajadused(self, sep=', ', kinnitatud=False, kasutamata=False, markused=True):
        # kinnitatud - kas kuvada ainult kinnitatud erivajadused
        res = ''
        li = []
        if self.staatus == const.S_STAATUS_VABASTATUD:
            res = _("Vabastatud")
        else:
            li1 = list(self.alatestisooritused)
            if li1:
                li = [a.alatest.nimi for a in li1 if a.staatus==const.S_STAATUS_VABASTATUD]
            else:
                # kui alatestisooritusi pole veel loodud
                if self.sooritaja.vabastet_kirjalikust:
                    li = [a.nimi for a in self.testiosa.alatestid if a.alatest_kood == const.ALATEST_RK_KIRJUTAMINE]
            if li:
                res = _("Vabastatud") + ' (%s)' % ','.join(li)

        test = self.testiosa.test
        li = []
        for eri in self.erivajadused:
            if eri.kasutamata and not kasutamata:
                continue
            if (kinnitatud or self.on_erivajadused_kinnitatud) and not eri.ei_vaja_kinnitust(test):
                # kui erivajadused on kinnitatud, siis näitame kinnitatud erivajadusi
                if eri.kinnitus:
                    buf = eri.erivajadus_nimi or ''
                    if (not buf or markused) and eri.kinnitus_markus:
                        buf += ' (%s)' % eri.kinnitus_markus
                    li.append(buf)
            else:
                # kui pole kinnitatud või ei vaja kinnitust, siis näitame taotletud erivajadusi
                if eri.taotlus:
                    buf = eri.erivajadus_nimi or ''
                    if (not buf or markused) and eri.taotlus_markus:
                        buf += ' (%s)' % eri.taotlus_markus
                    li.append(buf)                

        if self.tugiisik_kasutaja_id:
            li.append(_("Tugiisik"))
        res += ' ' + sep.join(li)
        return res.strip()

    @property
    def on_kinnitatud_erivajadusi(self):
        if self.on_erivajadused:
            if self.staatus == const.S_STAATUS_VABASTATUD:
                return True
            for a in self.alatestisooritused:
                if a.staatus == const.S_STAATUS_VABASTATUD:
                    return True
            test = self.testiosa.test
            for eri in self.erivajadused:
                if eri.kinnitus or eri.ei_vaja_kinnitust(test):
                    return True
        return False

    def give_hindamisolekud(self, pooleli=False):
        if self.staatus in (const.S_STAATUS_PUUDUS, const.S_STAATUS_VABASTATUD):
            for rcd in self.hindamisolekud:
                # ei või kustutada, sest võidakse hiljem taastada ja siis ei tea komplekti (ES-2475)
                rcd.puudus = True

        elif self.staatus in (const.S_STAATUS_KATKESTATUD, const.S_STAATUS_KATKESPROT, const.S_STAATUS_TEHTUD) or \
                 pooleli and self.staatus == const.S_STAATUS_POOLELI:
            sooritaja = self.sooritaja
            kursus = sooritaja.kursus_kood
            testiosa = self.testiosa
            arvutihinnatav = True
            for rcd in testiosa.hindamiskogumid:
                if rcd.staatus == const.B_STAATUS_KEHTIV and rcd.kursus_kood == kursus:
                    holek = self.give_hindamisolek(rcd)
                    if self.staatus == const.S_STAATUS_TEHTUD and not self.klastrist_toomata:
                        # alatestidega testi korral kontrollime, kas on mõnda selle hindamiskogumiga seotud alatesti teinud
                        testimiskorrata = not self.toimumisaeg_id
                        holek.puudus = self.check_hk_puudus(rcd, testiosa, testimiskorrata)
                    arvutihinnatav &= rcd.arvutihinnatav
                else:
                    # hindamiskogumil pole ylesandeid
                    holek = self.get_hindamisolek(rcd)
                    if holek:
                        holek.delete()
                        self.hindamisolekud.remove(holek)
            if not arvutihinnatav and self.hindamiskogumita:
                # testimiskorrata sooritusel toimub hindamine hindamiskogumita
                # (sest hindajale määratud ylesannete valik ei pea vastama hindamiskogumile);
                # muud holekud tehakse testimiskorrata soorituse korral ainult komplekti salvestamiseks
                holek = self.give_hindamisolek(None)
                
        # kui sooritaja on eemaldatud, siis ei ole vaja teha uusi kirjeid, 
        # aga juba tehtud kirjeid ei kustutata, 
        # sest võib-olla eemaldamine tühistatakse kunagi

    def check_hk_puudus(self, hindamiskogum, testiosa, testimiskorrata):
        """Selgitame välja, kas sooritaja võis sooritada antud hindamiskogumi ülesandeid
        Eeldame, et sooritus.staatus==const.S_STAATUS_TEHTUD.
        """
        from eis.model.eksam.alatestisooritus import Alatestisooritus
        from eis.model.eksam.ylesandevastus import Ylesandevastus
        
        puudus = False
        sooritus_id = self.id
        if not hindamiskogum:
            # testimiskorrata või eeltestisooritust hinnatakse hindamiskogumita
            return False

        hindamiskogum_id = hindamiskogum.id
        if testiosa.on_alatestid:
            # Kontrollitakse, kas on sooritanud mõnda sellist alatesti,
            # mis sisaldab antud hindamiskogumi ülesandeid
            # (Ei saa kasutada SessionR, sest seda tehakse p-testi toimumisprotokolli sisestamisel,
            # kus Session kaudu alles salvestatakse alatestisoorituste olekuid)
            q = (Session.query(sa.func.count(Alatestisooritus.id))
                 .filter(Alatestisooritus.staatus==const.S_STAATUS_TEHTUD)
                 .filter(Alatestisooritus.sooritus_id==sooritus_id)
                 .join((Testiylesanne,
                        Testiylesanne.alatest_id==Alatestisooritus.alatest_id))
                 )
            if testiosa.lotv:
                # võimalik, et on sooritanud sellist komplekti, mille ylesandeid siin ei ole
                # aga enne hindamist me ei pruugi veel teada, mis komplekti ta sooritas
                q = (q.join(Testiylesanne.valitudylesanded)
                     .filter(Valitudylesanne.hindamiskogum_id==hindamiskogum_id))
            else:
                q = q.filter(Testiylesanne.hindamiskogum_id==hindamiskogum_id)
            if q.scalar() == 0:
                puudus = True
                
        vastvorm_k = (const.VASTVORM_KE,
                      const.VASTVORM_SE,
                      #const.VASTVORM_KP,
                      const.VASTVORM_I)
        if not puudus and testiosa.vastvorm_kood in vastvorm_k:
            # kontrollime, kas hindamisolekut on sooritatud
            # Kontrollitakse, kas on sooritanud mõnda sellist ülesannet,
            # mis sisaldub antud hindamiskogumis
            q = (SessionR.query(sa.func.count(Ylesandevastus.id))
                 .filter(Ylesandevastus.sooritus_id==sooritus_id)                 
                 .filter(Ylesandevastus.loplik==True)                 
                 )
            if testiosa.lotv:
                q = (q.join((Valitudylesanne,
                             Valitudylesanne.id==Ylesandevastus.valitudylesanne_id))
                     .filter(Valitudylesanne.hindamiskogum_id==hindamiskogum_id))
            else:
                q = (q.join((Testiylesanne,
                             Testiylesanne.id==Ylesandevastus.testiylesanne_id))
                     .filter(Testiylesanne.hindamiskogum_id==hindamiskogum_id))
            puudus = q.scalar() == 0

        return puudus

    def get_hindamisolek(self, hindamiskogum):
        hk_id = hindamiskogum and hindamiskogum.id or None
        for rcd in self.hindamisolekud:
            if hk_id == rcd.hindamiskogum_id:
                return rcd

    def give_hindamisolek(self, hindamiskogum):
        sooritaja = self.sooritaja
        valimis = sooritaja.valimis
        hindamisprobleem = None
        if hindamiskogum:
            hindamistase = hindamiskogum.get_hindamistase(valimis, self.toimumisaeg)
        else:
            # testimiskorrata sooritust hinnatakse hindamiskogumita ja tasemel 1
            hindamiskogum = None
            hindamistase = const.HINDAJA1

        if hindamistase > const.HTASE_ARVUTI and sooritaja.vaie_esitatud:
            # vaide korral hindamine
            hindamistase = const.HINDAJA5

        rcd = self.get_hindamisolek(hindamiskogum)
        if not rcd:
            # lisame uue hindamisoleku
            if hindamistase > const.HTASE_ARVUTI:
                hindamisprobleem = const.H_PROBLEEM_SISESTAMATA
            hk_id = hindamiskogum and hindamiskogum.id or None
            rcd = Hindamisolek(hindamiskogum_id=hk_id,
                               sooritus_id=self.id,
                               staatus=const.H_STAATUS_HINDAMATA,
                               hindamistase=hindamistase,
                               hindamisprobleem=hindamisprobleem)
        else:
            # muudame vajadusel hindamisoleku parameetreid,
            # kui hindamiskogumid vms on vahepeal muutunud
            if rcd.puudus or rcd.mittekasitsi:
                # pole käsitsi midagi hinnata
                rcd.hindamistase = const.HTASE_ARVUTI
            elif hindamistase == const.HTASE_ARVUTI and rcd.hindamistase > hindamistase:
                # kogum on muutunud arvutihinnatavaks
                rcd.hindamistase = hindamistase
            elif hindamistase > rcd.hindamistase:
                # kogum on hindajaid juurde saanud
                rcd.hindamistase = hindamistase

        return rcd

    def get_sisestusolek(self, sisestuskogum_id, liik):
        for rcd in self.sisestusolekud:
            if sisestuskogum_id == rcd.sisestuskogum_id and liik == rcd.liik:
                return rcd

    def give_sisestusolek(self, sisestuskogum, liik):
        rcd = self.get_sisestusolek(sisestuskogum.id, liik)
        if not rcd:
            rcd = Sisestusolek(sooritus_id=self.id,
                               sisestuskogum_id=sisestuskogum.id,
                               staatus=const.H_STAATUS_HINDAMATA,
                               staatus1=const.H_STAATUS_HINDAMATA,
                               staatus2=const.H_STAATUS_HINDAMATA,
                               liik=liik)
        return rcd

    @property
    def soorituskomplektid(self):
        from eis.model.eksam.soorituskomplekt import Soorituskomplekt
        q = (Session.query(Soorituskomplekt)
             .filter_by(sooritus_id=self.id))
        return q.all()
    
    def get_komplekt_by_kv(self, kv_id):
        "Leitakse sooritaja komplekt antud komplektivalikust"
        from eis.model.eksam.soorituskomplekt import Soorituskomplekt
        q = (SessionR.query(Soorituskomplekt.komplekt_id)
             .filter_by(sooritus_id=self.id))
        if kv_id:
            q = q.filter_by(komplektivalik_id=kv_id)
        for k_id, in q.all():
            return Komplekt.get(k_id)
    
    def get_kriteeriumivastus(self, kriteerium_id):
        """Leitakse hinde kirje 
        """
        for rcd in self.kriteeriumivastused:
            if rcd.hindamiskriteerium_id == kriteerium_id:
                return rcd

    def give_kriteeriumivastus(self, kriteerium_id):
        rcd = self.get_kriteeriumivastus(kriteerium_id)
        if not rcd:
            rcd = Kriteeriumivastus(hindamiskriteerium_id=kriteerium_id,
                                    sooritus_id=self.id)
            self.kriteeriumivastused.append(rcd)
        return rcd

    def suuna_korrata(self, testikoht, testiruum):
        # testimiskorrata testis sooritaja suunamine kohale
        # NB! Peale kasutamist kutsuda välja testiruum.set_sooritajate_arv()        
        self.testikoht = testikoht
        self.testiruum = testiruum
        koht = testikoht.koht or Koht.get(testikoht.koht_id)
        self.piirkond_id = koht.piirkond_id                
        Session.flush()

    def suuna(self, testikoht, testiruum, tpr=None, algus=None, err=False, valim_kontroll=True):
        "Suuna.sooritus soorituskohta ja määra talle testiprotokoll"
        # NB! Peale kasutamist kutsuda välja testiruum.set_sooritajate_arv()
        rc = True
        error = None
        sooritaja = self.sooritaja
        assert sooritaja.lang, 'Soorituskeel puudub'
        kursus = sooritaja.kursus_kood
        toimumisaeg = self.toimumisaeg
        testiosa = self.testiosa or Testiosa.get(self.testiosa_id)
        if testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
            # pabertesti korral on testipaketid
            # vaatame, kas igas ruumis peab oma pakett olema või on testikoha peale üks pakett
            paketiruum = toimumisaeg.on_ruumiprotokoll and testiruum or None
            # leiame soorituskohale ja keelele vastava testipaketi
            pakett = testikoht.give_testipakett(sooritaja.lang, paketiruum)
        else:
            # e-testis ei ole testipakette
            pakett = None
        # protokollirühma maksimaalne võimalik suurus
        max_size = toimumisaeg.protok_ryhma_suurus

        log.debug('SUUNA %s tkoht=%s truum=%s lang=%s pakett=%s, max=%s' % (self.id, testikoht.id, testiruum and testiruum.id, self.sooritaja.lang, pakett and pakett.id, max_size))

        if rc and self.reg_toimumispaev_id and testiruum.toimumispaev_id != self.reg_toimumispaev_id:
            # testiruum ei sobi, sest.sooritus peab olema kindlal päeval
            error = _("Sooritajat ei või suunata teise toimumispäevaga ruumi")
            rc = False

        if rc and sooritaja.valimis and testiruum:
            tpv = testiruum.toimumispaev
            if tpv and tpv.valim == False:
                # valimi jaoks pole see päev lubatud
                if valim_kontroll:
                    error = _("Selle ruumi aeg ei ole valimis lubatud")
                    rc = False
                else:
                    error = _("Tegelikult ei ole selle ruumi aeg valimis lubatud")
                    
        if rc and tpr is not None:
            # soovitud testiprotokoll on juba ette antud
            assert tpr.testiruum == testiruum, 'Testiruum vale'
            if max_size and len(tpr.sooritused) >= max_size:
                # protokollirühm ei sobi, kuna on täis
                error = _("Sooritajat ei saa suunata protokollirühma, mis on juba täis")
                rc = False
            if tpr.kursus_kood and tpr.kursus_kood != kursus:
                # protokollirühm ei sobi, kuna on teise kursuse jaoks
                error = _("Sooritajat ei saa suunata muu kursuse protokollirühma")
                rc = False
        elif rc:
            # leiame esimese sobiva valmis protokollirühma
            for r_tpr in testiruum.testiprotokollid:
                if not pakett or r_tpr.testipakett == pakett:
                    # e-test või p-testi sama keele pakett
                    if r_tpr.kursus_kood == kursus or not r_tpr.kursus_kood:
                        # yhes protokolliryhmas tohivad olla yheainsa kursuse sooritajad
                        if not algus or r_tpr.algus == algus:
                            # sisseastumistestidel on protokolliryhmal algus
                            if not max_size or r_tpr.soorituste_arv < max_size or \
                                   r_tpr.soorituste_arv == max_size and r_tpr == self.testiprotokoll:
                                tpr = r_tpr
                                break

        if rc:
            if tpr:
                # protokolliryhm on leitud
                if kursus and not tpr.kursus_kood:
                    # kui protokollirühm on käsitsi loodud ja on veel tyhi, siis sel kursust ei ole veel
                    tpr.kursus_kood = kursus
            else:
                # kui sellist pole, siis loome uue protokolli
                tpr = Testiprotokoll(tahis='',
                                     tahised='',
                                     testiruum=testiruum,
                                     kursus_kood=kursus,
                                     testipakett=pakett,
                                     algus=algus)
            if not tpr.tahis:
                # koos suunamisega toimub ka protokollide uuesti nummerdamine
                tpr.gen_tahis()
                tpr.flush()                
            # lisame protokollita soorituse sellele protokollile
            if self.testiprotokoll != tpr:
                log.debug('suunan protokolli %s (%s)' % (tpr.tahis, tpr.id))
                tpr.sooritused.append(self)
                if tpr.algus:
                    self.kavaaeg = tpr.algus
            log.debug('tpr tahis=%s soorituste_arv=%s max=%s' % (tpr.tahis, tpr.soorituste_arv, max_size))
            if self.testikoht != testikoht:
                self.tahis = self.tahised = None
                self.testikoht = testikoht
            koht = testikoht.koht or Koht.get(testikoht.koht_id)
            self.piirkond_id = koht.piirkond_id
            if self.testiruum != testiruum:
                self.testiruum = testiruum
                self.kavaaeg = tpr.algus or testiruum.algus
            Session.flush()
            if toimumisaeg.on_kogused and not self.tahis:
                if toimumisaeg.testiosa.vastvorm_kood not in (const.VASTVORM_KP, const.VASTVORM_SP):
                    # kui kogused on juba arvutatud, aga sooritusel puudub tähis,
                    # siis genereerime ka tähise
                    self.gen_tahis()
        if err:
            return rc, error
        else:
            if error:
                log.error(error)
            return rc

    def log_update(self):
        log_fields = ('staatus',
                      'reg_toimumispaev_id',
                      'kavaaeg',
                      'tahised',
                      'hindamine_staatus',
                      'pallid',
                      'pallid_arvuti',
                      'pallid_kasitsi',
                      'tulemus_protsent',
                      'max_pallid',
                      'testiarvuti_id',
                      'testikoht_id',
                      'testiruum_id',
                      'tugiisik_kasutaja_id',
                      'remote_addr',
                      'autentimine')
        old_values, new_values = self._get_changed_values()
        if new_values:
            fields = [r[0] for r in new_values]
            found = False
            for key in log_fields:
                if key in fields:
                    found = True
                    log.debug('muutus soorituslogi.%s' % key)
                    break
            if found:
                self.add_soorituslogi()
                
    def log_insert(self):
        self.add_soorituslogi()

    def add_soorituslogi(self):
        request = usersession.get_request()
        if request:
            environ = request.environ
            remote_addr = request.remote_addr
        else:
            environ = {}
            remote_addr = None
        server_addr = environ.get('HOSTNAME') or environ.get('SERVER_ADDR')

        if self._logi:
            self._logi.tahised = self.tahised
            self._logi.reg_toimumispaev_id = self.reg_toimumispaev_id
            self._logi.kavaaeg = self.kavaaeg
            self._logi.staatus = self.staatus
            self._logi.stpohjus = self.stpohjus
            self._logi.hindamine_staatus = self.hindamine_staatus
            self._logi.pallid = self.pallid
            self._logi.pallid_arvuti = self.pallid_arvuti
            self._logi.pallid_kasitsi = self.pallid_kasitsi
            self._logi.tulemus_protsent = self.tulemus_protsent
            self._logi.max_pallid = self.max_pallid
            self._logi.testiarvuti_id = self.testiarvuti_id
            self._logi.autentimine = self.autentimine
            self._logi.testikoht_id = self.testikoht_id
            self._logi.testiruum_id = self.testiruum_id
            self._logi.tugiisik_kasutaja_id = self.tugiisik_kasutaja_id
        else:
            self._logi = \
                Soorituslogi(sooritus=self,
                             tahised=self.tahised,
                             reg_toimumispaev_id=self.reg_toimumispaev_id,
                             kavaaeg=self.kavaaeg,
                             staatus=self.staatus,
                             stpohjus=self.stpohjus,
                             hindamine_staatus=self.hindamine_staatus,
                             pallid=self.pallid,
                             pallid_arvuti=self.pallid_arvuti,
                             pallid_kasitsi=self.pallid_kasitsi,
                             tulemus_protsent=self.tulemus_protsent,
                             max_pallid=self.max_pallid,
                             testiarvuti_id=self.testiarvuti_id,
                             autentimine=self.autentimine,
                             testikoht_id=self.testikoht_id,
                             testiruum_id=self.testiruum_id,
                             tugiisik_kasutaja_id=self.tugiisik_kasutaja_id,
                             url=request and request.url[:100] or None,                            
                             remote_addr=remote_addr,
                             server_addr=server_addr)

#### TAGASISIDE EELVAATE JAOKS
class TempKasutaja:
    def __init__(self, nimi):
        self.synnikpv = date.today() - timedelta(days=random.randint(2400, 8000))
        self.nimi = nimi
        self.sugu = const.SUGU_N
        
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

def tempSooritaja(c, test, lang, tehtud):
    "Eelvaates kasutatav sooritaja"
    tmp_j = c.new_item(id=0,
                       test=test,
                       nimi=_("Eesnimi Perekonnanimi"),
                       lang=lang or test.lang,
                       klass="6",
                       paralleel="a",
                       kool_koht=c.new_item(nimi=_("Testkool")),
                       esitaja_kasutaja=TempKasutaja(c.user.fullname),
                       millal=date.today().strftime('%d.%m.%Y'),
                       kasutaja=TempKasutaja('Eesnimi Perekonnanimi'),
                       staatus=const.S_STAATUS_POOLELI,
                       hindamine_staatus=const.H_STAATUS_HINDAMATA,
                       sooritused=[])
    if tehtud:
        tmp_j.staatus = const.S_STAATUS_TEHTUD
        tmp_j.hindamine_staatus = const.H_STAATUS_HINNATUD
    return tmp_j

class TempSoorituskomplekt:
    def __init__(self, komplektivalik_id=None, komplekt_id=None):
        self.komplektivalik_id = komplektivalik_id
        self.komplekt_id = komplekt_id

    @property
    def komplekt(self):
        if self.komplekt_id:
            return Komplekt.get(self.komplekt_id)
        
class TempSooritus:
    "Andmebaasiväline pseudo-sooritus"
    
    def __init__(self, testiosa_id=None, toimumisaeg=None, komplekt=None):
        self.id = gen_temp_id()
        self.testiosa_id = testiosa_id
        self.toimumisaeg = toimumisaeg
        self.toimumisaeg_id = None
        self.testiruum_id = None
        self.testiruum = None
        self.pallid = None
        self.pallid_arvuti = None
        self.pallid_kasitsi = None
        self.max_pallid = None
        self.staatus = None
        self.lisaaeg = 0
        self.piiraeg_muutus = None
        self.ylesandevastused = list()
        self.alatestisooritused = list()
        self.eelvaade_komplekt_id = None
        self.hindamine_staatus_nimi = ''
        self.peatatud_aeg = None
        self.ajakulu = None
        self.sisestusolekud = list()
        self.peatus_algus = None
        self.hindamisolekud = list()
        self.lopp = None
        self.tahised = ''
        self.ylesanneteta_tulemus = False
        self.sooritaja = None
        #self.sooritustagasisided = list()
        #self.sooritaja = TempSooritaja(self)
        self.npvastused = list()
        self.give_hindamisolekud()
        if komplekt:
            self._set_komplekt(komplekt)
        self.is_linear = False
        self.soorituskomplektid = list()
        
    def _set_komplekt(self, komplekt):
        hkogumid_id = [hk.id for hk in komplekt.komplektivalik.hindamiskogumid]
        for holek in self.hindamisolekud:
            if holek.hindamiskogum_id in hkogumid_id:
                holek.puudus = False
                holek.komplekt_id = komplekt.id
        
    def get_komplekt(self, alatest_id):
        kv = self.testiosa.get_komplektivalik(alatest_id)
        hkogumid_id = [hk.id for hk in kv.hindamiskogumid]
        for holek in self.hindamisolekud:
            if (not alatest_id or holek.hindamiskogum_id in hkogumid_id) and holek.komplekt_id:
                return holek.komplekt

    def get_komplekt_by_kv(self, kv_id):
        "Leitakse sooritaja komplekt antud komplektivalikust"
        for sk in self.soorituskomplektid:
            if not kv_id or sk.komplektivalik_id == kv_id:
                return sk.komplekt

    def get_komplekt_id_by_kv(self, kv_id):
        k = self.get_komplekt_by_kv(kv_id)
        if k:
            return k.id
        
    def calc_max_pallid(self):
        pass
    
    @property
    def testiosa(self):
        if self.testiosa_id:
            return Testiosa.get(self.testiosa_id)

    @property
    def alatestid(self):
        return [r for r in self.testiosa.alatestid]

    @property
    def eelvaade_komplekt(self):
        if self.eelvaade_komplekt_id:
            return Komplekt.get(self.eelvaade_komplekt_id)

    @property
    def staatus_nimi(self):
        return usersession.get_opt().S_STAATUS.get(self.staatus)    
    
    def get_tulemus(self):
        return self.get_tulemus_pro()
    
    def get_tulemus_pro(self):
        pallid = self.pallid or 0
        max_pallid = self.max_pallid
        if not max_pallid:
            return fstr(self.pallid)
        return '%sp %s-st, %s%%' % (fstr(pallid), 
                                    fstr(max_pallid), 
                                    fstr(self.tulemus_protsent))
        #fstr(pallid*100/max_pallid))

    def get_tulemus_eraldi(self):
        if self.pallid is not None:
            # yleni arvutihinnatav test
            return self.get_tulemus_pro()
        elif self.pallid_arvuti is not None:
            # osaliselt arvutihinnatav ylesanne
            return Sooritus.get_tulemus_eraldi_(self.pallid_arvuti,
                                                self.pallid_kasitsi,
                                                self.pallid)

    def give_alatestisooritus(self, alatest_id, alatest=None, sooritaja=None):
        r = self.get_alatestisooritus(alatest_id)
        if not r:
            r = TempAlatestisooritus(alatest_id=alatest_id)
            r.staatus = const.S_STAATUS_ALUSTAMATA
            self.alatestisooritused.append(r)
        return r

    def get_alatestisooritus(self, alatest_id):
        for r in self.alatestisooritused:
            if r.alatest_id == alatest_id:
                return r

    def getq_alatestisooritus(self, alatest_id):
        return self.get_alatestisooritus(alatest_id)
       
    def get_piiraeg(self, testiosa):
        piiraeg = testiosa.piiraeg
        if piiraeg:
            piiraeg += self.lisaaeg or 0
            ajakulu = 0
            if self.staatus in (const.S_STAATUS_POOLELI, const.S_STAATUS_KATKESTATUD):
                ajakulu = (datetime.now() - self.algus).seconds
            kasutamata = piiraeg - ajakulu
            return piiraeg, ajakulu, kasutamata
        return None, None, None
    
    @property
    def piiraeg(self):
        if self.testiosa.piiraeg:
            return self.testiosa.piiraeg + (self.lisaaeg or 0)

    @property
    def kasutamata_aeg(self):
        piiraeg, ajakulu, kasutamata = self.get_piiraeg(self.testiosa)
        return kasutamata
    
    def give_hindamisolekud(self, pooleli=False):
        for rcd in self.testiosa.hindamiskogumid:
            if rcd.staatus == const.B_STAATUS_KEHTIV:
                self.give_hindamisolek(rcd)
                
    def get_hindamisolek(self, hindamiskogum):
        for rcd in self.hindamisolekud:
            if hindamiskogum.id == rcd.hindamiskogum_id:
                return rcd

    def give_hindamisolek(self, hindamiskogum):
        rcd = self.get_hindamisolek(hindamiskogum)
        if not rcd:
            rcd = TempHindamisolek(hindamiskogum)
            self.hindamisolekud.append(rcd)
            rcd.sooritus = self
        return rcd

    def set_staatus(self, staatus, stpohjus=None):
        self.staatus = staatus
        self.stpohjus = stpohjus
        if staatus == const.S_STAATUS_TEHTUD:
            # kui testiosa on tehtud, siis peavad kõik alatestid ka tehtud olema
            # (välja arvatud testiväline alatest)
            for atos in self.alatestisooritused:
                if atos.staatus not in (const.S_STAATUS_TEHTUD, const.S_STAATUS_VABASTATUD):
                    if not atos.alatest.testivaline:
                        atos.staatus = const.S_STAATUS_TEHTUD
                        atos.lopp = self.lopp

        if self.ajakulu is not None:
            # arvutame testi koguajakulu
            sooritaja = self.sooritaja
            if sooritaja:
                ajakulud = [tos.ajakulu for tos in sooritaja.sooritused if tos.ajakulu is not None]
                sooritaja.ajakulu = len(ajakulud) and sum(ajakulud) or None
            
    def calc_vastustearvud(self):
        pass

    def calc_alatestitulemus(self, pallid, is_delf):
        return pallid

    def get_npvastused(self):
        di = {}
        for rcd in self.npvastused:
            di[rcd.normipunkt_id] = rcd
        return di

    def add_npvastus(self, normipunkt):
        r = TempNpvastus(normipunkt=normipunkt)
        self.npvastused.append(r)
        return r

class TempNpvastus(object):
    def __init__(self, normipunkt=None, yv=None):
        self.id = gen_temp_id()
        self.normipunkt_id = normipunkt.id
        self.nvaartus = self.svaartus = None
        self.nptagasiside_id = None
        self.ylesandevastus = yv
        self.viga = None
        
    @property
    def nptagasiside(self):
        if self.nptagasiside_id:
            return Nptagasiside.get(self.nptagasiside_id)
    
    @property
    def normipunkt(self):
        return Normipunkt.get(self.normipunkt_id)

    def set_value(self, value, err=None):
        if isinstance(value, (int, float)):
            self.nvaartus = value
            self.svaartus = None
        else:
            self.nvaartus = None
            self.svaartus = value
        self.viga = err
        
    def get_str_value(self):
        if self.nvaartus is not None:
            return fstr(self.nvaartus, 2)
        else:
            return self.svaartus

    def get_value(self):
        if self.nvaartus is not None:
            return self.nvaartus
        else:
            return self.svaartus

class TempAlatestisooritus(TempSooritus):
    def __init__(self, alatest_id=None):
        self.alatest_id = alatest_id
        self.algus = None
        self.staatus = None
        self.pallid = None
        self.yl_arv = None
        self.tehtud_yl_arv = None
        self.ajakulu = None
        self.lopp = None
        self.seansi_algus = None
        # koolipsyh testi tagasiside jaoks
        self.oigete_arv = 0
        self.valede_arv = 0
        self.valimata_valede_arv = 0
        self.valimata_oigete_arv = 0
        self.oigete_suhe = 1
        
    @property
    def piiraeg(self):
        alatest = Alatest.get(self.alatest_id)
        return alatest.piiraeg

    @property
    def kasutamata_aeg(self):
        piiraeg, ajakulu, kasutamata = self.get_piiraeg(self.alatest)
        return kasutamata

    def set_yl_arv(self, komplekt_id):
        self.tehtud_yl_arv = self.yl_arv = None

    @property
    def alatest(self):
        return Alatest.get(self.alatest_id)
       
    def get_piiraeg(self, alatest):
        piiraeg = alatest.piiraeg
        if piiraeg:
            ajakulu = 0
            kasutamata = piiraeg
            return piiraeg, ajakulu, kasutamata
        return None, None, None

class TempHindamisolek(object):

    def __init__(self, hindamiskogum):
        self.hindamiskogum_id = hindamiskogum.id
        self.hindamised = list()
        self.id = -1
        self.puudus = False
        self.mittekasitsi = False
        self.hindamisprobleem = None
        self.komplekt_id = None
        self.hindamistase = const.HTASE_ARVUTI
        
    @property
    def hindamiskogum(self):
        return Hindamiskogum.get(self.hindamiskogum_id)

    @property
    def komplekt(self):
        if self.komplekt_id:
            return Komplekt.get(self.komplekt_id)

    @komplekt.setter
    def komplekt(self, value):
        self.komplekt_id = value and value.id or None

