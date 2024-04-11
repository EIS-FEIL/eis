"Ülesande andmemudel"

from eis.model.entityhelper import *

class Ylesandelogi(EntityHelper, Base):
    """Ülesande koostamise ajalugu
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    aeg = Column(DateTime, nullable=False) # logi aeg
    liik = Column(String(256)) # logitava olemi kirjeldus
    vanad_andmed = Column(Text) # vanad andmed
    uued_andmed = Column(Text) # uued andmed
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True, nullable=False) # viide ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='ylesandelogid')
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    _parent_key = 'ylesanne_id'
    
    def set_modifier(self):
        EntityHelper.set_modifier(self)
        self.aeg = datetime.now()

