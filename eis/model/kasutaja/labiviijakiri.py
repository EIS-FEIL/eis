from eis.model.entityhelper import *

log = logging.getLogger(__name__)

class Labiviijakiri(EntityHelper, Base):
    """Läbiviija kirje seos välja saadetud kirjadega
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    kiri_id = Column(Integer, ForeignKey('kiri.id'), index=True, nullable=False) # viide kirjale
    kiri = relationship('Kiri', foreign_keys=kiri_id, back_populates='labiviijakirjad')
    labiviija_id = Column(Integer, ForeignKey('labiviija.id'), index=True) # viide läbiviija kirjele
    labiviija = relationship('Labiviija', foreign_keys=labiviija_id, back_populates='labiviijakirjad')
