# -*- coding: utf-8 -*-
# $Id: koolioppekava.py 1096 2017-01-11 06:17:05Z ahti $
"Soorituskoha õppekavad ja haridustasemed"

from eis.model.entityhelper import *

class Koolioppekava(EntityHelper, Base):
    """Soorituskoha õppekavad ja õppekavajärgsed haridustasemed.
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True) 
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True, nullable=False) # viide kohale
    koht = relationship('Koht', foreign_keys=koht_id, back_populates='koolioppekavad')
    oppetase_kood = Column(String(1)) # õppetase, EISi klassifikaator OPPETASE: y=const.OPPETASE_YLD - üldharidus; u=const.OPPETASE_KUTSE - kutseharidus; o=const.OPPETASE_KORG - kõrgharidus; NULL - plangivaba tase (alusharidus või huviharidus)
    kavatase_kood = Column(String(25), nullable=False) # õppetase/haridustase, klassifikaator KAVATASE (kutse- ja kõrghariduse korral õppekava õppetaseme kood EHISes; alus-, kesk- ja gümnaasiumitaseme korral õppetaseme kood EHISes)
    on_ehisest = Column(Boolean, sa.DefaultClause('1')) # kas andmed on pärit EHISest (kui pole, siis seda kirjet EHISe päringu tulemuse põhjal ei kustutata)
    _parent_key = 'koht_id'
