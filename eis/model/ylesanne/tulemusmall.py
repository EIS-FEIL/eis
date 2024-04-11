# -*- coding: utf-8 -*-
# $Id: tulemusmall.py 444 2016-03-11 16:18:31Z ahti $
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

class Tulemusmall(EntityHelper, Base):
    """Tulemuste reeglite mallid. EISi siseselt ei kasutata.
    QTI responseProcessing
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    nimi = Column(String(100)) # malli nimi
    kirjeldus = Column(String(256)) # malli kirjeldus
    rp_uri = Column(String(256)) # malli URI
    rp_location = Column(String(256)) # asukoht
    rp_reeglid = Column(Text) # reeglite sisu

    ylesanne_list = relationship('Ylesanne', back_populates='tulemusmall')

# responseProcessing:
#     setOutcomeValue_kood="completion_staatus"
#     setOutcomeValue_expression_id
#     responseCondition_id
    
# Expression:
#     type=baseValue
#     baseType=kood
#     value=incomplete

# ResponseIf:
#     type=and
#     setOutComeValue_idntifier=FIRSTDOOR
#     setOutcomeValue_id
    
# responseIf
#   expression.ElementGroup = tehe (and, gt, ordered, divide, not, substring,...)
#   *responserule.ElementGroup
#       responseCondition
#       responseProcessingFragment
#       setOutcomeValue
#       exitResponse
#       lookupOutcomeValue
