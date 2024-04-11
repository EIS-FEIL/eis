# -*- coding: utf-8 -*-
"Õpilaste rühm"

from eis.model.entityhelper import *
from eis.model.kasutaja import *

class Opperyhm(EntityHelper, Base):
    """Õpilaste rühm. Õpetaja jagab ise oma õpilased rühmadesse.
    Õpetaja kasutab rühmi tööde jagamisel.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nimi = Column(String(100), nullable=False) # rühma nimetus
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # õpetaja, kelle rühm see on
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='opperyhmad')
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True) # õppeasutus
    koht = relationship('Koht', foreign_keys=koht_id)
    opperyhmaliikmed = relationship('Opperyhmaliige', order_by='Opperyhmaliige.id', back_populates='opperyhm')
    #nimekirjad = relationship('Nimekiri', order_by='Nimekiri.id')
    
    def delete_subitems(self):    
        self.delete_subrecords(['opperyhmaliikmed',
                                ])

    def has_permission(self, permission, perm_bit, user=None):
        rc = False
        if not user:
            user = usersession.get_user()
        if not user:
            return rc
        return self.kasutaja_id == user.id and self.koht_id == user.koht_id
