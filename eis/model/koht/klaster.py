import random
from eis.model.entityhelper import *

class Klaster(EntityHelper, Base):
    """Eksamiserverite klastrid, milles toimub testi sooritamine
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    int_host = Column(String(50), unique=True, nullable=False) # serveri nimi sisevõrgus, andmevahetuseks
    staatus = Column(Integer, sa.DefaultClause('0'), nullable=False) # staatus: 0 - pole kasutusel; 1 - kasutusel
    seqmult = Column(Integer) #  100 000 000 kordaja, sekventside algus

    @classmethod
    def get_host(cls, klaster_id):
        "Leitakse määratud klastri host"
        if klaster_id:
            item = Klaster.getR(klaster_id)
            if item and item.staatus:
                return item.int_host

    @classmethod
    def give_klaster(cls, sooritaja):
        klaster_id = sooritaja.klaster_id
        k_id, host = cls.get_klaster(klaster_id)
        if klaster_id != k_id:
            sooritaja.klaster_id = k_id
        return k_id, host
           
    @classmethod
    def get_klaster(cls, klaster_id=None):
        q = (SessionR.query(Klaster.id, Klaster.int_host)
             .filter_by(staatus=const.B_STAATUS_KEHTIV)
             )
        if klaster_id:
            q = q.filter_by(id=klaster_id)
        else:
            cnt = q.count()
            if cnt > 0:
                n = random.randint(0, cnt-1)
                q = q.order_by(Klaster.id).offset(n)                
        klaster_id, host = q.first()
        return klaster_id, host
           
