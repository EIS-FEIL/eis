"Testi andmemudel"
from eis.model.entityhelper import *
_ = usersession._

from .toimumisaeg import Toimumisaeg

class Tagastusymbrikuliik(EntityHelper, Base):
    """Tagastusümbriku liik vastab üldjuhul alatestile
    (st testiprotokollirühmas on iga alatesti ülesannete jaoks oma ümbrik)
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tahis = Column(String(10), nullable=False) # ümbriku liigi tähis
    nimi = Column(String(100)) # ümbriku liigi nimetus
    toimumisaeg_id = Column(Integer, ForeignKey('toimumisaeg.id'), index=True, nullable=False) # viide toimumisajale
    toimumisaeg = relationship('Toimumisaeg', foreign_keys=toimumisaeg_id, back_populates='tagastusymbrikuliigid')
    hindamiskogumid = relationship('Hindamiskogum', secondary='tagastusymbrikuliik_hk') # hindamiskogumid, mille ülesannete vastuseid ümbrik sisaldab
    #hindamiskogumid = relationship('Hindamiskogum', secondary='tagastusymbrikuliik_hk', back_populates='tagastusymbrikuliigid') # hindamiskogumid, mille ülesannete vastuseid ümbrik sisaldab
    maht = Column(Integer) # mitu testitööd mahub ühte ümbrikusse
    sisukohta = Column(Integer, sa.DefaultClause('1'), nullable=False) # mille kohta ümbrik teha: 1 - testiprotokollirühma kohta; 2 - sama ruumi kahe testiprotokollirühma kohta; 3 - testipaketi kohta
    tagastusymbrikud = relationship('Tagastusymbrik', back_populates='tagastusymbrikuliik')
    __table_args__ = (
        sa.UniqueConstraint('toimumisaeg_id','tahis'),
        )
    _parent_key = 'toimumisaeg_id'

    SISUKOHTA_TPR = 1 # testiprotokollirühma ümbrik
    SISUKOHTA_TPR2 = 2 # kahe testiprotokollirühma kohta
    SISUKOHTA_PAKETT = 3 # testipaketi kohta

    @classmethod
    def opt_sisukohta(cls):
        return [(cls.SISUKOHTA_TPR, _("Protokollirühm")),
                (cls.SISUKOHTA_TPR2, _("2 protokollirühma")),
                (cls.SISUKOHTA_PAKETT, _("Testipakett")),
                ]
    
    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        toimumisaeg = self.toimumisaeg or self.toimumisaeg_id and Toimumisaeg.get(self.toimumisaeg_id)
        if toimumisaeg:
            toimumisaeg.logi('Tagastusümbriku liik %s %s' % (self.id, liik), vanad_andmed, uued_andmed, logitase)

    def gen_tahis(self):
        if not self.tahis:
            ta = self.toimumisaeg or Toimumisaeg.get(self.toimumisaeg_id)
            for n in range(1,1000):
                tahis = '%d' % n
                for rcd in ta.tagastusymbrikuliigid:
                    if rcd.tahis == tahis:
                        tahis = None
                        break
                if tahis:
                    self.tahis = tahis
                    break

    def copy(self, toimumisaeg=None):
        toimumisaeg_id = toimumisaeg and toimumisaeg.id or None
        cp = EntityHelper.copy(self, toimumisaeg_id=toimumisaeg_id)
        for hk in self.hindamiskogumid:
            cp.hindamiskogumid.append(hk)
        return cp

    def delete_subitems(self):    
        self.delete_subrecords(['tagastusymbrikud',
                                ])
