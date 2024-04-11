"Logi andmebaas"
from eiscore.entitybase import *
from .meta import Base, DBSession

class Ltest(Base):
    """Koormustesti logiandmed
    """
    # vt WrapSession
    __tablename__ = 'ltest'
    id = Column(Integer, primary_key=True, autoincrement=True)
    aeg = Column(DateTime, nullable=False, index=True) # logikirje aeg
    algus = Column(DateTime) # pöördumise alguse aeg (sama pöördumise transaktsioonide sidumiseks)
    isikukood = Column(String(50)) # kasutaja isikukood
    kestus = Column(Integer) # transaktsiooni kestus ms
    liik = Column(String(20)) # transaktsiooni lõpp: commit/rollback
    url = Column(String(200)) # tegevuse URL
    meetod = Column(String(10)) # HTTP meetod (get, post)
    remote_addr = Column(String(60)) # klient
    server_addr = Column(String(60)) # server
    user_agent = Column(String(150)) # brauser
    test_jrk = Column(Integer) # koormustesti jrk nr (omistatakse peale testi lõppu)
    logging = False

    @classmethod
    def add(cls, msec, liik, inited, request):
        item = Ltest(kestus=msec, liik=liik, algus=inited)
        if request:
            item.set_request(request)
        DBSession.add(item)
        DBSession.flush()
        return item.id

    def set_request(self, request):
        def _max(value, n):
            return value and value[:n] or None
        environ = request.environ
        remote_addr = request.remote_addr
        self.url = _max(request.url, 200)
        self.meetod = request.method
        self.remote_addr = _max(remote_addr, 60)
        server_addr = environ.get('HOSTNAME') or environ.get('SERVER_ADDR')
        self.server_addr = _max(server_addr, 60)
        self.user_agent = _max(environ.get('HTTP_USER_AGENT'), 150)

    def before_insert(self):
        self.aeg = datetime.now()
        if not self.isikukood:
            self.isikukood = usersession.get_userid()        
        
    def before_update(self):
        pass
