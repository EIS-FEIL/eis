"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Loendur(EntityHelper, Base):
    """Tabamuste loenduri väärtus
    """   
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ylesandevastus_id = Column(Integer, ForeignKey('ylesandevastus.id'), index=True, nullable=False)
    ylesandevastus = relationship('Ylesandevastus', foreign_keys=ylesandevastus_id, back_populates='loendurid') # viide ülesande vastusele
    tahis = Column(String(25), nullable=False) # tabamuste loenduri tähis
    tabamuste_arv = Column(Integer) # antud tähisega hindamismaatriksis tabatud ridade arv
