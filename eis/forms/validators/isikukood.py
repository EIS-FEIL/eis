"""
Isikukoodi klass ja validaator
"""
import formencode
from formencode.validators import *
import re
from datetime import datetime, date
from unidecode import unidecode
import eiscore.const as const
import eiscore.i18n as i18n
_ = i18n._

# globaalne seade, mida saab eemalt mõjutada
check_digit = True

class String(formencode.validators.String):
    strip = True

class Isikukood(FormValidator):
    """
    Kontrollitakse isikukoodi sobivust.
    """
    field_names = None
    validate_partial_form = True
    check_digit = None # kas kontrollida isikukoodi kontrolljärku

    def country_code(self, value):
        global check_digit
        rc = True
        country = code = None
        if value:
            if self.check_digit is None:
                cd = check_digit
            else:
                cd = self.check_digit
            value = value.strip().upper()
            m = re.match(r'([A-Z]{2})(.+)', value)
            if m:
                # riigi kood on ees
                country, code = m.groups()
            else:
                # riigi koodi pole - vaikimisi on Eesti 
                country = const.RIIK_EE
                code = value
            if country in (const.RIIK_EE, const.RIIK_LT):
                # riigid, mille isikukoodi oskame kontrollida
                obj = IsikukoodEE(code, check_digit=cd)
                if not obj.parse():
                    rc = False
        return rc, country, code

    def _validate_python(self, value, state):
        "Isikukoodi kontroll"
        global check_digit
        if value:
            rc, country, code = self.country_code(value)
            if not rc:
                msg = _("Vigane isikukood")
                raise Invalid(msg, value, state)
        elif self.not_empty:
            msg = _("Palun sisestada isikukood")
            raise Invalid(msg, value, state)

    def _convert_to_python(self, value, state):
        if value is not None:
            if value.startswith(const.RIIK_EE):
                # Eesti isikukoodid salvestame ilma riigi prefiksita
                value = value[2:]
            return value.strip().upper()

class IsikukoodP:
    "Isikukoodi parser formaadi kontrollimiseks ja riigi eraldamiseks"
    country = None
    code = None
    isikukood = None

    def __init__(self, value, validate=True):
        "Eristatakse, kas väärtus võib olla isikukood või kasutajatunnus"
        rc, self.country, self.code = Isikukood().country_code(value)
        if rc:
            # sobib isikukoodiks
            if self.country == const.RIIK_EE:
                # ilma riigi prefiksita
                self.isikukood = self.code
            else:
                # koos riigi prefiksiga
                self.isikukood = f'{self.country}{self.code}'

    def filter(self, Kasutaja):
        "Päringutes kasutamiseks"
        if self.isikukood:
            return Kasutaja.isikukood == self.isikukood
        else:
            # kasutaja, keda pole
            return Kasutaja.id == None

    def get(self, Kasutaja, write=False):
        if self.valid:
            if write:
                q = Kasutaja.query
            else:
                q = Kasutaja.queryR
            return q.filter(self.filter(Kasutaja)).first()
        
    @property
    def valid(self):
        "Kas väärtus sobib isiku määramiseks"
        return bool(self.isikukood)

    @property
    def isikukood_ee(self):
        "Tagastatakse Eesti isikukood, kui on Eesti isikukood"
        if self.country == const.RIIK_EE:
            return self.isikukood
        
class IsikukoodEE(object):
    """
    Isikukoodi kontrollimine.
    """

    _pattern = re.compile(r"""^\s*(?P<full>
        (?P<S>[123456])
        (?P<Y>[0-9]{2})
        (?P<M>[0-9]{2})
        (?P<D>[0-9]{2})
        (?P<N>[0-9]{3})
        (?P<C>[0-9])
        )\s*$""", re.X)
    
    _centuries = dict((n, 1800+(n-1)//2*100) for n in range(1,7))
    _check_digit = True

    def __init__(self, value, check_digit=True):
        self.birthdate = None
        self.sex = None
        self.code = value
        self._check_digit = check_digit
        
    def parse(self):
        """
        Parsitakse isikukood.
        Kui leitakse vigu, tagastatakse False.
        Kui vigu ei ole, tagastatakse True ning seatakse self.birthdate ja self.sex.
        """
        match = self._pattern.match(self.code)
        if not match:
            return False
        parts = dict((key, int(value)) for key,value in list(match.groupdict().items()))
        try:
            birthdate = date(self._centuries[parts['S']] + parts['Y'],
                             parts['M'],
                             parts['D'])
        except ValueError:
            return False

        if self._check_digit:
            if birthdate > date.today():
                return False
            if parts['C'] != self._calculate_check(match.group('full')):
                return False

        self.birthdate = birthdate
        self.sex = self._detect_sex(parts['S'])
        return True

    def _calculate_check(self, code):
        checksums = [sum(int(char)*((pos + offset)%9 + 1)
                for pos,char in enumerate(code[0:10])) % 11
            for offset in [0,2]] + [0]
        return [s for s in checksums if s<10][0]

    def _detect_sex(self, firstchar):
        return int(firstchar) % 2 and 'M' or 'N'

class MIDphone(FormValidator):
    """
    Kontrollitakse telefoni sobivust m-ID jaoks
    """
    field_names = None
    validate_partial_form = True

    def _convert_to_python(self, value, state):
        if value:
            value = value.strip().replace(' ','')
            if value and value.startswith('372') and len(value) >= 10:
                value = '+' + value
            elif value and value[0] != '+':
                value = '+372' + value
        # test-telefon on +37200007
        if value and not re.match(r'^\+\d{8,}$', value):
            msg = _("Palun sisestada korrektne telefoninumber")
            raise Invalid(msg, value, state)
        if not value and self.not_empty:
            msg = _("Palun sisestada telefoninumber")
            raise Invalid(msg, value, state)
        return value

