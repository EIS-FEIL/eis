"Testikorralduse andmemudel"

import pickle
from cgi import FieldStorage
import mimetypes

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *

class Kysimusehinne(EntityHelper, Base):
    """Hindaja antud hinne ülesande ühele küsimusele.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ylesandehinne_id = Column(Integer, ForeignKey('ylesandehinne.id'), index=True, nullable=False) # viide ylesande hinde kirjele
    ylesandehinne = relationship('Ylesandehinne', foreign_keys=ylesandehinne_id, back_populates='kysimusehinded')
    kysimusevastus_id = Column(Integer, ForeignKey('kysimusevastus.id'), index=True, nullable=False) # viide hinnatavale vastusele
    kysimusevastus = relationship('Kysimusevastus', foreign_keys=kysimusevastus_id, back_populates='kysimusehinded')
    toorpunktid = Column(Float) # hindaja antud toorpunktid (ülesande skaala järgi)
    pallid = Column(Float) # hindepallid (testiülesande skaala järgi)
    markus = Column(Text) # märkused
    nullipohj_kood = Column(String(10)) # null punkti andmise põhjus, klassifikaator NULLIPOHJ

    sisestuslogid = relationship('Sisestuslogi', back_populates='kysimusehinne')
    kysimusehindemarkused = relationship('Kysimusehindemarkus', back_populates='kysimusehinne')

    _parent_key = 'ylesandehinne_id'
    __table_args__ = (
        sa.UniqueConstraint('ylesandehinne_id','kysimusevastus_id'),
        )

    @property
    def s_toorpunktid(self):
        if self.toorpunktid == 0 and \
                self.nullipohj_kood == const.NULLIPOHJ_VASTAMATA:
            return const.PUNKTID_VASTAMATA
        return self.toorpunktid

    def get_kysimusehindemarkus(self, ekspert_labiviija_id):
        """Leitakse ekspertrühma liikme märkuse kirje
        """
        for rcd in self.kysimusehindemarkused:
            if rcd.ekspert_labiviija_id == ekspert_labiviija_id:
                return rcd

    def give_kysimusehindemarkus(self, ekspert_labiviija_id):
        rcd = self.get_kysimusehindemarkus(ekspert_labiviija_id)
        if not rcd:
            rcd = Kysimusehindemarkus(ylesandehinne=self,
                                      ekspert_labiviija_id=ekspert_labiviija_id)
            self.kysimusehindemarkused.append(rcd)
        return rcd

    def set_kysimusehindemarkus(self, markus, ekspert_labiviija_id):
        if markus:
            m = self.give_kysimusehindemarkus(ekspert_labiviija_id)
            m.markus = markus
        else:
            m = self.get_kysimusehindemarkus(ekspert_labiviija_id)
            if m:
                m.delete()

      
    def delete_subitems(self):    
        self.delete_subrecords(['kysimusehindemarkused',
                                ])
