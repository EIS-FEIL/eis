
import json
from eis.model.entityhelper import *

class Verifflog(EntityHelper, Base):
    """Veriff verifitseerimispäringute logi
    """
    __tablename__ = 'verifflog'    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sooritus_id = Column(Integer) # soorituse ID, millelt verifitseerimisele suunati
    kasutaja_id = Column(Integer) # kasutaja ID
    session_id = Column(String(36), index=True) # Veriff sessiooni ID
    sess_data = Column(Text) # sessiooni loomise päringu vastus (json)
    started = Column(DateTime) # verifitseerimise algus veriffis (webhooki saamise aeg)
    submitted = Column(DateTime) # verifitseerimise lõpp veriffis (webhooki saamise aeg)
    dec_data = Column(Text) # verifitseerimise otsuse andmed (json)
    code = Column(Integer) # verifitseerimise tulemuse kood (9001,9102,9103,9104,9121)
    riik = Column(String(2)) # verifitseerimisel kasutatud dokumendi riik
    isikukood = Column(String(50)) # verifitseeritud isikukood
    rc = Column(Boolean) # True - verifitseeritud isik on sama, mis autenditud; False - ei ole sama või ei saanud verifitseerida

    DEC_NONE = 0
    DEC_9001_OK = 90010
    DEC_9001_NOK = 90011
    
    @classmethod
    def opt_dec(cls):
        return ((cls.DEC_NONE, 'otsus puudub'),
                (cls.DEC_9001_OK, 'positiivne otsus ja sama isik'), # approved
                (cls.DEC_9001_NOK, 'positiivne otsus, aga vale isik'), # approved
                (9102, 'negatiivne otsus'), # declined
                (9103, 'vajab kordamist'), # resubmission_requested
                (9104, 'aegunud'), # abandoned/expired
                (9121, 'ülevaatamisel')) # review

    @classmethod
    def dec_desc(cls, code, rc):
        if code == 9001 and rc:
            code = cls.DEC_9001_OK
        elif code == 9001 and not rc:
            code = cls.DEC_9001_NOK
        for key, value in cls.opt_dec():
            if key == code:
                return value

    @property
    def sess_json(self):
        try:
            return json.loads(self.sess_data)
        except:
            return {}

    @property
    def dec_json(self):
        try:
            return json.loads(self.dec_data)
        except:
            return {}
