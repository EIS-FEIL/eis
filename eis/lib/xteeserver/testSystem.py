"""
X-tee adapterserveri monitooringuteenus
"""

from eis.lib.pyxadapterlib.xutils import *
from eis import model
from eis.model import const
import eis.lib.helpers as h
from eis.lib.xtee.xroad import fstr, test_me

def serve(paring, header=None, attachments=[], context=None):
    error = None
    # kontrollime, et andmebaas on kättesaadav
    r = model.Olekuinfo.get(model.Olekuinfo.ID_KASUTAJA)
    res = E.response(datetime.now())
    return res, []

if __name__ == '__main__':
    from eis.scripts.scriptuser import *

    paring = E.request()
    test_me(serve, 'testSystem.v1', paring, named_args)    

