import mimetypes
from eis.model.entityhelper import *
from .sooritajakiri import Sooritajakiri
log = logging.getLogger(__name__)

class Kiri(EntityHelper, Base):
    """Välja saadetud kirjad (teated)
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    saatja_kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide kasutajale, kes algatas saatmise
    saatja_kasutaja = relationship('Kasutaja', foreign_keys=saatja_kasutaja_id)
    tyyp = Column(String(25), nullable=False) # kirja tüüp
    teema = Column(String(256)) # kirja teema
    sisu = Column(Text) # kirja sisu (võib puududa paberkirja korral)
    filename = Column(String(256)) # manuse failinimi
    filedata = Column(LargeBinary) # manuse faili sisu
    sisu_url = Column(String(256)) # teatega kaasa saadetud URL (StateOS)
    teatekanal = Column(Integer, nullable=False) # kirja saatmise viis: 1=const.TEATEKANAL_EPOST - e-posti teel; 2=const.TEATEKANAL_POST - posti teel; 3=const.TEATEKANAL_KALENDER - eesti.ee teavituskalendri kaudu; 4=const.TEATEKANAL_STATEOS - StateOS kaudu (kuni 31.03.2023); 5=const.TEATEKANAL_EIS - ainult EISis
    kirjasaajad = relationship('Kirjasaaja', back_populates='kiri')
    sooritajakirjad = relationship('Sooritajakiri', back_populates='kiri')
    labiviijakirjad = relationship('Labiviijakiri', back_populates='kiri')
    
    TYYP_REGAMISTEADE = 'regteade'
    TYYP_TYHISTUSTEADE = 'tyhteade'
    TYYP_MEELDETULETUS = 'meeldetuletus'
    TYYP_SOORITUSKOHATEADE = 'kohateade'
    TYYP_TULEMUS = 'tulemus'
    TYYP_VAIDEMENETLUS = 'vaidemenetlus'
    TYYP_VAIDEETTEPANEK = 'vaideettepanek'
    TYYP_VAIDEOTSUS_KORRALDAJALE = 'vaideotsuskorraldajale'
    TYYP_VAIDEOTSUS_SOORITAJALE = 'vaideotsussooritajale'
    TYYP_LABIVIIJA_MAARAMINE = 'labiviijamaaramine'    
    TYYP_LABIVIIJA_TEADE = 'labiviijateade'
    TYYP_LABIVIIJA_MEELDE = 'labiviijameeldetuletus'
    TYYP_LABIVIIJA_TASU = 'labiviijatasu'
    TYYP_LABIVIIJA_LEPING = 'labiviijaleping'
    TYYP_KOOL_VALIM = 'koolvalim'
    TYYP_KOOL_TULEMUS = 'kooltulemus'
    TYYP_MUU = 'muu'
    TYYP_SKANN_LAADITUD = 'skann_laaditud'
    TYYP_KORRALDAMATA = 'korraldamata'
    TYYP_HINDAMATA = 'hindamata'
    TYYP_PLANK_A1 = 'planka1' # plankide aruande tähtaja teade 11.okt
    TYYP_PLANK_A2 = 'planka2' # plankide aruande meeldetuletus peale 1.nov
    TYYP_MUUSK = 'muusk'
    
    opt_sooritajateated = [(TYYP_REGAMISTEADE, 'Registreerimisteade'),
                           (TYYP_TYHISTUSTEADE, 'Registreerimise tühistamise teade'),
                           (TYYP_MEELDETULETUS, 'Tasumise meeldetuletus'),
                           (TYYP_SOORITUSKOHATEADE, 'Soorituskohateade'),
                           (TYYP_TULEMUS, 'Tulemuste teavitus'),
                           (TYYP_SKANN_LAADITUD, 'Skannitud testitöö teavitus'),
                           (TYYP_MUU, 'Muu teade'),
                           ]
    opt_labiviijateated = [(TYYP_LABIVIIJA_MAARAMINE, 'Läbiviija määramise teade'),
                           (TYYP_LABIVIIJA_TEADE, 'Läbiviija teade'),
                           (TYYP_LABIVIIJA_MEELDE, 'Läbiviija meeldetuletus'),
                           (TYYP_LABIVIIJA_TASU, 'Läbiviija tasu teade'),
                           (TYYP_LABIVIIJA_LEPING, 'Lepingu sõlmimise teavitus'),
                           (TYYP_KOOL_TULEMUS, 'Tulemuste avaldamise teavitus'),
                           (TYYP_HINDAMATA, 'Hindamise meeldetuletus'),
                           (TYYP_MUU, 'Muu teade'),
                           ]
    opt_ametnikuteated = [(TYYP_VAIDEMENETLUS, 'Vaide menetlussevõtmise teade hindamisjuhile'),
                          (TYYP_VAIDEETTEPANEK, 'Vaide ettepanek komisjonile'),
                          (TYYP_VAIDEOTSUS_KORRALDAJALE, 'Vaideotsuse teade korraldajale'),
                          (TYYP_KORRALDAMATA, 'Korraldamise meeldetuletus koolile'),
                          (TYYP_KOOL_VALIM, 'Valimisse kuulumise teade koolile'),
                          (TYYP_PLANK_A1, 'Plankide aruande teade'),
                          (TYYP_PLANK_A2, 'Plankide aruande meeldetuletus'),
                          (TYYP_MUUSK, 'Muu soorituskoha teade'),
                          ]

    @property
    def has_file(self):
        return self.filedata is not None
    
    @property
    def fileext(self):
        if self.filename:
            return self.filename.split('.')[-1]

    @property
    def mimetype(self):
        if self.filename:
            (mimetype, encoding) = mimetypes.guess_type(self.filename)        
            return mimetype

    @property
    def teatekanal_nimi(self):
        return usersession.get_opt().TEATEKANAL.get(self.teatekanal)

    @property
    def tyyp_nimi(self):
        return self.get_tyyp_nimi(self.tyyp)

    @classmethod    
    def get_tyyp_nimi(cls, tyyp):
        for t, nimetus in cls.opt_sooritajateated + cls.opt_labiviijateated + cls.opt_ametnikuteated:
            if tyyp == t:
                return nimetus
