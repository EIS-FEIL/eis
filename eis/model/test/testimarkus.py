"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import Opt
from eis.model.kasutaja import *
from eis.model.koht import *

class Testimarkus(EntityHelper, Base):
    """Testi märkused (eeltesti korral, korraldajate poolt)
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False) # viide testile
    test = relationship('Test', foreign_keys=test_id, back_populates='testimarkused')
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    aeg = Column(DateTime) # märkuse kirjutamise aeg
    sisu = Column(Text) # märkuse sisu
    teema = Column(String(100)) # märkuse teema
    ylem_id = Column(Integer, ForeignKey('testimarkus.id'), index=True) # viide ülemale märkusele, mida antud märkus kommenteerib
    ylem = relationship('Testimarkus', foreign_keys=ylem_id, remote_side=id, back_populates='alamad')
    alamad = relationship('Testimarkus', back_populates='ylem')
    _parent_key = 'test_id'
    
    def set_modifier(self):
        EntityHelper.set_modifier(self)
        self.aeg = datetime.now()

    def delete_subitems(self):    
        self.delete_subrecords(['alamad'])

    @property
    def alamate_arv(self):
        return sum([m.alamate_arv + 1 for m in self.alamad]) or 0

