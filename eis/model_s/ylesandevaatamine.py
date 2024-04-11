import cgi
import eiscore.const as const
from eis.model_s.entityhelper import *
from .meta import Base, DBSession

class Ylesandevaatamine(EntityHelper, Base):
    """Ülesande esmase lahendajale kuvamise aja salvestamise tabel.
    Aega ei salvestata kohe tabelis Ylesandevastus, sest valikülesande korral
    võib lahendaja vaadata mitut valikut ning kõigi algusaeg on vaja salvestada,
    kuid Ylesandevastuse tabelis on jooksvalt üheainsa valiku kirje
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    sooritus_id = Column(Integer, index=True, nullable=False) # viide sooritusele
    valitudylesanne_id = Column(Integer, index=True, nullable=False) # viide valitudülesandele
    testiylesanne_id = Column(Integer, index=True, nullable=False) # viide testiülesandele
    komplekt_id = Column(Integer, index=True, nullable=False) # viide komplektile
    algus = Column(DateTime, nullable=False) # ylesande lugemise aeg

    @classmethod
    def get_algus_by_vy(cls, sooritus_id, valitudylesanne_id):
        q = (DBSession.query(cls)
             .filter_by(sooritus_id=sooritus_id)
             .filter_by(valitudylesanne_id=valitudylesanne_id)
             .order_by(cls.algus)
             )
        return q.first()

    @classmethod
    def get_last_algus_by_vy(cls, sooritus_id, valitudylesanne_id):
        q = (DBSession.query(sa.func.max(cls.algus))
             .filter_by(sooritus_id=sooritus_id)
             .filter_by(valitudylesanne_id=valitudylesanne_id)
             )
        return q.scalar()

    @classmethod
    def get_algus_by_ty(cls, sooritus_id, testiylesanne_id, komplekt_id):
        q = (DBSession.query(cls)
             .filter_by(sooritus_id=sooritus_id)
             .filter_by(testiylesanne_id=testiylesanne_id)
             .filter_by(komplekt_id=komplekt_id)
             .order_by(cls.algus)
             )
        return q.first()
        
    @classmethod
    def set_algus(cls, sooritus_id, vy):
        #rcd = cls.get_algus_by_vy(sooritus_id, valitudylesanne_id)
        #if not rcd:
        rcd = Ylesandevaatamine(sooritus_id=sooritus_id,
                                valitudylesanne_id=vy.id,
                                testiylesanne_id=vy.testiylesanne_id,
                                komplekt_id=vy.komplekt_id,
                                algus=datetime.now())
        DBSession.add(rcd)
        DBSession.flush()
        return rcd
