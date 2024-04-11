# -*- coding: utf-8 -*-
import hashlib

from eis.model.entityhelper import *
from eis.model.koht import Koht
from eis.model.klassifikaator import Klrida

log = logging.getLogger(__name__)


class Kasutajaajalugu(EntityHelper, Base):
    """Kasutajale paroolide andmise ajalugu
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='kasutajaajalood')
    
