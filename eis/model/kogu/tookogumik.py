"Töökogumik"

from eis.model.entityhelper import *
from .tkvaataja import Tkvaataja
from .tkosa import Tkosa
from .tkylesanne import Tkylesanne
_ = usersession._

class Tookogumik(EntityHelper, Base):
    """Töökogumik
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    nimi = Column(String(100), nullable=False) # nimekirja nimetus
    aine_kood = Column(String(10)) # õppeaine, klassifikaator AINE
    klass = Column(String(10)) # klass
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # töökogumiku omanik
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    avalik = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas kõik pedagoogid võivad seda töökogumikku vaadata
    tkosad = relationship('Tkosa', order_by='Tkosa.seq', back_populates='tookogumik')
    tkvaatajad = relationship('Tkvaataja', back_populates='tookogumik')
    
    def delete_subitems(self):    
        self.delete_subrecords(['tkosad',
                                'tkvaatajad',
                                ])

    def copy(self):
        cp = EntityHelper.copy(self)
        for osa in self.tkosad:
            if not osa.ylem_tkosa_id:
                cp_osa = osa.copy(cp)
        cp.avalik = False
        return cp
    
    @property
    def ylesannete_arv(self):
        from .tkosa import Tkosa
        from .tkylesanne import Tkylesanne
        cnt = 0
        if self.id:
            q = (SessionR.query(sa.func.count(Tkylesanne.id))
                 .join(Tkylesanne.tkosa)
                 .filter(Tkosa.tookogumik_id==self.id)
                 )
            cnt = q.scalar()
        return cnt

    @property
    def testide_arv(self):
        from .tkosa import Tkosa
        from .tktest import Tktest
        cnt = 0
        if self.id:
            q = (SessionR.query(sa.func.count(Tktest.id))
                 .join(Tktest.tkosa)
                 .filter(Tkosa.tookogumik_id==self.id)
                 )
            cnt = q.scalar()
        return cnt

    @classmethod
    def minu_tookogumik(cls, kasutaja_id):
        "Leitakse või luuakse see töökogumik, kuhu vaikimisi pannakse omatehtud ülesanded"
        nimi = _("Minu koostatud")
        item = (Session.query(Tookogumik)
                .filter_by(kasutaja_id=kasutaja_id)
                .filter_by(nimi=nimi)
                .first())
        if not item:
            item = cls.lisa_tookogumik(kasutaja_id)
            item.nimi = nimi
        return item

    @classmethod
    def lisa_tookogumik(cls, kasutaja_id):
        item = Tookogumik(kasutaja_id=kasutaja_id,
                          nimi=_('Töökogumik'))
        tkosa = Tkosa(tookogumik=item,
                      seq=1)
        return item
    
    @classmethod
    def lisa_ylesanne(cls, kasutaja_id, ylesanne_id, tookogumik_id):
        "Ülesande lisamine töökogumikku"
        if tookogumik_id:
            # lisame antud töökogumikku
            tk = Tookogumik.get(tookogumik_id)
        else:
            # lisame vaikimisi töökogumikku
            tk = cls.minu_tookogumik(kasutaja_id)
        if not tk or tk.kasutaja_id != kasutaja_id:
            return
        for tkosa in tk.tkosad:
            break
        if not tkosa:
            tkosa = Tkosa(tookogumik=tk,
                          seq=1)
            Session.flush()
        q = (Session.query(Tkylesanne.id)
             .filter(Tkylesanne.tkosa_id==tkosa.id)
             .filter(Tkylesanne.ylesanne_id==ylesanne_id)
             )
        if q.count() == 0:
            item = Tkylesanne(tkosa=tkosa,
                              ylesanne_id=ylesanne_id)
            return True

    @classmethod
    def get_opt(cls, kasutaja_id, ylesanne_id):
        "Kasutaja töökogumikud koos infoga, kas antud ylesanne on töökogumikus või mitte"
        q = (Session.query(Tookogumik.id, Tookogumik.nimi, sa.func.count(Tkylesanne.id))
             .filter_by(kasutaja_id=kasutaja_id)
             .join(Tookogumik.tkosad)
             .outerjoin((Tkylesanne,
                         sa.and_(Tkylesanne.tkosa_id==Tkosa.id,
                                 Tkylesanne.ylesanne_id==ylesanne_id)))
             .group_by(Tookogumik.id, Tookogumik.nimi)
             .order_by(Tookogumik.nimi)
             )
        return [(r[0], r[1], r[2]) for r in q.all()]
    
    def has_permission(self, permission, perm_bit, lang=None, user=None):
        """Kontrollitakse jooksva kasutaja õigust 
        antud tegevusele antud kogus
        """
        if not user:
            user = usersession.get_user()
        rc = user and self.kasutaja_id == user.id
        if not rc and perm_bit == const.BT_SHOW:
            # kasutaja pole omanik
            # vaatame, kas on vaatamise õigus
            if self.avalik:
                # avalik töökogumik on nähtav kõigile pedagoogidele
                rc = user.has_permission('tookogumikud', const.BT_INDEX)
            if not rc:
                # kas on jagatud
                q = (SessionR.query(sa.func.count(Tkvaataja.id))
                     .filter(Tkvaataja.tookogumik_id==self.id)
                     .filter(Tkvaataja.kasutaja_id==user.id))
                if q.scalar():
                    rc = True
            
        return rc
