import hashlib
from datetime import datetime, timedelta
from eis.model.entityhelper import *
log = logging.getLogger(__name__)

class Paring_logi(EntityHelper, Base):
    """X-tee teenuste kasutamise logi
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    isikukood = Column(String(50)) # X-tee päise isikukood, teenuse kasutaja
    paring = Column(String(30), nullable=False) # X-tee teenuse nimi
    asutus = Column(String(30), nullable=False) # X-tee päise asutus (v4 MemberCode), teenuse kasutaja
    paritav = Column(String(50)) # isiku isikukood, kelle andmeid päritakse
    aeg = Column(DateTime, nullable=False) # esimese eksimuse aeg
    klient = Column(String(512)) # X-tee protokolli v4 päise klient, teenuse kasutaja
    
    @classmethod
    def log(cls, xrheader, paritav=None):
        
        client = xrheader.client
        if client:
            # v4 klient
            klient = '.'.join([client.xRoadInstance,
                               client.memberClass,
                               client.memberCode,
                               client.subsystemCode])
            asutus = client.memberCode
            paring = xrheader.service.serviceCode
        else:
            klient = asutus = xrheader.consumer
            paring = xrheader.service
            
        isikukood = xrheader.userId
        if paritav and len(paritav) != 11:
            from eis.lib.pyxadapterlib.xutils import SoapFault
            raise SoapFault('Server.Adapter.InvalidCode', 'Vigane isikukood')
        if isikukood and len(isikukood) > 25:
            from eis.lib.pyxadapterlib.xutils import SoapFault
            raise SoapFault('Server.Adapter.InvalidUserId', 'Vigane kasutaja isikukood')
        cls(isikukood=isikukood,
            paring=paring,
            asutus=asutus,
            klient=klient,
            aeg=datetime.now(),
            paritav=paritav)

        Session.commit()

