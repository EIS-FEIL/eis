# -*- coding: utf-8 -*-
"Testikorralduse andmemudel"

from eis.model.entityhelper import *
_ = usersession._

class Vaidelogi(EntityHelper, Base):
    """Vaide menetlemise logi
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vaie_id = Column(Integer, ForeignKey('vaie.id'), index=True, nullable=False)
    vaie = relationship('Vaie', foreign_keys=vaie_id, back_populates='vaidelogid') # viide vaidele
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False)
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id) # tegutsenud kasutaja
    tegevus = Column(Integer, nullable=False) # tegevus: 0 - menetlusse võtmine; 1 - tulemuse arvutamine; 2 - otsuse loomine; 3 - allkirjastamine; 4 - edastamine; 5 - lõpetatuks märkimine; 11 - otsuse eelnõu loomine; 12 - otsuse eelnõu edastamine; 13 - otsustamisele võtmine; 14 - vaide tagasi võtmine
    tapsustus = Column(String(256)) # tegevuse täpsustus
    _parent_key = 'vaie_id'

    TEGEVUS_MENETLUSSE = 0
    TEGEVUS_ARVUTUSED = 1
    TEGEVUS_EELNOU = 11
    TEGEVUS_EELNOU_EDASTA = 12
    TEGEVUS_OTSUSTAMISEL = 13
    TEGEVUS_OTSUS = 2
    TEGEVUS_ALLKIRI = 3
    TEGEVUS_EDASTA = 4
    TEGEVUS_LOPETA = 5
    TEGEVUS_TAGASIVOTMINE = 14
    
    @property
    def tegevus_nimi(self):
        tegevused = {self.TEGEVUS_MENETLUSSE: _("Menetlusse võtmine"),
                     self.TEGEVUS_ARVUTUSED: _("Tulemuste arvutamine"),
                     self.TEGEVUS_EELNOU: _("Otsuse eelnõu loomine"),
                     self.TEGEVUS_EELNOU_EDASTA: _("Otsuse eelnõu saadetud"),
                     self.TEGEVUS_OTSUSTAMISEL: _("Ärakuulamise lõpp"),
                     self.TEGEVUS_OTSUS: _("Otsuse loomine"),
                     self.TEGEVUS_ALLKIRI: _("Allkirjastamine"),
                     self.TEGEVUS_EDASTA: _("Edastamine"),
                     self.TEGEVUS_LOPETA: _("Menetluse lõpetamine"),
                     self.TEGEVUS_TAGASIVOTMINE: _("Vaide tagasi võtmine"),
                     }
        return tegevused.get(self.tegevus)
