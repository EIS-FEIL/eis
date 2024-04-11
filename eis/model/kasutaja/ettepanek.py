# -*- coding: utf-8 -*-
# $Id: ettepanek.py 890 2016-09-29 13:46:02Z ahti $

import mimetypes
from eis.model.entityhelper import *

log = logging.getLogger(__name__)

class Ettepanek(EntityHelper, Base):
    """Avaliku vaate kasutajate küsimused ja ettepanekud
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide kasutajale, kes algatas saatmise
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id) 
    saatja = Column(String(255), nullable=False) # saatja nimi
    epost = Column(String(255), nullable=False) # e-posti aadress
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True) # kasutaja koht
    koht = relationship('Koht', foreign_keys=koht_id) 
    teema = Column(String(255), nullable=False) # teema
    sisu = Column(Text, nullable=False) # sisu
    url = Column(String(150)) # tegevuse URL, kust tagasisidet anti
    ootan_vastust = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas pöörduja ootab vastuskirja
    on_vastatud = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas on vastatud
    vastus = Column(Text) # vastuse sisu
