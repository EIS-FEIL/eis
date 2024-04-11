"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import Opt
from eis.model.kasutaja import *
from eis.model.koht import *
from .komplekt import Komplekt
from .hindamiskogum import Hindamiskogum

class Komplektivalik(EntityHelper, Base):
    """Testi ülesandekomplektide valik.
    Komplektivalik ühendab alatestid, mida samad komplektid katavad.
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    testiosa_id = Column(Integer, ForeignKey('testiosa.id'), index=True, nullable=False) # viide testiosale
    testiosa = relationship('Testiosa', foreign_keys=testiosa_id, back_populates='komplektivalikud')
    komplektid = relationship('Komplekt', order_by='Komplekt.tahis', back_populates='komplektivalik') # komplektid
    alatestid = relationship('Alatest', order_by='Alatest.seq', back_populates='komplektivalik') # komplektidega kaetud alatestid
    kursus_kood = Column(String(10)) # lai või kitsas (matemaatika korral), klassifikaator KURSUS (komplektivaliku kõigil alatestidel peab olema sama kursus)
    alatestideta = Column(Boolean) # unikaalsuse kontroll, et ei tekiks mitu alatestideta komplektivalikut: kursusteta ja alatestideta komplektivaliku korral True (unikaalses indeksis); muidu NULL (unikaalset indeksit ei sega)
    hindamiskogumid = relationship('Hindamiskogum', back_populates='komplektivalik') # hindamiskogumid

    _parent_key = 'testiosa_id'

    __table_args__ = (
        sa.UniqueConstraint('testiosa_id','alatestideta'),
        )

    @property
    def str_alatestid(self):
        li = [str(rcd.seq) for rcd in self.alatestid]
        return ', '.join(li)

    @property
    def opt_alatestid(self):
        return [(item.id, item.nimi) for item in self.alatestid]

    @property
    def opt_komplektid(self):
        return [(item.id, item.tahis) for item in self.komplektid]

    def get_opt_komplektid(self, toimumisaeg, full=False):
        "Leitakse toimumisajal sooritajale lubatud komplektid"
        from eis.model.testimine.toimumisaeg import Toimumisaeg
        if full:
            q = SessionR.query(Komplekt)
        else:
            q = SessionR.query(Komplekt.id, Komplekt.tahis)
        q = q.filter(Komplekt.komplektivalik_id==self.id)
        if toimumisaeg:
            q = (q.join(Komplekt.toimumisajad)
                 .filter(Toimumisaeg.id==toimumisaeg.id)
                 )
        q = q.filter(Komplekt.staatus==const.K_STAATUS_KINNITATUD)
        q = q.order_by(Komplekt.tahis)
        if full:
            return list(q.all())
        else:
            return [(k_id, tahis) for (k_id, tahis) in q.all()]

    def give_komplekt(self):
        from .komplekt import Komplekt
        if len(self.komplektid) == 0:
            k = Komplekt(komplektivalik=self, tahis='K')
            self.komplektid.append(k)
        return self.komplektid[0]

    def delete_subitems(self):    
        self.delete_subrecords(['komplektid',
                                #'hindamiskogumid',
                                ])

    @property
    def lukus(self):
        for k in self.komplektid:
            if k.lukus:
                return True
        return False

    @property
    def kursus_nimi(self):
        if self.kursus_kood:
            test = self.testiosa and self.testiosa.test
            aine = test and test.aine_kood
            if aine:
                return Klrida.get_str('KURSUS', self.kursus_kood, ylem_kood=aine)            
    
    def give_valitudylesanded(self, komplekt=None):
        from .testiosa import Testiosa
        testiosa = self.testiosa or Testiosa.get(self.testiosa_id)
        komplektid = komplekt and [komplekt] or list(self.komplektid)
        if len(testiosa.alatestid):
            for alatest in self.alatestid:
                for ty in alatest.testiylesanded:
                    for k in komplektid:
                        # et ei tuleks InvalidRequestError: The transaction is inactive due to a rollback...
                        Session.flush() 
                        ty.give_valitudylesanded(k)

            # kustutame need valitudylesanded, mis ei ole enam sellest komplektivalikust
            muud_ty = [ty.id for ty in testiosa.testiylesanded if ty.alatest not in self.alatestid]
            for k in komplektid:
                for vy in k.valitudylesanded:
                    if vy.testiylesanne_id in muud_ty:
                        vy.delete()
                
        else:
            for ty in testiosa.testiylesanded:
                for k in komplektid:
                    Session.flush()
                    ty.give_valitudylesanded(k)

    def get_default_hindamiskogum(self):
        "Leitakse komplektivaliku vaikimisi hindamiskogum"
        for k in self.hindamiskogumid:
            if k.vaikimisi:
                return k
            
    def give_default_hindamiskogum(self):
        "Luuakse komplektivaliku vaikimisi hindamiskogum"
        k = self.get_default_hindamiskogum()
        if not k:
            from .testiosa import Testiosa
            testiosa = self.testiosa or Testiosa.get(self.testiosa_id)
            # leiame unikaalse tähise
            tahised = [hk.tahis for hk in testiosa.hindamiskogumid]
            tahis = prefix = 'HK'
            for n in range(100):
                if tahis not in tahised:
                    break
                tahis = f'{prefix}{n}'
            # loome hindamiskogumi
            k = Hindamiskogum(testiosa=testiosa,
                              komplektivalik=self,
                              tahis=tahis,
                              nimi='Hindamiskogum',
                              vaikimisi=True,
                              arvutihinnatav=True,
                              max_pallid=0)
        return k
