"Testi andmemudel"
from eis.model.entityhelper import *

class Rveksam(EntityHelper, Base):
    """Niisuguse rahvusvahelise eksami kirjeldus, mida EIS ei korralda, kuid mille tunnistuste kirjed on EISis
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    nimi = Column(String(256), nullable=False) # eksami nimetus
    rveksam_kood = Column(String(10)) # rahvusvaheliselt tunnustatud eksamite klassifikaator
    aine_kood = Column(String(10), nullable=False) # õppeaine, klassifikaator AINE (määrab keele - inglise, saksa, vene või prantsuse)
    rvosaoskused = relationship('Rvosaoskus', order_by='Rvosaoskus.seq', back_populates='rveksam')
    rveksamitulemused = relationship('Rveksamitulemus', order_by='Rveksamitulemus.seq', back_populates='rveksam')
    keeletase_kood = Column(String(10)) # keeleoskuse tase, klassifikaator KEELETASE (kui on NULL, siis on tase kirjeldatud tulemuste juures)
    vastab_tasemele = Column(Boolean) # true - vastab tasemele; false - võrreldav tasemega
    on_tase_tunnistusel = Column(Boolean) # kas tunnistusele on märgitud kogutulemus EN skaalal
    on_tulemus_tunnistusel = Column(Boolean) # kas kogutulemus on märgitud tunnistusele
    on_tulemus_sooritusteatel = Column(Boolean) # kas kogutulemus on märgitud sooritusteatele
    on_osaoskused_tunnistusel = Column(Boolean) # kas osaoskuste tulemus on märgitud tunnistusele
    on_osaoskused_sooritusteatel = Column(Boolean) # kas osaoskuste tulemus on märgitud sooritusteatele
    on_osaoskused_jahei = Column(Boolean) # kas osaoskuste läbimine märgitakse linnukesega
    on_kehtivusaeg = Column(Boolean) # kas sisestatakse kuupäevade vahemik, mil tunnistus kehtib
    on_tunnistusenr = Column(Boolean) # kas sisestatakse tunnistusenumber
    tulemusviis = Column(String(1)) # tulemuse esitamise viis (P - pallid, S - protsendid, T - tähised)
    alates = Column(Float) # pallide või protsentide vahemiku algus
    kuni = Column(Float) # pallide või protsentide vahemiku lõpp
    markus = Column(Text) # märkused
    kantav_tulem = Column(Boolean) # kas sisestamisel on võimalik kanda tulemusi tunnistuselt testisooritusele
    
    TULEMUSVIIS_PALL = 'P'
    TULEMUSVIIS_PROTSENT = 'S'
    TULEMUSVIIS_TAHIS = 'T'

    opt_tulemusviis = [(TULEMUSVIIS_PALL, 'Skaala punktidena'),
                      (TULEMUSVIIS_PROTSENT, 'Skaala protsentidena'),
                      (TULEMUSVIIS_TAHIS, 'Skaala ainult tähistena'),
                      ]

    @property
    def on_arvtulemus(self):
        return self.tulemusviis == self.TULEMUSVIIS_PALL or \
               self.tulemusviis == self.TULEMUSVIIS_PROTSENT

    @property
    def in_use(self):
        from .rvsooritaja import Rvsooritaja
        a = SessionR.query(Rvsooritaja.id).\
            filter(Rvsooritaja.rveksamitulemus==self).\
            first()
        if a:
            return True
        else:
            return False

    def delete_subitems(self):    
        self.delete_subrecords(['rveksamitulemused',
                                'rvosaoskused'
                                ])
