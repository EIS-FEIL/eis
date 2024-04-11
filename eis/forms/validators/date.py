# -*- coding: utf-8 -*-
"Validaatorid"

import re
from datetime import datetime, date
import formencode
from formencode.validators import *
import eiscore.i18n as i18n
_ = i18n._

class EstDateConverter(DateConverter):
    """
    Kuupaeva konverter/validaator Eesti kuupaeva vorminguga
    """
    month_style = 'dmy'
    separator = '.'

class EstTimeConverter(TimeConverter):
    # lisatud eraldaja punkti võimalus kooloni asemel
    def _to_python_tuple(self, value, state):
        value = value.replace('.', ':')
        return TimeConverter._to_python_tuple(self, value, state)

    def _convert_from_python(self, value, state):
        buf = TimeConverter._convert_from_python(self, value, state)
        if buf:
            buf = buf.replace(':', '.')
        return buf
   
        
class DateRange(FormValidator):
    """
    Kontrollitakse ajavahemikku.
    """
    field_names = None
    validate_partial_form = True
    __unpackargs__ = ('*', 'field_names')

    def _validate_python(self, field_dict, state):
        nameStart = self.field_names[0]
        nameEnd = self.field_names[1]
        if len(self.field_names) >= 3:
            message = self.field_names[2]
        else:
            message = None
        errors = {}

        dtStart = field_dict[nameStart]
        dtEnd = field_dict[nameEnd]        
        if dtStart and dtEnd:
            if dtStart > dtEnd:
                if message:
                    errors[nameEnd] = message
                else:
                    errors[nameEnd] = _("Vahemik ei saa lõppeda enne algust")
            
        if errors:
            error_list = list(errors.items())
            error_list.sort()
            error_message = '<br>\n'.join(
                ['%s: %s' % (name, value) for name, value in error_list])
            raise Invalid(error_message,
                          field_dict,
                          state,
                          error_dict=errors)    

class Piiraeg(FancyValidator):

    with_sec = False

    def _convert_to_python(self, value, state):
        time = value.strip()
        if self.with_sec:
            n_sec = -1
            n_min = -2
            n_hour = -3
            msg = _("Palun sisestada kujul hh.mm.ss")
        else:
            n_sec = None
            n_min = -1
            n_hour = -2
            msg = _("Palun sisestada kujul hh.mm")
            
        try:
            parts = list(map(int, re.split('[:.]', time)))
        except:
            raise Invalid(msg, value, state)               
        result = 0
        if n_sec:
            if parts[n_sec] > 59:
                msg = _("Sekundid peavad olema vahemikus 0-59")
                raise Invalid(msg, value, state)
            result = parts[n_sec]
        if len(parts) >= 0 - n_min:
            if parts[n_min] > 59:
                msg = _("Minutid peavad olema vahemikus 0-59")
                raise Invalid(msg, value, state)                
            result += parts[n_min] * 60
        if len(parts) >= 0 - n_hour:
            result += parts[n_hour] * 3600

        if result == 0:
            result = None
            #msg = _("Nullaega pole mõtet sisestada")
            #raise Invalid(msg, value, state)
        return result

    def _convert_from_python(self, value, state):
        if isinstance(value, (int, float)):
            hours = value / 3600
            minutes = value % 3600 / 60
            seconds = value % 60
            if self.with_sec:
                # HHMMSS
                return '%02i.%02i.%i' % (hours, minutes, seconds)
            else:
                # HHMM
                return '%02i.%02i' % (hours, minutes)
        else:
            return value

def _ddFromStr(sDate):
    """
    Kui parameeter on teisendatav kuupäevaks, siis tagastatakse väärtus kuupäevana.
    Muidu tagastatakse None.
    """
    dd = None
    if type(sDate) in (date, datetime):
        dd = sDate
    else:
        try:
            match = re.match(r'(?P<day>\d+).(?P<month>\d+).(?P<year>\d+)', sDate)
            if match:
                (d,m,y) = match.groups()
                nYear = int(y)
                nMonth = int(m)
                nDay = int(d)
                if nYear < 100:
                    # mõtleme ise sajandi juurde
                    dd = date(nYear + 2000, nMonth, nDay)
                    if dd > date.today():
                        # aga nii, et ei oleks tulevikus
                        dd = date(nYear + 1900, nMonth, nDay)
                else:
                    dd = date(nYear, nMonth, nDay)
        except:
            pass
    return dd
