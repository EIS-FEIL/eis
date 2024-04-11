# -*- coding: utf-8 -*-
# $Id: asukohamaarus.py 389 2016-03-03 13:51:55Z ahti $

from eis.model.entityhelper import *

class Asukohamaarus(EntityHelper, Base):
    """Eksamikohtade asukohamäärus (kohanimed sees- või alalütlevas käändes).
    Taseme- ja seaduse tundmise eksami diplomile kirjutatakse eksamikoht käändes (kus?).
    Kui eksamikoha asula nime lõpp leitakse siit tabelist, siis rakendatakse tabelis toodud vormi.
    Kui asula nime lõppu siit ei leita, siis lisatakse asula nimele "s".
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    seq = Column(Integer) # järjekorranumber
    nimetav = Column(String(30), nullable=False) # kohanime lõpp nimetavas käändes
    kohamaarus = Column(String(30), nullable=False) # kohanime lõpp sees- või alalütlevas käändes

    @classmethod
    def get_for(cls, kohanimi):
        for rcd in cls.query.all():
            if kohanimi.upper().endswith(rcd.nimetav.upper()):
                l = len(rcd.nimetav)
                nimetav = kohanimi[0-l:]
                kohamaarus = rcd.kohamaarus
                if nimetav[0].isupper():
                    kohamaarus = kohamaarus[0].upper() + kohamaarus[1:]
                else:
                    kohamaarus = kohamaarus[0].lower() + kohamaarus[1:]
                kohanimi = kohanimi[:0-l] + kohamaarus
                return kohanimi
        return kohanimi + 's'

    def get_seq(self):
        rc = Session.query(sa.func.max(Asukohamaarus.seq)).scalar()
        return (rc or 0) + 1
