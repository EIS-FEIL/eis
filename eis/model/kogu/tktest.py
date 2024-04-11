from eis.model.entityhelper import *

class Tktest(EntityHelper, Base):
    """Töökogumikku kuuluv test
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    seq = Column(Integer) # osasisene järjekorranumber
    tkosa_id = Column(Integer, ForeignKey('tkosa.id'), index=True, nullable=False) # viide töökogumiku osale
    tkosa = relationship('Tkosa', foreign_keys=tkosa_id, back_populates='tktestid')
    test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False) # viide kogusse kuuluvale testile
    test = relationship('Test', foreign_keys=test_id) # viide testile 
    ylesandekogu_id = Column(Integer, ForeignKey('ylesandekogu.id'), index=True, nullable=True) # viide kogule, millest ülesanne on võetud
    ylesandekogu = relationship('Ylesandekogu', foreign_keys=ylesandekogu_id, back_populates='tktestid')
    _parent_key = 'kogu_id'


