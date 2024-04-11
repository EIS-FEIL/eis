from eis.model.entityhelper import *

class Testiopetaja(EntityHelper, Base):
    """Test.sooritaja seos aineõpetajatega, kes sooritajale antud testi ainet õpetavad
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    sooritaja_id = Column(Integer, ForeignKey('sooritaja.id'), index=True, nullable=False) # viide sooritajale (testisoorituse kirjele)
    sooritaja = relationship('Sooritaja', foreign_keys=sooritaja_id, back_populates='testiopetajad')
    opetaja_kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide aineõpetajale
    opetaja_kasutaja = relationship('Kasutaja', foreign_keys=opetaja_kasutaja_id)

    __table_args__ = (
        sa.UniqueConstraint('sooritaja_id','opetaja_kasutaja_id'),
        )
