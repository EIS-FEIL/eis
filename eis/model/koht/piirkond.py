from eis.model.entityhelper import *
from eis.model.klassifikaator import Klrida

from .koht import Koht

class Piirkond(EntityHelper, Base):
    """Testide korraldamise piirkond
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    nimi = Column(String(100)) # nimi
    ylem_id = Column(Integer, ForeignKey('piirkond.id'), index=True)  # viide ülemale piirkonnale, mille alampiirkond on antud piirkond
    ylem = relationship('Piirkond', foreign_keys=ylem_id, remote_side=id, back_populates='alamad')
    alamad = relationship('Piirkond', back_populates='ylem') # alampiirkonnad
    kohad = relationship('Koht', back_populates='piirkond') # soorituskohad antud piirkonnas
    staatus = Column(Integer, nullable=False) # olek
    kasutajapiirkonnad = relationship('Kasutajapiirkond', back_populates='piirkond')
    
    def default(self):
        if not self.staatus:
            self.staatus = const.B_STAATUS_KEHTIV

    @property
    def staatus_nimi(self):
        if self.staatus == const.B_STAATUS_KEHTIV:
            return usersession.get_opt().STR_KEHTIV
        elif self.staatus == const.B_STAATUS_KEHTETU:
            return usersession.get_opt().STR_KEHTETU

    @classmethod
    def get_tree(cls):
        li = list(cls.query.order_by(Piirkond.nimi).all())
        roots = []
        for rcd in li:
            if not rcd.ylem:
                roots.append(rcd)
        return roots

    @classmethod
    def get_str(cls, id):
        if id:
            item = cls.get(id)
            if item:
                return item.nimi
    
    def get_kohad_q(self):
        """Leitakse soorituskohad antud piirkonnas ja selle alampiirkonnis
        """
        f = []
        for prk_id in self.get_alamad_id():
            f.append(Koht.piirkond_id==prk_id)
        q = Koht.query.\
            filter(Koht.on_soorituskoht==True).\
            filter(sa.or_(*f))
        return q

    def get_kohad(self):
        """Leitakse soorituskohad antud piirkonnas ja selle alampiirkonnis
        """
        return self.get_kohad_q().order_by(Koht.nimi).all()

    @classmethod
    def get_opt_prk(cls, ylem_id, filtered=None):
        """Koostatakse antud piirkonna vahetute alamate loetelu
        filtered on list/set lubatud id-dest või None
        """
        if ylem_id == 0:
            return []
        li = []
        q = cls.query.\
            filter_by(staatus=const.B_STAATUS_KEHTIV).\
            filter_by(ylem_id=ylem_id)
        for rcd in q.order_by(Piirkond.nimi):
            if not filtered or rcd.id in filtered:
                li.append((rcd.id, rcd.nimi))
        return li

    @classmethod
    def get_ylemad_n(cls, id, n):
        """Koostatakse täpselt n-pikkune list ylematest või 0-dest
        """
        li = []
        if id:
            rcd = cls.get(id)
            li = rcd.get_ylemad_id()
        while len(li) < n:
            li.append(0)
        return li

    def get_nimi_ylematega(self):
        if self.ylem:
            return self.ylem.get_nimi_ylematega() + ', ' + self.nimi
        else:
            return self.nimi

    def get_opt_kohad(self):
        """Leitakse soorituskohad antud piirkonnas ja selle alampiirkonnis
        """
        return [(rcd.id, rcd.nimi) for rcd in self.get_kohad()]

    def get_parents(self):
        if self.ylem_id:
            return self.ylem.get_parents() + [self.ylem]
        else:
            return []

    def get_alamad_id(self):
        li = [self.id]
        for rcd in self.alamad:
            li += rcd.get_alamad_id()
        return li

    def get_ylemad_id(self):
        li = [self.id]
        if self.ylem_id:
            li = self.ylem.get_ylemad_id() + li
        return li

    def has_permission(self, permission, perm_bit, user=None):
        """Kontrollitakse jooksva kasutaja õigust 
        antud tegevusele antud kohal.
        """
        if not user:
            user = usersession.get_user()
        if not user:
            return False

        rc = False
        kasutaja = user.get_kasutaja()
        if kasutaja:
            rc = kasutaja.has_permission(permission, perm_bit, piirkond_id=self.id)
        return rc
