"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Sisuvaatamine(EntityHelper, Base):
    """Ülesande sisuploki lahendajale nähtavana kuvamise logi.
    Kasutusel tagasisidefunktsioonide bvcount(), bvtime() jaoks.
    """
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ylesandevastus_id = Column(Integer, ForeignKey('ylesandevastus.id'), index=True, nullable=False)
    ylesandevastus = relationship('Ylesandevastus', foreign_keys=ylesandevastus_id, back_populates='sisuvaatamised') # viide ülesande vastusele
    sisuplokk_id = Column(Integer, index=True, nullable=False) # viide sisuplokile
    #sisuplokk = relationship('Sisuplokk', foreign_keys=sisuplokk_id)
    algus = Column(DateTime, nullable=False) # ylesande brauseris laadimise aeg (brauseri aeg)
    lopp = Column(DateTime, nullable=False) # aeg, mil ülesandelt lahkuti või logi salvestati (brauseri aeg)
    nahtav_logi = Column(String(1000)) # nähtavuse logi, koosneb tekstidest [+-]SEK, kus + tähendab sisuploki kuvamist, - tähendab sisuploki peitmist ja SEK näitab, mitu sekundit peale algust kuvamine või peitmine toimus
    nahtav_kordi = Column(Integer) # nähtavaks muutmiste arv
    nahtav_aeg = Column(Integer) # nähtavana olnud sekundite arv 

class TempSisuvaatamine(object):
    "Andmebaasiväline pseudo-sooritus"
    sisuplokk_id = None
    algus = None
    lopp = None
    nahtav_logi = None
    nahtav_kordi = None
    nahtav_aeg = None
    
    def __init__(self, sisuplokk_id=None, algus=None):
        self.sisuplokk_id = sisuplokk_id
        self.algus = algus

