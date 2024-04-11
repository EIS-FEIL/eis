# -*- coding: utf-8 -*-
# $Id: kysimusehindemarkus.py 1096 2017-01-11 06:17:05Z ahti $
"Testikorralduse andmemudel"

import pickle
from cgi import FieldStorage
import mimetypes

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *

class Kysimusehindemarkus(EntityHelper, Base):
    """Eksperthindaja märkus küsimuse hinde kohta (vaide korral hindamisel)
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kysimusehinne_id = Column(Integer, ForeignKey('kysimusehinne.id'), index=True, nullable=False) # viide ülesande küsimuse hindepallide kirjele, mille kohta märkus käib
    kysimusehinne = relationship('Kysimusehinne', foreign_keys=kysimusehinne_id, back_populates='kysimusehindemarkused')
    ekspert_labiviija_id = Column(Integer, ForeignKey('labiviija.id'), index=True, nullable=False) # viide eksperthindajale, kelle märkusega on tegu
    ekspert_labiviija = relationship('Labiviija', foreign_keys=ekspert_labiviija_id, back_populates='kysimusehindemarkused')
    markus = Column(Text) # märkuse tekst
    _parent_key = 'kysimusehinne_id'
    __table_args__ = (
        sa.UniqueConstraint('kysimusehinne_id','ekspert_labiviija_id'),
        )


