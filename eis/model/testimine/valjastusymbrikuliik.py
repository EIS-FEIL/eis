"Testi andmemudel"
from eis.model.entityhelper import *
from .toimumisaeg import Toimumisaeg
_ = usersession._

class Valjastusymbrikuliik(EntityHelper, Base):
    """Väljastusümbriku liik
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tahis = Column(String(10), nullable=False) # liigi tähis, määratakse automaatselt kujul 1,2,...
    nimi = Column(String(256)) # nimetus
    toimumisaeg_id = Column(Integer, ForeignKey('toimumisaeg.id'), index=True, nullable=False) # viide toimumisajale
    toimumisaeg = relationship('Toimumisaeg', foreign_keys=toimumisaeg_id, back_populates='valjastusymbrikuliigid')
    maht = Column(Integer) # mitu testitööd mahub ühte ümbrikusse
    lisatoode_koef = Column(Float) # lisatööde koefitsient, millega korrutatakse sooritajate arv läbi ja ümardatakse üles ning saadakse antud liiki ümbrikus saadetavate tööde arv
    lisatoode_arv = Column(Integer) # lisatööde arv, mis liidetakse sooritajate arvule
    ymarduskordaja = Column(Integer, sa.DefaultClause('1')) # testiruumi saadetavate tööde arv peab selle arvuga jaguma (tavaliselt 1, 5 või 10)
    keeleylene = Column(Boolean, sa.DefaultClause('0'), nullable=False) # false - eraldi väljastusümbrik iga keele ja kursuse kohta; true - ühine väljastusümbrik kõigile keeltele ja kursustele (tehtud matemaatika riigieksami mustandite jaoks)
    sisukohta = Column(Integer, sa.DefaultClause('4'), nullable=False) # mille kohta ümbrik teha: 3 - testipaketi kohta; 4 - testiruumi kohta
    valjastusymbrikud = relationship('Valjastusymbrik', back_populates='valjastusymbrikuliik')
    __table_args__ = (
        sa.UniqueConstraint('toimumisaeg_id','tahis'),
        )
    _parent_key = 'toimumisaeg_id'

    SISUKOHTA_PAKETT = 3 # testipaketi kohta
    SISUKOHTA_RUUM = 4 # testiruumi kohta

    @classmethod
    def opt_sisukohta(cls):
        return [(cls.SISUKOHTA_RUUM, _("Testiruum")),
                (cls.SISUKOHTA_PAKETT, _("Testipakett")),
                ]
      
    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        toimumisaeg = self.toimumisaeg or self.toimumisaeg_id and Toimumisaeg.get(self.toimumisaeg_id)
        if toimumisaeg:
            toimumisaeg.logi('Väljastusümbriku liik %s %s' % (self.id, liik), vanad_andmed, uued_andmed, logitase)

    def post_create(self):
        self.gen_tahis()

    def gen_tahis(self):
        if not self.tahis:
            ta = self.toimumisaeg or Toimumisaeg.get(self.toimumisaeg_id)
            for n in range(1,1000):
                tahis = '%d' % n
                for rcd in ta.valjastusymbrikuliigid:
                    if rcd.tahis == tahis:
                        tahis = None
                        break
                if tahis:
                    self.tahis = tahis
                    break

    def get_count(self, testipakett_id, kursus, tr_tahis=None):
        "Mitu ymbrikku on väiksema tähisega testiruumides samas paketis ja mitu on kokku"
        from eis.model.testimine.valjastusymbrik import Valjastusymbrik
        from eis.model.testimine.testiruum import Testiruum

        q = (Session.query(sa.func.sum(Valjastusymbrik.ymbrikearv))
             .filter(Valjastusymbrik.testipakett_id==testipakett_id)
             .filter(Valjastusymbrik.valjastusymbrikuliik_id==self.id)
             .filter(Valjastusymbrik.kursus_kood==kursus))
        if tr_tahis:
            # mitu ymbrikku on enne selle testiruumi tähisega ymbrikku
            q = (q.join(Valjastusymbrik.testiruum)
                 .filter(Testiruum.tahis<tr_tahis))
        return q.scalar() or 0


    def delete_subitems(self):    
        self.delete_subrecords(['valjastusymbrikud',
                                ])
