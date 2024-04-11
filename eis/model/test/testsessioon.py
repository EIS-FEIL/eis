"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import Opt
from eis.model.kasutaja import *
from eis.model.koht import *

class Testsessioon(EntityHelper, Base):
    """Testsessioon
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    seq = Column(Integer) # järjekorranumber (testsessioonide loetelu järjestamiseks)
    nimi = Column(String(100), nullable=False) # nimetus
    vaide_tahtaeg = Column(Date) # vaide tähtaeg
    oppeaasta = Column(Integer, nullable=False) # õppeaasta, millesse testsessioon kuulub (läheb tunnistusele, selle põhjal genereeritakse ka tunnistuste numbreid)
    testimiskorrad = relationship('Testimiskord', back_populates='testsessioon') 
    testiliik_kood = Column(String(10)) # testsessiooni kuuluvate testide liik, klassifikaator TESTILIIK
    staatus = Column(Integer, nullable=False) # olek: 1 - kasutusel, 0 - pole kasutusel
    vaikimisi = Column(Boolean) # kas panna uute testimiskordade korral vaikimisi sessiooniks
    
    @property
    def kehtib(self):
        return bool(self.staatus)

    def default(self):
        self.staatus = const.B_STAATUS_KEHTIV

    def set_seq(self):
        pass

    @classmethod
    def get_opt(cls, testiliik_kood=None, staatus=1):
        q = Testsessioon.query
        if testiliik_kood:
            if isinstance(testiliik_kood, list):
                q = q.filter(sa.or_(Testsessioon.testiliik_kood.in_(testiliik_kood),
                                    Testsessioon.testiliik_kood==None))
            else:
                q = q.filter(sa.or_(Testsessioon.testiliik_kood==testiliik_kood,
                                    Testsessioon.testiliik_kood==None))
        if staatus is not None:
            q = q.filter_by(staatus=staatus)
        return [(item.id, item.nimi) for item in q.order_by(sa.desc(Testsessioon.seq),Testsessioon.nimi).all()]

    @classmethod
    def get_default(cls, testiliik_kood):
        "Leitakse vaikimisi testsessioon.id"
        q = (SessionR.query(Testsessioon.id)
             .filter_by(staatus=const.B_STAATUS_KEHTIV)
             .filter_by(vaikimisi=True))
        if isinstance(testiliik_kood, list):
            q = q.filter(sa.or_(Testsessioon.testiliik_kood.in_(testiliik_kood),
                                Testsessioon.testiliik_kood==None))
        else:
            q = q.filter(sa.or_(Testsessioon.testiliik_kood==testiliik_kood,
                                Testsessioon.testiliik_kood==None))
        q = q.order_by(sa.desc(Testsessioon.seq))
        for ts_id, in q.all():
            return ts_id


