# -*- coding: utf-8 -*-
"Kasutaja poolt sisestatud väärtuste valideerimine"

import formencode

from .validators import *

from . import admin
from . import minu
from . import ekk
from . import avalik

#formencode.api.set_stdtranslation(domain="FormEncode", languages=["et"])

class NotYetImplementedForm(Schema):
    "Valideerimisskeem vaikimisi kasutamiseks vormides, kus ei ole oma skeemi"
    pass
