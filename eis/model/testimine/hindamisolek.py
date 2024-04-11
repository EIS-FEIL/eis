"Testikorralduse andmemudel"
from eis.model.entityhelper import *
from .hindamine import Hindamine
_ = usersession._

class Hindamisolek(EntityHelper, Base):
    """Soorituse hindamise kehtiv olek hindamiskogumite lõikes.
    Iga soorituse ja hindamiskogumi kohta on üks kirje.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sooritus_id = Column(Integer, ForeignKey('sooritus.id'), index=True, nullable=False) # viide hinnatavale sooritusele
    sooritus = relationship('Sooritus', foreign_keys=sooritus_id, back_populates='hindamisolekud')
    staatus = Column(Integer, sa.DefaultClause('0'), nullable=False) # sisestamise olek: 0=const.H_STAATUS_HINDAMATA - alustamata; 1=const.H_STAATUS_POOLELI - hindamisel; 2=const.H_STAATUS_LYKATUD - loobutud; 3=const.H_STAATUS_HINNATUD - hinnatud
    hindamiskogum_id = Column(Integer, ForeignKey('hindamiskogum.id'), index=True) # viide hindamiskogumile (puudub testimiskorrata testi hindamisel)
    hindamiskogum = relationship('Hindamiskogum', foreign_keys=hindamiskogum_id) 
    hindamistase = Column(Integer, sa.DefaultClause('0'), nullable=False) # kõrgeim vajalik hindamine: 0 - ei vaja hindamist (hindamiskogum on täielikult arvutihinnatav); 1=const.HINDAJA1 - ühekordne hindamine; 2=const.HINDAJA2 - kahekordne hindamine; 3=const.HINDAJA3 - kolmas hindamine; 4=const.HINDAJA4 - eksperthindamine erinevuste korral (IV hindamine); 5=const.HINDAJA5 - eksperthindamine vaide korral; 6=const.HINDAJA6 - eksperthindamine kohtu poolt
    hindamisprobleem = Column(Integer, sa.DefaultClause('0'), nullable=False) # antud hindamistaseme hindamisprobleem: 0=const.H_PROBLEEM_POLE - pole; 1=const.H_PROBLEEM_SISESTAMATA - sisestamata; 2=const.H_PROBLEEM_SISESTUSERINEVUS - sisestusvead; 3=const.H_PROBLEEM_HINDAMISERINEVUS - hindamiserinevus; 4=const.H_PROBLEEM_TOOPUUDU - töö puudu või jääb hindamata; 5=const.H_PROBLEEM_VAIE - vaidehindamine tehtud, kuid vaideotsuse eelnõud veel pole ja vaidehindamist ei arvestata
    selgitus = Column(String(100)) # hindamisprobleemi vabatekstiline selgitus
    puudus = Column(Boolean, sa.DefaultClause('0'), nullable=False) # true - ühtki hindamisoleku ülesannet pole sooritatud; false - on midagi hinnata
    mittekasitsi = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas kõik on arvutiga hinnatav (käsitsihinnatavate küsimuste vastuseid pole)
    min_hindamistase = Column(Integer, sa.DefaultClause('0'), nullable=False) # hindamistase, millest madalamaks ei saa tagasi minna (ilma hindamiserinevuseta kolmandat hindamist vajavate tööde määramisel antakse väärtus 3)
    pallid = Column(Float) # soorituse lõplikud pallid antud hindamiskogumi eest 
    toorpunktid = Column(Float) # soorituse toorpunktide summa antud hindamiskogumi eest
    hindamiserinevus = Column(Float) # hindamiserinevus (pallide vahe) juhul, kui on vaja olnud kolmandat hindamist
    komplekt_id = Column(Integer, ForeignKey('komplekt.id'), index=True) # viide komplektile
    komplekt = relationship('Komplekt', foreign_keys=komplekt_id)
    hindamised = relationship('Hindamine', order_by='Hindamine.liik,Hindamine.staatus', back_populates='hindamisolek')
    __table_args__ = (
        sa.UniqueConstraint('sooritus_id','hindamiskogum_id'),
        )
    _parent_key = 'sooritus_id'

    def komplekt_on_hindamiskogumis(self):
        """Kas sooritatud komplekti mõni ylesanne kuulub sellesse hindamiskogumisse?
        Lõdva struktuuri korral ei pruugi kõik hindamiskogumid sooritamiseks olla
        """
        komplekt = self.komplekt
        hkogum = self.hindamiskogum
        if komplekt and hkogum:
            li = komplekt.get_testiylesanded_id(hkogum)
            return len(li) > 0
    
    @property
    def staatus_nimi(self):
        return usersession.get_opt().H_STAATUS.get(self.staatus)

    @property
    def hindamisprobleem_nimi(self):
        return usersession.get_opt().H_PROBLEEM.get(self.hindamisprobleem)

    def get_hindamine(self, liik, sisestus=1, hindaja_kasutaja_id=None, minusisestatud=False):
        """Kui on minusisestatud, siis leitakse selle kasutaja
        hindamise kirje antud liigi ja sisestuse järgi.
        Kui pole minusisestatud, siis leitakse mõni tühistamata
        kirje antud liigi ja sisestuse järgi.
        """
        for rcd in self.hindamised:
            if rcd.liik == liik:
                if sisestus == rcd.sisestus:
                    if minusisestatud and rcd.sisestaja_kasutaja_id == usersession.get_user().id or \
                            not minusisestatud and not rcd.tyhistatud:
                        if not hindaja_kasutaja_id or \
                                hindaja_kasutaja_id == rcd.hindaja_kasutaja_id:
                            # ignoreeritakse tagasi lükatud ja edasi suunatud hindamisi
                            return rcd

    def give_hindamine(self, liik, sisestus=1, hindaja_kasutaja_id=None, labivaatus5=True, labiviija_id=None, eityhista=False, unikaalne=True):
        from .hindamisprotokoll import Hindamisprotokoll
        if isinstance(liik, Hindamisprotokoll):
            hpr = liik
            liik = hpr.liik
        else:
            hpr = None

        rcd = None
        for r in list(self.hindamised):
            if r.liik == liik and sisestus == r.sisestus:
                if labiviija_id and r.labiviija_id == labiviija_id:
                    # sama hindaja
                    r.uus_hindamine = None
                    rcd = r
                elif hindaja_kasutaja_id and r.hindaja_kasutaja_id == hindaja_kasutaja_id:
                    # sama hindaja
                    r.uus_hindamine = None
                    rcd = r
                elif r.tyhistatud:
                    continue
                elif r.hindaja_kasutaja_id and hindaja_kasutaja_id and \
                        hindaja_kasutaja_id != r.hindaja_kasutaja_id and \
                        not r.tyhistatud:
                    if not r.unikaalne:
                        # avaliku vaate hindamiskogumita hindamine, võib olla mitu hindajat, iga hindab oma ylesannet
                        continue
                    if eityhista:
                        return
                    # ignoreeritakse tagasi lükatud ja edasi suunatud hindamisi
                    if r.created > datetime.now() - timedelta(seconds=2):
                        # äsja on see töö teisele hindajale antud?
                        raise Exception('Antud juba teisele hindajale (hindamisolek %d, olemasolev kirje %d)' % (self.id, r.id))
                    r.tyhistatud = True
                    r.flush()
                else:
                    rcd = r

        if rcd and rcd.tyhistatud:
            # juhul, kui hindaja on varem olnud selle töö hindaja, aga tyhistatud
            r.tyhistatud = False
            r.flush()

        if not rcd:
            rcd = Hindamine(liik=liik, 
                            hindamisolek=self,
                            staatus=const.H_STAATUS_MAARATUD,
                            sisestus=sisestus,
                            unikaalne=unikaalne)
            if hindaja_kasutaja_id:
                rcd.hindaja_kasutaja_id = hindaja_kasutaja_id
            if labiviija_id:
                rcd.labiviija_id = labiviija_id
            if liik == const.HINDAJA5 and labivaatus5:
                # lisame seosed nende ekspertidega, kes on parajasti aktiivsed ekspertrühma liikmed
                q = SessionR.query(Labiviija.id).\
                    filter(Labiviija.kasutajagrupp_id==const.GRUPP_HINDAMISEKSPERT).\
                    filter(Labiviija.toimumisaeg_id==self.sooritus.toimumisaeg_id).\
                    filter(Labiviija.aktiivne==True)
                for lv_id, in q.all():
                    rcd.give_labivaatus(lv_id)
            
            self.hindamised.append(rcd)
        if hpr and rcd.hindamisprotokoll != hpr:
            rcd.hindamisprotokoll = hpr
        if self.staatus == const.H_STAATUS_HINDAMATA:
            self.staatus = const.H_STAATUS_POOLELI
        return rcd

    def give_hindamine3(self, hindaja_kasutaja_id, hindaja_id, sisestamisega=None):
        "Luuakse kolmanda hindamise kirjed"

        # p-testi korral on vaja hindamisprotokolli
        if self.hindamiskogum.sisestuskogum_id:
            tpr = self.sooritus.testiprotokoll
            hpr = tpr.give_hindamisprotokoll(const.HINDAJA3, 
                                             self.hindamiskogum.sisestuskogum_id)
            hpr.tehtud_toodearv = 1 # on vaja 0-st suuremat arvu, muidu protokolli sisestamise vormil ei kuvata
        else:
            hpr = None

        self.hindamistase = const.HINDAJA3
        self.hindamisprobleem = const.H_PROBLEEM_SISESTAMATA

        self.selgitus = _("III hindamine tegemata")
        hindamine = self.give_hindamine(const.HINDAJA3)
        if hindaja_kasutaja_id:
            hindamine.hindaja_kasutaja_id = hindaja_kasutaja_id
            hindamine.labiviija_id = hindaja_id

        hindamine.hindamisprotokoll = hpr
        hindamine.flush()

        hindamine2 = None
        # p-testi korral on kahekordne sisestamine ja on vaja teise sisestuse kirje ka luua
        if sisestamisega is None:
            vastvorm = self.hindamiskogum.testiosa.vastvorm_kood
            sisestamisega = vastvorm in (const.VASTVORM_KP, const.VASTVORM_SP)
        if sisestamisega:
            hindamine2 = self.give_hindamine(const.HINDAJA3, sisestus=2)
            if hindaja_kasutaja_id:
                hindamine2.hindaja_kasutaja_id = hindaja_kasutaja_id
                hindamine2.labiviija_id = hindaja_id
            hindamine2.hindamisprotokoll = hpr
            hindamine2.flush()                

        return hindamine, hindamine2

    def delete_subitems(self):    
        self.delete_subrecords(['hindamised',
                                ])
