# -*- coding: utf-8 -*-
"Ülesande andmemudel"

from PIL import Image
import mimetypes
import re
from lxml import etree
import urllib.request, urllib.parse, urllib.error

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *

class Lahendusjuhis(EntityHelper, Base):
    """Ülesande lahendusjuhis
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    juhis = Column(Text) # ülesande lahendusjuhis
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True) # viide ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='lahendusjuhis')
    #nupujuhis = Column(Text) # lahendaja tekstitoimeti nupurea juhend
    nupuriba = Column(Text) # lahendaja tekstitoimeti nupureal kuvatavate ikoonide nimed, komaeraldatud
    matriba = Column(Text) # lahendaja matemaatikaredaktori nupureal kuvatavate ikoonide nimed, komaeraldatud    
    wmatriba = Column(Text) # lahendaja WIRIS MathType redaktori nupurea seaded

    #on_tahemargid = Column(Boolean, sa.DefaultClause('true')) # kas lugeda kokku sisuploki tähemärkide arv (toimetajate ja tõlkijate tasu arvestamiseks)
    tahemargid = Column(Integer) # originaalkeeles sisuploki tähemärkide arv (originaalkeeles)
    _parent_key = 'ylesanne_id'    
    trans = relationship('T_Lahendusjuhis', cascade='all', back_populates='orig')

    logging = True
            
    def copy(self):
        cp = EntityHelper.copy(self)
        self.copy_subrecords(cp, ['trans',
                                  ])
        return cp

    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .ylesanne import Ylesanne

        ylesanne = self.ylesanne or self.ylesanne_id and Ylesanne.get(self.ylesanne_id)
        if ylesanne:
            ylesanne.logi('Lahendusjuhis', vanad_andmed, uued_andmed, logitase)

    def count_tahemargid(self, lang):
        """Loetakse kokku juhise tähemärgid
        """
        def _html2txt(s):
            "Kireva teksti teisendamine tavaliseks"
            return re.sub(r'<[^>]*>', '', s)

        def _len(value, rtf):
            "Teksti sisu tähtede lugemine"
            if rtf and value:
                value = _html2txt(value)
            if value:
                value = re.sub(r'\s+', ' ', value).strip()
            return value and len(value) or 0
       
        total = 0
        tr = self.tran(lang, False)
        if tr:
            tr.tahemargid = total = _len(tr.juhis, True)

        return total
