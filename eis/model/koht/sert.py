# -*- coding: utf-8 -*-
# $Id: sert.py 1096 2017-01-11 06:17:05Z ahti $

from eis.model.entityhelper import *

class Sert(EntityHelper, Base):
    """Kohalike serverite serdid ja keskserveri sert
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True) # viide soorituskohale; keskserveri korral 1; CA korral NULL
    koht = relationship('Koht', foreign_keys=koht_id, back_populates='sert')
    key_pem = Column(Text) # CA võti (CA korral)
    req_pem = Column(Text) # serditaotlus PEM kujul (kohaliku serveri korral)
    cert_pem = Column(Text) # sert PEM kujul: kohaliku serveri korral kohalikule serverile keskserveri poolt väljastatud sert; keskserveri korral koormusjaoturi veebiserveri sert või selle väljastaja sert, millega kohalik server saab vastaspoolt valideerida; CA korral CA sert
    notbefore = Column(String(30)) # serveri serdi kehtivuse algusaeg
    notafter = Column(String(30)) # serveri serdi kehtivuse lõppaeg
    srl = Column(String(32)) # kohaliku serveri serdi seerianumber; keskserveri korral ca.srl

    @classmethod
    def give_ca_sert(cls):
        rcd = Sert.query.filter_by(koht_id=None).first()
        if not rcd:
            rcd = Sert()
        return rcd
