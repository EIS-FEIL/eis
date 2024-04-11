"Testikorralduse andmemudel"

import pickle
from cgi import FieldStorage
import mimetypes

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *

class Ainepdf(EntityHelper, Base):
    """Ainete seosed eksamikorralduse materjalide väljatrükkimise PDF mallidega
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    aine_kood = Column(String(10), nullable=False) # ainete klassifikaator
    tyyp = Column(String(30), nullable=False) # PDF malli tyyp (faili nimi on kujul TYYP_NIMI.py)
    nimi = Column(String(50), nullable=False) # PDF malli nimi (faili nimi on kujul TYYP_NIMI.py)    
    __table_args__ = (
        sa.UniqueConstraint('aine_kood','tyyp'),
        )

    @classmethod
    def get_default_for(cls, aine_kood, tyyp):
        rcd = cls.query.\
            filter_by(aine_kood=aine_kood).\
            filter_by(tyyp=tyyp).\
            first()
        if rcd:
            return rcd.nimi

    @classmethod
    def get_default_dict(cls, aine_kood):
        di = {}
        for rcd in cls.query.filter_by(aine_kood=aine_kood).all():
            di[rcd.tyyp] = rcd.nimi
        return di
            
