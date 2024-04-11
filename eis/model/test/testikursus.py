# -*- coding: utf-8 -*-
"Testi andmemudel"
from eis.model.entityhelper import *

class Testikursus(EntityHelper, Base):
    """Tunnistusele märgitav testi õppeaine sõltuvalt valitud kursusest 
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False) # viide testile
    test = relationship('Test', foreign_keys=test_id, back_populates='testikursused')
    kursus_kood = Column(String(10)) # lai või kitsas (matemaatika korral), klassifikaator KURSUS
    aine_kood = Column(String(10), nullable=False) # õppeaine, klassifikaator AINE (dubleerib test.aine_kood)
    tunnaine_kood = Column(String(10)) # õppeaine nimetus tunnistusel, klassifikaator TUNNAINE
    max_pallid = Column(Float) # max hindepallide arv antud kursuse korral
    _parent_key = 'test_id'    
    __table_args__ = (
        sa.UniqueConstraint('test_id','kursus_kood'),
        )
