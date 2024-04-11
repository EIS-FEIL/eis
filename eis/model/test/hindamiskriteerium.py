# -*- coding: utf-8 -*-
"Hindamiskogumi hindamiskriteerium"
from eis.model.entityhelper import *

class Hindamiskriteerium(EntityHelper, Base):
    """Hindamiskogumi hindamiskriteerium
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    hindamiskogum_id = Column(Integer, ForeignKey('hindamiskogum.id'), index=True) # viide hindamiskogumile
    hindamiskogum = relationship('Hindamiskogum', foreign_keys=hindamiskogum_id, back_populates='hindamiskriteeriumid')
    aine_kood = Column(String(10), nullable=False) # õppeaine, mille hindamisaspekt see on
    aspekt_kood = Column(String(10)) # viide aspektile, klassifikaator ASPEKT
    max_pallid = Column(Float) # max toorpunktide arv, mida selle kriteeriumiga hinnatakse
    pintervall = Column(Float) # lubatud punktide intervall (käsitsi hindamisel)
    kaal = Column(Float, sa.DefaultClause('1'), nullable=False) # kaal, millega kriteeriumi toorpunktid korrutatakse
    hindamisjuhis = Column(Text) # kirjeldus (kui puudub, siis kasutatakse vaikimisi kirjeldusena aspektide klassifikaatoris olevat)
    seq = Column(Integer, nullable=False) # hindamiskriteeriumi järjekord hindamiskogumis
    kuvada_statistikas = Column(Boolean, sa.DefaultClause('1')) # kas kuvada kriteerium statistikaraportis
    pkirj_sooritajale = Column(Boolean) # kas kuvada punktide kirjeldused sooritajale
    kriteeriumihinded = relationship('Kriteeriumihinne', back_populates='hindamiskriteerium')
    kriteeriumivastused = relationship('Kriteeriumivastus', back_populates='hindamiskriteerium')    
    kritkirjeldused = relationship('Kritkirjeldus', order_by=sa.desc(sa.text('Kritkirjeldus.punktid')), back_populates='hindamiskriteerium')
    trans = relationship('T_Hindamiskriteerium', cascade='all', back_populates='orig')
    _parent_key = 'hindamiskogum_id'

    def copy(self):
        cp = EntityHelper.copy(self)
        self.copy_subrecords(cp, ['trans',
                                  'kritkirjeldused',
                                  ])
        return cp

