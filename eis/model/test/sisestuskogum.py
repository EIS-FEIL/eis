# -*- coding: utf-8 -*-
"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import Opt
from eis.model.kasutaja import *
from eis.model.koht import *

from .testiosa import Testiosa

class Sisestuskogum(EntityHelper, Base):
    """Ülesannete sisestuskogum.
    Sisestuskogumil on mõte ainult p-testi korral.
    Sisestuskogumite kaupa toimub hindamisprotokollide sisestamine ja 
    objektiivse hindamisega sisestuskogumi korral vastuste sisestamine.
    Sisestuskogum koosneb hindamiskogumitest.
    Ühe sisestuskogumi kõik ülesanded peavad kuuluma samasse komplektivalikusse.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True) 
    testiosa_id = Column(Integer, ForeignKey('testiosa.id'), index=True, nullable=False) # viide testiosale
    testiosa = relationship('Testiosa', foreign_keys=testiosa_id, back_populates='sisestuskogumid')
    tahis = Column(String(10), nullable=False) # tähis
    nimi = Column(String(100)) # nimetus
    hindamine_kood = Column(String(10)) # hindamise liik, klassifikaator HINDAMINE, peab olema sama kui selle sisestuskogumi hindamiskogumites
    on_skannimine = Column(Boolean, sa.DefaultClause('0'), nullable=False) # p-testi korral: kas toimub skannimine või sisestamine
    on_hindamisprotokoll = Column(Boolean, sa.DefaultClause('0'), nullable=False) # sisestatava p-testi korral: kas sisestuskogumis on mõni hindamiskogum, mida sisestatakse hindamisprotokolliga
    on_vastused = Column(Boolean, sa.DefaultClause('0'), nullable=False) # sisestatava p-testi korral: kas sisestuskogumis on mõni hindamiskogum, mille korral sisestatakse vastused töölt (ühe töö kaupa)
    naita_pallid = Column(Boolean, sa.DefaultClause('0')) # vastuste sisestamise korral: kas kuvada vastuste sisestajale sisestuskogumi eest arvutatud pallid ja toorpunktid 
    hindamiskogumid = relationship('Hindamiskogum', order_by='Hindamiskogum.tahis', back_populates='sisestuskogum')
    tasu = Column(Float) # kogumi sisestamise tasu
    #testiylesanded = relationship('Testiylesanne', order_by='Testiylesanne.sisestuskogum_seq')    
    #komplektivalik_id = Column(Integer)
    #komplektivalik_id = Column(Integer, nullable=False)
    #komplektivalik = relationship('Komplektivalik')
    _parent_key = 'testiosa_id'

    __table_args__ = (
        sa.UniqueConstraint('testiosa_id','tahis'),
        )

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        testiosa = self.testiosa or self.testiosa_id and Testiosa.get(self.testiosa_id)
        if testiosa:
            testiosa.logi('Sisestuskogum %s (%s) %s' % (self.id, self.tahis, liik), vanad_andmed, uued_andmed, logitase)

    def post_create(self):
        self.gen_tahis()

    def gen_tahis(self):
        if not self.tahis:
            testiosa = self.testiosa or Testiosa.get(self.testiosa_id)
            for n in range(1,1000):
                tahis = '%d' % n
                for rcd in testiosa.sisestuskogumid:
                    if rcd.tahis == tahis:
                        tahis = None
                        break
                if tahis:
                    self.tahis = tahis
                    break

    def get_komplektivalik(self):
        """Yhe hindamiskogumi kõik ylesanded peavad kuuluma samasse komplektivalikusse.
        Leiame selle komplektivaliku.
        """
        for hk in self.hindamiskogumid:
            return hk.get_komplektivalik()
    
