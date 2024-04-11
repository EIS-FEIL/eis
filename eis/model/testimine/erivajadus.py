"Testikorralduse andmemudel"
from eis.model.entityhelper import *
from eis.model.usersession import get_opt
from .sooritus import Sooritus

class Erivajadus(EntityHelper, Base):
    """Sooritajate eritingimused
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    erivajadus_kood = Column(String(10)) # eritingimused vanade kirjete korral, eritingimuste klassifikaator ERIVAJADUS
    taotlus = Column(Boolean) # kas eritingimusi on taotletud
    taotlus_markus = Column(Text) # selgitus eritingimuste taotlemise juurde
    kinnitus = Column(Boolean) # kas eritingimused on kinnitatud
    kinnitus_markus = Column(Text) # selgitus eritingimuste kinnitamise juurde
    sooritus_id = Column(Integer, ForeignKey('sooritus.id'), index=True, nullable=False) # viide soorituse kirjele
    sooritus = relationship('Sooritus', foreign_keys=sooritus_id, back_populates='erivajadused')
    kasutamata = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas lubatud eritingimust ei kasutatud (märgitakse toimumise protokollile)
    _parent_key = 'sooritus_id' 

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        sooritus = self.sooritus or \
            self.sooritus_id and Sooritus.get(self.sooritus_id)
        if sooritus:
            sooritus.logi('Erivajadus %s %s' % (self.id, liik), vanad_andmed, uued_andmed, logitase)

    @classmethod
    def pole_vaja_kinnitust(cls, kood, test):
        # põhikooli esimese 10 eritingimuse taotlused ei vaja Innoves kinnitamist
        # (välja arvatud aines "eesti keel teise keelena", vt ES-1437)
        if test.aine_kood == const.AINE_ET2:
            return False
        li = get_opt().klread_kood('ERIVAJADUS', kinnituseta=True)
        KOODID_KINNITUSETA = [r[0] for r in li]
        return kood in KOODID_KINNITUSETA
    
    def ei_vaja_kinnitust(self, test):
        return Erivajadus.pole_vaja_kinnitust(self.erivajadus_kood, test)
