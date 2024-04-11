"Töökogumiku struktuur"

from eis.model.entityhelper import *

class Tkosa(EntityHelper, Base):
    """Töökogumiku struktuur
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    seq = Column(Integer) # osa järjekorranumber struktuuris
    nimi = Column(String(100)) # nimekirja nimetus
    tookogumik_id = Column(Integer, ForeignKey('tookogumik.id'), index=True, nullable=False) # töökogumik, mille osa see on
    tookogumik = relationship('Tookogumik', back_populates='tkosad')
    ylem_tkosa_id = Column(Integer, ForeignKey('tkosa.id'), index=True) # viide ülemosa, kui on alamosa
    ylem_tkosa = relationship('Tkosa', foreign_keys=ylem_tkosa_id, remote_side=id, back_populates='alam_tkosad')
    alam_tkosad = relationship('Tkosa', back_populates='ylem_tkosa')
    tkylesanded = relationship('Tkylesanne', back_populates='tkosa')
    tktestid = relationship('Tktest', back_populates='tkosa')    

    def copy(self, tookogumik):
        cp = EntityHelper.copy(self)
        cp.tookogumik = tookogumik
        self.copy_subrecords(cp, ['tkylesanded', 'tktestid'])
        for osa in self.alam_tkosad:
            cp_osa = osa.copy(tookogumik)
            cp_osa.ylem_tkosa = cp
        return cp
    
    def delete_subitems(self):    
        self.delete_subrecords(['alam_tkosad',
                                'tkylesanded',
                                'tktestid',
                                ])

