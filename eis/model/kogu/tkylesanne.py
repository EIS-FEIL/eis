from eis.model.entityhelper import *

class Tkylesanne(EntityHelper, Base):
    """Töökogumikku kuuluv ülesanne
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    seq = Column(Integer) # osasisene järjekorranumber
    tkosa_id = Column(Integer, ForeignKey('tkosa.id'), index=True, nullable=False) # viide töökogumiku osale
    tkosa = relationship('Tkosa', foreign_keys=tkosa_id, back_populates='tkylesanded')
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True, nullable=False) # viide kogusse kuuluvale ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id)
    ylesandekogu_id = Column(Integer, ForeignKey('ylesandekogu.id'), index=True, nullable=True) # viide kogule, millest ülesanne on võetud
    ylesandekogu = relationship('Ylesandekogu', foreign_keys=ylesandekogu_id, back_populates='tkylesanded')
    _parent_key = 'tkosa_id'


