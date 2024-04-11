# -*- coding: utf-8 -*-

import hashlib
from datetime import datetime, timedelta

from eis.model.entityhelper import *

class Paring_tunnistus(EntityHelper, Base):
    """X-tee kaudu tunnistuste allalaadimise logi
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    isikukood = Column(String(50), nullable=False) # X-tee päise isikukood, teenuse kasutaja
    paring = Column(String(30), nullable=False) # X-tee teenuse nimi
    asutus = Column(String(10), nullable=False) # X-tee päise asutus, teenuse kasutaja
    tunnistus_id = Column(Integer, ForeignKey('tunnistus.id'), index=True, nullable=False) # viide alla laaditud tunnistusele
    tunnistus = relationship('Tunnistus', foreign_keys=tunnistus_id)
    aeg = Column(DateTime, nullable=False) # esimese eksimuse aeg

    @classmethod
    def log(cls, xrheader, tunnistus_id):
        client = xrheader.client
        if client:
            # v4 klient
            klient = '.'.join([client.xRoadInstance,
                               client.memberClass,
                               client.memberCode,
                               client.subsystemCode])
            asutus = client.memberCode
            paring = xrheader.service.serviceCode
        else:
            klient = asutus = xrheader.consumer
            paring = xrheader.service
        
        cls(isikukood=xrheader.userId,
            paring=paring,
            asutus=asutus,
            aeg=datetime.now(),
            tunnistus_id=tunnistus_id)

        Session.commit()

