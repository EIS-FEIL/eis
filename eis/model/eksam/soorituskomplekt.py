"Testikorralduse andmemudel"
from eis.model.entityhelper import *

_ = usersession._

class Soorituskomplekt(EntityHelper, Base):
    """Soorituse ülesandekomplekti valik
    """
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sooritus_id = Column(Integer, index=True, nullable=False) # viide sooritusele
    komplektivalik_id = Column(Integer, index=True, nullable=False) # viide komplektivalikule
    komplekt_id = Column(Integer, index=True) # viide valitud komplektile
    __table_args__ = (
        sa.UniqueConstraint('sooritus_id','komplektivalik_id'),
        )
    _parent_key = 'sooritus_id'

    @property
    def komplektivalik(self):
        from eis.model.test.komplektivalik import Komplektivalik
        return Komplektivalik.get(self.komplektivalik_id)

    @property
    def komplekt(self):
        from eis.model.test.komplekt import Komplekt
        return Komplekt.get(self.komplekt_id)   

    @classmethod
    def get_by_sooritus(cls, sooritus_id):
        q = (Session.query(Soorituskomplekt)
             .filter_by(sooritus_id=sooritus_id)
             )
        return [r for r in q.all()]
