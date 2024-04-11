"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Kriteeriumivastus(EntityHelper, Base):
    """Sooritusele hindamiskriteeriumi eest antud pallid
    Erinevalt tabelis Kriteeriumihinne olevatest ühe hindaja pandud hinnetest
    on siin lõplikud hinded.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sooritus_id = Column(Integer, index=True, nullable=False) # viide sooritusele
    #sooritus = relationship('Sooritus', foreign_keys=sooritus_id, back_populates='kriteeriumivastused')
    hindamiskriteerium_id = Column(Integer, ForeignKey('hindamiskriteerium.id'), index=True, nullable=False) # viide hindamiskriteeriumile
    hindamiskriteerium = relationship('Hindamiskriteerium', foreign_keys=hindamiskriteerium_id)
    #hindamiskriteerium = relationship('Hindamiskriteerium', foreign_keys=hindamiskriteerium_id, back_populates='kriteeriumivastused')
    toorpunktid = Column(Float) # toorpunktid (hindamiskriteeriumi skaala järgi)
    pallid = Column(Float) # hindepallid (peale kaaluga korrutamist)
    toorpunktid_enne_vaiet = Column(Float) # toorpunktid enne vaidlustamist
    pallid_enne_vaiet = Column(Float) # hindepallid enne vaidlustamist
    __table_args__ = (
        sa.UniqueConstraint('sooritus_id','hindamiskriteerium_id'),
        )

    def get_tulemus(self, max_pallid, digits=3):
        if self.pallid is not None:
            pallid = self.pallid
            if not max_pallid:
                return fstr(pallid, digits)
            return '%sp %s-st, %s%%' % (fstr(pallid, digits), 
                                        fstr(max_pallid, digits),
                                        fstr(pallid*100/max_pallid, digits))
