from eis.model.entityhelper import *

class Proctoriolog(EntityHelper, Base):
    """Proctorio poole pöördumiste logi
    """
    __tablename__ = 'proctoriolog'    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sooritus_id = Column(Integer, index=True) # soorituse ID
    kasutaja_id = Column(Integer) # kasutaja ID
    take_url = Column(String(2000)) # sooritamise URL
    review_url = Column(String(2000)) # kontrollimise URL (kehtib 1 tund peale loomist)
    url_key = Column(String(32)) # EISi testisoorituse URLi osa, mida teab ainult Proctorio (et välistada ilma Proctoriota lahendamine)
    toimumisaeg_id = Column(Integer, index=True) # toimumisaja ID

    @classmethod
    def get_last(cls, toimumisaeg_id, sooritus_id=None):
        q = (SessionR.query(Proctoriolog)
             .filter_by(toimumisaeg_id=toimumisaeg_id)
             )
        if sooritus_id:
            q = q.filter_by(sooritus_id=sooritus_id)
        q = q.order_by(sa.desc(Proctoriolog.id))
        rcd = q.first()
        return rcd
