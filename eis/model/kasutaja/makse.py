# -*- coding: utf-8 -*-
from eis.model.entityhelper import *

log = logging.getLogger(__name__)

class Makse(EntityHelper, Base):
    """Pangalingi maksed
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    stamp = Column(String(20), nullable=False) # päringu ID, VK_STAMP
    msg = Column(String(70), nullable=False) # mille eest maksti, VK_MSG
    amount = Column(Float, nullable=False) # kui palju maksti, VK_AMOUNT
    saadud = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas pangast on vastus saadud
