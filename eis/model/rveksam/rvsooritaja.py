"Testi andmemudel"
from eis.model.entityhelper import *
from .rvsooritus import Rvsooritus

class Rvsooritaja(EntityHelper, Base):
    """Rahvusvahelise eksami soorituse andmed
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    rveksam_id = Column(Integer, ForeignKey('rveksam.id'), index=True, nullable=False) # viide eksamile
    rveksam = relationship('Rveksam', foreign_keys=rveksam_id)
    tunnistus_id = Column(Integer, ForeignKey('tunnistus.id'), index=True, nullable=False) # viide tunnistusele
    tunnistus = relationship('Tunnistus', foreign_keys=tunnistus_id, back_populates='rvsooritaja')
    sooritaja_id = Column(Integer, ForeignKey('sooritaja.id'), index=True) # viide sooritaja kirjele juhul, kui rahvusvahelise eksami tunnistus on antud EISis tehtud testi põhjal
    sooritaja = relationship('Sooritaja', foreign_keys=sooritaja_id, back_populates='rvsooritajad')
    kehtib_kuni = Column(DateTime) # tunnistuse kehtivuse lõpp
    keeletase_kood = Column(String(10)) # keeleoskuse tase, klassifikaator KEELETASE
    #(kui on NULL, siis on tase kirjeldatud tulemuste juures)
    rveksamitulemus_id = Column(Integer, ForeignKey('rveksamitulemus.id'), index=True) # viide tulemusele (tulemuse kirjes on ka saadud keeletase, foreign_keys=rveksamitulemus_id)
    rveksamitulemus = relationship('Rveksamitulemus', foreign_keys=rveksamitulemus_id)
    tulemus = Column(Float) # tulemus pallides või protsentides
    rvsooritused = relationship('Rvsooritus', order_by='Rvsooritus.id', back_populates='rvsooritaja') # viide osaoskuste sooritustele (eksamisoorituse korral)
    arvest_lopetamisel = Column(Boolean) # kas tunnistust arvestatakse lõpetamise tingimuste kontrollimisel
    
    @property
    def aine_kood(self):
        "Aine kood, vajalik keeletase_nimi jaoks"
        return self.rveksam.aine_kood

    def get_rvsooritus(self, rvosaoskus_id):
        for r in self.rvsooritused:
            if r.rvosaoskus_id == rvosaoskus_id:
                return r

    def give_rvsooritus(self, rvosaoskus_id):
        r = self.get_rvsooritus(rvosaoskus_id)
        if not r:
            r = Rvsooritus(rvosaoskus_id=rvosaoskus_id)
            self.rvsooritused.append(r)
        return r

    def delete_subitems(self):    
        self.delete_subrecords(['rvsooritused',
                                ])
        self.tunnistus.delete()       
