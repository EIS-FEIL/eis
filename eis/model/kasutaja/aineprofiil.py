# -*- coding: utf-8 -*-
# $Id: aineprofiil.py 1096 2017-01-11 06:17:05Z ahti $

import hashlib

from eis.model.entityhelper import *

from eis.model.koht import Koht
from eis.model.klassifikaator import Klrida

log = logging.getLogger(__name__)

class Aineprofiil(EntityHelper, Base):
    """Kasutaja konkreetses aines testi läbiviijana rakendamise profiil
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='aineprofiilid')
    aine_kood = Column(String(10)) # viide õppeainele, klassifikaator AINE
    keeletase_kood = Column(String(10)) # keeleoskuse tase, klassifikaator KEELETASE (riigikeele aine korral)
    kasutajagrupp_id = Column(Integer, ForeignKey('kasutajagrupp.id'), index=True, nullable=False) # viide kasutajagrupile: 29=const.GRUPP_HINDAJA_S - suuline hindaja; 30=const.GRUPP_HINDAJA_K - kirjalik hindaja; 36=const.GRUPP_INTERVJUU - intervjueerija; 38=const.GRUPP_KOMISJON - eksamikomisjoni liige (SE ja TE); 46=const.GRUPP_KOMISJON_ESIMEES - eksamikomisjoni esimees (SE ja TE, foreign_keys=kasutajagrupp_id); 47=const.GRUPP_KONSULTANT - konsultant
    kasutajagrupp = relationship('Kasutajagrupp', foreign_keys=kasutajagrupp_id)
    rangus = Column(Float) # rangus
    halve = Column(Float) # ranguse standardhälve
    koolitusaeg = Column(Date) # koolituse kuupäev
    kaskkirikpv = Column(Date) # läbiviija käskkirja lisamise kuupäev
