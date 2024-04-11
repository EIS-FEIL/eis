"Testikorralduse andmemudel"

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.test import *
from .hindamisolek import Hindamisolek

class Tagastusymbrik(EntityHelper, Base):
    """Testiprotokollirühma ja tagastusümbrikuliigiga seotud tagastusümbrike kogus. 
    Igast tagastusümbrikuliigist on oma ümbrik.
    Ilma liigita ümbrik on peaümbrik.
    Kui protokollirühma suurus on suurem kui tagastusümbriku maht, siis on ühe 
    kirje kohta tegelikkuses mitu ümbrikut (sama numbriga). 
    Eeldame, et kõiki ühele kirjele vastavaid ümbrikke liigutatakse alati koos.
    See on sellepärast nii, et vastasel juhul tekiks ümbrike 
    hindajatele hindamiseks väljastamisel probleem,
    kuna ei ole teada, milliste sooritajate tööd millises ümbrikus asuvad.
    Kui ühe protokolli ümbrikud satuks erinevate hindajate kätte,
    siis poleks teada, milliste sooritajate tööd milliste hindajate käes on.
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    tahised = Column(String(54), nullable=False) # tagastusümbrikuliigile vastava ümbriku korral: testi, testiosa, testimiskorra, testikoha, testiprotokolli, tagastusümbrikuliigi tähised, kriips vahel (2 protokolli ümbrikul on testiprotokollide tähised kaldkriipsuga eraldatud); peaümbriku korral: testi, testiosa, testimiskorra, testikoha tähised, kriips vahel (peaümbriku korral ei ole tähis unikaalne, kuna kõigil sama koha testipakettidel on sama tähis; triipkoodile trükitakse seepärast lisaks tähisele ka paketi keele kood)
    testipakett_id = Column(Integer, ForeignKey('testipakett.id'), index=True, nullable=False) # viide testipaketile
    testipakett = relationship('Testipakett', foreign_keys=testipakett_id, back_populates='tagastusymbrikud')
    testiprotokoll_id = Column(Integer, ForeignKey('testiprotokoll.id'), index=True) # viide testiprotokollile; kui puudub, siis on peaümbrik
    testiprotokoll = relationship('Testiprotokoll', foreign_keys=testiprotokoll_id, back_populates='tagastusymbrikud')
    testiprotokoll2_id = Column(Integer, ForeignKey('testiprotokoll.id'), index=True) # viide teisele testiprotokollile, kui tagastusymbrikuliik.arvutus=2
    testiprotokoll2 = relationship('Testiprotokoll', foreign_keys=testiprotokoll2_id)
    tagastusymbrikuliik_id = Column(Integer, ForeignKey('tagastusymbrikuliik.id'), index=True) # tagastusümbrikuliik; kui puudub, siis on peaümbrik
    tagastusymbrikuliik = relationship('Tagastusymbrikuliik', foreign_keys=tagastusymbrikuliik_id, back_populates='tagastusymbrikud')
    staatus = Column(Integer, sa.DefaultClause('1'), nullable=False) # olek, M_STAATUS
    labiviija_id = Column(Integer, ForeignKey('labiviija.id'), index=True) # viide hindajale (või hindajate paarile), kui ümbrik on hindajale hindamiseks väljastatud
    labiviija = relationship('Labiviija', foreign_keys=labiviija_id)
    ymbrikearv = Column(Integer, sa.DefaultClause('1'), nullable=False) # ümbrike arv, mis on saadud tööde arvu jagamisel ümbriku mahuga
    valjastatud = Column(DateTime) # hindajale väljastamise aeg, vajalik hindaja ümbrike sortimiseks väljastamise järjekorras
    arvutus = Column(Integer) # arvutusprotsessi tunnus
    __table_args__ = (
        sa.UniqueConstraint('testipakett_id', 'testiprotokoll_id','tagastusymbrikuliik_id'),
        )
    _parent_key = 'testipakett_id'

    @property
    def staatus_nimi(self):
        return usersession.get_opt().M_STAATUS.get(self.staatus)

    @property
    def tehtud_toodearv(self):
        from .sooritus import Sooritus
        if self.testiprotokoll_id:
            tyl = self.tagastusymbrikuliik
            if tyl:
                # kui ymbriku liik on seotud hindamiskogumitega, siis arvestame neid sooritajaid,
                # kes on vähemalt yht neist hindamiskogumitest teinud
                li_hk_id = [hk.id for hk in tyl.hindamiskogumid]
                if li_hk_id:
                    q = (Session.query(sa.func.count(Sooritus.id))
                         .filter(Sooritus.testiprotokoll_id==self.testiprotokoll_id)
                         .filter(Sooritus.staatus==const.S_STAATUS_TEHTUD)
                         .filter(Sooritus.hindamisolekud.any(
                             sa.and_(Hindamisolek.hindamiskogum_id.in_(li_hk_id),
                                     Hindamisolek.puudus==False))
                                 )
                         )
                    return q.scalar()
        tpr = self.testiprotokoll
        if tpr:
            return tpr.tehtud_toodearv
