# -*- coding: utf-8 -*-
"Ülesande andmemudel"

from eis.model.entityhelper import *

class Punktikirjeldus(EntityHelper, Base):
    """Ülesande hindamisaspekti eest antavate punktide kirjeldus
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    hindamisaspekt_id = Column(Integer, ForeignKey('hindamisaspekt.id'), index=True) # viide hindamisaspektile
    hindamisaspekt = relationship('Hindamisaspekt', foreign_keys=hindamisaspekt_id, back_populates='punktikirjeldused')
    punktid = Column(Float) # punktide arv (sammuga 0,5)
    kirjeldus = Column(Text) # kirjeldus
    trans = relationship('T_Punktikirjeldus', cascade='all', back_populates='orig')
    _parent_key = 'hindamisaspekt_id'

    def copy(self):
        cp = EntityHelper.copy(self)
        self.copy_subrecords(cp, ['trans',
                                  ])
        return cp

