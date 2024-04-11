import formencode
from .validators import *

class LoginParoolForm(Schema):
    username = String
    parool = String

class ParoolForm(Schema):
    parool_vana = String(if_missing=None, not_empty=True)
    parool_uus = String(not_empty=True, min=5)
    parool_uus2 = String(not_empty=True)
    chained_validators = [FieldsMatch('parool_uus', 'parool_uus2')]

class IsikuandmedForm(Schema):
    k_postiindeks = String(max=5)
    k_telefon = String(max=20)
    k_epost = Email(max=30)
    epost2 = Email
    # aadress
    a_kood = formencode.ForEach(String)
    a_normimata = String(max=200)
    teavita = formencode.ForEach(String)
    chained_validators = [FieldsMatch('k_epost', 'epost2')]

class KontaktuuendamineForm(Schema):
    chk_epost = Email(max=30, not_empty=True)
    chk_epost2 = Email
    chained_validators = [FieldsMatch('chk_epost', 'chk_epost2')]

class MinuteatedForm(Schema):
    staatus = formencode.ForEach(Int)
    teatekanal = Int(if_missing=None)
    
