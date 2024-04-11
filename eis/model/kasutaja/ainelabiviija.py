# -*- coding: utf-8 -*-
from eis.model.entityhelper import *

log = logging.getLogger(__name__)

class Ainelabiviija(EntityHelper, Base):
    """Kasutaja konkreetses aines testi läbiviijana rakendamise tähis
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    profiil_id = Column(Integer, ForeignKey('profiil.id'), index=True, nullable=False) # viide kasutaja profiilile
    profiil = relationship('Profiil', foreign_keys=profiil_id, back_populates='ainelabiviijad')
    aine_kood = Column(String(10)) # viide õppeainele, klassifikaator AINE
    tahis = Column(Integer) # läbiviija tähis antud aines, unikaalne aine piires
    __table_args__ = (
        sa.UniqueConstraint('profiil_id', 'aine_kood'),
        sa.UniqueConstraint('aine_kood', 'tahis'),
        )

    @classmethod
    def gen_tahis(cls, aine_kood):
        tahis = (Session.query(sa.func.max(cls.tahis))
                 .filter_by(aine_kood=aine_kood)
                 .scalar()) or 0
        return tahis + 1

    @classmethod
    def give_tahis_for(cls, aine_kood, kasutaja):
        p = kasutaja.profiil
        if p:
            item = (cls.query
                    .filter_by(profiil_id=p.id)
                    .filter_by(aine_kood=aine_kood)
                    .first())
            if not item:
                item = cls(profiil_id=p.id,
                           aine_kood=aine_kood,
                           tahis=cls.gen_tahis(aine_kood))
                Session.flush()
            return item.tahis
