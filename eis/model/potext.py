# -*- coding: utf-8 -*-

from .entityhelper import *

class Potext(EntityHelper, Base):
    """Tõlketekstid
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    msgid = Column(String(1024)) # tekst algkeeles (eesti keeles)
    msgstr = Column(String(1024)) # tekst tõlkekeeles
    lang = Column(String(2)) # tõlkekeel
