"""
Kontaktandmete salvestamine (e-posti aadressita).
Kui EISi andmebaasis kasutaja isiku kirjet ei ole, siis antakse veateade.
Kui isikukirje on olemas, siis salvestatakse sisendis antud andmed.
"""
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *
from eis import model
import eiscore.const as const
import eis.lib.helpers as h
import eis.lib.utils as utils
from .muuda_kontakt1_kod import _save

import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):
    error = teade = None
    ik = header.userId[2:]
    model.Paring_logi.log(header, paritav=ik)
    k = model.Kasutaja.get_by_ik(ik)
    if not k:
        error = 'Isikuandmeid ei leitud'
    else:
        error = _save(k, paring)

    if error:
        res = E.response(E.teade(error))
    else:
        model.Session.commit()
        res = E.response(E.teade('Kontaktandmed salvestatud'),
                     E.edasi(''))

    return res, []

