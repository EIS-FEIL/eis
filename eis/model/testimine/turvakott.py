# -*- coding: utf-8 -*-
# $Id: turvakott.py 1096 2017-01-11 06:17:05Z ahti $
"Testikorralduse andmemudel"

import pickle
from cgi import FieldStorage
import mimetypes

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *
_ = usersession._

class Turvakott(EntityHelper, Base):
    """Materjalide eksamikeskusest väljastamise või 
    eksamikeskusse tagastamise turvakott
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    kotinr = Column(String(11)) # koti nr
    testipakett_id = Column(Integer, ForeignKey('testipakett.id'), index=True, nullable=False) # viide testipaketile
    testipakett = relationship('Testipakett', foreign_keys=testipakett_id, back_populates='turvakotid')
    suund = Column(String(1), nullable=False) # suund: 1=const.SUUND_VALJA - väljastuskott; 2=const.SUUND_TAGASI - tagastuskott 
    staatus = Column(Integer, sa.DefaultClause('1'), nullable=False) # olek, M_STAATUS
    #sa.UniqueConstraint('kotinr')
    _parent_key = 'testipakett_id'

    @property
    def suund_nimi(self):
        if self.suund == const.SUUND_VALJA:
            return _("Väljastuskott")
        elif self.suund == const.SUUND_TAGASI:
            return _("Tagastuskott")

    @property
    def staatus_nimi(self):
        return usersession.get_opt().M_STAATUS.get(self.staatus)
        
