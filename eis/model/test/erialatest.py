"Testi andmemudel"
from eis.model.entityhelper import *

from .komplekt import Komplekt

class Erialatest(EntityHelper, Base):
    """Testi ülesandekomplekti erivajaduste erisused alatestide kaupa
    """
        
    id = Column(Integer, primary_key=True, autoincrement=True)
    lisaaeg = Column(Float) # testi sooritamiseks antav lisaaeg sekundites, lisandub testiosa piirajale
    dif_hindamine = Column(Boolean) # kas on diferentseeritud hindamine
    komplekt_id = Column(Integer, ForeignKey('komplekt.id'), index=True, nullable=False) # viide ülesandekomplektile
    komplekt = relationship('Komplekt', foreign_keys=komplekt_id, back_populates='erialatestid')
    alatest_id = Column(Integer, ForeignKey('alatest.id'), index=True, nullable=False) # viide alatestile
    alatest = relationship('Alatest', foreign_keys=alatest_id, back_populates='erialatestid')
    _parent_key = 'komplekt_id'

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        komplekt = self.komplekt or self.komplekt_id and Komplekt.get(self.komplekt_id)
        if komplekt:
            komplekt.logi('Erialatest %s (%s) %s' % (self.id, self.alatest_id, liik), vanad_andmed, uued_andmed, logitase)

