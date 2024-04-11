"Testikorralduse andmemudel"
from eis.model.entityhelper import *

class Sisestusolek(EntityHelper, Base):
    """Soorituse sisestamise kehtiv olek sisestuskogumite ja sisestuste lõikes.
    Sisestatakse vastuseid või hindamisprotokolle.
    Vastuste sisestamisel (liik=NULL) toimub selle tabeli põhjal arvestus,
    millises olekus on soorituse sisestuskogumi sisestamine
    (mis on veel sisestamata ja kes saab sisestada).
    Hindamisprotokollide sisestamisel toimub arvestus hindamisprotokolli kirje põhjal ja
    sisestusoleku kirje on vajalik ainult hiljem sisestajate töömahu kokku arvutamiseks.
    Selle tabeli põhjal toimib läbiviijate aruande sisestajate osa.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sooritus_id = Column(Integer, ForeignKey('sooritus.id'), index=True, nullable=False) # viide hinnatavale sooritusele
    sooritus = relationship('Sooritus', foreign_keys=sooritus_id, back_populates='sisestusolekud')
    staatus = Column(Integer, sa.DefaultClause('1'), nullable=False) # sisestamise olek: 0=const.H_STAATUS_HINDAMATA - alustamata; 1=const.H_STAATUS_POOLELI - sisestamisel; 2=const.H_STAATUS_LYKATUD - loobutud; 6=const.H_STAATUS_HINNATUD - sisestatud
    sisestuskogum_id = Column(Integer, index=True, nullable=False) # viide sisestuskogumile
    #sisestuskogum = relationship('Sisestuskogum', foreign_keys=sisestuskogum_id)
    staatus1 = Column(Integer, sa.DefaultClause('0'), nullable=False) # I sisestamise olek: 0=const.H_STAATUS_HINDAMATA - alustamata; 1=const.H_STAATUS_POOLELI - sisestamisel; 2=const.H_STAATUS_LYKATUD - loobutud; 6=const.H_STAATUS_HINNATUD - sisestatud
    sisestaja1_kasutaja_id = Column(Integer, index=True) # viide I sisestaja kasutajale
    #sisestaja1_kasutaja = relationship('Kasutaja', foreign_keys=sisestaja1_kasutaja_id)
    sisestaja1_algus = Column(DateTime) # esimese sisestamise algus, vajalik hiljem tunnis sisestamiste arvu väljavõtte jaoks
    staatus2 = Column(Integer, sa.DefaultClause('0'), nullable=False) # II sisestamise olek: 0=const.H_STAATUS_HINDAMATA - alustamata; 1=const.H_STAATUS_POOLELI - sisestamisel; 2=const.H_STAATUS_LYKATUD - loobutud; 6=const.H_STAATUS_HINNATUD - sisestatud
    sisestaja2_kasutaja_id = Column(Integer, index=True) # viide II sisestaja kasutajale
    #sisestaja2_kasutaja = relationship('Kasutaja', foreign_keys=sisestaja2_kasutaja_id)
    sisestaja2_algus = Column(DateTime) # teise sisestamise algus, vajalik hiljem tunnis sisestamiste arvu väljavõtte jaoks
    skann = Column(LargeBinary) # skannitud testitöö PDF-failina
    liik = Column(Integer, nullable=False) # hindamisprotokolli liik: 1=const.HINDAJA - I hindamine; 2=const.HINDAJA2 - II hindamine ; 3=const.HINDAJA3 - III hindamine; 4=const.HINDAJA4 - eksperthindamine; 0=const.VASTUSTESISESTUS - vastuste sisestamine
    pallid = Column(Float) # soorituse pallid antud sisestuskogumi eest
    toorpunktid = Column(Float) # soorituse toorpunktide summa antud sisestuskogumi eest
    __table_args__ = (
        sa.UniqueConstraint('sooritus_id','sisestuskogum_id','liik'),
        )
    _parent_key = 'sooritus_id'

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
