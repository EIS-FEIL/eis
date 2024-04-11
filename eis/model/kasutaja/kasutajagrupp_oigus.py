from eis.model.entityhelper import *
log = logging.getLogger(__name__)

from .kasutajagrupp import Kasutajagrupp
from .kasutajaoigus import Kasutajaoigus

class Kasutajagrupp_oigus(EntityHelper, Base):
    """Seos kasutajagruppide ja õiguste vahel
    """
    kasutajagrupp_id = Column(Integer, ForeignKey('kasutajagrupp.id'), index=True, nullable=False, primary_key=True) # viide kasutajagrupile
    kasutajagrupp = relationship('Kasutajagrupp', foreign_keys=kasutajagrupp_id, back_populates='kasutajagrupp_oigused')
    kasutajaoigus_id = Column(Integer, ForeignKey('kasutajaoigus.id'), index=True, nullable=False, primary_key=True) # viide kasutajaõigusele
    kasutajaoigus = relationship('Kasutajaoigus', foreign_keys=kasutajaoigus_id, back_populates='kasutajagrupp_oigused')
    nimi = Column(String(80), nullable=False) # õiguse nimi, päringute lihtsustamiseks dubleerib Kasutajaoigus.nimi
    grupp_tyyp = Column(Integer, nullable=False) # grupi tüüp, päringute lihtsustamiseks dubleerib Kasutajagrupp.tyyp
    grupp_staatus = Column(Integer, nullable=False) # grupi olek, päringute lihtsustamiseks dubleerib Kasutajagrupp.staatus
    bitimask = Column(Integer, sa.DefaultClause('0'), nullable=False) # õiguste bitimask (1 - loetelu, 2 - vaatamine, 4 - lisamine, 8 - muutmine, 16 - kustutamine)
    __table_args__ = (
        sa.UniqueConstraint('kasutajagrupp_id','kasutajaoigus_id'),
        )
    
    def set_modifier(self):
        EntityHelper.set_modifier(self)
        kasutajaoigus = self.kasutajaoigus or Kasutajaoigus.get(self.kasutajaoigus_id)
        kasutajagrupp = self.kasutajagrupp or Kasutajagrupp.get(self.kasutajagrupp_id)
        self.nimi = kasutajaoigus.nimi
        self.grupp_tyyp = kasutajagrupp.tyyp
        self.grupp_staatus = kasutajagrupp.staatus

    @classmethod
    def get_item(cls, **args):
        return cls.query.\
               filter_by(kasutajagrupp_id=args['kasutajagrupp_id']).\
               filter_by(kasutajaoigus_id=args['kasutajaoigus_id']).\
               first()
            
