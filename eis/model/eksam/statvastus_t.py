"Vastused väljavõtte jaoks"
from eis.model.entityhelper import *

class Statvastus_t(Base):
    """Küsimuste vastused Exceli väljavõtte kiirendamiseks.
    Uuendatakse vaate statvastus põhjal testi või toimumisaja kaupa siis,
    kui tulemusi arvutatakse
    """
    id = Column(BigInteger, primary_key=True, autoincrement=True)    
    statvastus_t_seis_id = Column(Integer, ForeignKey('statvastus_t_seis.id'), index=True, nullable=False) # arvutusprotsessi ID, millega andmed on leitud    
    kood1 = Column(String(201)) # küsimuse kood, eripaari korral koos kooloni ja esimese valiku koodiga
    selgitus1 = Column(String(255)) # küsimuse selgitus või eripaari esimese valiku selgitus
    kysimus_seq = Column(Integer) # küsimuse jrk
    valik1_seq = Column(Integer) # eripaari korral esimese valiku jrk
    ks_punktid = Column(Float) # antud vastuse punktid; vastamata jätmisel alati 0
    svpunktid = Column(Float) # eripaari korral eripaari punktid, muidu küsimuse punktid
    kv_punktid = Column(Float) # küsimuse punktid
    max_punktid = Column(Float) # eripaari korral eripaari max toorpunktid, muidu küsimuse toorpunktid
    oige = Column(Float) # vastuse õigsus (1 - õige; 0,5 - osaliselt õige, 0 - vale või loetamatu või vastamata)
    vastus = Column(Text) # vastus või eripaari teise valiku kood
    selgitus = Column(String(255)) # vastuse selgitus
    kvsisu_seq = Column(Integer) # vastuse jrk nr
    kvsisu_id = Column(Integer, index=True) # viide vastuse sisu kirjele
    kysimus_id = Column(Integer, index=True) # viide küsimuse kirjele
    kysimusevastus_id = Column(Integer, index=True) # viide küsimusevastuse kirjele
    ylesandevastus_id = Column(Integer, index=True) # viide ülesandevastuse kirjele
    max_vastus = Column(Integer) # kood1 max vastuste arv
    valik1_id = Column(Integer, index=True)
    valik2_id = Column(Integer, index=True)
    valitudylesanne_id = Column(Integer, index=True)
    testiylesanne_id = Column(Integer, index=True)
    tulemus_id = Column(Integer, index=True)
    ylesanne_id = Column(Integer, index=True)
    sooritus_id = Column(Integer, index=True)
    sooritaja_id = Column(Integer, index=True)
    toimumisaeg_id = Column(Integer, index=True)
    testiosa_id = Column(Integer, index=True)
    testikoht_id = Column(Integer, index=True)
    staatus = Column(Integer) # soorituse staatus
    __tablename__ = 'statvastus_t'

class Statvastus_t_seis(EntityHelper, Base):
    """Tabeli statvastus_t uuendamise andmed
    """
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    testiosa_id = Column(Integer, index=True) # viide testiosale, mille andmed uuendati
    toimumisaeg_id = Column(Integer, index=True) # viide toimumisajale, mille andmed uuendati
    seisuga = Column(DateTime) # andmete uuendamise aeg
    protsess_id = Column(Integer) # arvutusprotsessi ID, millega andmed uuendati

    @classmethod
    def on_arvutatud(cls, testiosa_id, toimumisaeg_id):
        "Kas statvastus_t on täidetud"
        q = (SessionR.query(Statvastus_t_seis.id)
             .filter_by(testiosa_id=testiosa_id)
             .filter_by(toimumisaeg_id=toimumisaeg_id)
             )
        for r in q.all():
            return True
        return False
    
