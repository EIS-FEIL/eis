"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Vastusaspekt(EntityHelper, Base):
    """Ühele ülesandele antud vastuse tulemus ühes aspektis.
    Erinevalt tabelis Hinne olevatest ühe hindaja pandud hinnetest
    on siin lõplikud hinded.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ylesandevastus_id = Column(Integer, ForeignKey('ylesandevastus.id'), index=True, nullable=False) # viide ülesande vastusele
    ylesandevastus = relationship('Ylesandevastus', foreign_keys=ylesandevastus_id, back_populates='vastusaspektid')
    hindamisaspekt_id = Column(Integer, ForeignKey('hindamisaspekt.id'), index=True, nullable=False) # viide hinnatavale aspektile
    hindamisaspekt = relationship('Hindamisaspekt', foreign_keys=hindamisaspekt_id)
    toorpunktid = Column(Float) # toorpunktid (ülesande skaala järgi)
    pallid = Column(Float) # hindepallid (testiülesande skaala järgi)
    toorpunktid_enne_vaiet = Column(Float) # toorpunktid enne vaidlustamist
    pallid_enne_vaiet = Column(Float) # hindepallid enne vaidlustamist
    nullipohj_kood = Column(String(10)) # null punkti andmise põhjus, klassifikaator NULLIPOHJ
    __table_args__ = (
        sa.UniqueConstraint('ylesandevastus_id','hindamisaspekt_id'),
        )

    def get_tulemus(self, max_pallid, digits=3):
        if self.pallid is not None:
            pallid = self.pallid
            if not max_pallid:
                return fstr(pallid, digits)
            return '%sp %s-st, %s%%' % (fstr(pallid, digits), 
                                        fstr(max_pallid, digits),
                                        fstr(pallid*100/max_pallid, digits))
