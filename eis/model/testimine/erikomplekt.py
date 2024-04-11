"Testikorralduse andmemudel"

from eis.model.entityhelper import *
from eis.model.test import Komplekt

class Erikomplekt(EntityHelper, Base):
    """Komplekti seos erivajadustega sooritustega,
    mis näitab, milliste sooritajate jaoks komplekt on mõeldud
    """
    # loogilises mudelis: Erivajadused
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sooritus_id = Column(Integer, ForeignKey('sooritus.id'), index=True, nullable=False) # viide sooritusele (millega on määratud.sooritaja ja testiosa toimumisaeg, foreign_keys=sooritus_id)
    sooritus = relationship('Sooritus', back_populates='erikomplektid')
    komplekt_id = Column(Integer, ForeignKey('komplekt.id'), index=True) # viide komplektile
    #komplekt = relationship('Komplekt', foreign_keys=komplekt_id, back_populates='erikomplektid')
    komplekt = relationship('Komplekt', foreign_keys=komplekt_id)
    _parent_key = 'komplekt_id'

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        komplekt = self.komplekt or self.komplekt_id and Komplekt.get(self.komplekt_id)
        if komplekt:
            komplekt.logi('Erikomplekt %s %s' % (self.id, liik), vanad_andmed, uued_andmed, logitase)

