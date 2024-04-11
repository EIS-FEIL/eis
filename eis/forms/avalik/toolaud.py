# -*- coding: utf-8 -*-
"Töölaua valideerimisskeemid"

import formencode
from eis.forms.validators import *

class KalenderForm(Schema):
    "Otsingu vorm"
    f_sisu = String(if_missing=None)
