# -*- coding: utf-8 -*-
"Soorituskoha andmete muudatuste logi"

from eis.model.entityhelper import *
_ = usersession._

class Kohalogi(EntityHelper, Base):
    """Soorituskoha andmete muudatuste logi
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True) 
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True) # viide muudatuse teinud kasutajale (puudub automaatse ADS uuenduse korral)
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    allikas = Column(Integer, nullable=False) # muudatuse allikas: 1 - EKK, 2 - soorituskoht; 3 - EHIS
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True, nullable=False) # viide muudetud kohale
    koht = relationship('Koht', foreign_keys=koht_id, back_populates='kohalogid')
    vali = Column(String(50), nullable=False) # muudetud välja nimi
    vana = Column(String(200)) # vana väärtus
    uus = Column(String(200)) # uus väärtus
    _parent_key = 'koht_id'

    ALLIKAS_EKK = 1
    ALLIKAS_SK = 2
    ALLIKAS_EHIS = 3

    @property
    def allikas_nimi(self):
        if self.allikas == self.ALLIKAS_EKK:
            return _("Haridus- ja Noorteamet")
        elif self.allikas == self.ALLIKAS_SK:
            return _("Soorituskoht")
        elif self.allikas == self.ALLIKAS_EHIS:
            return _("EHIS")

