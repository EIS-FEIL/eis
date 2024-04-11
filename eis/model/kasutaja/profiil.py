# -*- coding: utf-8 -*-
import hashlib

from eis.model.entityhelper import *
from eis.model.koht import Koht
from eis.model.klassifikaator import Klrida

log = logging.getLogger(__name__)

        
class Profiil(EntityHelper, Base):
    """Kasutaja testi läbiviijana rakendamise profiil
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='profiil')

    on_vaatleja = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas on vaatleja
    v_skeeled = Column(String(60)) # vaatlemise keeled eraldatuna tühikuga
    v_koolitusaeg = Column(Date) # vaatlemiskoolituse kuupäev
    v_kaskkirikpv = Column(Date) # vaatlejana käskkirja lisamise kuupäev
    s_skeeled = Column(String(60)) # suulise hindamise keeled eraldatuna tühikuga
    k_skeeled = Column(String(60)) # kirjaliku hindamise keeled eraldatuna tühikuga    
    on_testiadmin = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas on testide administraator
    markus = Column(Text) # märkused (sisestab Innove)
    oma_markus = Column(Text) # märkused (sisestab isik ise, nt kuhu saata eksamimaterjalid)

    arveldusarve = Column(String(20)) # kasutaja arveldusarve nr
    on_psammas = Column(Boolean) # kas on liitunud pensionikindlustuse II sambaga
    psammas_protsent = Column(Integer) # 2 - vanaduspension 2%; 3 - vanaduspension 3% (kui on liitunud II sambaga)
    on_pensionar = Column(Boolean) # kas on vanaduspensionär
    on_ravikindlustus = Column(Boolean) # kas on kehtiv ravikindlustusleping
    ainelabiviijad = relationship('Ainelabiviija', back_populates='profiil')
    #leping_kinnitatud = Column(Date) # lepingu kinnitamise kuupäev

    def set_k_lang(self, lang):
        if not self.k_skeeled:
            self.k_skeeled = ''
        if lang not in self.k_skeeled:
            self.k_skeeled = self.k_skeeled.strip() + ' ' + lang
 
    def set_s_lang(self, lang):
        if not self.s_skeeled:
            self.s_skeeled = ''
        if lang not in self.s_skeeled:
            self.s_skeeled = self.s_skeeled.strip() + ' ' + lang

    def set_v_lang(self, lang):
        if not self.v_skeeled:
            self.v_skeeled = ''
        if lang not in self.v_skeeled:
            self.v_skeeled = self.v_skeeled.strip() + ' ' + lang
   
    def delete_subitems(self):    
        self.delete_subrecords(['ainelabiviijad',
                                ])
