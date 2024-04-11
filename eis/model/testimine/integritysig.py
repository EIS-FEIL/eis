# # -*- coding: utf-8 -*-
# "Testitulemuste andmete terviklus"
# from eis.model.entityhelper import *
    
# class Integritysig(EntityHelper, Base):
#     """Testi tulemustele võetud allkirjad andmetervikluse kontrollimiseks
#     """
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     data = Column(Text) # agregeeritud andmed - tekst, mille iga rida on ühe agregeeritud Sooritajarasi kirjes olev räsi
#     data_hash = Column(String(50)) # andmete SHA-256 räsi (base64)
#     response = Column(Text) # allkirjastamispäringu vastus (json string, saadud Catenalt)
#     signature_id = Column(String(50)) # allkirja id (Catena vastusest)
#     signature = Column(Text) # allkiri (Catena vastusest)
#     signed = Column(DateTime) # allkirjastamise aeg (Catena vastusest)
#     verified = Column(DateTime) # viimase kontrollimise aeg
#     status = Column(Integer) # kontrollimise olek: 1 - OK; 0 - NOK
#     err_msg = Column(String(256)) # allkirja kontrolli veateade
#     sooritajalogid = relationship('Sooritajalogi', back_populates='integritysig')
    
