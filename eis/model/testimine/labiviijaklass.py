# -*- coding: utf-8 -*-
"Testikorralduse andmemudel"

import pickle
from cgi import FieldStorage
import mimetypes

from eis.model.entityhelper import *

class Labiviijaklass(EntityHelper, Base):
    """Millise klassi õpilasi hindaja hindab (kasutusel kooli poolt määratud hindaja korral)
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    labiviija_id = Column(Integer, ForeignKey('labiviija.id'), index=True, nullable=False) # viide hindaja kirjele
    labiviija = relationship('Labiviija', foreign_keys=labiviija_id, back_populates='labiviijaklassid')
    klass = Column(String(10)) # klass
    paralleel = Column(String(40)) # paralleel
    _parent_key = 'labiviija_id'
    __table_args__ = (
        sa.UniqueConstraint('labiviija_id', 'klass', 'paralleel'),
        )

