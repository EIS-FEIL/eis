from eis.model.entityhelper import *
_ = usersession._

class Grupiylesanne(EntityHelper, Base):
    """Ülesannete kuulumine gruppidesse
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    ylesandegrupp_id = Column(Integer, ForeignKey('ylesandegrupp.id'), index=True, nullable=False) # viide ülesandegrupile
    ylesandegrupp = relationship('Ylesandegrupp', back_populates='grupiylesanded')
    valitudylesanne_id = Column(Integer, ForeignKey('valitudylesanne.id'), index=True, nullable=False) # viide testi valitud ülesandele
    valitudylesanne = relationship('Valitudylesanne', back_populates='grupiylesanded')
