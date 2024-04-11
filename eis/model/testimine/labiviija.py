"Testikorralduse andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import Klrida
from eis.model.kasutaja import *
from eis.model.test import *
from .hindamine import Hindamine
from .labiviijaklass import Labiviijaklass
from .toimumisaeg import Toimumisaeg

class Labiviija(EntityHelper, Base):
    """Testi läbiviijad.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tahis = Column(Integer) # hindaja tähis, kopeerib välja Ainelabiviija.tahis
    staatus = Column(Integer, sa.DefaultClause('1'), nullable=False) # olek, 0=const.L_STAATUS_KEHTETU - kehtetu; 1=const.L_STAATUS_MAARATUD - määramata või määratud; 3=const.L_STAATUS_OSALENUD - osalenud; 4=const.L_STAATUS_PUUDUNUD - puudunud
    toimumisaeg_id = Column(Integer, ForeignKey('toimumisaeg.id'), index=True)
    toimumisaeg = relationship('Toimumisaeg', foreign_keys=toimumisaeg_id, back_populates='labiviijad')
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide läbiviija kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='labiviijad')
    kasutajagrupp_id = Column(Integer, ForeignKey('kasutajagrupp.id'), index=True, nullable=False) # kasutajagrupp, mis näitab läbiviija õigused
    kasutajagrupp = relationship('Kasutajagrupp', foreign_keys=kasutajagrupp_id)

    # Hindaja väljad
    liik = Column(Integer) # hindaja liik: 1=const.HINDAJA1 - hindaja I; 2=const.HINDAJA2 - hindaja II; 3=const.HINDAJA3 - hindaja III
    lang = Column(String(2)) # hindamise keel
    hindamiskogum_id = Column(Integer, ForeignKey('hindamiskogum.id'), index=True) # viide hinnatavale hindamiskogumile, hindaja korral kohustuslik
    hindamiskogum = relationship('Hindamiskogum', foreign_keys=hindamiskogum_id)
    hindaja1_id = Column(Integer, ForeignKey('labiviija.id'), index=True) # paaris hindamise korral viide I hindaja kirjele; hindaja-intervjueerija korral viide intervjueerija kirjele
    hindaja1 = relationship('Labiviija', foreign_keys=hindaja1_id, remote_side=id, back_populates='paarishindajad')
    paarishindajad = relationship('Labiviija', back_populates='hindaja1') # hindajad, kes kuuluvad antud kirjega samasse paari
    on_paaris = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas on paarishindaja
    planeeritud_toode_arv = Column(Integer) # hindajale planeeritud hinnatavate tööde arv
    toode_arv = Column(Integer) # määratud või ette võetud tööde arv (hinnatud tööd ja pooleli tööd)
    hinnatud_toode_arv = Column(Integer) # hinnatud (hindamine kinnitatud) tööde arv (hindaja korral); intervjueeritud tööde arv, kus intervjueerija oli ise hindaja (hindaja-intervjueerija korral); intervjueeritud tööde arv, kus intervjueerija polnud hindaja (intervjueerija korral)
    tasu_toode_arv = Column(Integer) # tasustatud tööde arv - hinnatud tööde arv ilma oma kooli õpilasteta (hindaja korral); intervjueeritud tööde arv, kus intervjueerija oli ise hindaja (hindaja-intervjueerija korral); intervjueeritud tööde arv, kus intervjueerija polnud hindaja (intervjueerija korral)    

    # Üldised läbiviija väljad
    tasustatav = Column(Boolean, sa.DefaultClause('1'), nullable=False) # kas töötasu arvestatakse (kui läbiviija osaleb samal kuupäeval mitmes testis ja kõigi eest ei soovita talle maksta, siis märgitakse siia, et pole tasustatav)
    tasu = Column(Float) # läbiviija töötasu
    meeldetuletusaeg = Column(DateTime) # meeldetuletuse aeg
    teateaeg = Column(DateTime) # teate aeg
    yleaja = Column(Boolean) # kas tööaeg läks üle aja
    toolopp = Column(DateTime) # töö lõpetamise kellaaeg (kui läks üle aja)
    testikoht_id = Column(Integer, ForeignKey('testikoht.id'), index=True) # viide testikohale (kohustuslik kõigile peale kirjaliku hindaja)
    testikoht = relationship('Testikoht', foreign_keys=testikoht_id, back_populates='labiviijad')
    testiruum_id = Column(Integer, ForeignKey('testiruum.id'), index=True) # viide testiruumile (kohustuslik kõigile peale kirjaliku hindaja)
    testiruum = relationship('Testiruum', foreign_keys=testiruum_id, back_populates='labiviijad')
    hindamised = relationship('Hindamine', foreign_keys='Hindamine.labiviija_id', back_populates='labiviija')
    labiviijakirjad = relationship('Labiviijakiri', order_by='Labiviijakiri.id', back_populates='labiviija')
    aktiivne = Column(Boolean, sa.DefaultClause('1'), nullable=False) # kas läbiviija on parajasti aktiivne (ekspertrühma liige ei pruugi kogu aeg aktiivne olla)
    valimis = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas on valimi hindaja
    muu_koha_hindamine = Column(Boolean) # soorituskohas määratud hindaja korral: false - hindab oma soorituskoha töid; true - hindab teiste soorituskohtade töid
    kysimusehindemarkused = relationship('Kysimusehindemarkus', back_populates='ekspert_labiviija') # vaidehindaja korral
    aspektihindemarkused = relationship('Aspektihindemarkus', back_populates='ekspert_labiviija') # vaidehindaja korral
    ylesandehindemarkused = relationship('Ylesandehindemarkus', back_populates='ekspert_labiviija') # vaidehindaja korral
    labivaatused = relationship('Labivaatus', back_populates='ekspert_labiviija') # vaidehindaja korral
    labiviijaklassid = relationship('Labiviijaklass', back_populates='labiviija') # kooli poolt määratud hindaja korral
    labiviijaylesanded = relationship('Labiviijaylesanne', back_populates='labiviija') # testimiskorrata testile määratud hindaja korral loetelu ylesannetest, mida hindab
    
    __table_args__ = (
        sa.UniqueConstraint('toimumisaeg_id', 'kasutaja_id', 'kasutajagrupp_id', 'liik', 'lang', 'testiruum_id', 'testikoht_id', 'hindamiskogum_id', 'valimis'),
        )
    _parent_key = 'testikoht_id'

    def get_tasu(self):
        tasu = None
        if self.kasutajagrupp_id == const.GRUPP_INTERVJUU:
            if self.staatus == const.L_STAATUS_OSALENUD and self.tasu_toode_arv:
                # sooritajate arv saadakse hindamisprotokollilt ja mitte toimumise protokollilt,
                # kuna need sooritajad, kes on kõrvaldatud eksami ajal, tuleb välja jätta,
                # aga need sooritajad, kes on kõrvaldatud peale hindamist, tuleb sisse jätta,
                # aga toimumise protokollilt ei saa aru, millal on kõrvaldatud

                # leiame tasu nende soorituste eest, kus intervjueerija ei olnud hindaja
                if self.hindamiskogum:
                    tasu = self.hindamiskogum.intervjuu_tasu or 0
                else:
                    tasu = sum([hk.intervjuu_tasu or 0 for hk in self.toimumisaeg.testiosa.hindamiskogumid if hk.staatus])
                tasu *= self.tasu_toode_arv

        elif self.kasutajagrupp_id == const.GRUPP_HIND_INT:
            if self.hindaja1.staatus == const.L_STAATUS_OSALENUD and self.tasu_toode_arv:
                # leiame tasu nende soorituste eest, kus intervjueerija oli ise hindaja
                if self.hindamiskogum:
                    tasu = self.hindamiskogum.intervjuu_lisatasu or 0
                else:
                    tasu = sum([hk.intervjuu_lisatasu or 0 for hk in self.toimumisaeg.testiosa.hindamiskogumid if hk.staatus])
                tasu *= self.tasu_toode_arv
            
        elif self.kasutajagrupp_id == const.GRUPP_VAATLEJA:
            if self.staatus == const.L_STAATUS_OSALENUD:
                tasu = self.toimumisaeg.vaatleja_tasu or 0
                if self.yleaja:
                    tasu += self.toimumisaeg.vaatleja_lisatasu or 0

        elif self.kasutajagrupp_id == const.GRUPP_KOMISJON:
            if self.staatus == const.L_STAATUS_OSALENUD:
                tasu = self.toimumisaeg.komisjoniliige_tasu or 0
                if self.yleaja:
                    tasu += self.toimumisaeg.vaatleja_lisatasu or 0
                    
        elif self.kasutajagrupp_id == const.GRUPP_KOMISJON_ESIMEES:
            if self.staatus == const.L_STAATUS_OSALENUD:
                tasu = self.toimumisaeg.esimees_tasu or 0
                if self.yleaja:
                    tasu += self.toimumisaeg.vaatleja_lisatasu or 0

        elif self.kasutajagrupp_id == const.GRUPP_T_ADMIN:
            if self.staatus == const.L_STAATUS_OSALENUD:
                tasu = self.toimumisaeg.admin_tasu or 0
                # administraator ei saa lisatasu - vt EH-211
                    
        elif self.kasutajagrupp_id == const.GRUPP_KONSULTANT:
            #if self.staatus == const.L_STAATUS_OSALENUD:
                tasu = self.toimumisaeg.konsultant_tasu or 0                  
        
        elif self.liik:
            # on hindaja või hindamisekspert(vaidehindaja)
            if self.tasu_toode_arv is not None:
                if self.hindamiskogum:
                    # kirjalik hindaja
                    tasu = self.tasu_toode_arv * (self.hindamiskogum.tasu or 0)
                else:
                    # suuline hindaja või vaidehindaja, arvestame kõiki hindamiskogumeid
                    too_tasu = sum([hk.tasu or 0 for hk in self.toimumisaeg.testiosa.hindamiskogumid if hk.staatus])
                    tasu = self.tasu_toode_arv * (too_tasu or 0)
        return tasu

    @property 
    def staatus_nimi(self):
        return usersession.get_opt().L_STAATUS.get(self.staatus)
        #return Klrida.get_str('L_STAATUS', str(self.staatus))

    @property
    def liik_nimi(self):
        return usersession.get_opt().HINDAJA.get(self.liik)

    @property
    def lang_nimi(self):
        if self.lang:
            return Klrida.get_lang_nimi(self.lang)

    @property
    def kasutajagrupp_nimi(self):
        if self.kasutajagrupp_id == const.GRUPP_HINDAMISEKSPERT:
            return 'Vaidehindaja'
        else:
            return self.kasutajagrupp.nimi

    def set_klassid(self, klassid):
        for r in list(self.labiviijaklassid):
            try:
                n = klassid.index((r.klass, r.paralleel))
                klassid.pop(n)
            except ValueError:
                r.delete()

        for klass, paralleel in klassid:
            item = Labiviijaklass(klass=klass,
                                  paralleel=paralleel)
            self.labiviijaklassid.append(item)

    def remove_labiviija(self):
        """
        Läbiviija eemaldamine
        Kui on komisjoni esimees või kui pole kohustuslik, siis kustutatakse kirje.
        Kui antud läbiviija kirje on ainuke samast rollist samas ruumis,
        siis eemaldatakse sellest kasutaja.
        Kui samas rollis on veel kirjeid, siis kustutatakse kirje ära.
        """
        toimumisaeg = self.toimumisaeg
        grupp_id = self.kasutajagrupp_id

        # kui läbiviijal on juba töid, siis ei saa eemaldada
        if self.id and self.kasutaja_id:
            q = Session.query(sa.func.count(Hindamine.id))
            if q.filter(Hindamine.labiviija_id==self.id).scalar() > 0:
                log.debug('lv ei saa eemaldada, ta on hindamistes läbiviija')
                return False
            if q.filter(Hindamine.intervjuu_labiviija_id==self.id).scalar() > 0:
                log.debug('lv ei saa eemaldada, ta on hindamistes intervjuu läbiviija')
                return False
            if q.filter(Hindamine.kontroll_labiviija_id==self.id).scalar() > 0:
                log.debug('lv ei saa eemaldada, ta on hindamistes kontrollija')
                return False

        if grupp_id == const.GRUPP_KOMISJON or \
           grupp_id == const.GRUPP_KOMISJON_ESIMEES and not toimumisaeg.esimees_maaraja or \
           grupp_id == const.GRUPP_VAATLEJA and not toimumisaeg.vaatleja_maaraja or \
           grupp_id == const.GRUPP_HINDAJA_S and not self.valimis and not toimumisaeg.hindaja1_maaraja or \
           grupp_id == const.GRUPP_HINDAJA_S and self.valimis and not toimumisaeg.hindaja1_maaraja_valim or \
           grupp_id == const.GRUPP_HINDAJA_S2 and not self.valimis and not toimumisaeg.hindaja2_maaraja or \
           grupp_id == const.GRUPP_HINDAJA_S2 and self.valimis and not toimumisaeg.hindaja2_maaraja_valim or \
           grupp_id == const.GRUPP_INTERVJUU and not toimumisaeg.intervjueerija_maaraja or \
           grupp_id == const.GRUPP_T_ADMIN and not toimumisaeg.admin_maaraja:
            # kui pole kohustuslik, siis võib kohe kustutada
            self.delete()
            return True

        if grupp_id == const.GRUPP_INTERVJUU:
            lv2 = self.get_hind_int()
            if lv2:
                lv2.delete()
                
        q = (Labiviija.query
             .filter_by(kasutajagrupp_id=grupp_id)
             .filter(Labiviija.id != self.id)
             .filter_by(testiruum_id=self.testiruum_id)
             .filter_by(testikoht_id=self.testikoht_id))
        if q.count() > 0:
            # selle rolli kirjeid on veel
            self.delete()
            return True
        else:
            # see on ainuke selle rolli kirje, jätame tühja kirje alles
            self.kasutaja_id = None
            self.tahis = None
            self.staatus = const.L_STAATUS_MAARAMATA
            return False

    def delete_subitems(self):
        self.delete_subrecords(['labiviijaklassid',
                                'labiviijaylesanded',
                                'labiviijakirjad',
                                ])

    def get_kiirvalik_q(self):
        """Eelistatud läbiviijate päringu koostamine
        (ainult nendest, kes on antud soorituskohaga seotud)
        """
        return self.testikoht.get_kiirvalik_q(self.kasutajagrupp_id)

    def get_valik_q(self, on_piirkond=True):
        """Võimalike läbiviijate päringu koostamine
        """
        return self.testikoht.get_valik_q(self.kasutajagrupp_id)

    def get_labiviijad_opt(self):
        """Võimalike läbiviijate loetelu
        """
        return self.testikoht.get_labiviijad_opt(self.kasutajagrupp_id)

    def set_kasutaja(self, kasutaja, toimumisaeg=None):
        if isinstance(kasutaja, int):
            self.kasutaja_id = kasutaja
            kasutaja = Kasutaja.get(kasutaja)
        else:
            self.kasutaja = kasutaja

        if not kasutaja:
            self.tahis = None
            self.staatus = const.L_STAATUS_MAARAMATA
        else:
            if not toimumisaeg:
                toimumisaeg = self.toimumisaeg or Toimumisaeg.get(self.toimumisaeg_id)
            aine_kood = toimumisaeg.testiosa.test.aine_kood
            self.staatus = const.L_STAATUS_MAARATUD
            if self.kasutajagrupp_id in (const.GRUPP_HINDAJA_S,
                                         const.GRUPP_HINDAJA_S2,
                                         const.GRUPP_HINDAJA_K,
                                         const.HINDAJA1,
                                         const.GRUPP_INTERVJUU):
                # hindajal on vaja tähist
                self.tahis = Ainelabiviija.give_tahis_for(aine_kood, kasutaja)
            else:
                self.tahis = None

    @classmethod
    def get_hindaja_by_user(cls, toimumisaeg_id, testikoht_id=None, user=None):
        from .testikoht import Testikoht

        if not user:
            user = usersession.user
        q = cls.query.\
            filter(cls.toimumisaeg_id==toimumisaeg_id).\
            filter(cls.kasutaja_id==user.id).\
            filter(cls.liik!=None)
        if testikoht_id:
            q = q.filter(sa.or_(cls.testikoht_id==None,
                                cls.testikoht_id==testikoht_id))
        elif user.koht_id:
            q = q.filter(sa.or_(cls.testikoht_id==None,
                                cls.testikoht.has(Testikoht.koht_id==user.koht_id)))
        return q.first()

    @classmethod
    def get_hindaja(cls, toimumisaeg_id, kasutaja_id, testikoht_id=None, testiruum_id=None, hindamiskogum_id=None, kehtiv=True):
        q = cls.query.\
            filter(cls.toimumisaeg_id==toimumisaeg_id).\
            filter(cls.kasutaja_id==kasutaja_id).\
            filter(cls.liik!=None).\
            filter(cls.testiruum_id==testiruum_id)
        if hindamiskogum_id:
            q = q.filter(cls.hindamiskogum_id==hindamiskogum_id)
        if kehtiv:
            q = q.filter(cls.staatus!=const.L_STAATUS_KEHTETU)            
        return q.first()

    def get_hindaja2(self):
        return Labiviija.query.filter_by(hindaja1_id=self.id).first()

    def get_hind_int(self):
        rcd = Labiviija.query.filter_by(hindaja1_id=self.id).\
              filter_by(kasutajagrupp_id=const.GRUPP_HIND_INT).first()
        if rcd:
            rcd.staatus = self.staatus
            rcd.kasutaja_id = self.kasutaja_id
            rcd.lang = self.lang
            rcd.hindamiskogum = self.hindamiskogum
            return rcd
    
    def give_hind_int(self):
        rcd = self.get_hind_int()
        if not rcd:
            rcd = Labiviija(staatus=self.staatus,
                            toimumisaeg=self.toimumisaeg,
                            kasutaja_id=self.kasutaja_id,
                            kasutajagrupp_id=const.GRUPP_HIND_INT,
                            lang=self.lang,
                            hindamiskogum=self.hindamiskogum,
                            hindaja1=self,
                            testikoht=self.testikoht,
                            testiruum=self.testiruum,
                            tasustatav=self.tasustatav,
                            toode_arv=0,
                            hinnatud_toode_arv=0,
                            tasu_toode_arv=0)                            
        return rcd
    
    @classmethod
    def give_hindaja(cls, toimumisaeg_id, kasutaja_id, liik, testiosa, hindamiskogum_id, testiruum=None, grupp_id=None, lang=None):
        "Hindaja kirje saamine"
        if not grupp_id:
            if testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_KP, const.VASTVORM_I):
                grupp_id = const.GRUPP_HINDAJA_K
            elif liik == const.HINDAJA1:
                grupp_id = const.GRUPP_HINDAJA_S
            elif liik == const.HINDAJA2:
                grupp_id = const.GRUPP_HINDAJA_S2
            elif liik == const.HINDAJA3:
                grupp_id = const.GRUPP_HINDAJA_S
            else:
                grupp_id = liik
            
        q_lv = Labiviija.query.\
            filter(Labiviija.kasutaja_id==kasutaja_id).\
            filter(Labiviija.liik==liik).\
            filter(Labiviija.toimumisaeg_id==toimumisaeg_id).\
            filter(Labiviija.kasutajagrupp_id==grupp_id).\
            filter(Labiviija.hindamiskogum_id==hindamiskogum_id)
        if testiruum:
            q_lv = q_lv.filter(Labiviija.testiruum_id==testiruum.id)
        if lang:
            q_lv = q_lv.filter(Labiviija.lang==lang)
        labiviija = q_lv.first()
        if not labiviija:
            labiviija = Labiviija(staatus=const.L_STAATUS_MAARATUD,
                                  toimumisaeg_id=toimumisaeg_id,
                                  kasutajagrupp_id=grupp_id,
                                  liik=liik,
                                  hindamiskogum_id=hindamiskogum_id,
                                  lang=lang or testiosa.test.lang,
                                  toode_arv=0,
                                  hinnatud_toode_arv=0,
                                  tasu_toode_arv=0)
            if testiruum:
               labiviija.testiruum = testiruum
               labiviija.testikoht = testiruum.testikoht
            labiviija.set_kasutaja(kasutaja_id)
        return labiviija

    @classmethod
    def get_testiruumid_id(cls, kasutaja_id, toimumisaeg_id, koht_id):
        "Leitakse testiruumid, kus antud kasutaja on antud toimumisajal antud kohas testiadmin"
        from .testikoht import Testikoht
        q = (SessionR.query(Labiviija.testiruum_id)
             .filter(Labiviija.kasutaja_id==kasutaja_id)
             .filter(Labiviija.kasutajagrupp_id==const.GRUPP_T_ADMIN)
             .filter(Labiviija.toimumisaeg_id==toimumisaeg_id)
             .join(Labiviija.testikoht)
             .filter(Testikoht.koht_id==koht_id)
             )
        return [testiruum_id for testiruum_id, in q.all()]

    def calc_toode_arv(self):
        from .sooritus import Sooritus
        from .hindamisolek import Hindamisolek
        from .sooritaja import Sooritaja
        from .labivaatus import Labivaatus
        from .vaie import Vaie
        
        if self.kasutajagrupp_id in (const.GRUPP_VAATLEJA,
                                     const.GRUPP_KOMISJON,
                                     const.GRUPP_KOMISJON_ESIMEES,
                                     const.GRUPP_KONSULTANT,
                                     const.GRUPP_T_ADMIN):
            kohal = (const.S_STAATUS_POOLELI,
                     const.S_STAATUS_KATKESTATUD,
                     const.S_STAATUS_KATKESPROT,
                     const.S_STAATUS_TEHTUD,
                     const.S_STAATUS_EEMALDATUD)
            q = SessionR.query(sa.func.count(Sooritus.id)).\
                filter(Sooritus.testiruum_id==self.testiruum_id).\
                filter(Sooritus.staatus.in_(kohal))
            self.toode_arv = self.hinnatud_toode_arv = self.tasu_toode_arv = q.scalar()

        elif self.kasutajagrupp_id == const.GRUPP_HINDAMISEKSPERT:
            # vaidehindaja:
            # arvesame kõiki sooritusi, millel on ettepanek olemas
            # ja mille mõneks läbivaatajaks on hindaja märgitud
            # (läbivaatuse staatust ei kontrolli, kuna seda nad ei märgi)
            q = SessionR.query(Sooritus.id).\
                join((Vaie, Vaie.sooritaja_id==Sooritus.sooritaja_id)).\
                filter(Vaie.ettepanek_dok!=None).\
                join(Sooritus.hindamisolekud).\
                join(Hindamisolek.hindamised).\
                filter(Hindamine.liik==const.HINDAJA5).\
                join(Hindamine.labivaatused).\
                filter(Labivaatus.ekspert_labiviija_id==self.id)
            self.toode_arv = self.hinnatud_toode_arv = self.tasu_toode_arv = q.distinct().count()

        else:
            on_sh_int = False
            if self.kasutajagrupp_id == const.GRUPP_INTERVJUU:
                vastvorm = self.toimumisaeg.testiosa.vastvorm_kood
                if vastvorm in (const.VASTVORM_SH, const.VASTVORM_I):
                    # intervjueerimine on toimunud süsteemis
                    q = (SessionR.query(sa.func.count(Sooritus.id))
                         .filter(Sooritus.intervjuu_labiviija_id==self.id))
                    self.toode_arv = q.scalar()
                    q = q.filter(Sooritus.staatus==const.S_STAATUS_TEHTUD)
                    on_sh_int = True
                else:
                    # p-testis on intervjueerija märgitud sisestamisel
                    # jätame välja sooritused, mida intervjueerija ise hindas
                    q = (SessionR.query(sa.func.count(Hindamine.id))
                         .filter(Hindamine.tyhistatud==False)
                         .filter(Hindamine.liik==const.HINDAJA1)
                         .filter(Hindamine.sisestus==1)
                         .filter(Hindamine.intervjuu_labiviija==self))

                    # vajadusel loome hindaja-intervjueerija kirje
                    q2 = q.filter(Hindamine.hindaja_kasutaja_id==self.kasutaja_id)
                    lv2 = q2.scalar() and self.give_hind_int() or self.get_hind_int()
                    if lv2:
                        lv2.calc_toode_arv()
                        
                    q = q.filter(Hindamine.hindaja_kasutaja_id!=self.kasutaja_id)
                    self.toode_arv = q.scalar()
                    q = q.join(Hindamine.hindamisolek)                                
            elif self.kasutajagrupp_id == const.GRUPP_HIND_INT:
                # hindaja-intervjueerijad - sooritused, mida on ise hinnanud
                q = (SessionR.query(sa.func.count(Hindamine.id))
                    .filter(Hindamine.intervjuu_labiviija==self.hindaja1)
                    .filter(Hindamine.tyhistatud==False)
                    .filter(Hindamine.staatus != const.H_STAATUS_LYKATUD)
                    .filter(Hindamine.liik==const.HINDAJA1)
                    .filter(Hindamine.sisestus==1)
                    .filter(Hindamine.hindaja_kasutaja_id==self.kasutaja_id))
                self.toode_arv = q.scalar()
                q = q.join(Hindamine.hindamisolek)                
            else:
                # hindajad
                # staatus - jätame välja tagasi lükatud hindamised
                q = (SessionR.query(sa.func.count(Hindamine.id))
                     .filter(sa.or_(Hindamine.labiviija_id==self.id,
                                    Hindamine.kontroll_labiviija_id==self.id))
                     .filter(Hindamine.tyhistatud==False)
                     .filter(Hindamine.staatus != const.H_STAATUS_LYKATUD)
                     .filter(Hindamine.sisestus==1)
                     .join(Hindamine.hindamisolek)
                     .filter(Hindamisolek.mittekasitsi==False))
                self.toode_arv = q.scalar()
                q = q.filter(Hindamine.staatus==const.H_STAATUS_HINNATUD)

            self.hinnatud_toode_arv = q.scalar()
            
            # töötasu arvestatakse nende sooritajate pealt,
            # kes ei õpi samas koolis, kus läbiviija töötab (EH-155)
            q_tookohad_id = (SessionR.query(Pedagoog.koht_id.distinct())
                             .filter(Pedagoog.kasutaja_id==self.kasutaja_id))
            tookohad_id = [k_id for k_id, in q_tookohad_id.all()]
            if tookohad_id and on_sh_int:
                q = (q.join(Sooritus.sooritaja)
                     .filter(sa.exists().where(sa.and_(
                         Hindamisolek.sooritus_id==Sooritus.id,
                         Hindamisolek.hindamiskogum_id==Hindamiskogum.id,
                         sa.or_(Hindamiskogum.oma_kool_tasuta==False,
                                Sooritaja.kool_koht_id==None,
                                ~ Sooritaja.kool_koht_id.in_(tookohad_id))))
                                )
                    )
            elif tookohad_id:
                q = (q.join(Hindamisolek.sooritus)
                     .join(Sooritus.sooritaja)
                     .join(Hindamisolek.hindamiskogum)
                     .filter(sa.or_(Hindamiskogum.oma_kool_tasuta==False,
                                    Sooritaja.kool_koht_id==None,
                                    ~ Sooritaja.kool_koht_id.in_(tookohad_id)))
                     )
            #log_query(q)
            self.tasu_toode_arv = q.scalar()
