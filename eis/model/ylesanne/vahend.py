"Ülesande andmemudel"

from eis.model.entityhelper import *
from .abivahend import Abivahend

class Vahend(EntityHelper, Base):
    """Ülesande lahendajale lubatud abivahendid
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    vahend_kood = Column(String(10)) # abivahendi kood tabelis Abivahend
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True, nullable=False) # viide ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='vahendid')
    _parent_key = 'ylesanne_id'
    __table_args__ = (
        sa.UniqueConstraint('ylesanne_id','vahend_kood'),
        )

    @property
    def abivahend(self):
        return Abivahend.get_by_kood(self.vahend_kood)
