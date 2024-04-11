"""
Kontaktandmete salvestamine (e-posti aadressiga).
Kui EISi andmebaasis kasutaja isiku kirjet ei ole, siis antakse veateade.
Kui isikukirje on olemas, siis salvestatakse sisendis antud andmed.
"""
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *
from eis import model
import eiscore.const as const
import eis.lib.helpers as h
import eis.lib.utils as utils
from eis.lib.xtee.xroad import *
import formencode
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
        epost = get_text(paring, 'epost_aadr')
        try:
            formencode.validators.Email().to_python(epost)
        except formencode.api.Invalid as ex:
            error = 'E-posti aadress %s on vigane' % epost
        else:
            k.epost = epost
            error = _save(k, paring)

    if error:
        res = E.response(E.teade(error))
    else:
        model.Session.commit()
        res = E.response(E.teade('Kontaktandmed salvestatud'),
                     E.edasi(''))

    return res, []

def _save(k, paring):
    error = None
    # if save_nimi:
    #     k.eesnimi = paring.find('eesnimi').text
    #     k.perenimi = paring.find('perenimi').text

    if not k.kodakond_kood:
        k.kodakond_kood = get_text(paring, 'kodak')
    
    k.telefon = get_text(paring, 'kontakt_tel', 20)
    #r = paring.find('epost_teavita')
    if not k.epost:
        error = 'E-teavitus on aktiveeritud, täida ka e-posti aadress!'

    asula = get_text(paring, 'asula')

    aadress = paring.find('aadress')
    if aadress is not None:
        k.postiindeks = get_text(aadress, 'indeks', 5)
        lahiaadress = get_text(aadress, 'lahiaadress')
    else:
        lahiaadress = None

    if not asula or not lahiaadress:
        error = 'Sisestage aadress'
    else:
        k.aadress_id, k.normimata = model.Aadress.from_ehak(asula, lahiaadress)        
    return error
