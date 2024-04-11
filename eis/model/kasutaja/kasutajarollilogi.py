from eis.model.entityhelper import *
log = logging.getLogger(__name__)

class Kasutajarollilogi(EntityHelper, Base):
    """Kasutajarollide andmise logi
    """
   
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale, kelle õigusi muudeti
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    kasutajagrupp_id = Column(Integer, nullable=False) # kasutajagrupp
    tyyp = Column(Integer, nullable=False) # grupi tüüp: 1=const.USER_TYPE_EKK - eksamikeskuse grupp; 4=const.USER_TYPE_KOOL - soorituskoha grupp
    kasutajaroll_id = Column(Integer, ForeignKey('kasutajaroll.id'), index=True) # viide kasutajarollile, mida muudeti
    kasutajaroll = relationship('Kasutajaroll', foreign_keys=kasutajaroll_id, back_populates='kasutajarollilogid')
    muutja_kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale, kes muutis
    muutja_kasutaja = relationship('Kasutaja', foreign_keys=muutja_kasutaja_id)
    aeg = Column(DateTime, nullable=False) # õiguse muutmise aeg
    sisu = Column(Text) # muudetud andmed
    jira_nr = Column(Integer) # õiguse muutmiseks tehtud JIRA pileti nr
    selgitus = Column(Text) # õiguse muutmise selgitus

    @property
    def jira_url(self):
        if self.jira_nr:
            return f'https://projektid.edu.ee/jira/browse/EJ-{self.jira_nr}'
