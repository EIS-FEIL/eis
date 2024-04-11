# -*- coding: utf-8 -*-
# $Id: kasutajapiirkond.py 1096 2017-01-11 06:17:05Z ahti $

import hashlib

from eis.model.entityhelper import *
from eis.model.koht import Koht
from eis.model.klassifikaator import Klrida

log = logging.getLogger(__name__)

class Kasutajapiirkond(EntityHelper, Base):
    """Piirkonnad, milles saab kasutajat testide läbiviimises rakendada
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='kasutajapiirkonnad')
    piirkond_id = Column(Integer, ForeignKey('piirkond.id'), index=True, nullable=False) # viide piirkonnale
    piirkond = relationship('Piirkond', back_populates='kasutajapiirkonnad')

    @classmethod
    def give(cls, kasutaja, piirkond):
        "Kui isik ei ole antud piirkonnas, siis lisame talle selle piirkonna"
        if piirkond:
            piirkonnad_id = piirkond.get_ylemad_id()            
            kasutaja_id = kasutaja.id
            rcd = None
            if kasutaja_id:
                q = cls.query.\
                    filter(cls.kasutaja_id==kasutaja_id).\
                    filter(cls.piirkond_id.in_(piirkonnad_id))
                rcd = q.first()
            if rcd is None:
                # kui ei ole, siis lisame isikule piirkonna
                rcd = cls(kasutaja=kasutaja,
                          piirkond_id=piirkond.id)
