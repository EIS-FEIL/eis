"Testikorralduse andmemudel"

from eis.model.entityhelper import *
from .kysimusevastus import Kysimusevastus
from .loendur import Loendur

_ = usersession._

class Ylesandevastus(EntityHelper, Base):
    """Sooritaja poolt ühele ülesandele antud vastus
    """
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sooritus_id = Column(Integer, index=True, nullable=True) # viide sooritusele (puudub ülesande eelvaates lahendamisel)
    valitudylesanne_id = Column(Integer, index=True) # viide testi valitud ülesandele
    testiylesanne_id = Column(Integer, index=True, nullable=True) # viide testiülesandele (puudub ülesande eelvaates lahendamisel)
    tahis = Column(String(10)) # testiülesande tähis 
    alatest_id = Column(Integer) # viide alatestile

    loplik = Column(Boolean) # true - viimati valitud komplekti kuuluva ülesande vastus; null - mõne varem proovitud komplekti ülesande vastus
    algus = Column(DateTime, index=True) # ülesande esimese lugemise aeg
    viimane_algus = Column(DateTime) # ülesande viimase lugemise aeg
    lopp = Column(DateTime) # viimane vastuste salvestamise aeg
    ajakulu = Column(Integer) # vastamiseks kulutatud sekundite arv
    staatus = Column(Integer) # vastuse olek (1 - on arvutatud, 0 - vajab üle arvutamist)
    toorpunktid = Column(Float) # toorpunktid (ülesande skaala järgi)
    toorpunktid_arvuti = Column(Float) # arvutihinnatav osa toorpunktidest
    toorpunktid_kasitsi = Column(Float) # käsitsihinnatav osa toorpunktidest    
    pallid = Column(Float) # hindepallid (testiülesande skaala järgi)
    pallid_arvuti = Column(Float) # arvutihinnatav osa hindepallidest
    pallid_kasitsi = Column(Float) # käsitsihinnatav osa hindepallidest
    toorpunktid_enne_vaiet = Column(Float) # toorpunktid enne vaidlustamist
    pallid_enne_vaiet = Column(Float) # hindepallid enne vaidlustamist
    yhisosa_pallid = Column(Float) # seotud testimiskordade ühisossa kuulunud küsimuste hindepallide summa
    max_pallid = Column(Float) # max hindepallid vastavalt soorituse komplektile
    arvutuskaik = Column(Text) # arvutihindamise arvutuskäik HTMLina
    muudetav = Column(Boolean, sa.DefaultClause('true'), nullable=False) # kas lahendaja saaks vastust veel muuta juhul, kui sooritus oleks pooleli (testi sooritamisel alati true, jagatud töös false peale ülesande vastuse kinnitamist)
    kehtiv = Column(Boolean, sa.DefaultClause('true')) # kas on ülesande kõigi vastuste seast viimane vaadatav vastus (testi sooritamisel alati true, jagatud töös: false - kui vastust pole veel kinnitatud ja muudetav=true; true - kui vastus on kinnitatud ja ei ole kinnitatud mõnd järgmist vastust; NULL - kui on kinnitatud juba mõni järgmine vastus)
    skann = Column(LargeBinary) # skannitud vastus JPG-pildina
    laius_orig = Column(Integer) # skannitud pildi tegelik laius
    korgus_orig = Column(Integer) # skannitud pildi tegelik kõrgus
    oigete_arv = Column(Integer) # õigete vastuste arv (koolipsühholoogitesti jaoks)
    valede_arv = Column(Integer) # valede vastuste arv (koolipsühholoogitesti jaoks)
    valimata_valede_arv = Column(Integer) # valimata valede vastuste arv, sisaldub õigete arvus (koolipsühholoogitesti jaoks)
    valimata_oigete_arv = Column(Integer) # valimata valede vastuste arv, sisaldub valede arvus (koolipsühholoogitesti jaoks)    
    oigete_suhe = Column(Float) # õigete vastuste suhe kõikidesse vastustesse (koolipsühholoogitesti jaoks)
    #vastamata_arv = Column(Integer) # vastuste arv, mis pole õiged ega valed (on vastamata või loetamatu)
    vastuseta = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas vastuseid pole (on ainult tühjad vastused)
    lopetatud = Column(Boolean) # kas kõik kohustuslikud küsimused on vastatud
    mittekasitsi = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas on arvutihinnatav: true - käsitsi pole midagi hinnata (arvutihinnatavad küsimused või hübriidhinnatud või käsitsihinnatavad küsimused vastamata); false - kuulub käsitsi hindamisele; väli on mõeldud arvestamiseks ainult e-hinnatavate testide korral, sest p-hindamise korral ei peagi vastused andmebaasis olema
    on_toorvastus = Column(Boolean) # kas vastused on veel toorvastuse tabelist ümber paigutamata
    kysimusevastused = relationship('Kysimusevastus', back_populates='ylesandevastus') # antud vastused
    ylesandehinded = relationship('Ylesandehinne', back_populates='ylesandevastus') # hindajate pandud hinded 
    vastusaspektid = relationship('Vastusaspekt', back_populates='ylesandevastus') # lõplikud aspektide hinded   
    sisuvaatamised = relationship('Sisuvaatamine', order_by=sa.desc(sa.text('Sisuvaatamine.algus')), back_populates='ylesandevastus')
    loendurid = relationship('Loendur', back_populates='ylesandevastus') # tabamuste loendurite väärtused
    npvastused = relationship('Npvastus', back_populates='ylesandevastus') # saadud tagasiside, tagasisidega ülesande korral
    valikujrk = Column(ARRAY(Integer)) # sisuplokkide ID-de järjekord antud soorituses (kui ylesanne.segamini=true)
    _parent_key = 'sooritus_id'     
    __table_args__ = (
        sa.UniqueConstraint('sooritus_id','testiylesanne_id','valitudylesanne_id','muudetav', 'kehtiv', deferrable=True, initially='deferred'),
        )

    @property
    def sooritus(self):
        from eis.model.testimine import Sooritus
        return Sooritus.get(self.sooritus_id)
    
    @property
    def valitudylesanne(self):
        from eis.model.test import Valitudylesanne
        return Valitudylesanne.get(self.valitudylesanne_id)

    @property
    def testiylesanne(self):
        from eis.model.test import Testiylesanne
        return Testiylesanne.get(self.testiylesanne_id)
    
    def get_vastusaspekt(self, aspekt_id):
        for rcd in self.vastusaspektid:
            if rcd.hindamisaspekt_id == aspekt_id:
                return rcd

    def give_vastusaspekt(self, aspekt_id):
        from eis.model.testimine import Vastusaspekt
        rcd = self.get_vastusaspekt(aspekt_id)
        if rcd is None:
            rcd = Vastusaspekt(ylesandevastus=self, hindamisaspekt_id=aspekt_id)
        return rcd

    def delete_subitems(self):    
        self.delete_subrecords(['kysimusevastused',
                                'vastusaspektid',
                                'loendurid',
                                'sisuvaatamised',
                                ])
        for nv in self.npvastused:
            if not nv.sooritus_id:
                nv.delete()

    def get_kysimusevastus(self, kysimus_id, sisestus=1):
        if kysimus_id and self.id:
            # otsime kiiresti
            kv = Kysimusevastus.query.\
                 filter(Kysimusevastus.ylesandevastus_id==self.id).\
                 filter(Kysimusevastus.kysimus_id==kysimus_id).\
                 filter(Kysimusevastus.sisestus==sisestus).\
                 first()
            if kv:
                return kv
            
        for kv in self.kysimusevastused:
            if kv.kysimus_id == kysimus_id and kv.sisestus == sisestus:
                return kv

    def give_kysimusevastus(self, kysimus_id, sisestus=1):
        # sisestus=1 on sisestatavate vastuste korral esimene sisestus,
        # e-testi korral sooritamine ise
        kv = self.get_kysimusevastus(kysimus_id, sisestus)
        if not kv:
            kv = Kysimusevastus(ylesandevastus=self, 
                                kysimus_id=kysimus_id,
                                sisestus=sisestus)
            self.kysimusevastused.append(kv)
        return kv

    def get_ylesandehinne(self):
        if len(self.ylesandehinded):
            return self.ylesandehinded[0]

    def calc_max_pallid(self, ty_id, vy_id):
        from eis.model.test import Testiylesanne, Valitudylesanne
        ty = Testiylesanne.get(ty_id)
        ty_max_pallid = ty.max_pallid
        if ty_max_pallid is None:
            if not vy_id:
                vy_id = self.valitudylesanne_id
            vy = vy_id and Valitudylesanne.get(vy_id)
            if vy:
                ylesanne = vy.ylesanne
                if ylesanne:
                    ty_max_pallid = ylesanne.max_pallid
        if self.max_pallid != ty_max_pallid and ty_max_pallid is not None:
            self.max_pallid = ty_max_pallid

    def get_responses(self, sisestus=1):
        responses = {}
        for kv in self.kysimusevastused:
            if kv.sisestus == sisestus:
                kood = kv.kood or kv.kysimus.kood
                responses[kood] = kv
        return responses

    def get_tagasiside(self, handler, ylesanne, lang):
        "Leitakse ülesande tagasiside"
        import eis.lib.npcalc
        npc = eis.lib.npcalc.Npcalc(handler, None, None, None, None)
        msg, jatka = npc.calc_ylesanne_tagasiside(self, ylesanne, lang)
        return msg

    def get_protsent(self):
        try:
            pallid = self.pallid
            max_pallid = self.max_pallid
        except AttributeError:
            return
        if pallid is not None and max_pallid:
            return pallid * 100 / self.max_pallid
        
    def get_tulemus(self, digits=3):
        if self.pallid is not None:
            pallid = self.pallid
            max_pallid = self.max_pallid
            if not max_pallid:
                return fstr(pallid)
            return _("{p1}p {p2}-st, {p3}%").format(p1=fstr(pallid, digits), 
                                                    p2=fstr(max_pallid, digits),
                                                    p3=fstr(pallid*100/max_pallid, digits))
 
    def get_tulemus_eraldi(self):
        vy = self.valitudylesanne
        #if vy and vy.ylesanne.arvutihinnatav:
        if self.mittekasitsi:
            # yleni arvutihinnatav ylesanne
            return self.get_tulemus()
        elif self.pallid_arvuti is not None:
            # osaliselt arvutihinnatav ylesanne
            return self.get_tulemus_eraldi_(self.max_pallid,
                                            self.pallid_arvuti,
                                            self.pallid_kasitsi,
                                            self.pallid)
        else:
            return _("max {p}p").format(p=fstr(self.max_pallid))

    def get_tulemus_eraldi2(self):
        "Tulemuse kuvamine peale avaliku ylesande või tööylesande lahendamist"
        vy = self.valitudylesanne
        total = self.toorpunktid
        if self.mittekasitsi and total is not None:
            # yleni arvutihinnatav ylesanne
            msg = _("Tulemus: {p1} punkti {p2}-st võimalikust").format(p1=fstr(total), p2=fstr(self.max_pallid))
            return msg
        elif self.pallid_arvuti is not None:
            # osaliselt arvutihinnatav ylesanne
            return self.get_tulemus_eraldi_(self.max_pallid,
                                            self.pallid_arvuti,
                                            self.pallid_kasitsi,
                                            self.pallid)
        else:
            msg = _("Ülesanne ei ole arvutihinnatav")
            return msg
        
    @classmethod
    def get_tulemus_eraldi_(cls, max_pallid, pallid_arvuti, pallid_kasitsi, pallid):
        buf = _("Esialgsed arvutihinnatavad punktid: {p}").format(p=fstr(pallid_arvuti) or '-')
        buf += '<br/>' + _("Subjektiivhinnatavad punktid: {p}").format(p=fstr(pallid_kasitsi) or '?')
        buf += '<br/>' + _("Tulemus kokku: {p}").format(p=fstr(pallid) or '?')
        return buf        
