"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import Opt
from eis.model.kasutaja import *
from eis.model.koht import *
from .eeltest import Eeltest
_ = usersession._

class Komplekt(EntityHelper, Base):
    """Testi ülesannete komplekt (variant)
    """
        
    id = Column(Integer, primary_key=True, autoincrement=True)
    staatus = Column(Integer, nullable=False) # olek: 1=const.K_STAATUS_KOOSTAMISEL - koostamisel; 2=const.K_STAATUS_KINNITATUD - kinnitatud; 8=const.K_STAATUS_ARHIIV - arhiveeritud
    lukus = Column(Integer) # muutmise lukustus: NULL - komplekt on kinnitamata; 1=const.LUKUS_KINNITATUD - komplekt on kinnitatud ja muuta võib ainult ülesannete hindamise osa; 2=const.LUKUS_KATSE_SOORITATUD - komplekt on sooritatud KATSE testimiskorral või eelvaates, ei ole hinnatud, muuta võib ainult hindamise osa, muutja saab lukust lahti võtta; 3=const.LUKUS_KATSE_HINNATUD - komplekt on sooritatud ja hinnatud ainult KATSE testimiskorral, midagi ei või muuta, muutja saab lukust lahti võtta; 4=const.LUKUS_SOORITATUD - komplekt on kasutatud mitte-KATSE testimiskorral või testimiskorrata, hinnatud ei ole, muuta võib ainult hindamise osa, lukust lahti võtmiseks vaja eriõigusi; 5=const.LUKUS_HINNATUD - komplekti on kasutatud mitte-KATSE testimiskorral või testimiskorrata, on hinnatud, muuta ei või midagi, lukust lahti võtmiseks on vaja eriõigusi
    tahis = Column(String(10), nullable=False) # tähis
    valitudylesanded = relationship('Valitudylesanne', order_by='Valitudylesanne.testiylesanne_id,Valitudylesanne.seq', back_populates='komplekt')
    eeltestid = relationship('Eeltest', secondary='eeltest_komplekt', back_populates='komplektid') # eeltestid antud komplekti testimiseks
    komplektivalik_id = Column(Integer, ForeignKey('komplektivalik.id'), index=True, nullable=False) # viide komplektivalikule
    komplektivalik = relationship('Komplektivalik', foreign_keys=komplektivalik_id, back_populates='komplektid') 
    testifailid = relationship('Testifail', back_populates='komplekt') 
    erialatestid = relationship('Erialatest', back_populates='komplekt')
    erikomplektid = relationship('Erikomplekt', back_populates='komplekt')
    toimumisajad = relationship('Toimumisaeg', secondary='toimumisaeg_komplekt', back_populates='komplektid')
    skeeled = Column(String(60)) # testi keelte koodid eraldatuna tühikuga
    
    lisaaeg = Column(Float) # komplekti erialatestide lisaaegade summa
    dif_hindamine = Column(Boolean) # kas komplekti erialatestidest mõnes on dif_hindamine

    __table_args__ = (
        sa.UniqueConstraint('komplektivalik_id','tahis'),
        )
    _parent_key = 'komplektivalik_id'

    @property
    def lukus_nimi(self):
        if self.lukus:
            di = {const.LUKUS_KINNITATUD: _("Kinnitatud komplekt"),
                  const.LUKUS_KATSE_SOORITATUD: _("Katsetamisel sooritatud komplekt"),
                  #const.LUKUS_KATSE_SOORITATUD: _("KATSE testimiskorral sooritatud komplekt"),
                  const.LUKUS_KATSE_HINNATUD: _("Katsetamisel hinnatud sooritustega komplekt"),
                  #const.LUKUS_KATSE_HINNATUD: _("KATSE testimiskorral hinnatud sooritustega komplekt"),
                  const.LUKUS_SOORITATUD: _("Sooritatud komplekt"),
                  const.LUKUS_HINNATUD: _("Hinnatud sooritustega komplekt"),
                  }
            return di[self.lukus]
        else:
            return _("Pole lukus")

    @property
    def keeled(self):
        if not self.skeeled:
            return []
        return self.skeeled.split()

    def copy_lang(self, t):
        """Kopeerime testilt kõik keeled.
        """
        self.skeeled = t.skeeled

    @property 
    def staatus_nimi(self):
        return Klrida.get_str('K_STAATUS', str(self.staatus)) 

    def set_modifier(self):
        EntityHelper.set_modifier(self)
        #self.set_lukus()
    
    def default(self):
        if not self.staatus:
            self.staatus = const.K_STAATUS_KOOSTAMISEL

    def copy(self):
        """Komplektist tehakse sama testi sisse koopia.
        """
        cp = EntityHelper.copy(self)
        Session.autoflush = False # integrity errori pärast
        cp.komplektivalik_id = self.komplektivalik_id
        cp.staatus = const.K_STAATUS_KOOSTAMISEL
        cp.tahis = None
        cp.gen_tahis()
        self.copy_subrecords(cp, ['testifailid',
                                  #'testilisamaterjalid',
                                  ])

        map_vy = {}
        for vy in self.valitudylesanded:
            cp_vy = vy.copy(ignore=['komplekt_id'])
            cp.valitudylesanded.append(cp_vy)
            map_vy[vy.id] = cp_vy

        Session.autoflush = True    
        return cp
    
    def give_erialatest(self, alatest_id=None):
        """Tagastatakse erialatest antud alatesti jaoks.
        Kui testis pole alateste, siis on alatest_id==None.
        """
        from .erialatest import Erialatest

        rcd = self.get_erialatest(alatest_id)
        if rcd is None:
            rcd = Erialatest(komplekt=self, alatest_id=alatest_id)
            self.erialatestid.append(rcd)
        return rcd

    def get_erialatest(self, alatest_id=None):
        """Tagastatakse erialatest antud alatesti jaoks.
        Kui testis pole alateste, siis on alatest_id==None.
        """
        for rcd in self.erialatestid:
            if not alatest_id:
                if not rcd.alatest_id:
                    return rcd
            elif rcd.alatest_id == int(alatest_id):
                return rcd

    def getq_valitudylesanne(self, ylesanne_id, testiylesanne_id=None):
        from .valitudylesanne import Valitudylesanne
        q = (Session.query(Valitudylesanne)
             .filter(Valitudylesanne.komplekt_id==self.id)
             )
        if ylesanne_id:
            q = q.filter(Valitudylesanne.ylesanne_id==ylesanne_id)
        if testiylesanne_id:
            q = q.filter(Valitudylesanne.testiylesanne_id==testiylesanne_id)
        q = q.order_by(Valitudylesanne.seq)
        return q.first()
    
    def get_valitudylesanne(self, ylesanne_id, testiylesanne_id=None):
        for vy in self.valitudylesanded:
            if ylesanne_id:
                if vy.ylesanne_id == ylesanne_id:
                    return vy
            elif testiylesanne_id:
                if vy.testiylesanne_id == testiylesanne_id:
                    return vy

    def get_testiylesanded_id(self, hk=None):
        "Leiame testiylesannete id-d, mis on selles komplektis kasutusel"
        li = []
        for vy in self.valitudylesanded:
            if vy.ylesanne_id:
                if not hk or vy.hindamiskogum_id == hk.id or \
                   not vy.hindamiskogum_id and vy.testiylesanne.hindamiskogum_id == hk.id:
                    li.append(vy.testiylesanne_id)
        return li

    def delete_subitems(self):    
        self.delete_subrecords(['valitudylesanded',
                                'testifailid',
                                'erialatestid',
                                #'testilisamaterjalid',
                                ])

    @property
    def on_erivajadus(self):
        return self.lisaaeg or self.dif_hindamine

    def gen_tahis(self):
        from .komplektivalik import Komplektivalik

        if not self.tahis:
            kvalik = self.komplektivalik or self.komplektivalik_id and Komplektivalik.get(self.komplektivalik_id)
            for n in range(1,100):
                kood = '%d' % n
                if kvalik:
                    for k in kvalik.komplektid:
                        if k.tahis == kood:
                            kood = None
                            break
                if kood:
                    self.tahis = kood
                    break

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .komplektivalik import Komplektivalik
        kvalik = self.komplektivalik or self.komplektivalik_id and Komplektivalik.get(self.komplektivalik_id)
        if kvalik:
            testiosa = kvalik.testiosa
            testiosa.logi('Komplekt %s (%s) %s' % (self.id, self.tahis, liik), vanad_andmed, uued_andmed, logitase)

