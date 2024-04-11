"Testikorralduse andmemudel"

from eis.model.entityhelper import *
from eis.model.klassifikaator import Klrida

from .testiruum import Testiruum
from .tagastusymbrik import Tagastusymbrik
from .hindamisprotokoll import Hindamisprotokoll

class Testiprotokoll(EntityHelper, Base):
    """Testiprotokollirühm
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tahis = Column(String(3), nullable=False) # protokollirühma tähis (01, 02, ...), unikaalne testikoha piires
    tahised = Column(String(43), nullable=False) # testi, testiosa, testimiskorra, testikoha, testiprotokolli tähised, kriips vahel
    testipakett_id = Column(Integer, ForeignKey('testipakett.id'), index=True) # viide testipaketile (puudub e-testi korral)
    testipakett = relationship('Testipakett', foreign_keys=testipakett_id, back_populates='testiprotokollid')
    testiruum_id = Column(Integer, ForeignKey('testiruum.id'), index=True, nullable=False) # viide testiruumile
    testiruum = relationship('Testiruum', foreign_keys=testiruum_id, back_populates='testiprotokollid')
    kursus_kood = Column(String(10)) # valitud kursus, lai või kitsas (matemaatika korral), klassifikaator KURSUS        
    toodearv = Column(Integer) # sooritajate arv (arvutatakse koguste arvutamisel ja seal ka kuvatakse)
    tehtud_toodearv = Column(Integer) # tehtud ja valimis olevate sooritajate arv (arvutatakse protokolli kinnitamisel)
    algus = Column(DateTime) # testi alguse kellaaeg protokollirühmas (kasutusel sisseastumiseksami korral)
    sooritused = relationship('Sooritus', order_by='Sooritus.tahis', back_populates='testiprotokoll') 
    tagastusymbrikud = relationship('Tagastusymbrik', back_populates='testiprotokoll', foreign_keys='Tagastusymbrik.testiprotokoll_id')
    hindamisprotokollid = relationship('Hindamisprotokoll', back_populates='testiprotokoll')
    __table_args__ = (
        sa.UniqueConstraint('tahised'),
        )
    _parent_key = 'testiruum_id'

    @property
    def kursus_nimi(self):
        if self.kursus_kood:
            aine = self.testiruum.testikoht.testiosa.test.aine_kood
            if aine:
                return Klrida.get_str('KURSUS', self.kursus_kood, ylem_kood=aine)            

    def delete_subitems(self):    
        self.delete_subrecords(['hindamisprotokollid',
                                'tagastusymbrikud',
                                ])

    @property
    def soorituste_arv(self):
        if self.id:
            from .sooritus import Sooritus
            cnt = (Session.query(sa.func.count(Sooritus.id))
                   .filter(Sooritus.testiprotokoll_id==self.id)
                   .scalar())
        else:
            cnt = len(self.sooritused)
        return cnt

    def gen_tahis(self):
        """Genereeritakse testikoha piires unikaalne tähis
        """
        if not self.tahis:
            testikoht = self.testiruum.testikoht

            # leiame senise maksimaalse tähise
            q = (Session.query(Testiprotokoll.tahis)
                 .join(Testiprotokoll.testiruum)
                 .filter(Testiruum.testikoht_id==testikoht.id))
            if self.id:
                q = q.filter(Testiprotokoll.id!=self.id)
            cnt = 0
            for tahis, in q.all():
                try:
                    n_tahis = int(tahis)
                except ValueError:
                    continue
                else:
                    cnt = max(cnt, n_tahis)
            self.tahis = '%02d' % (cnt + 1)
            self.set_tahised()

    def set_tahised(self):
        testikoht = self.testiruum.testikoht
        self.tahised = '%s-%s' % (testikoht.tahised, self.tahis)        

    def get_tahised_tk(self):
        "Lühendatud tähised"
        return '%s-%s' % (self.testiruum.testikoht.tahis, self.tahis)

    def get_tagastusymbrik(self, tagastusymbrikuliik):
        for rcd in self.tagastusymbrikud:
            if rcd.tagastusymbrikuliik == tagastusymbrikuliik:
                return rcd

    def give_tagastusymbrik(self, tagastusymbrikuliik):
        rcd = self.get_tagastusymbrik(tagastusymbrikuliik)
        if not rcd:
            rcd = Tagastusymbrik(testiprotokoll=self,
                                 testipakett=self.testipakett,
                                 tahised=self.tahised+'-'+tagastusymbrikuliik.tahis,
                                 tagastusymbrikuliik=tagastusymbrikuliik)
            self.tagastusymbrikud.append(rcd)
        return rcd

    def get_hindamisprotokoll(self, liik, sisestuskogum_id):
        for rcd in self.hindamisprotokollid:
            if rcd.liik == liik and rcd.sisestuskogum_id == sisestuskogum_id:
                return rcd

    def give_hindamisprotokoll(self, liik, sisestuskogum_id):
        rcd = self.get_hindamisprotokoll(liik, sisestuskogum_id)
        if not rcd:
            rcd = Hindamisprotokoll(testiprotokoll=self,
                                    liik=liik,
                                    sisestuskogum_id=sisestuskogum_id)
            self.hindamisprotokollid.append(rcd)
        return rcd
