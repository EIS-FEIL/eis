import hashlib

from eis.model.entityhelper import *
from eis.model.koht import Koht
from eis.model.klassifikaator import Klrida

log = logging.getLogger(__name__)

class Volitus(EntityHelper, Base):
    """Volitused teiste sooritajate tulemuste vaatamiseks
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    opilane_kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale, kelle tulemusi lubatakse vaadata
    opilane_kasutaja = relationship('Kasutaja', foreign_keys=opilane_kasutaja_id, back_populates='opilane_volitused')
    volitatu_kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale, kellel on luba vaadata teise kasutaja tulemusi
    volitatu_kasutaja = relationship('Kasutaja', foreign_keys=volitatu_kasutaja_id, back_populates='volitatu_volitused')
    andja_kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale, kes volituse andis
    andja_kasutaja = relationship('Kasutaja', foreign_keys=andja_kasutaja_id)
    tyhistaja_kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide kasutajale, kes volituse tühistas (kui on tühistatud, foreign_keys=tyhistaja_kasutaja_id)
    tyhistaja_kasutaja = relationship('Kasutaja', foreign_keys=tyhistaja_kasutaja_id)
    kehtib_alates = Column(DateTime, nullable=False) # volituse kehtimise algus
    kehtib_kuni = Column(DateTime, nullable=False) # volituse kehtimise lõpp
    tyhistatud = Column(DateTime) # volituse tühistamise aeg
    
    @classmethod
    def get_opilased_opt(cls, volitatu_kasutaja_id):
        from .kasutaja import Kasutaja
        kasutaja = Kasutaja.get(volitatu_kasutaja_id)
        li = [(kasutaja.id, kasutaja.nimi)] + \
            [(rcd.id, rcd.nimi) for rcd in kasutaja.get_opilased()]
        return li

    @property
    def kehtib_kuni_ui(self):
        """Andmebaasis on kuupäeval väärtus, mida kasutajale ei näidata.
        """
        if self.kehtib_kuni >= const.MAX_DATETIME:
            return None
        else:
            return self.kehtib_kuni

    @property
    def staatus(self):
        if self.kehtib_kuni > datetime.now() and \
                self.tyhistatud is None:
            return const.B_STAATUS_KEHTIV
        else:
            return const.B_STAATUS_KEHTETU

    @property
    def staatus_nimi(self):
        if self.staatus == const.B_STAATUS_KEHTIV:
            return usersession.get_opt().STR_KEHTIV
        else:
            return usersession.get_opt().STR_KEHTETU
