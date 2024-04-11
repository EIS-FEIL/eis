"Testikorralduse andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import Klrida
from .testiruum import Testiruum

class Valjastusymbrik(EntityHelper, Base):
    """Testiruumi ja väljastusümbrikuliigiga seotud ümbrike kogus.
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    testipakett_id = Column(Integer, ForeignKey('testipakett.id'), index=True, nullable=False) # viide testipaketile
    testipakett = relationship('Testipakett', foreign_keys=testipakett_id, back_populates='valjastusymbrikud')
    kursus_kood = Column(String(10)) # valitud kursus, lai või kitsas (matemaatika korral), klassifikaator KURSUS            
    testiruum_id = Column(Integer, ForeignKey('testiruum.id'), index=True) # viide testiruumile, kui ümbrik on ruumikaupa (ümbriku liigis on sisukohta=3)
    testiruum = relationship('Testiruum', foreign_keys=testiruum_id, back_populates='valjastusymbrikud')
    valjastusymbrikuliik_id = Column(Integer, ForeignKey('valjastusymbrikuliik.id'), index=True, nullable=False) # väljastusümbrikuliik
    valjastusymbrikuliik = relationship('Valjastusymbrikuliik', foreign_keys=valjastusymbrikuliik_id, back_populates='valjastusymbrikud')
    toodearv = Column(Integer, nullable=False) # väljastatavate tööde arv, mis on saadud testiruumi sooritajate arvule lisatööde koefitsienti ja ümarduskordajat rakendades
    ymbrikearv = Column(Integer, sa.DefaultClause('1'), nullable=False) # ümbrike arv, mis on saadud tööde arvu jagamisel ümbriku mahuga
    arvutus = Column(Integer) # arvutusprotsessi tunnus
    __table_args__ = (
        sa.UniqueConstraint('testipakett_id', 'testiruum_id', 'valjastusymbrikuliik_id', 'kursus_kood'),
        )
    _parent_key = 'testipakett_id'

    @property
    def kursus_nimi(self):
        if self.kursus_kood:
            aine = self.testipakett.testikoht.testiosa.test.aine_kood
            if aine:
                return Klrida.get_str('KURSUS', self.kursus_kood, ylem_kood=aine)            

