from eis.lib.baseresource import *
_ = i18n._
import eis.handlers.admin.paroolid as paroolid
from eis.lib.xtee import ehis

log = logging.getLogger(__name__)

class ParoolidController(paroolid.ParoolidController):

    _permission = 'paroolid'

    def _can_set_pwd(self, kasutaja):
        "Parooli saab muuta tavalisel kasutajal, kellel pole õiguseid"
        rc = False
        if kasutaja:
            if kasutaja.on_labiviija:
                return False, _("Selle kasutaja parooli muutmiseks on eriõiguseid vaja")
            for r in kasutaja.kasutajarollid:
                # sh kontrollitakse, kas on ametniku roll
                if r.kehtiv:
                    return False, _("Selle kasutaja parooli muutmiseks on eriõiguseid vaja")                    

            # kontrollime, et isik on oma kooli õpilane
            isikukood = kasutaja.isikukood
            message = ehis.uuenda_opilased(self, [isikukood])
            if message:
                # päring ebaõnnestus
                return False, message
            opilane = model.Opilane.get_by_ik(isikukood)
            if opilane and opilane.koht_id == self.c.user.koht_id:
                return True, None
        return False, _("Selle kasutaja parooli ei saa muuta, sest ta pole oma kooli õpilane")

    def _perm_params(self):
        if not self.c.user.koht_id:
            return False
