# -*- coding: utf-8 -*-
"Testikorralduse andmemudel"

import pickle
from cgi import FieldStorage
import mimetypes

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *

class Labivaatus(EntityHelper, Base):
    """Eksperthindaja poolne hindamise läbivaatus (vaide korral rühmaga hindamisel).
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    hindamine_id = Column(Integer, ForeignKey('hindamine.id'), index=True, nullable=False) # viide hindamise kirjele
    hindamine = relationship('Hindamine', foreign_keys=hindamine_id, back_populates='labivaatused')
    ekspert_labiviija_id = Column(Integer, ForeignKey('labiviija.id'), index=True, nullable=False) # viide vaidehindajale
    ekspert_labiviija = relationship('Labiviija', foreign_keys=ekspert_labiviija_id, back_populates='labivaatused')
    markus = Column(Text) # märkused 
    staatus = Column(Integer, sa.DefaultClause('0'), nullable=False) # olek: 0 - läbi vaatamata; 1 - läbi vaadatud
    _parent_key = 'hindamine_id'
    __table_args__ = (
        sa.UniqueConstraint('hindamine_id','ekspert_labiviija_id'),
        )

