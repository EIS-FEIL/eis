# -*- coding: utf-8 -*-
# $Id: khstatistika.py 1096 2017-01-11 06:17:05Z ahti $
"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Khstatistika(EntityHelper, Base):
    """Üksikküsimuste eest antud punktide statistika.
    Mõeldud eeskätt nende küsimuste jaoks, mille vastuseid andmebaasis ei hoita.
    Erinevalt kvstatistika tabelist ei käi see statistika vastuste kaupa,
    vaid küsimuse kaupa (ühel küsimusel võib olla mitu vastust).
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kysimusestatistika_id = Column(Integer, ForeignKey('kysimusestatistika.id'), index=True, nullable=False) # viide küsimusele
    kysimusestatistika = relationship('Kysimusestatistika', foreign_keys=kysimusestatistika_id, back_populates='khstatistikad')
    vastuste_arv = Column(Integer, nullable=False) # antud vastuse andnute arv
    toorpunktid = Column(Float) # hindaja antud toorpunktid (ülesande skaala järgi)
    pallid = Column(Float) # hindepallid (testiülesande skaala järgi)
    nullipohj_kood = Column(String(10)) # null punkti andmise põhjus, klassifikaator NULLIPOHJ
