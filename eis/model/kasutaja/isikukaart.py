from eis.model.entityhelper import *
log = logging.getLogger(__name__)

class Isikukaart(EntityHelper, Base):
    """EHISe isikukaart
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    isikukood = Column(String(50), nullable=False) # isikukood
    data = Column(Text) # isikukaardi päringu vastus JSONina
    isikukaart_tood = relationship('Isikukaart_too', back_populates='isikukaart')

    @classmethod
    def get_current(cls, isikukood):
        "Leitakse isiku värskeim isikukaart"
        return (Isikukaart.query.filter_by(isikukood=isikukood)
                .order_by(sa.desc(Isikukaart.id))
                .first())
    
class Isikukaart_too(EntityHelper, Base):
    """EHISe isikukaardi töötamise kirje
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    isikukaart_id = Column(Integer, ForeignKey('isikukaart.id'), index=True, nullable=False) # viide isikukaardi kirjele
    isikukaart = relationship('Isikukaart', back_populates='isikukaart_tood')
    liik = Column(String(50)) # haridustase (HUVIKOOL, POHIKOOL, ...)
    oppeasutus = Column(String(100)) # õppeasutus
    oppeasutus_id = Column(Integer) # õppeasutuse EHIS ID
    ametikoht = Column(String(100)) # ametikoht
    ametikoht_algus = Column(Date) # töötamise algus
    ametikoht_lopp = Column(Date) # töötamise lõpp
    on_tunniandja = Column(Integer) # on tunniandja
    on_oppejoud = Column(Integer) # on õppejõud
    taitmise_viis = Column(String(50)) # ametikoha täitmise viis
    ametikoht_koormus = Column(Float) # koormus
    tooleping = Column(String(100)) # tööleping
    ametikoht_kval_vastavus = Column(String(100)) # kvalifikatsiooninõuetele vastavus
    ametijark = Column(String(50)) # ametijärk
    haridustase = Column(String(50)) # omandatud haridustase
    lapsehooldus_puhkus = Column(Boolean) # lapsehoolduspuhkusel
    isikukaart_too_oppekavad = relationship('Isikukaart_too_oppekava', back_populates='isikukaart_too')
    isikukaart_too_oppeained = relationship('Isikukaart_too_oppeaine', back_populates='isikukaart_too')

class Isikukaart_too_oppekava(EntityHelper, Base):
    """EHISe isikukaardi töötamise õppekava kirje
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    isikukaart_too_id = Column(Integer, ForeignKey('isikukaart_too.id'), index=True, nullable=False) # viide isikukaardi töötamise kirjele
    isikukaart_too = relationship('Isikukaart_too', back_populates='isikukaart_too_oppekavad')
    kl_oppekava = Column(String(50)) # õppekava klassifikaator
    oppekava_kood = Column(String(50)) # kood
    oppekava_nimetus = Column(String(100)) # nimetus
    kvalifikatsiooni_vastavus = Column(String(100)) # kvalifikatsiooni vastavus kehtivas raamistikus
    akad_kraad = Column(String(100)) # akadeemiline kraad või diplom
    kval_dokument = Column(String(100)) # kvalifikatsiooni dokument

class Isikukaart_too_oppeaine(EntityHelper, Base):
    """EHISe isikukaardi töötamise õppeaine kirje
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    isikukaart_too_id = Column(Integer, ForeignKey('isikukaart_too.id'), index=True, nullable=False) # viide isikukaardi töötamise kirjele
    isikukaart_too = relationship('Isikukaart_too', back_populates='isikukaart_too_oppeained')
    oppeaine = Column(String(100)) # õppeaine
    kooliaste = Column(String(50)) # kooliaste
    maht = Column(Float) # koormus õppeaineti
    kval_vastavus = Column(String(100)) # kvalifikatsiooninõuetele vastavus
