"Testikorralduse andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *

class Hindamisprotokoll(EntityHelper, Base):
    """Hindamisprotokoll ühendab sama liiki hindamise kirjed, 
    mille hinnatavad kuuluvad samasse testiprotokolli ja 
    hindamiskogumid kuuluvad samasse sisestuskogumisse.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    liik = Column(Integer, nullable=False) # hindamise liik (kui hindamisprotokoll on olemas, siis sama, mis hindamisprotokollis): 1=const.HINDAJA - I hindamine; 2=const.HINDAJA2 - II hindamine ; 3=const.HINDAJA3 - III hindamine; 4=const.HINDAJA4 - eksperthindamine
    sisestuskogum_id = Column(Integer, ForeignKey('sisestuskogum.id'), index=True) # viide sisestuskogumile
    sisestuskogum = relationship('Sisestuskogum', foreign_keys=sisestuskogum_id)
    #tahised = Column(String(20)) # testiprotokolli tähised ja sisestuskogumi tähis, kriips vahel
    testiprotokoll_id = Column(Integer, ForeignKey('testiprotokoll.id'), index=True, nullable=False) # viide testiprotokollile
    testiprotokoll = relationship('Testiprotokoll', foreign_keys=testiprotokoll_id, back_populates='hindamisprotokollid')
    staatus = Column(Integer, sa.DefaultClause('0'), nullable=False) # sisestamise olek: 0=const.H_STAATUS_HINDAMATA - alustamata; 1=const.H_STAATUS_POOLELI - sisestamisel; 2=const.H_STAATUS_LYKATUD - loobutud; 3=const.H_STAATUS_HINNATUD - sisestatud
    staatus1 = Column(Integer, sa.DefaultClause('0'), nullable=False) # I sisestamise olek: 0=const.H_STAATUS_HINDAMATA - alustamata; 1=const.H_STAATUS_POOLELI - sisestamisel; 2=const.H_STAATUS_LYKATUD - loobutud; 3=const.H_STAATUS_HINNATUD - sisestatud
    sisestaja1_kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True)
    sisestaja1_kasutaja = relationship('Kasutaja', foreign_keys=sisestaja1_kasutaja_id) # viide I sisestaja kasutajale
    staatus2 = Column(Integer, sa.DefaultClause('0'), nullable=False) # II sisestamise olek: 0=const.H_STAATUS_HINDAMATA - alustamata; 1=const.H_STAATUS_POOLELI - sisestamisel; 2=const.H_STAATUS_LYKATUD - loobutud; 3=const.H_STAATUS_HINNATUD - sisestatud
    sisestaja2_kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide II sisestaja kasutajale
    sisestaja2_kasutaja = relationship('Kasutaja', foreign_keys=sisestaja2_kasutaja_id)
    tehtud_toodearv = Column(Integer) # tehtud ja valimis olevate hindamiskogumisoorituste arv (arvutatakse protokolli kinnitamisel)
    hindamised = relationship('Hindamine', back_populates='hindamisprotokoll')
    __table_args__ = (
        sa.UniqueConstraint('testiprotokoll_id','sisestuskogum_id','liik'),
        )
    _parent_key = 'testiprotokoll_id'

    def get_tahised(self):
        sk = self.sisestuskogum
        return '%s-%s' % (self.testiprotokoll.tahised, sk and sk.tahis or '')
    
    def get_short_tahised(self):
        # tähiste viimased kolm kohta
        return '-'.join(self.get_tahised().split('-')[3:])

    @property
    def liik_nimi(self):
        return usersession.get_opt().HINDAJA.get(self.liik)
    
    @property 
    def staatus_nimi(self):
        return usersession.get_opt().HPR_STAATUS.get(self.staatus)

    @property 
    def staatus1_nimi(self):
        return usersession.get_opt().HPR_STAATUS.get(self.staatus1)

    @property 
    def staatus2_nimi(self):
        return usersession.get_opt().HPR_STAATUS.get(self.staatus2)

    def can_sis1(self, kasutaja_id):
        """Kas kasutaja võib olla esimene sisestaja?
        Võib siis, kui on ise juba I sisestaja 
        või (seda veel pole või on loobutud) ja ta pole ise II sisestaja.
        """
        return self.sisestaja1_kasutaja_id == kasutaja_id or \
            self.sisestaja2_kasutaja_id != kasutaja_id and \
            (not self.sisestaja1_kasutaja_id or self.staatus1 == const.H_STAATUS_LYKATUD)

    def can_sis2(self, kasutaja_id):
        """Kas kasutaja võib olla teine sisestaja?
        """
        return self.sisestaja2_kasutaja_id == kasutaja_id or \
            self.sisestaja1_kasutaja_id != kasutaja_id and \
            (not self.sisestaja2_kasutaja_id or self.staatus2 == const.H_STAATUS_LYKATUD)        

    def calc_tehtud_toodearv(self, tpr_id=None):
        """Tehtud tööde arvu arvutamine
        """
        from .hindamisolek import Hindamisolek
        from .sooritus import Sooritus
        from .sooritaja import Sooritaja
        from eis.model.eksam.alatestisooritus import Alatestisooritus
        
        if not tpr_id:
            tpr_id = self.testiprotokoll_id or self.testiprotokoll.id

        sk_id = self.sisestuskogum_id
        Session.flush()
        q = (Session.query(sa.func.count(Sooritus.id))
             .filter(Sooritus.testiprotokoll_id==tpr_id)
             .join(Sooritus.hindamisolekud)
             .filter(Hindamisolek.puudus==False)
             .join(Hindamisolek.hindamiskogum)
             .filter(Hindamiskogum.sisestuskogum_id==sk_id)
             .join(Sooritus.sooritaja)
             )
        # kas võib tehtuks...?
        q = q.filter(Sooritus.staatus==const.S_STAATUS_TEHTUD) 

        # leiame alatestid, mis sisaldavad selle sisestuskogumi ülesandeid
        alatestid_id = set()
        sisestuskogum = Sisestuskogum.get(sk_id)
        for hk in sisestuskogum.hindamiskogumid:
            for ty in hk.testiylesanded:
                if not ty.alatest_id:
                    break
                alatestid_id.add(ty.alatest_id)
        if alatestid_id:
            # kui testiosal on alatestid, siis kontrollime, et sooritaja
            # poleks antud hindamisprotokolli alatestidest vabastatud
            q = q.filter(sa.exists().where(
                sa.and_(Alatestisooritus.sooritus_id==Sooritus.id,
                        Alatestisooritus.alatest_id.in_(alatestid_id),
                        Alatestisooritus.staatus==const.S_STAATUS_TEHTUD)
                ))
        
        self.tehtud_toodearv = q.scalar()
