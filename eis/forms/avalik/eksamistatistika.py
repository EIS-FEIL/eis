import formencode
from eis.forms.validators import *
from eis.model import const

class EksamistatistikaForm(Schema):
    aasta = Number(if_missing=None)
    alla = Number(if_missing=None)
    yle = Number(if_missing=None)
    sugu = formencode.ForEach(String)
    maakond = formencode.ForEach(String)
    kov = formencode.ForEach(String)
    koolityyp = formencode.ForEach(String)
    oppekeel = formencode.ForEach(String)
    soorituskeel = formencode.ForEach(String)
    ko = formencode.ForEach(String) # kool_id
    oppevorm = formencode.ForEach(String)
    test_id = String(if_missing=None)
