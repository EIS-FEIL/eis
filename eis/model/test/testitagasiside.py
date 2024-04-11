# -*- coding: utf-8 -*-
"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.usersession import _
from .test import Test
from eis.model.countchar import CountChar

class Testitagasiside(EntityHelper, Base):
    """Testi tagasiside tekstid
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('test.id'), unique=True, index=True, nullable=False) # viide testile
    test = relationship('Test', foreign_keys=test_id, back_populates='testitagasiside')
    sissejuhatus_opilasele = Column(Text) # sissejuhatus õpilasele
    kokkuvote_opilasele = Column(Text) # kokkuvõte õpilasele
    sissejuhatus_opetajale = Column(Text) # sissejuhatus õpetajale
    kokkuvote_opetajale = Column(Text) # kokkuvõte õpetajale    
    ts_loetelu = Column(Boolean, sa.DefaultClause('true'), nullable=False) # kas tagasiside tekstid kuvada loeteluna
    ylgrupp_kuva = Column(Integer, sa.DefaultClause('0'), nullable=False) # kuidas kuvada ülesannete grupid: 0 - ei kuva gruppide kaupa; 1 - grupid üksteise all; 2 - grupid üksteise kõrval
    ylgrupp_nimega = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kui kuvada ülesannete grupid, kas siis kuvada ka grupi nimetus
    nsgrupp_kuva = Column(Integer, sa.DefaultClause('0'), nullable=False) # kuidas kuvada tagasiside grupid: 0 - ei kuva gruppide kaupa; 1 - grupid üksteise all; 2 - grupid üksteise kõrval
    nsgrupp_nimega = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kui kuvada tagasiside grupid, kas siis kuvada ka grupi nimetus
    kompaktvaade = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas vaikimisi kuvada õpetajale kompaktne vaade
    tahemargid = Column(Integer) # tähemärkide arv
    ts_sugu = Column(Boolean) # kas kuvada grupi tagasiside soo kaupa
    trans = relationship('T_Testitagasiside', cascade='all', back_populates='orig')
    _parent_key = 'test_id'    

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        if self.logging:
            test = self.test or self.test_id and Test.get(self.test_id)
            if test:
                test.logi('Testi tagasiside %s %s' % (self.id or '', liik), vanad_andmed, uued_andmed, logitase)
   
    def copy(self, ignore=[], **di):
        cp = EntityHelper.copy(self, ignore=ignore, **di)
        self.copy_subrecords(cp, ['trans'])
        return cp

    def count_tahemargid(self, lang):
        cch = CountChar(self.test.lang, lang)
        tr = cch.tran(self)
        
        total = 0
        if tr:
            total += cch.count(tr.sissejuhatus_opilasele, True) + \
                     cch.count(tr.kokkuvote_opilasele, True) + \
                     cch.count(tr.sissejuhatus_opetajale, True) + \
                     cch.count(tr.kokkuvote_opetajale, True)
            tr.tahemargid = total
        return total
