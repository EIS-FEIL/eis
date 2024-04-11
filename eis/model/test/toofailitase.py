# -*- coding: utf-8 -*-
# $Id: toofailitase.py 1096 2017-01-11 06:17:05Z ahti $
"Tööde PDF failid koos hindamisjuhendiga koolidele jagamiseks"

from eis.model.entityhelper import *
  
class Toofailitase(EntityHelper, Base):
    """Õppekavad ja õppekavajärgsed haridustasemed, mida omaval koolil on võimalus faili alla laadida
    Võimalikud haridustasemed sõltuvad õppetasemest.
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    toofail_id = Column(Integer, ForeignKey('toofail.id'), index=True, nullable=False) # viide failile
    toofail = relationship('Toofail', foreign_keys=toofail_id, back_populates='toofailitasemed')
    kavatase_kood = Column(String(25), nullable=False) # õppekavajärgne haridustase, klassifikaator KAVATASE  
