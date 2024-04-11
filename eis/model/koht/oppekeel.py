# -*- coding: utf-8 -*-
# $Id: oppekeel.py 1096 2017-01-11 06:17:05Z ahti $
"Õppeasutuse õppekeel"

from eis.model.entityhelper import *

class Oppekeel(EntityHelper, Base):
    """Õppeasutuse õppekeeled
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True) 
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True, nullable=False) # viide õppeasutuse kohale
    koht = relationship('Koht', foreign_keys=koht_id, back_populates='oppekeeled')
    oppekeel = Column(String(25)) # õppekeele kood EHISe klassifikaatoris: E - eesti; I - inglise; D - saksa; S - soome; V - vene
    _parent_key = 'koht_id'

