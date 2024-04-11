"Testimise andmemudel"
from eis.model.entityhelper import *

class Soorituslogi(EntityHelper, Base):
    """Soorituse kirje muudatuste logi
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    sooritus_id = Column(Integer, ForeignKey('sooritus.id'), index=True, nullable=False) # viide sooritusele
    sooritus = relationship('Sooritus', foreign_keys=sooritus_id, back_populates='soorituslogid')
    tahised = Column(String(20)) # soorituskoha ja soorituse tähised, kriips vahel
    reg_toimumispaev_id = Column(Integer) # registreerimisel määratud toimumispäev 
    kavaaeg = Column(DateTime) # sooritajale kavandatud alguse aeg
    staatus = Column(Integer, nullable=False) # sooritamise olek
    hindamine_staatus = Column(Integer, sa.DefaultClause('0'), nullable=False) # hindamise olek
    pallid = Column(Float) # saadud hindepallid
    pallid_arvuti = Column(Float) # (esialgne) arvutihinnatav osa hindepallidest
    pallid_kasitsi = Column(Float) # mitte-arvutihinnatav osa hindepallidest
    tulemus_protsent = Column(Float) # saadud hindepallid protsentides suurimast võimalikust tulemusest
    max_pallid = Column(Float) # võimalikud max pallid (sõltub alatestidest vabastusest ja lõdva struktuuri korral komplektist)
    testiarvuti_id = Column(Integer) # viide testi sooritamiseks kasutatud arvutile
    autentimine = Column(String(2)) #.sooritaja autentimisviis: p - parooliga; i - id-kaardiga; i2 - digitaalse isikutunnistusega
    testikoht_id = Column(Integer) # viide testikohale
    testiruum_id = Column(Integer) # viide testiruumile
    tugiisik_kasutaja_id = Column(Integer) # viide tugiisikule
    url = Column(String(200)) # andmeid muutnud tegevuse URL
    remote_addr = Column(String(60)) # muutja klient
    server_addr = Column(String(60)) # muutja server

    _parent_key = 'sooritus_id'
    
    @property 
    def staatus_nimi(self):
        return usersession.get_opt().S_STAATUS.get(self.staatus)

    @property 
    def hindamine_staatus_nimi(self):
        return usersession.get_opt().H_STAATUS.get(self.hindamine_staatus)

    @property
    def testikoht(self):
        if self.testikoht_id:
            return Testikoht.get(self.testikoht_id)

    @property
    def testiruum(self):
        if self.testiruum_id:
            return Testiruum.get(self.testiruum_id)        
