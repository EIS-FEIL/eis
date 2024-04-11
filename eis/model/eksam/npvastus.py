"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Npvastus(EntityHelper, Base):
    """Normipunkti väärtus soorituse korral
    """
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sooritus_id = Column(Integer, index=True, nullable=True) # viide sooritusele
    #sooritus = relationship('Sooritus', foreign_keys=sooritus_id, back_populates='npvastused')
    ylesandevastus_id = Column(Integer, ForeignKey('ylesandevastus.id'), index=True) # viide ylesandele antud vastusele (tagasisidega ülesande korral, jagatud töös)
    ylesandevastus = relationship('Ylesandevastus', foreign_keys=ylesandevastus_id, back_populates='npvastused')
    normipunkt_id = Column(Integer, index=True, nullable=False) # viide normipunkti kirjele
    #normipunkt = relationship('Normipunkt', foreign_keys=normipunkt_id, back_populates='npvastused') 
    nvaartus = Column(Float) # arvuline väärtus (kui on arv)
    svaartus = Column(String(256)) # tekstiline väärtus (kui pole arv)
    viga = Column(String(256)) # valemi arvutamise veateade
    nptagasiside_id = Column(Integer, index=True) # viide antud tagasiside tekstile
    #nptagasiside = relationship('Nptagasiside', foreign_keys=nptagasiside_id, back_populates='npvastused')
    __table_args__ = (
        sa.UniqueConstraint('ylesandevastus_id','normipunkt_id'),
        )
    
    def __repr__(self):
        return '<Npvastus %s %s %s>' % (self.id, self.normipunkt_id, self.nvaartus)

    @property
    def normipunkt(self):
        from eis.model.test.normipunkt import Normipunkt
        return Normipunkt.get(self.normipunkt_id)

    @property
    def nptagasiside(self):
        from eis.model.test.nptagasiside import Nptagasiside
        return Nptagasiside.get(self.nptagasiside_id)
    
    def set_value(self, value, err=None):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            self.nvaartus = value
            self.svaartus = None
        else:
            self.nvaartus = None
            self.svaartus = value
        self.viga = err and err[:256] or None
        
    def get_str_value(self):
        if self.nvaartus is not None:
            return fstr(self.nvaartus, 2)
        else:
            return self.svaartus

    def get_value(self):
        if self.nvaartus is not None:
            return self.nvaartus
        else:
            return self.svaartus
