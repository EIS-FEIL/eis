"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Helivastus(EntityHelper, Base):
    """Helifaili seosed sooritustega ja ülesannetega
    """
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    helivastusfail_id = Column(Integer, ForeignKey('helivastusfail.id'), index=True, nullable=False) # viide faili kirjele
    helivastusfail = relationship('Helivastusfail', foreign_keys=helivastusfail_id, back_populates='helivastused')
    sooritus_id = Column(Integer, ForeignKey('sooritus.id'), index=True, nullable=False) # viide sooritusele
    sooritus = relationship('Sooritus', foreign_keys=sooritus_id, back_populates='helivastused')
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True) # viide ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id)
    testiylesanne_id = Column(Integer, ForeignKey('testiylesanne.id'), index=True) # viide testiülesandele
    testiylesanne = relationship('Testiylesanne', foreign_keys=testiylesanne_id)

    @classmethod
    def get_hvf_by_sooritus(cls, sooritused_id, ty_id):
        q = (Session.query(Helivastus.helivastusfail_id)
             .distinct()
             .filter(Helivastus.sooritus_id.in_(sooritused_id))
             .filter(Helivastus.testiylesanne_id==ty_id)
             .order_by(Helivastus.helivastusfail_id)
             )
        return q.all()

