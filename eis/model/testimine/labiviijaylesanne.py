"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Labiviijaylesanne(EntityHelper, Base):
    """Testimiskorrata testile määratud hindaja korral valitud ülesanded, mida hindaja võib hinnata
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    labiviija_id = Column(Integer, ForeignKey('labiviija.id'), index=True, nullable=False) # viide hindaja kirjele
    labiviija = relationship('Labiviija', foreign_keys=labiviija_id, back_populates='labiviijaylesanded')
    testiylesanne_id = Column(Integer, ForeignKey('testiylesanne.id'), index=True, nullable=False)
    testiylesanne = relationship('Testiylesanne', foreign_keys=testiylesanne_id)
    _parent_key = 'labiviija_id'
    __table_args__ = (
        sa.UniqueConstraint('labiviija_id', 'testiylesanne_id'),
        )

