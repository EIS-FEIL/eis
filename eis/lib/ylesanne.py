"Ülesande pseudokontroller"

from eis.lib.base import *
from eis.lib.block import *

log = logging.getLogger(__name__)

class YlesanneController(object):

    def __init__(self, ylesanne):
        self.ylesanne = ylesanne
        self.plokikontrollerid = []
        for plokk in self.ylesanne.sisuplokid:
            # luuakse plokk.ctrl
            BlockController.get(plokk, ylesanne, None)

    def check(self):
        "Skriptiga ylesannete kontrollimiseks"
        rc = True
        has_interaction = False
        arvutihinnatav = self.ylesanne.arvutihinnatav
        print('Ülesanne %d: %s' % (self.ylesanne.id, self.ylesanne.nimi))
        for plokk in self.ylesanne.sisuplokid:
            print('  Sisuplokk %d (%s)' % (plokk.id, plokk.tyyp_nimi), end=' ')
            has_interaction |= plokk.is_interaction
            rc1, li = plokk.ctrl.check(arvutihinnatav)
            rc &= rc1

            if not li:
                print("  OK")
            else:
                print("")
                for line in li:
                    print('  PROBLEEM ' + line)
