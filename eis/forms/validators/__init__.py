import formencode
import sqlalchemy as sa
from .isikukood import *
from .date import *
from .ranges import *
from .identifier import *
from .toorpunkt import *
from .email import Email
import eiscore.i18n as i18n
_ = i18n._

from formencode.api import is_validator, FancyValidator, Invalid, NoDefault

import logging
log = logging.getLogger(__name__)

class Schema(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = False

class Number(formencode.validators.Number):
    def _convert_to_python(self, value, state):
        if isinstance(value, str):
            value = value.replace(',','.')
        return formencode.validators.Number._to_python(self, value, state)
           
class NameRus(String):

    ruRE = re.compile(r"^[\- абвгдеёжзийклмнопрстуфхцчшщьыъэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ]*$")

    def _convert_to_python(self, value, state):
        value = super(NameRus, self)._convert_to_python(value, state)
        if value:
            value = value.strip()
        return value

    def _validate_other(self, value, state):
        super(NameRus, self).validate_other(value, state)
        if value:
            if not self.ruRE.match(value):
                msg = _("Palun kirjutada nimi vene tähtedega")
                raise Invalid(msg, value, state)

class IDRange(FancyValidator):
    "Ylesannete ID-de vahemik kujul ID1,ID2,ID3-ID4,ID5-"

    def _convert_to_python(self, value, state):
        try:
            self.str_to_list(value)
            return value
        except Exception as ex:
            msg = _("Palun sisestada ID või mitu ID-d (eraldatud tühikute või komadega) või ID-de vahemik (sidekriipsuga)") 
            raise Invalid(msg, value, state)

    def str_to_list(self, value):
        li = []
        value = (value or '').replace(' ', ',')
        for buf in value.split(','):
            buf = buf.strip()
            if not buf:
                continue
            id1 = id2 = None
            if buf.find('-') > -1:
                buf1, buf2 = buf.split('-')
                if buf1:
                    id1 = int(buf1)
                if buf2:
                    id2 = int(buf2)
                if id1 and id2:
                    assert id1 <= id2, 'range error'
            else:
                id1 = id2 = int(buf)
            li.append((id1, id2))
        return li

    def str_from_list(self, value):
        li_range = []
        range_start = range_end = None
        for id1, id2 in sorted(value):
            if id1 and (id1 == id2):
                li_range.append(f'{id1}')
            elif id1 and id2:
                li_range.append(f'{id1}-{id2}')
            elif id1:
                li_range.append(f'{id1}-')
            elif id2:
                li_range.append(f'-{id2}')
        return ','.join(li_range)

    @classmethod
    def filter(cls, value, field):
        "Päringusse filtri moodustamine"
        try:
            li_id = IDRange().str_to_list(value)
        except Exception:
            return
        else:
            flt = None
            for id1, id2 in li_id:
                if id1 and id1 == id2:
                    f = (field == id1)
                elif id1 and id2:
                    f = sa.and_(id1 <= field, field <= id2)
                elif id1:
                    f = (id1 <= field)
                elif id2:
                    f = (field <= id2)
                else:
                    continue
                if flt is None:
                    flt = f
                else:
                    flt = sa.or_(flt, f)
            return flt
