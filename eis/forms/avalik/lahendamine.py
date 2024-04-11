# -*- coding: utf-8 -*-
# $Id: lahendamine.py 9 2015-06-30 06:34:46Z ahti $
"Ülesannete valideerimisskeemid"

import formencode
from eis.forms.validators import *

class AvalikotsingForm(Schema):
    "Otsingu vorm"
    id = Int(if_missing=None, min=1)
    ylkogu_id = Int(if_missing=None)
    
class LahendamineForm(Schema):
    "Otsingu vorm"


