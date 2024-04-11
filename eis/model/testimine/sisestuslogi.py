# -*- coding: utf-8 -*-
# $Id: sisestuslogi.py 1096 2017-01-11 06:17:05Z ahti $
"Testikorralduse andmemudel"

import pickle
from cgi import FieldStorage
import mimetypes

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *

class Sisestuslogi(EntityHelper, Base):
    """Sisestamise muudatused
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # sisestaja kasutaja
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    hindamine_id = Column(Integer, ForeignKey('hindamine.id'), index=True, nullable=False) # viide hindamise kirjele
    hindamine = relationship('Hindamine', foreign_keys=hindamine_id, back_populates='sisestuslogid')
    ylesandehinne_id = Column(Integer, ForeignKey('ylesandehinne.id'), index=True) # hindepallide muutmise korral viide hinde kirjele
    ylesandehinne = relationship('Ylesandehinne', foreign_keys=ylesandehinne_id, back_populates='sisestuslogid')
    kysimusehinne_id = Column(Integer, ForeignKey('kysimusehinne.id'), index=True) # hindepallide muutmise korral viide küsimuse hinde kirjele
    kysimusehinne = relationship('Kysimusehinne', foreign_keys=kysimusehinne_id, back_populates='sisestuslogid')
    aspektihinne_id = Column(Integer, ForeignKey('aspektihinne.id'), index=True) # aspekti hindepallide muutmise korral viide aspektihinde kirjele
    aspektihinne = relationship('Aspektihinne', foreign_keys=aspektihinne_id, back_populates='sisestuslogid')
    liik = Column(Integer, nullable=False) # mida muudeti: 1 - hindepallid; 2 - komplekt; 3 - hindaja; 4 - intervjueerija
    vana = Column(String(50)) # uus väärtus
    uus = Column(String(50)) # vana väärtus
    aeg = Column(DateTime) # andmete muutmise aeg
    _parent_key = 'hindamine_id'

    LIIK_PALLID = 1
    LIIK_KOMPLEKT = 2
    LIIK_HINDAJA = 3
    LIIK_INTERVJUEERIJA = 4   

    @property
    def liik_nimi(self):
        LIIK = {self.LIIK_PALLID: 'Hindepallid',
                self.LIIK_KOMPLEKT: 'Komplekt',
                self.LIIK_HINDAJA: 'Hindaja',
                self.LIIK_INTERVJUEERIJA: 'Intervjueerija',
                }
        return LIIK.get(self.liik)

    def set_modifier(self):
        EntityHelper.set_modifier(self)
        self.aeg = datetime.now()
