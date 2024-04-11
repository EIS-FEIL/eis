"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import Opt
from eis.model.kasutaja import *
from eis.model.koht import *

class Testiisik(EntityHelper, Base):
    """Testiga seotud isik
    """
   
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    kasutajagrupp_id = Column(Integer, ForeignKey('kasutajagrupp.id'), index=True, nullable=False) # viide kasutajagrupile
    kasutajagrupp = relationship('Kasutajagrupp', foreign_keys=kasutajagrupp_id)
    test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False) # viide testile
    test = relationship('Test', foreign_keys=test_id, back_populates='testiisikud')
    kehtib_alates = Column(Date, nullable=False) # õiguse kehtimise algus
    kehtib_kuni = Column(Date, nullable=False) # õiguse kehtimise lõpp
    _parent_key = 'test_id'

    @classmethod
    def has_role(cls, group_id, kasutaja_id, test_id):
        today = date.today()
        q = (SessionR.query(sa.func.count(Testiisik.id))
             .filter(Testiisik.kasutaja_id==kasutaja_id)
             .filter(Testiisik.test_id==test_id)
             .filter(Testiisik.kasutajagrupp_id==group_id)
             .filter(Testiisik.kehtib_alates<=today)
             .filter(Testiisik.kehtib_kuni>=today)
             )
        return bool(q.scalar())
    
    @property
    def kehtib_kuni_ui(self):
        """Andmebaasis on kuupäeval väärtus, mida kasutajale ei näidata.
        """
        if self.kehtib_kuni >= const.MAX_DATE:
            return None
        else:
            return self.kehtib_kuni

    @property
    def kehtiv(self):
        return not self.kehtib_kuni or self.kehtib_kuni >= date.today()

    @property
    def kehtiv_str(self):
        if self.kehtiv:
            return usersession.get_opt().STR_KEHTIV
        else:
            return usersession.get_opt().STR_KEHTETU

    def get_permissions(self):
        return self.kasutajagrupp.get_permissions()

    def has_permission(self, permission, perm_bit):

        role_perms = self.get_permissions()
        p = role_perms.get(permission)
        return p and p & perm_bit

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .test import Test
        test = self.test or self.test_id and Test.get(self.test_id)
        if test:
            test.logi('Testiisik %s %s' % (self.id, liik), vanad_andmed, uued_andmed, logitase)

    def default(self):
        if not self.kehtib_alates:
            self.kehtib_alates = const.MIN_DATE
        if not self.kehtib_kuni:
            self.kehtib_kuni = const.MAX_DATE

