# -*- coding: utf-8 -*-
# $Id: aspektihindemarkus.py 1096 2017-01-11 06:17:05Z ahti $
"Testikorralduse andmemudel"

import pickle
from cgi import FieldStorage
import mimetypes

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *

class Aspektihindemarkus(EntityHelper, Base):
    """Eksperthindaja märkus aspekti hinde kohta (vaide korral hindamisel)
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    aspektihinne_id = Column(Integer, ForeignKey('aspektihinne.id'), index=True, nullable=False) # viide ülesande aspekti hindepallide kirjele, mille kohta märkus käib
    aspektihinne = relationship('Aspektihinne', foreign_keys=aspektihinne_id, back_populates='aspektihindemarkused')
    ekspert_labiviija_id = Column(Integer, ForeignKey('labiviija.id'), index=True, nullable=False) # viide eksperthindajale, kelle märkusega on tegu
    ekspert_labiviija = relationship('Labiviija', foreign_keys=ekspert_labiviija_id, back_populates='aspektihindemarkused')
    markus = Column(Text) # märkuse tekst
    _parent_key = 'aspektihinne_id'
    __table_args__ = (
        sa.UniqueConstraint('aspektihinne_id','ekspert_labiviija_id'),
        )


