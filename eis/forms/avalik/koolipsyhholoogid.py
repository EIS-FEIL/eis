"Administreerimisliidese valideerimisskeemid"

import formencode
from eis.forms.validators import *
from eis.model import const

class KoolipsyhholoogidForm(Schema):
    "Otsingu vorm"
    pass

class KoolipsyhholoogForm(Schema):

    k_eesnimi = String(max=50, not_empty=True)
    k_perenimi = String(max=50, not_empty=True)
    isikukood = String(not_empty=True)
    k_synnikpv = EstDateConverter(not_empty=True)
    k_sugu = String(not_empty=True)
    parool = String(if_missing=None)
    k_postiindeks = String(max=5)
    k_telefon = String(max=20)
    k_epost = Email(strip=True, max=255)
    # aadress
    a_kood = formencode.ForEach(String)
    a_normimata = String(max=200)

class LitsentsidForm(Schema):
    pass
