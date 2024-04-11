"""
Riigiportaali autenditud kasutaja suunamine EISi põhiseaduse ja kodakondsuse seaduse tundmise eksamitele registreerimise vormile. Teenusega genereeritakse EISis unikaalne ühekordselt kasutatav URL, mis seotakse teenuse kasutaja identiteediga. Riigiportaal suunab kasutaja sellele URLile, EIS loeb kasutaja autendituks ilma täiendava sisse logimiseta ning avab soovitud liiki eksamitele registreerimise vormi.
"""
from eis import model
from eis.model import const
from .legacyX import add_legacy

import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):
    """Eesti.ee portaali kaudu sisenemise teenus
    Päringu sisendist saame kasutaja andmed ja genereerime võtme, millega need andmed seostame.
    Päringu väljundis anname võtmega URLi, mille poole kasutaja hiljem brauseriga otse pöördub
    ja kus saame võtme järgi kasutajaandmed kätte.
    """
    model.Paring_logi.log(header)
    return add_legacy(paring, header, context, const.TESTILIIK_SEADUS)
    
