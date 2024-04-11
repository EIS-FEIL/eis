# -*- coding: utf-8 -*-
"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Kriteeriumihinne(EntityHelper, Base):
    """Hindaja antud hinne hindamiskogumi hindamiskriteeriumile.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    hindamine_id = Column(Integer, ForeignKey('hindamine.id'), index=True, nullable=False) # viide hindamise/sisestamise kirjele
    hindamine = relationship('Hindamine', foreign_keys=hindamine_id, back_populates='kriteeriumihinded')
    hindamiskriteerium_id = Column(Integer, ForeignKey('hindamiskriteerium.id'), index=True, nullable=False) # viide hindamiskriteeriumile
    hindamiskriteerium = relationship('Hindamiskriteerium', foreign_keys=hindamiskriteerium_id)
    #hindamiskriteerium = relationship('Hindamiskriteerium', foreign_keys=hindamiskriteerium_id, back_populates='kriteeriumihinded')
    toorpunktid = Column(Float) # toorpunktid (hindamiskriteeriumi skaala järgi)
    pallid = Column(Float) # hindepallid (peale kaaluga korrutamist)
    markus = Column(Text) # märkused
    nullipohj_kood = Column(String(10)) # null punkti andmise põhjus, klassifikaator NULLIPOHJ
    _parent_key = 'hindamine_id'
    __table_args__ = (
        sa.UniqueConstraint('hindamine_id','hindamiskriteerium_id'),
        )

    @property
    def s_toorpunktid(self):
        if self.toorpunktid == 0 and \
                self.nullipohj_kood == const.NULLIPOHJ_VASTAMATA:
            return const.PUNKTID_VASTAMATA
        return self.toorpunktid
