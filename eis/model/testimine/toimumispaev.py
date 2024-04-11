"Testi andmemudel"
from eis.model.entityhelper import *

class Toimumispaev(EntityHelper, Base):
    """Toimumisaja kuupäev ja kellaaeg
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    toimumisaeg_id = Column(Integer, ForeignKey('toimumisaeg.id'), index=True, nullable=False) # viide toimumisajale
    toimumisaeg = relationship('Toimumisaeg', foreign_keys=toimumisaeg_id, back_populates='toimumispaevad')
    seq = Column(Integer, nullable=False) # toimumispäeva jrk nr toimumisajal (toimumise sessioon)
    aeg = Column(DateTime, nullable=False) # testi kuupäev koos alguskellaga (kui kell on 00.00, siis kell puudub)
    alustamise_lopp = Column(DateTime) # kellaaeg, millest varem peab sooritamist alustama (kui toimumisaeg.aja_jargi_alustatav=True)
    lopp = Column(DateTime) # kellaaeg, millal hiljemalt peab sooritamine lõppema (isegi, kui piiraeg ei ole täis)
    valim = Column(Boolean) # True - sellele ajale saab valimisse kuuluvaid sooritajaid suunata; False - sellele ajale ei või valimi sooritajaid suunata; None - sellel toimumisajal ei ole määratud valimi sooritajate aeg
    testiruumid = relationship('Testiruum', back_populates='toimumispaev')
    sooritused = relationship('Sooritus', back_populates='reg_toimumispaev')
    _parent_key = 'toimumisaeg_id'
