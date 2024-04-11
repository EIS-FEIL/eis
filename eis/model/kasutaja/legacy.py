from eis.model.entityhelper import *

class Legacy(EntityHelper, Base):
    "X-tee kaudu autentimise (legacyXYZ teenusega suunamise) andmed"
    
    id = Column(Integer, primary_key=True)
    kood = Column(String(32), nullable=False) # genereeritud juhuarv, mille seostab URLi kirjega
    risikukood = Column(String(50), nullable=False) # riik ja isikukood, X-tee päisevälja userId väärtus
    eesnimi = Column(String(50)) # X-tee päisevälja userName algus kuni viimase tühikuni
    perenimi = Column(String(50)) # X-tee päisevälja userName lõpp alates viimasest tühikust 
    aeg = Column(DateTime, nullable=False) # aeg
    param = Column(String(10)) # testiliik, kui on vaja suunata kindla testiliigi regamisele
    
