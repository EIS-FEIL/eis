import formencode
from eis.forms.validators import *
from eis.model import const

class KlassidForm(Schema):
    klassid_id = formencode.ForEach(String)
    op_id = formencode.ForEach(String)
    
class GruppForm(Schema):
    klassid_id = formencode.ForEach(String)
    op_id = formencode.ForEach(String)
    valimis = Bool(if_missing=None)
