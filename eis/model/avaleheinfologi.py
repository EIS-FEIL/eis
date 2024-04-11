"Avalehe teadete muudatused"
import pickle
from eis.model.entityhelper import *

class Avaleheinfologi(EntityHelper, Base):
    """Avalehe teadete muudatused
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    aeg = Column(DateTime, nullable=False) # logi aeg
    avaleheinfo_id = Column(Integer, nullable=False) # viide teate kirjele
    liik = Column(String(1), nullable=False) # tegevuse liik: U - muutmine; I - lisamine; D - kustutamine
    data = Column(LargeBinary) # andmed (pickle)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    
    def set_modifier(self):
        EntityHelper.set_modifier(self)
        self.aeg = datetime.now()

    def as_obj(self, c):
        d=self.data
        data = pickle.loads(self.data)
        obj = c.new_item.create_from_dict(data)
        if obj and obj.kuni and obj.kuni >= const.MAX_DATE:
            obj.kuni_ui = None
        else:
            obj.kuni_ui = obj.kuni
        return obj
        
