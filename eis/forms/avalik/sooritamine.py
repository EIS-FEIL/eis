# -*- coding: utf-8 -*-
"Avaliku vaate testide valideerimisskeemid"

import formencode
from eis.forms.validators import *

class OtsingForm(Schema):
    "Otsingu vorm"
    test_id = Int(if_missing=None, min=1)
    testimiskord_id = Int(if_missing=None, min=1)
    avaldamistase = Int(if_missing=0)
    omanik = String(if_missing=None)
    aine = String(if_missing=None)
    nimi = String(if_missing=None)
    
class VaieForm(Schema):
    "Vaide koostamise vorm"
    
    #k_maakond_id = Int()
    #k_vald_id = Int()
    #k_asula_id = Int()
    #k_aadress = String()
    k_postiindeks = String()
    k_telefon = String()
    k_epost = Email(strip=True, max=255)
    f_markus = String(not_empty=True)
    f_otsus_epostiga = Bool(if_missing=False)
    # aadress
    a_kood = formencode.ForEach(String)
    a_normimata = String(max=200)

class SkannidTellimineForm(Schema):
    #soovib_p = Bool
    soovib_skanni = Bool
    k_epost = Email(strip=True, max=255, not_empty=True)
    chained_validators = [AnyNotEmpty('soovib_skanni')]
