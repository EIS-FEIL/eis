# -*- coding: utf-8 -*-
"Ülesande andmemudel"

from eis.model.entityhelper import *

class Kritkirjeldus(EntityHelper, Base):
    """Hindamiskogumi hindamiskriteeriumi eest antavate punktide kirjeldus
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    hindamiskriteerium_id = Column(Integer, ForeignKey('hindamiskriteerium.id'), index=True) # viide hindamiskriteeriumile
    hindamiskriteerium = relationship('Hindamiskriteerium', foreign_keys=hindamiskriteerium_id, back_populates='kritkirjeldused')
    punktid = Column(Float) # punktide arv (sammuga 0,5)
    kirjeldus = Column(Text) # kirjeldus
    trans = relationship('T_Kritkirjeldus', cascade='all', back_populates='orig')
    _parent_key = 'hindamiskriteerium_id'

    def copy(self):
        cp = EntityHelper.copy(self)
        self.copy_subrecords(cp, ['trans',
                                  ])
        return cp

