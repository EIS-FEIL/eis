from eis.model.entityhelper import *
log = logging.getLogger(__name__)

class Abivahend(EntityHelper, Base):
    """Ülesande lahendamise abivahend
    """
    id = Column(Integer, primary_key=True, autoincrement=True) 
    jrk = Column(Integer) # järjekorranumber valikutes
    kood = Column(String(10), nullable=False) # väärtuse kood
    nimi = Column(String(500), nullable=False) # nimetus
    kirjeldus = Column(Text) # täiendav kirjeldus
    pais = Column(Text) # HTML päisesse lisatav osa (vahendite korral)
    ikoon_url = Column(String(100)) # ikooni failinimi (vahendite korral)
    laius = Column(Integer) # kuvamisel kasutatav laius (vahendite korral)
    korgus = Column(Integer) # kuvamisel kasutatav kõrgus (vahendite korral)    
    kehtib = Column(Boolean) # olek: 1 - kehtib; 0 - ei kehti
    trans = relationship('T_Abivahend', cascade='all', back_populates='orig') # kui cascade puudub, siis antakse kustutamisel viga
    
    @classmethod
    def get_by_kood(cls, kood):
        q = cls.query.filter_by(kood=kood)
        return q.first()

    @property
    def ctran(self):
        "Jooksvalt valitud keele tõlkekirje"
        return self.tran(usersession.get_lang())

    @classmethod
    def get_opt(cls):
        q = (Session.query(Abivahend.kood,
                           Abivahend.nimi)
             .filter_by(kehtib=True)
             .order_by(Abivahend.jrk, Abivahend.nimi))
        return [(k,v) for (k,v) in q.all()]
        
