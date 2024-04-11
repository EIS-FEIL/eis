import pickle
from .entityhelper import *
from .avaleheinfologi import Avaleheinfologi
from eis.model.klassifikaator import CacheObj
log = logging.getLogger(__name__)
_ = usersession._

# erakorralise info puhver (30 sek)
ai_cache = CacheObj(0,30)

class Avaleheinfo(EntityHelper, Base):
    """Olulise info teated avalehel kuvamiseks
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    tyyp = Column(Integer, nullable=False) # teate tüüp: 1 - hoiatus (punane); 2 - tulemus (roheline); 3 - teavitus/info (sinine)
    pealkiri = Column(String(100), nullable=False) # teate pealkiri
    sisu = Column(Text, nullable=False) # teate sisu
    lisasisu = Column(Text) # rohkem infot
    kellele = Column(String(10), nullable=False) # kellele kuvatakse (komaga eraldatud): X - kõigile; J - sooritajatele; P - õpetajatele; Ox - kõigile õpilastele; O9 - 9. kl õpilastele; M - soorituskoha admin
    alates = Column(Date, nullable=False) # kuvamise alguse kuupäev
    kuni = Column(Date, nullable=False) # kuvamise lõpu kuupäev
    
    # välja tyyp väärtused
    TYYP_HOIATUS = 1 # hoiatus (punane)
    TYYP_TULEMUS = 2 # tulemus (roheline)
    TYYP_INFO = 3 # teavitus/info (sinine)
    TYYP_EMERGENCY = 0 # erakorraline teadaanne (punane teade päises)

    ID_EMERGENCY = 0 # erakorralisele teatele reserveeritud ID
    
    # välja kellele väärtused
    KELLELE_X = 'X'
    KELLELE_SOORITAJA = 'J'
    KELLELE_OPILANE = 'Ox'
    KELLELE_OPILANE9 = 'O9'
    KELLELE_PEDAGOOG = 'P'
    KELLELE_ADMIN = 'M'

    @property
    def tyyp_nimi(self):
        if self.tyyp == Avaleheinfo.TYYP_EMERGENCY:
            return _("Erakorraline teade")
        for value, title in Avaleheinfo.opt_tyyp():
            if value == self.tyyp:
                return title

    @classmethod
    def opt_tyyp(cls):
        return [(Avaleheinfo.TYYP_HOIATUS, _("Hoiatus (punane)")),
                (Avaleheinfo.TYYP_TULEMUS, _("Tulemus (roheline)")),
                (Avaleheinfo.TYYP_INFO, _("Teavitus/info (sinine)")),
                ]

    @classmethod
    def opt_kellele(cls):
        return [(Avaleheinfo.KELLELE_X, _("Kõigile")),
                (Avaleheinfo.KELLELE_SOORITAJA, _("Sooritaja")),
                (Avaleheinfo.KELLELE_OPILANE, _("Õpilane")),
                (Avaleheinfo.KELLELE_OPILANE9, _("Õpilane (9. kl)")),
                (Avaleheinfo.KELLELE_PEDAGOOG, _("Pedagoog")),
                (Avaleheinfo.KELLELE_ADMIN, _("Koolijuht / soorituskoha admin")),
                ]
    
    @property
    def kuni_ui(self):
        """Andmebaasis on kuupäeval väärtus, mida kasutajale ei näidata.
        """
        if not self.kuni or self.kuni >= const.MAX_DATE:
            return None
        else:
            return self.kuni

    logging = True
    logging_type1 = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        "Muudatuste logimine"
        if self.id is None:
            return
        data = self.pack_row()
        logi = Avaleheinfologi(avaleheinfo_id=self.id,
                               kasutaja_id=usersession.get_user().id,
                               liik=liik,
                               data=pickle.dumps(data))
        
    @classmethod
    def get_emergency(cls, last_m):
        "Erakorralise teate lugemine. Andmebaasi säästmiseks hoitakse puhvris mõnda aega"
        key = 'EMERGENCY'
        value = ai_cache.get(key)
        if value and last_m and (last_m > value[0]):
            # puhvris on teade olemas, aga sessioon teab uuemast teatest
            value = None
        if value is None:
            # puhver tyhi või aegunud
            sisu = modified = None
            q = (Session.query(Avaleheinfo.modified, Avaleheinfo.sisu, Avaleheinfo.kuni)
                 .filter(Avaleheinfo.id==cls.ID_EMERGENCY))
            for r in q.all():
                modified, sisu, kuni = r
                if kuni < date.today():
                    # teade pole aktiivne
                    sisu = None
                modified = str(modified.timestamp())
            value = ai_cache[key] = modified, sisu
        return value
            
