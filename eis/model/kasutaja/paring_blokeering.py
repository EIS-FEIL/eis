# -*- coding: utf-8 -*-

import hashlib
from datetime import datetime, timedelta

from eis.model.entityhelper import *

log = logging.getLogger(__name__)

class Paring_blokeering(EntityHelper, Base):
    """X-tee teenuste kasutamise blokeerimine 
    valede sisendandmete kasutamise eest.
    Kui 10 minuti jooksul tehakse 3 eksimust, siis 
    blokeeritakse teenuse kasutamine 24 tunniks.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    isikukood = Column(String(50), nullable=False) # X-tee päise isikukood, teenuse kasutaja
    paring = Column(String(30), nullable=False) # blokeeritava X-tee teenuse nimi
    eksimuste_arv = Column(Integer, nullable=False) # eksimuste arv 10 minuti jooksul
    aeg = Column(DateTime, nullable=False) # esimese eksimuse aeg
    kuni = Column(DateTime) # blokeeringu kehtivuse lõpp, kui on blokeeritud

    @classmethod
    def check(cls, xrheader):
        isikukood = xrheader.userId
        client = xrheader.client
        if client:
            # v4 klient
            paring = xrheader.service.serviceCode
        else:
            paring = xrheader.service

        blokeering = cls.query.\
            filter_by(isikukood=isikukood).\
            filter_by(paring=paring).\
            first()
        if blokeering and blokeering.kuni and \
                blokeering.kuni > datetime.now():
            error = 'Teenuse kasutamine on blokeeritud kuni %s. ' % \
                (blokeering.kuni.strftime('%d.%m.%Y %H:%M'))
            return error

    @classmethod
    def increment(cls, xrheader):
        """Teenuse kasutaja sisestas valed andmed.
        Jätame meelde ja kui 10 minuti jooksul on 3 korda seda juhtunud,
        siis blokeeritakse teenuse kasutamine 24 tunniks.
        """
        error = ''
        isikukood = xrheader.userId
        client = xrheader.client
        if client:
            # v4 klient
            paring = xrheader.service.serviceCode
        else:
            paring = xrheader.service

        blokeering = cls.query.\
            filter_by(isikukood=isikukood).\
            filter_by(paring=paring).\
            first()

        if not blokeering:
            # esimene eksimus
            blokeering = cls(isikukood=isikukood,
                             paring=paring,
                             eksimuste_arv=1,
                             aeg=datetime.now())
    
        elif blokeering.aeg < datetime.now() - timedelta(minutes=10):
            # varasemad eksimused on aegunud
            blokeering.eksimuste_arv = 1
            blokeering.aeg = datetime.now()

        else:
            # viimase 10 minuti jooksul on juba eksitud
            blokeering.eksimuste_arv += 1
            if blokeering.eksimuste_arv >= 3:
                blokeering.kuni = datetime.now() + timedelta(days=1)
                error = 'Teenuse kasutamine on blokeeritud kuni %s. ' % \
                    (blokeering.kuni.strftime('%d.%m.%Y %H:%M'))

        Session.commit()
        return error
