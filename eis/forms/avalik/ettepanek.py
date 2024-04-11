# -*- coding: utf-8 -*-
# $Id: ettepanek.py 890 2016-09-29 13:46:02Z ahti $
"Avaliku vaate administreerimisliidese valideerimisskeemid"

import formencode
from eis.forms.validators import *

class EttepanekForm(Schema):
    epost = Email(strip=True, max=255, not_empty=True)    
    teema = String(max=255, not_empty=True)
    sisu = String(not_empty=True)
    ootan_vastust = Bool(if_missing=False)
