"Töökogumike valideerimisskeemid"

import formencode
from eis.forms.validators import *

class OtsingForm(Schema):
    "Otsingu vorm"
    id = Int(if_missing=None, min=1)
    nimi = String(if_missing=None)
    aine = String(if_missing=None)
    klass = String(if_missing=None)

class TookogumikForm(Schema):
    "Töökogumiku vorm"
    f_nimi = String(not_empty=True, max=256)
    itemid = formencode.ForEach(String)
    
class YlesandekoguOtsingForm(Schema):
    "Otsingu vorm"
    aine = String(if_missing=None)
    aste = String(if_missing=None)
    klass = String(if_missing=None)
    term = String(if_missing=None)
    #tb = formencode.ForEach(String)

class YlesandeOtsingForm(Schema):
    "Otsingu vorm"
    ylesanne_id = Int(if_missing=None, min=1)
    aine = String(if_missing=None)
    keeletase = String(if_missing=None)
    aste = String(if_missing=None)
    testiliik = String(if_missing=None)
    teema = String(if_missing=None)
    alateema = String(if_missing=None)
    opitulemus_id = Number(if_missing=None)
    lang = String(if_missing=None)
    kysimus = String(if_missing=None)
    staatus = Int(if_missing=None)
    
class TestiOtsingForm(Schema):
    "Otsingu vorm"
    test_id = Int(if_missing=None, min=1)
    testiliik = String(if_missing=None)
    aine = String(if_missing=None)
    aste = String(if_missing=None)
    minu = Bool(if_missing=None)

class OtsivaatajaForm(Schema):
    "Otsingu vorm"
    eesnimi = String(if_missing=None)
    perenimi = String(if_missing=None)
