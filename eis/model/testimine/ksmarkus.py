"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Ksmarkus(EntityHelper, Base):
    """Avatud küsimuse vastuse sisse hindaja poolt lisatud kommentaarid ja vead
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kysimusevastus_id = Column(Integer, ForeignKey('kysimusevastus.id'), index=True, nullable=False) # viide kommenteeritavale vastusele
    kysimusevastus = relationship('Kysimusevastus', foreign_keys=kysimusevastus_id, back_populates='ksmarkused')
    seq = Column(Integer, nullable=False) # mitmes vastus (küsimuse piires)
    ylesandehinne_id = Column(Integer, ForeignKey('ylesandehinne.id'), index=True, nullable=True) # viide ylesande hinde kirjele, puudub automaatse tekstianalüüsi märkuste kirjel
    ylesandehinne = relationship('Ylesandehinne', foreign_keys=ylesandehinne_id, back_populates='ksmarkused')
    markus = Column(Text) # hindaja märkused json-stringina kujul [[offset,tüüp,tekst]] või [[offset,tüüp,tekst,pikkus]]
    _parent_key = 'ylesandehinne_id'
    __table_args__ = (
        sa.UniqueConstraint('kysimusevastus_id','seq','ylesandehinne_id'),
        )


