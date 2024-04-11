"Testi andmemudel"
from eis.model.entityhelper import *

class Toimumisaeg_komplekt(Base):
    __tablename__ = 'toimumisaeg_komplekt'
    toimumisaeg_id = Column(Integer, ForeignKey('toimumisaeg.id'), index=True, primary_key=True)
    komplekt_id = Column(Integer, ForeignKey('komplekt.id'), index=True, primary_key=True)
