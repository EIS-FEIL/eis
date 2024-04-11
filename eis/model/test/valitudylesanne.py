"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import Opt
from eis.model.kasutaja import *
from eis.model.koht import *

from .komplekt import Komplekt
from .testiosa import Testiosa

class Valitudylesanne(EntityHelper, Base):
    """Antud ülesandekomplektis testiülesandesse valitud ülesanne
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    seq = Column(Integer) # valikülesande järjekorranumber (kui on valikülesanne)
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True) # viide valitud ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='valitudylesanded')
    testiylesanne_id = Column(Integer, ForeignKey('testiylesanne.id'), index=True, nullable=False) # viide testiülesandele
    testiylesanne = relationship('Testiylesanne', foreign_keys=testiylesanne_id, back_populates='valitudylesanded')
    koefitsient = Column(Float) # testiülesande max pallide ja ülesande max pallide suhe, millega hindaja antud toorpunkte korrutades saadakse hindepallid
    komplekt_id = Column(Integer, ForeignKey('komplekt.id'), index=True, nullable=False) # viide komplektile
    komplekt = relationship('Komplekt', foreign_keys=komplekt_id, back_populates='valitudylesanded')
    test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False) # viide testile (testiylesanne.testiosa.test dubleerimine päringute lihtsutamiseks)
    test = relationship('Test', foreign_keys=test_id, back_populates='valitudylesanded') 
    hindamiskogum_id = Column(Integer, ForeignKey('hindamiskogum.id'), index=True) # viide hindamiskogumile, millesse testiülesanne kuulub (ainult lõdva struktuuriga testiosa korral, muidu on seos hindamiskogumiga testiülesande kirjes)
    hindamiskogum = relationship('Hindamiskogum', foreign_keys=hindamiskogum_id, back_populates='valitudylesanded') 
    selgitus = Column(Text) # selgitav tekst lahendajale (jagatud töö korral)
    #ylesandevastused = relationship('Ylesandevastus', back_populates='valitudylesanne')
    ylesandehinded = relationship('Ylesandehinne', back_populates='valitudylesanne')
    ylesandestatistikad = relationship('Ylesandestatistika', back_populates='valitudylesanne')
    grupiylesanded = relationship('Grupiylesanne', back_populates='valitudylesanne')
    trans = relationship('T_Valitudylesanne', cascade='all')
    
    __table_args__ = (
        sa.UniqueConstraint('testiylesanne_id', 'komplekt_id', 'seq'),
        )

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        komplekt = self.komplekt or self.komplekt_id and Komplekt.get(self.komplekt_id)
        if komplekt:
            komplekt.logi('Valitud ülesanne %s (%s) %s' % (self.id, self.testiylesanne_id, liik), vanad_andmed, uued_andmed, logitase)

    def set_modifier(self):
        EntityHelper.set_modifier(self)
        self.set_test()

    def set_test(self):
        if not self.test_id:
            ty = self.testiylesanne or Testiylesanne.get(self.testiylesanne_id)
            testiosa = ty.testiosa or Testiosa.get(ty.testiosa_id)
            self.test_id = testiosa.test_id

    def update_koefitsient(self, ty):
        y = self.ylesanne
        if y is not None and ty.max_pallid is None:
            self.koefitsient = 1
        elif y is not None and y.max_pallid and ty.max_pallid:
            self.koefitsient = ty.max_pallid / y.max_pallid
            if ty.hindamiskogum and ty.hindamiskogum.arvutus_kood == const.ARVUTUS_SUMMA:
                self.koefitsient *= 0.5
        else:
            self.koefitsient = 0

    @property
    def on_aspektid(self):
        if self.ylesanne:
            return len(self.ylesanne.hindamisaspektid) > 0

    def delete_subitems(self):    
        self.delete_subrecords(['ylesandestatistikad',
                                #'ylesandevastused',
                                'grupiylesanded',
                                ])

