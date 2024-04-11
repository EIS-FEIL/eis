"""
Isikukoodi klass ja validaator
"""
import formencode
from formencode.validators import *

import eiscore.i18n as i18n
_ = i18n._

import re
import logging
log = logging.getLogger(__name__)

class Identifier(FancyValidator):
    # +CombiningChar, Extender
    regexp = re.compile(r"^[A-Za-z0-9\.\-\_]*$")
    messages = {
        'bad': "Code may contain characters, numbers, underscore, minus and dot"
        }

    def _validate_python(self, value, state):
        if not value:
            return
        value = value.strip()
        if not self.regexp.search(value):
            raise Invalid(self.message('bad', state, value=value),
                          value, state)

    def _convert_to_python(self, value, state):
        return value.strip()

class PyIdentifier(FancyValidator):
    regexp = re.compile(r"^[A-Za-z\_][A-Za-z0-9\_]*$")
    def _validate_python(self, value, state):
        if not value:
            return
        value = value.strip()
        if not self.regexp.search(value) or \
           value and ((value[0] in '_0123456789') or (value[-1] == '_')):
            # algav alakriips on reserveeritud EISi parameetritele
            # lõppev alakriips on reserveeritud EISi jrk sufiksile koodi järel _N_
            msg = _("Kood võib sisaldada tähti, numbreid ja alakriipsu, kuid ei tohi alata numbriga, ei tohi alata ega lõppeda alakriipsuga")
            raise Invalid(msg, value, state)

    def _convert_to_python(self, value, state):
        return value.strip()

class Alphanum(FancyValidator):
    regexp = re.compile(r"^[A-Za-z0-9]*$")
    min = None
    max = None

    def _validate_python(self, value, state):
        if not value:
            return
        value = value.strip()
        if not self.regexp.search(value):
            request = state.request
            msg = _("Väärtus võib sisaldada ainult tähti ja numbreid")
            raise Invalid(msg, value, state)
        if self.max is not None and len(value) > self.max:
            request = state.request
            msg = _("Sisestada saab kuni {max} sümbolit").format(max=self.max)
            raise Invalid(msg, value, state)

    def _convert_to_python(self, value, state):
        return value.strip()
