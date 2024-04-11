# -*- coding: utf-8 -*-
# $Id: hindamiskysimus.py 1096 2017-01-11 06:17:05Z ahti $
"Ülesande andmemudel"

from PIL import Image
import mimetypes
import re
from lxml import etree
import urllib.request, urllib.parse, urllib.error

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *

class Hindamiskysimus(EntityHelper, Base):
    """Hindajate poolt hindamisjuhile esitatud küsimused ja saadud vastused
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True, nullable=False) # viide ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='hindamiskysimused')
    kysimus = Column(Text, nullable=False) # küsitud küsimus
    kysija_kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide küsijale
    kysija_kasutaja = relationship('Kasutaja', foreign_keys=kysija_kasutaja_id)
    kysimisaeg = Column(DateTime, nullable=False) # küsimise aeg
    vastus = Column(Text) # hindamisjuhi vastus küsimusele
    vastaja_kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide vastajale
    vastaja_kasutaja = relationship('Kasutaja', foreign_keys=vastaja_kasutaja_id)
    vastamisaeg = Column(DateTime) # vastamise aeg
    avalik = Column(Boolean, sa.DefaultClause('1'), nullable=False) # kas on kõigile hindajatele nähtav küsimus
    _parent_key = 'ylesanne_id'

    def set_modifier(self):
        EntityHelper.set_modifier(self)
        self.kysimisaeg = datetime.now()
    
