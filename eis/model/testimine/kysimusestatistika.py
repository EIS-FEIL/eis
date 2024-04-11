"Testikorralduse andmemudel"

from eis.model.entityhelper import *
         
class Kysimusestatistika(EntityHelper, Base):
    """Küsimuse statistika
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    testiosa_id = Column(Integer, ForeignKey('testiosa.id'), index=True, nullable=False) # viide testiosale
    testiosa = relationship('Testiosa', foreign_keys=testiosa_id)
    tkorraga = Column(Boolean, nullable=False, index=True) # kas on testimiskorraga soorituste statistika (või avaliku testi statistika)
    valimis = Column(Boolean) # NULL - valimi ja mitte-valimi statistika koos; true - valimi statistika; false - mitte-valimi statistika
    toimumisaeg_id = Column(Integer, ForeignKey('toimumisaeg.id'), index=True) # viide toimumisajale eksamikeskuse testi korral
    toimumisaeg = relationship('Toimumisaeg', foreign_keys=toimumisaeg_id, back_populates='kysimusestatistikad')
    nimekiri_id = Column(Integer, ForeignKey('nimekiri.id'), index=True) # viide testi sooritajate nimekirjale oma nimekirja sisese statistika korral
    nimekiri = relationship('Nimekiri', foreign_keys=nimekiri_id)
    valitudylesanne_id = Column(Integer, ForeignKey('valitudylesanne.id'), index=True) # viide komplekti valitud ülesandele, kui statistika on komplektisisene
    valitudylesanne = relationship('Valitudylesanne', foreign_keys=valitudylesanne_id)    
    kysimus_id = Column(Integer, index=True, nullable=False) # viide kysimusele
    vastuste_arv = Column(Integer) # vastuste arv (tabeli Kvsisu kirjete arv) - mõne küsimuse korral võib üks vastaja anda mitu vastust, kasutusel tabeli Kvstatistika kirjete sageduse arvutamiseks
    vastajate_arv = Column(Integer) # vastajate arv (tabeli Kysimusevastus kirjete arv), kasutusel tabeli Khstatistika kirjete sageduse arvutamiseks
    test_hinnatud_arv = Column(Integer) # vastajate arv, kelle kogu testitöö on hinnatud
    klahendusprotsent = Column(Float) # keskmine lahendusprotsent, keskmise tulemuse ja maksimaalse võimaliku tulemuse suhe
    rit = Column(Float) # korrelatsioonikordaja küsimuse punktide ja testi kogutulemuse vahel, küsimuse eristusjõu näitaja: corr(kv.pallid, sooritaja.pallid)
    rir = Column(Float) # korrelatsioonikordaja küsimuse punktide ja testi ülejäänud küsimuste punktide vahel: corr(kv.pallid, sooritaja.pallid-kv.pallid)
    kvstatistikad = relationship('Kvstatistika', order_by="[desc(Kvstatistika.vastuste_arv),Kvstatistika.kood1,Kvstatistika.kood2,Kvstatistika.sisu]", back_populates='kysimusestatistika')
    khstatistikad = relationship('Khstatistika', order_by="[desc(Khstatistika.vastuste_arv),desc(Khstatistika.toorpunktid)]", back_populates='kysimusestatistika')    
    
    def delete_subitems(self):    
        self.delete_subrecords(['kvstatistikad',
                                'khstatistikad',
                                ])

