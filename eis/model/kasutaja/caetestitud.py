from eis.model.entityhelper import *
log = logging.getLogger(__name__)
  
class Caetestitud(EntityHelper, Base):
    """Õppurite isikukoodid, kes on sooritanud CAE eeltesti,
    mis on üks eeltingimusi CAE rahvusvahelisele eksamile registreerimiseks
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    isikukood = Column(String(50), unique=True) # isikukood

    @classmethod
    def get_by_ik(cls, ik):
        return cls.query.filter_by(isikukood=ik).first()
    
