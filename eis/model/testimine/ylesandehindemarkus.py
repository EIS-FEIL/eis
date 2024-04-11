# -*- coding: utf-8 -*-
# $Id: ylesandehindemarkus.py 1096 2017-01-11 06:17:05Z ahti $
"Testikorralduse andmemudel"

import pickle
from cgi import FieldStorage
import mimetypes

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *

class Ylesandehindemarkus(EntityHelper, Base):
    """Eksperthindaja märkus ülesande vastuse kohta (vaide korral hindamisel)
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ylesandehinne_id = Column(Integer, ForeignKey('ylesandehinne.id'), index=True, nullable=False) # viide ülesande hindepallide kirjele, mille kohta märkus käib
    ylesandehinne = relationship('Ylesandehinne', foreign_keys=ylesandehinne_id, back_populates='ylesandehindemarkused')
    ekspert_labiviija_id = Column(Integer, ForeignKey('labiviija.id'), index=True, nullable=False) # viide eksperthindajale, kelle märkusega on tegu
    ekspert_labiviija = relationship('Labiviija', foreign_keys=ekspert_labiviija_id, back_populates='ylesandehindemarkused')
    markus = Column(Text) # märkuse tekst
    _parent_key = 'kysimusehinne_id'
    __table_args__ = (
        sa.UniqueConstraint('ylesandehinne_id','ekspert_labiviija_id'),
        )

