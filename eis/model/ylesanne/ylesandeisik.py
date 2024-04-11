"Ülesande andmemudel"

from eis.model.entityhelper import *

class Ylesandeisik(EntityHelper, Base):
    """Ülesandega seotud isik
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    kasutajagrupp_id = Column(Integer, ForeignKey('kasutajagrupp.id'), index=True, nullable=False) # viide kasutajagrupile
    kasutajagrupp = relationship('Kasutajagrupp', foreign_keys=kasutajagrupp_id)
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True) # viide ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='ylesandeisikud')
    kehtib_alates = Column(Date, nullable=False) # õiguste kehtimise algus
    kehtib_kuni = Column(Date, nullable=False) # õiguste kehtimise lõpp
    _parent_key = 'ylesanne_id'

    @classmethod
    def has_role(cls, group_id, kasutaja_id, ylesanne_id):
        today = date.today()
        q = (SessionR.query(sa.func.count(Ylesandeisik.id))
             .filter(Ylesandeisik.kasutaja_id==kasutaja_id)
             .filter(Ylesandeisik.ylesanne_id==ylesanne_id)
             .filter(Ylesandeisik.kehtib_alates<=today)
             .filter(Ylesandeisik.kehtib_kuni>=today)
             )
        if group_id:
            q = q.filter(Ylesandeisik.kasutajagrupp_id==group_id)
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

    def default(self):
        if not self.kehtib_alates:
            self.kehtib_alates = const.MIN_DATE
        if not self.kehtib_kuni:
            self.kehtib_kuni = const.MAX_DATE
    
    def pack_exp(self):
        """
        Pakkimine raw-eksportimiseks:
        kasutaja_id asemel _kasutaja_ik
        """
        di = {'class': self.__class__.__name__,
              '_kasutaja_ik': self.kasutaja.isikukood,
              'kasutajagrupp_id': self.kasutajagrupp_id,
              'kehtib_alates': self.kehtib_alates,
              'kehtib_kuni': self.kehtib_kuni,
              'ylesanne_id': self.ylesanne_id,
              }
        return [di]

