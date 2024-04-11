from eis.model.entityhelper import *
from eis.model.koht import Koht
from eis.model.klassifikaator import Klrida

log = logging.getLogger(__name__)

from .kasutajaoigus import Kasutajaoigus

class Kasutajagrupp(EntityHelper, Base):
    """Kasutajagrupp
    """
    id = Column(Integer, primary_key=True)
    
    nimi = Column(String(50)) # grupi nimi
    kirjeldus = Column(String(255)) # kirjeldus
    tyyp = Column(Integer, nullable=False) # grupi tüüp: 1=const.USER_TYPE_EKK - eksamikeskuse kasutaja; 2=const.USER_TYPE_Y - grupp isiku sidumiseks ülesandega; 3=const.USER_TYPE_T - grupp isiku sidumiseks testiga; 4=const.USER_TYPE_KOOL - soorituskoha kasutaja; 5=const.USER_TYPE_AV - EKK vaate avalik kasutaja
    staatus = Column(Integer, nullable=False) # olek: 1 - kehtib; 0 - kehtetu
    max_koormus = Column(Integer) # maksimaalne kasutajate arv, mille korral selle grupi kasutajal lubatakse sisse logida
    kasutajarollid = relationship('Kasutajaroll', back_populates='kasutajagrupp')
    pedagoogid = relationship('Pedagoog', back_populates='kasutajagrupp')    
    kasutajagrupp_oigused = relationship('Kasutajagrupp_oigus')

    @property
    def on_ylesandegrupp(self):
        """Kas grupp annab õiguse konkreetsele ülesandele
        """
        return self.id in (const.GRUPP_Y_KOOSTAJA,
                           const.GRUPP_Y_VAATAJA,
                           const.GRUPP_Y_TOIMETAJA,
                           const.GRUPP_Y_TOLKIJA,
                           const.GRUPP_Y_KUJUNDAJA)
    
    @property
    def on_testigrupp(self):
        """Kas grupp annab õiguse konkreetsele testile
        """
        return self.id in (const.GRUPP_T_KOOSTAJA,
                           const.GRUPP_T_VAATAJA,
                           const.GRUPP_T_TOIMETAJA,
                           const.GRUPP_T_TOLKIJA,
                           const.GRUPP_T_KUJUNDAJA)

    ainegrupid = (const.GRUPP_AINESPETS,
                  const.GRUPP_OSASPETS,
                  const.GRUPP_E_KORRALDUS,
                  const.GRUPP_AINETOORYHM,
                  const.GRUPP_T_KOOSTAJA,
                  const.GRUPP_HINDAMISJUHT,
                  const.GRUPP_HINDAMISEKSPERT)

    @property
    def on_ainegrupp(self):
        """Kas grupp annab õiguse mingi aine kõigile ülesannetele
        """
        return self.id in self.ainegrupid
        
    @property
    def on_ametnikugrupp(self):
        """Kas on EKK ametnike grupp
        """
        return self.tyyp in (const.USER_TYPE_EKK, const.USER_TYPE_AV)

    @property
    def on_avalikgrupp(self):
        """Kas on avalik grupp
        """
        return self.tyyp == const.USER_TYPE_TEST

    @classmethod
    def options(cls):
        return [(o.id, o.nimi) for o in cls.query.order_by(Kasutajagrupp.nimi).all()]

    @classmethod
    def get_oigused(cls, grupp_id):
        grupp = Kasutajagrupp.getR(grupp_id)
        oigused = {}
        if grupp:
            for ko in grupp.kasutajagrupp_oigused:
                oigused[ko.nimi] = ko.bitimask
        return oigused
    
    def lisaoigused(self, oigused):
        from .kasutajagrupp_oigus import Kasutajagrupp_oigus

        for (nimi,bitimask) in oigused:
            oigus = Kasutajaoigus.get_by(nimi=nimi)
            if not oigus:
                raise Exception('Puudub kasutajaoigus "%s"' % nimi)
            kg_oigus = Kasutajagrupp_oigus(kasutajagrupp=self,
                                           kasutajaoigus=oigus,
                                           nimi=oigus.nimi,
                                           bitimask=bitimask)
            self.kasutajagrupp_oigused.append(kg_oigus)
            #self.kasutajaoigused.append(oigus)

    def default(self):
        if not self.staatus:
            self.staatus = const.B_STAATUS_KEHTIV

    @property
    def staatus_nimi(self):
        if self.staatus == const.B_STAATUS_KEHTIV:
            return usersession.get_opt().STR_KEHTIV
        elif self.staatus == const.B_STAATUS_KEHTETU:
            return usersession.get_opt().STR_KEHTETU

    def set_modifier(self):
        EntityHelper.set_modifier(self)

        for kgo in self.kasutajagrupp_oigused:
            kgo.grupp_tyyp = self.tyyp
            kgo.grupp_staatus = self.staatus

    def has_permission(self, permission, perm_bit):
        # autenditud kasutaja
        role_perms = self.get_permissions()
        p = role_perms.get(permission)
        return p and p & perm_bit

    def get_permissions(self):
        permissions = dict()
        for o in self.kasutajagrupp_oigused:
            permissions[o.nimi] = o.bitimask
        return permissions

