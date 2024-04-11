"Testi andmemudel"
from eis.model.entityhelper import *

class Testilogi(EntityHelper, Base):
    """Testi koostamise ajalugu
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    aeg = Column(DateTime, nullable=False) # logitava sündmuse aeg
    tyyp = Column(Integer) # tyyp olekuinfo eristamiseks: 1=TESTILOGI_TYYP_OLEK - olekuinfo, kuvatakse lisaks logile ka koostamise vormil; NULL - muu logi
    liik = Column(String(256)) # logitava olemi kirjeldus
    vanad_andmed = Column(Text) # vanad andmed
    uued_andmed = Column(Text) # uued andmed
    test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False) # viide testile        
    test = relationship('Test', foreign_keys=test_id, back_populates='testilogid')
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    _parent_key = 'test_id'

    TESTILOGI_TYYP_OLEK = 1
    
    def set_modifier(self):
        EntityHelper.set_modifier(self)
        self.aeg = datetime.now()

