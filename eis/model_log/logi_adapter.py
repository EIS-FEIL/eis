"Logi andmebaas"
from eiscore.entitybase import *
from .meta import Base, DBSession

class Logi_adapter(Base):
    """X-tee serveri logi
    """
    __tablename__ = 'logi_adapter'
    id = Column(Integer, primary_key=True, autoincrement=True)
    algus = Column(DateTime) # päringu alguse aeg
    aeg = Column(DateTime, nullable=False, index=True) # logikirje aeg (päringu lõpp)
    client = Column(String(100)) # kliendi andmed
    userid = Column(String(66)) # riigi kood ja isikukood
    service = Column(String(50)) # kasutatud teenuse nimi
    input_xml = Column(Text) # sisendi XML/JSON
    output_xml = Column(Text) # väljundi XML/JSON
    remote_addr = Column(String(60)) # klient
    server_addr = Column(String(60)) # server
    url = Column(Text) # URL
    tyyp = Column(String(1)) # J - JSON; X - XML

    TYYP_JSON = 'J'
    TYYP_XML = 'X'
    
    @classmethod
    def add(cls, client, userid, service, input_xml, output_xml, started, request, tyyp=None):
        "X-tee sõnumite logimine"
        if not tyyp and request.content_type == 'application/json':
            tyyp = cls.TYYP_JSON
        else:
            tyyp = cls.TYYP_XML
        item = Logi_adapter(
            aeg=datetime.now(),
            client=client,
            userid=userid,
            service=service,
            input_xml=input_xml,
            output_xml=output_xml,
            algus=started,
            tyyp=tyyp)

        def _max(value, n):
            return value and value[:n] or None
        
        environ = request.environ
        remote_addr = request.remote_addr
        item.remote_addr = _max(remote_addr, 60)
        server_addr = environ.get('HOSTNAME') or environ.get('SERVER_ADDR')
        item.server_addr = _max(server_addr, 60)
        item.url = request.url
        DBSession.add(item)
        DBSession.flush()
        return item.id

    def before_insert(self):
        pass
    
    def before_update(self):
        pass

