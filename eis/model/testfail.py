# -*- coding: utf-8 -*-
"Digiallkirjastamise testfail"

from eis.model.entityhelper import *

class Testfail(EntityHelper, Base):
    """Digiallkirjastamise testimise testfail
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    fail_dok = Column(LargeBinary) # vaide avalduse digiallkirjastatud dokument
    fail_ext = Column(String(5)) # avalduse vorming: ddoc või bdoc või asice
