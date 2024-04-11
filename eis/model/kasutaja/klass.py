import hashlib
from eis.model.entityhelper import *
from eis.model.koht import Koht
from eis.model.klassifikaator import Klrida

log = logging.getLogger(__name__)
_ = usersession._

class Klass(EntityHelper, Base):
    """Klassi andmete uuendamise seis
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kool_id = Column(Integer, nullable=False) # EHISe kooli id
    klass = Column(String(10)) # klass 
    paralleel = Column(String(40)) # paralleel
    seisuga = Column(DateTime, nullable=False) # viimane EHISest andmete kontrollimise aeg
    __table_args__ = (
        sa.UniqueConstraint('kool_id','klass','paralleel'),
        )

    @classmethod
    def give(cls, kool_id, klass, paralleel=None):
        if paralleel:
            paralleel = paralleel.upper()
        item = cls.get_by_klass(kool_id, klass, paralleel)
        if not item:
            item = cls(kool_id=kool_id, klass=klass, paralleel=paralleel or None)
        return item

    @classmethod
    def get_by_klass(cls, kool_id, klass, paralleel=None):
        if paralleel:
            paralleel = paralleel.upper()
        q = cls.query.\
            filter_by(kool_id=kool_id).\
            filter_by(klass=klass).\
            filter(cls.paralleel==(paralleel or None))
        return q.first()          

    @classmethod
    def klass_ryhm(self, rklass):
        "Eristame klassi ja lasteaiarühma"
        if not rklass:
            return None, None
        elif rklass[0] == 'r':
            ryhm_id = int(rklass[1:])
            return None, ryhm_id
        else:
            # klass
            return rklass, None

class KlassID:
    "URLis kasutatav klassi ID, mis kodeerib klassi ja paralleeli"

    # sisseastumiseksami tagasisides sisseastujate "klass",
    # ei sisalda neid oma kooli õpilasi, kes ei kandideeri oma kooli
    KANDIDAADID = 'kandidaadid'
    
    def __init__(self, klass, paralleel):
        self.klass = klass
        self.paralleel = paralleel

    @property
    def id(self):
        "Klassi ID URLi jaoks"
        if self.paralleel:
            return f"{self.klass or ''}.{self.paralleel}"
        else:
            return self.klass

    @property
    def name(self):
        "Klassi nimetus tekstis kasutamiseks"
        if self.klass == self.KANDIDAADID:
            return _("Sisseastujad")
        elif self.paralleel:
            return f"{self.klass} {self.paralleel}"
        else:
            return self.klass

    @classmethod
    def parse_id(cls, klass_id):
        "Id väärtusest klassi ja paralleeli tuletamine"
        try:
            klass, paralleel = klass_id.split('.', 1)
        except:
            klass = klass_id
            paralleel = None
        return klass, paralleel

    @classmethod
    def from_id(cls, klass_id):
        "Objekti loomine id väärtuse põhjal"
        klass, paralleel = cls.parse_id(klass_id)
        return cls(klass, paralleel)

        
