"Logi andmebaas"
from .entityhelper import *
import eis.model.usersession as usersession
from .meta import Base, DBSession
import os
import logging
log = logging.getLogger(__name__)

class Logi(Base):
    """Sündmuste ja veateadete logi
    """
    __tablename__ = 'logi'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(32), index=True) # logikirje identifikaator
    request_id = Column(String(32), index=True) # brauseri pöördumise identifikaator
    aeg = Column(DateTime, nullable=False, index=True) # logikirje aeg
    isikukood = Column(String(50), index=True) # kasutaja isikukood
    kontroller = Column(String(50)) # rakenduse kontroller, milles logisündmus tekkis (või muu lk identifikaator)
    tegevus = Column(String(50)) # rakenduse tegevus, milles logisündmus tekkis 
    param = Column(Text) # rakenduse parameetrid, kui logisündmus tekkis
    tyyp = Column(Integer, index=True) # logitüüp: 1 - kasutuslogi; 2 - vealogi; 3 - sisselogimise logi; 4 - kasutajaõiguste muutmine; 5 - X-tee kliendi sõnumite logi; 6 - muu info; 7 - JSON sõnum; 8 - koha valik; 9 - webhook
    sisu = Column(Text) # logi sisu
    url = Column(String(200)) # tegevuse URL
    path = Column(String(160), index=True) # URLis sisalduv rada
    meetod = Column(String(10)) # HTTP meetod (get, post)
    remote_addr = Column(String(60)) # klient
    server_addr = Column(String(60)) # server
    user_agent = Column(String(150)) # brauser
    app = Column(String(10)) # rakendus: eis, ekk, plank, adapter
    koht_id = Column(Integer) # viide töökohale
    oppekoht_id = Column(Integer) # viide koolile, kus kasutaja õpib
    testiosa_id = Column(Integer) # viide testiosale, kui see on testi sooritamisel tekkinud logi (testisoorituste arvu saamiseks ajavahemikul)
    kestus = Column(Float) # päringu kestus sekundites
    logging = False

    @classmethod
    def add_logrow(cls, data):
        def _max(value, n):
            return value and value[:n] or None
        item = Logi(uuid=data['uuid'],
                    request_id=data['request_id'],
                    aeg=data['aeg'],
                    isikukood=data['isikukood'],
                    kontroller=data['kontroller'],
                    tegevus=data['tegevus'],
                    param=data['param'],
                    sisu=data['sisu'],
                    tyyp=data['tyyp'],
                    koht_id=data['koht_id'],
                    oppekoht_id=data['oppekoht_id'],
                    testiosa_id=data['testiosa_id'],
                    kestus=data['kestus'],
                    remote_addr=_max(data['remote_addr'], 60),
                    url=_max(data['url'], 200),
                    path=_max(data['path'], 160),
                    meetod=data['meetod'],
                    server_addr=_max(data['server_addr'], 60),
                    user_agent=_max(data['user_agent'], 150),
                    app=data['app'])
        DBSession.add(item)
        
    @property
    def tyyp_nimi(self):
        return usersession.get_opt().LOG_TYPES.get(self.tyyp) or self.tyyp

    def before_insert(self):
        if not self.aeg:
            self.aeg = datetime.now()
        if not self.isikukood:
            user = usersession.get_user()
            if user:
                self.isikukood = user.isikukood

    def before_update(self):
        pass
