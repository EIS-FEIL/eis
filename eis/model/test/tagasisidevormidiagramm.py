"Testi andmemudel"
# from eis.model.entityhelper import *
# from eis.model.usersession import _

# class Tagasisidevormidiagramm(EntityHelper, Base):
#     """Testi tagasisidevormi diagrammi parameetrid
#     """
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     tagasisidevorm_id = Column(Integer, ForeignKey('tagasisidevorm.id'), index=True, nullable=False) # viide tagasisidevormile
#     tagasisidevorm = relationship('Tagasisidevorm', foreign_keys=tagasisidevorm_id)
#     seq = Column(Integer, nullable=False) # diagrammi jrk nr, identifikaator vormi piires
#     params = Column(Text) # diagrammi parameetrid 
#     _parent_key = 'tagasisidevorm_id'    

