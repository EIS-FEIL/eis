from .entityhelper import *
log = logging.getLogger(__name__)

class Abiinfo(EntityHelper, Base):
    """Abiinfo
    """
    EKSAMISTATISTIKA = 'EKSAMISTATISTIKA'
    
    vorm = Column(String(100), primary_key=True) # vormi nimi
    kood = Column(String(100), primary_key=True) # välja nimi vormil
    sisu = Column(Text) # abiinfo sisu
    url = Column(String(150)) # juhendi URL
    
    @classmethod
    def get(cls, vorm, kood):
        return cls.query\
               .filter_by(vorm=vorm).filter_by(kood=kood)\
               .first()

    @classmethod
    def get_fields(cls, vorm):
        q = Abiinfo.query.filter_by(vorm=vorm)
        return [(r.kood, r.sisu, r.url) for r in q.all()]

    @classmethod
    def get_info(cls, kood):
        "Olulise info kirje"
        # kood: cls.EKSAMISTATISTIKA
        return cls.get(kood, kood)

    @classmethod
    def give_info(cls, kood):
        "Olulise info kirje"
        rcd = cls.get_info(kood)
        if not rcd:
            rcd = cls(vorm=kood, 
                      kood=kood)
        return rcd
