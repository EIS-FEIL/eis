from eis.model.entityhelper import *

class Seblog(EntityHelper, Base):
    """SEB avamise logi
    """
    __tablename__ = 'seblog'    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sooritus_id = Column(Integer, nullable=False, index=True) # soorituse ID
    #sooritus = relationship('Sooritus', foreign_keys=sooritus_id, back_populates='seblogid')
    url_key = Column(String(32)) # EISi testisoorituse URLi osa SEBiga lahendamisel
    avatud = Column(DateTime) # SEBi avamise aeg
    remote_addr = Column(String(36)) # sooritaja IP
    namespace = Column(String(255)) # tavalise brauseri seansi identifikaator (millega SEB konf alla laaditi)
    
    @classmethod
    def get_last(cls, sooritus_id):
        q = (SessionR.query(Seblog)
             .filter_by(sooritus_id=sooritus_id)
             )
        q = q.order_by(sa.desc(Seblog.id))
        rcd = q.first()
        return rcd
