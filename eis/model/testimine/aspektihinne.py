# -*- coding: utf-8 -*-
# $Id: aspektihinne.py 389 2016-03-03 13:51:55Z ahti $
"Testikorralduse andmemudel"

import pickle
from cgi import FieldStorage
import mimetypes

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *

class Aspektihinne(EntityHelper, Base):
    """Hindaja antud hinne ülesande aspektile.
    Kui ülesandel on hindamisaspektid, siis iga aspekti kohta on eraldi kirje.
    Muidu ei ole ühtki kirjet.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ylesandehinne_id = Column(Integer, ForeignKey('ylesandehinne.id'), index=True, nullable=False)
    ylesandehinne = relationship('Ylesandehinne', foreign_keys=ylesandehinne_id, back_populates='aspektihinded') # viide ylesande hinde kirjele
    hindamisaspekt_id = Column(Integer, ForeignKey('hindamisaspekt.id'), index=True, nullable=False)
    hindamisaspekt = relationship('Hindamisaspekt', foreign_keys=hindamisaspekt_id) # viide hinnatavale aspektile
    #hindamisaspekt = relationship('Hindamisaspekt', foreign_keys=hindamisaspekt_id, back_populates='aspektihinded') # viide hinnatavale aspektile
    toorpunktid = Column(Float) # hindaja antud toorpunktid (ülesande skaala järgi)
    pallid = Column(Float) # hindepallid (testiülesande skaala järgi)
    markus = Column(Text) # märkused
    nullipohj_kood = Column(String(10)) # null punkti andmise põhjus, klassifikaator NULLIPOHJ

    sisestuslogid = relationship('Sisestuslogi', back_populates='aspektihinne')
    aspektihindemarkused = relationship('Aspektihindemarkus', back_populates='aspektihinne')
    _parent_key = 'hinne_id'
    __table_args__ = (
        sa.UniqueConstraint('ylesandehinne_id','hindamisaspekt_id'),
        )

    @property
    def s_toorpunktid(self):
        if self.toorpunktid == 0 and \
                self.nullipohj_kood == const.NULLIPOHJ_VASTAMATA:
            return const.PUNKTID_VASTAMATA
        return self.toorpunktid

    def get_aspektihindemarkus(self, ekspert_labiviija_id):
        """Leitakse ekspertrühma liikme märkuse kirje
        """
        for rcd in self.aspektihindemarkused:
            if rcd.ekspert_labiviija_id == ekspert_labiviija_id:
                return rcd

    def give_aspektihindemarkus(self, ekspert_labiviija_id):
        rcd = self.get_aspektihindemarkus(ekspert_labiviija_id)
        if not rcd:
            rcd = Aspektihindemarkus(ylesandehinne=self,
                                      ekspert_labiviija_id=ekspert_labiviija_id)
            self.aspektihindemarkused.append(rcd)
        return rcd

    def set_aspektihindemarkus(self, markus, ekspert_labiviija_id):
        if markus:
            m = self.give_aspektihindemarkus(ekspert_labiviija_id)
            m.markus = markus
        else:
            m = self.get_aspektihindemarkus(ekspert_labiviija_id)
            if m:
                m.delete()

    
    def delete_subitems(self):    
        self.delete_subrecords(['aspektihindemarkused',
                                ])


