"Testimise andmemudel"
from eis.model.entityhelper import *

class Sooritajalogi(EntityHelper, Base):
    """Sooritaja registreeringu ja tulemuste muudatuste logi
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    sooritaja_id = Column(Integer, ForeignKey('sooritaja.id'), index=True, nullable=False) # viide registreeringule
    sooritaja = relationship('Sooritaja', foreign_keys=sooritaja_id, back_populates='sooritajalogid')
    kursus_kood = Column(String(10)) # valitud kursus
    staatus = Column(Integer, nullable=False) # omistatud olek, vt Sooritaja.staatus
    eesnimi = Column(String(50)) # testi sooritamise ajal kehtinud eesnimi
    perenimi = Column(String(50)) # testi sooritamise ajal kehtinud perekonnanimi
    lang = Column(String(2)) # soorituskeel
    pallid = Column(Float) # testi eest saadud hindepallid, testi lõpptulemus pallides
    hinne = Column(Integer) # testi eest saadud hinne, vahemikus 1-5    
    keeletase_kood = Column(String(10)) # eksamiga hinnatud keeleoskuse tase
    tulemus_aeg = Column(DateTime) # tulemuse viimase muutmise aeg
    pohjus = Column(String(1024)) # oleku muutmise põhjus
    
    data_sig = Column(String(512)) # räsitavad andmed: isikukood, nimi, testi ID, õppeaine, tulemus pallides, tulemuse kuupäev (semikooloniga eraldatud)
    data_hash = Column(String(50)) # andmete SHA-256 räsi (base64)
    sig_status = Column(Integer) # allkirjastamise olek: 0=const.G_STAATUS_NONE - ei ole vaja allkirjastada; 1=const.G_STAATUS_UNSIGNED - ootab allkirja; 2=const.G_STAATUS_SIGNED - allkirjastatud; 3=const.G_STAATUS_OLD - aegunud andmed (olemas on uuem kirje); 4=const.G_STAATUS_ERROR - andmed ei vasta tegelikkusele
    err_msg = Column(String(256)) # tervikluse kontrolli veateade
    url = Column(String(200)) # andmeid muutnud tegevuse URL
    remote_addr = Column(String(60)) # muutja klient
    server_addr = Column(String(60)) # muutja server
    
    _parent_key = 'sooritaja_id'
    
    @property 
    def staatus_nimi(self):
        return usersession.get_opt().S_STAATUS.get(self.staatus)
