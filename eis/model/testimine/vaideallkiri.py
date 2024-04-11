"Testikorralduse andmemudel"

from eis.model.entityhelper import *
_ = usersession._

class Vaideallkiri(EntityHelper, Base):
    """Vaideotsuse allkirjastajad, lisatakse kasutajarollide järgi otsuse genereerimisel.
    Hiljem, kui allkiri antakse, tehakse kirjes vastav märge.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vaie_id = Column(Integer, ForeignKey('vaie.id'), index=True, nullable=False)
    vaie = relationship('Vaie', foreign_keys=vaie_id, back_populates='vaideallkirjad') # viide vaidele
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # allkirjastaja
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id) # tegutsenud kasutaja
    jrk = Column(Integer, nullable=False) # allkirjastamise jrk nr (kasutajarollist)
    allkirjastatud = Column(DateTime) # allkirjastamise aeg (kui puudub, siis ei ole veel allkirjastatud)
    _parent_key = 'vaie_id'
