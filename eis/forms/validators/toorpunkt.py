# -*- coding: utf-8 -*-
"Validaatorid"

import re
from datetime import datetime, date
import formencode
from formencode.validators import *
import eiscore.i18n as i18n
_ = i18n._

class Toorpunkt(FancyValidator):
    "Toorpunkti sisestamisel sisestatakse arv voi '-' (vastamata)"

    def _convert_to_python(self, value, state):
        value = value.strip()
        if value != '-': # const.PUNKTID_VASTAMATA
            try:
                value = float(value.replace(',','.'))
            except ValueError:
                msg = _("Palun sisestada arv või -")
                raise Invalid(msg, value, state)
        return value

