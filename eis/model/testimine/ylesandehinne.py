"Testikorralduse andmemudel"

import pickle
from cgi import FieldStorage
import mimetypes

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *

from .aspektihinne import Aspektihinne
from .ylesandehindemarkus import Ylesandehindemarkus
from .kysimusehinne import Kysimusehinne
from .ksmarkus import Ksmarkus

class Ylesandehinne(EntityHelper, Base):
    """Hindaja antud hindepallid ühe ülesande vastusele.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    hindamine_id = Column(Integer, ForeignKey('hindamine.id'), index=True, nullable=False) # viide hindamise/sisestamise kirjele
    hindamine = relationship('Hindamine', foreign_keys=hindamine_id, back_populates='ylesandehinded')
    valitudylesanne_id = Column(Integer, ForeignKey('valitudylesanne.id'), index=True, nullable=False) # viide testi valitud ülesandele; mitme sisestamise korral võib sisestusvea korral ajutiselt erineda ylesandevastuses olevast väärtusest
    valitudylesanne = relationship('Valitudylesanne', foreign_keys=valitudylesanne_id)
    #valitudylesanne = relationship('Valitudylesanne', foreign_keys=valitudylesanne_id, back_populates='ylesandehinded')
    ylesandevastus_id = Column(Integer, ForeignKey('ylesandevastus.id'), index=True, nullable=False) # viide ylesandele antud vastusele ja ylesande hindele
    ylesandevastus = relationship('Ylesandevastus', foreign_keys=ylesandevastus_id, back_populates='ylesandehinded')
    toorpunktid = Column(Float) # küsimustele või aspektidele antud toorpunktide summa (ülesande skaala järgi)
    pallid = Column(Float) # küsimustele või aspektidele antud hindepallide summa (testiülesande skaala järgi)
    toorpunktid_kasitsi = Column(Float) # küsimustele või aspektidele antud toorpunktide summa ilma arvutihinnatud punktideta (ülesande skaala järgi)
    pallid_kasitsi = Column(Float) # küsimustele või aspektidele antud hindepallide summa ilma arvutihinnatud pallideta (testiülesande skaala järgi)
    nullipohj_kood = Column(String(10)) # null punkti andmise põhjus, klassifikaator NULLIPOHJ (kasutusel siis, kui antakse terve ülesande punktid korraga)
    markus = Column(Text) # märkused
    sisestus = Column(Integer, sa.DefaultClause('1'), nullable=False) # mitmes sisestamine (1 või 2)
    sisestatud = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas kõigi küsimuste hinded on sisestatud
    on_probleem = Column(Boolean) # kas hindaja on märkinud töö probleemseks (avaliku vaate hindamisel)
    probleem_sisu = Column(Text) # kui hindaja on märkinud töö probleemseks, siis probleemi sisu
    probleem_varv = Column(String(7)) # probleemse töö värv (#rrggbb või #rgb)
    kysimusehinded = relationship('Kysimusehinne', back_populates='ylesandehinne')
    aspektihinded = relationship('Aspektihinne', back_populates='ylesandehinne')
    sisestuslogid = relationship('Sisestuslogi', order_by='Sisestuslogi.id', back_populates='ylesandehinne')
    ylesandehindemarkused = relationship('Ylesandehindemarkus', order_by='Ylesandehindemarkus.id', back_populates='ylesandehinne')
    ksmarkused = relationship('Ksmarkus', back_populates='ylesandehinne')
    _parent_key = 'hindamine_id'
    __table_args__ = (
        sa.UniqueConstraint('ylesandevastus_id','hindamine_id'),
        )

    @property
    def s_toorpunktid(self):
        if self.toorpunktid == 0 and \
                self.nullipohj_kood == const.NULLIPOHJ_VASTAMATA:
            return const.PUNKTID_VASTAMATA
        return self.toorpunktid

    def get_aspektihinne(self, hindamisaspekt_id):
        """Leitakse aspektihinde kirje 
        """
        for rcd in self.aspektihinded:
            if rcd.hindamisaspekt_id == hindamisaspekt_id:
                return rcd


    def give_aspektihinne(self, hindamisaspekt_id):
        rcd = self.get_aspektihinne(hindamisaspekt_id)
        if not rcd:
            rcd = Aspektihinne(ylesandehinne=self,
                               hindamisaspekt_id=hindamisaspekt_id)
            #self.aspektihinded.append(rcd)
        return rcd


    def get_kysimusehinne(self, kysimusevastus):
        """Leitakse kysimusehinde kirje 
        """
        for rcd in self.kysimusehinded:
            if (rcd.kysimusevastus == kysimusevastus) or \
               (rcd.kysimusevastus_id == kysimusevastus.id):
                return rcd


    def give_kysimusehinne(self, kysimusevastus):
        rcd = self.get_kysimusehinne(kysimusevastus)
        if not rcd:
            rcd = Kysimusehinne(ylesandehinne=self,
                                kysimusevastus=kysimusevastus)
            #self.kysimusehinded.append(rcd)
        return rcd


    def get_ylesandehindemarkus(self, ekspert_labiviija_id):
        """Leitakse ekspertrühma liikme märkuse kirje
        """
        for rcd in self.ylesandehindemarkused:
            if rcd.ekspert_labiviija_id == ekspert_labiviija_id:
                return rcd

    def give_ylesandehindemarkus(self, ekspert_labiviija_id):
        rcd = self.get_ylesandehindemarkus(ekspert_labiviija_id)
        if not rcd:
            rcd = Ylesandehindemarkus(ylesandehinne=self,
                                      ekspert_labiviija_id=ekspert_labiviija_id)
            #self.ylesandehindemarkused.append(rcd)
        return rcd

    def set_ylesandehindemarkus(self, markus, ekspert_labiviija_id):
        if markus:
            m = self.give_ylesandehindemarkus(ekspert_labiviija_id)
            m.markus = markus
        else:
            m = self.get_ylesandehindemarkus(ekspert_labiviija_id)
            if m:
                m.delete()

    def get_ksmarkus(self, kv, seq):
        """Leitakse teksti sisse hindaja lisatud märkus
        """
        for rcd in self.ksmarkused:
            if rcd.kysimusevastus == kv and rcd.seq == seq:
                return rcd

    def give_ksmarkus(self, kv, seq):
        rcd = self.get_ksmarkus(kv, seq)
        if not rcd:
            rcd = Ksmarkus(kysimusevastus=kv,
                           seq=seq,
                           ylesandehinne=self)
            #self.ksmarkused.append(rcd)
        return rcd
    
    def delete_subitems(self):
        self.delete_subrecords(['sisestuslogid',
                                'kysimusehinded',
                                'aspektihinded',
                                'ylesandehindemarkused',
                                'ksmarkused',
                                ])

