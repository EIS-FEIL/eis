from .entityhelper import *
from .klassifikaator import cache_id
log = logging.getLogger(__name__)

class Seade(EntityHelper, Base):
    """Süsteemi üldised seaded
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(50)) # parameetri nimi
    svalue = Column(String(50)) # tekstilise parameetri väärtus
    nvalue = Column(Integer) # täisarvulise parameetri väärtus

    @classmethod
    def get_value(self, key):
        cache_key = f'SEADE.{key}'
        if cache_id.has_key(key):
            return cache_id.get(cache_key)
        else:
            q = Seade.queryR.filter_by(key=key)
            for r in q.all():
                value = r.svalue or r.nvalue
                cache_id[cache_key] = value
                return value
        
                    
