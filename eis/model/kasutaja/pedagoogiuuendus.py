# -*- coding: utf-8 -*-
from eis.model.entityhelper import *
log = logging.getLogger(__name__)

class Pedagoogiuuendus(EntityHelper, Base):
    """Pedagoogide andmete EHISest uuendamise seis
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kool_id = Column(Integer, index=True) # EHISe kooli id
    ehis_aine_kood = Column(String(25)) # aine (EHISe klassifikaator)
    ehis_aste_kood = Column(String(25)) # kooliaste (EHISe klassifikaator)
    seisuga = Column(DateTime, nullable=False) # viimane EHISest andmete kontrollimise aeg
    __table_args__ = (
        sa.UniqueConstraint('kool_id','ehis_aine_kood','ehis_aste_kood'),
        )

    @classmethod
    def give(cls, kool_id, ehis_aine_kood, ehis_aste_kood):
        item = cls.get_by(kool_id, ehis_aine_kood, ehis_aste_kood)
        if not item:
            item = cls(kool_id=kool_id,
                       ehis_aine_kood=ehis_aine_kood,
                       ehis_aste_kood=ehis_aste_kood)
        return item

    @classmethod
    def get_by(cls, kool_id, ehis_aine_kood, ehis_aste_kood):
        q = (cls.query
             .filter_by(kool_id=kool_id)
             .filter_by(ehis_aine_kood=ehis_aine_kood)
             .filter_by(ehis_aste_kood=ehis_aste_kood)
             )
        return q.first()          

