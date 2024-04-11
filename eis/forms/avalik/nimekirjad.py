"Registreerimise valideerimisskeemid"

import formencode
from eis.forms.validators import *
import eiscore.const as const

class SisseastumineForm(Schema):
    k_epost = Email(max=30)
    epost2 = Email(max=30)
    chained_validators = [MustBeCopy('k_epost', 'epost2')]
    
