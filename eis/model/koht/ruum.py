from eis.model.entityhelper import *
from eis.model.klassifikaator import Klrida

class Ruum(EntityHelper, Base):
    """Testi sooritamise ruum
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True, nullable=False) # viide soorituskohale
    koht = relationship('Koht', foreign_keys=koht_id, back_populates='ruumid')
    tahis = Column(String(20)) # tähis
    etestikohti = Column(Integer) # kohti e-testi sooritajatele
    ptestikohti = Column(Integer) # kohti p-testi sooritajatele
    staatus = Column(Integer, nullable=False) # olek
    varustus = Column(String(512)) # varustus
    testiruumid = relationship('Testiruum', back_populates='ruum') 

    def default(self):
        if not self.staatus:
            self.staatus = const.B_STAATUS_KEHTIV

    @property
    def staatus_nimi(self):
        if self.staatus == const.B_STAATUS_KEHTIV:
            return usersession.get_opt().STR_KEHTIV
        elif self.staatus == const.B_STAATUS_KEHTETU:
            return usersession.get_opt().STR_KEHTETU

    def update_testiruumid(self):
        from eis.model.testimine import Testiruum, Testikoht, Toimumisaeg
        from eis.model.test import Testiosa

        if not self.id:
            self.flush()

        q = (Testiruum.query.filter_by(ruum_id=self.id)
             .filter(Testiruum.algus>=date.today())
             .join(Testiruum.testikoht)
             .join(Testikoht.toimumisaeg)
             .join(Toimumisaeg.testiosa))

        vastvorm_p = (const.VASTVORM_KP, const.VASTVORM_SP)
        vastvorm_e = (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I, const.VASTVORM_SH)
        qp = (q.filter(Testiosa.vastvorm_kood.in_(vastvorm_p))
              .filter(sa.or_(Testiruum.kohti==None,
                             Testiruum.kohti!=self.ptestikohti))
              )
        for rcd in qp.all():
            rcd.kohti = self.ptestikohti

        qe = (q.filter(Testiosa.vastvorm_kood.in_(vastvorm_e))
              .filter(sa.or_(Testiruum.kohti==None,
                             Testiruum.kohti!=self.etestikohti))
              )
        for rcd in qe.all():
            rcd.kohti = self.etestikohti

    @property
    def in_use(self):
        from eis.model.testimine import Testiruum
        q = SessionR.query(Testiruum.id).filter(Testiruum.ruum==self)
        return q.first() is not None
