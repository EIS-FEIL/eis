from eis.lib.baseresource import *
import eis.handlers.ekk.hindamine.analyyskvstatistikad as analyyskvstatistikad
_ = i18n._

log = logging.getLogger(__name__)

class AnalyyskvstatistikadController(analyyskvstatistikad.AnalyyskvstatistikadController):
    "Vastuste analyysi vastuste loetelu kuvamine"
    _permission = 'ekk-testid'

    def _perm_params(self):
        return {'obj': self.c.test}

    def __before__(self):
        c = self.c
        c.test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(c.test_id)
        kst_id = self.request.matchdict.get('kst_id')
        c.kst = model.Kysimusestatistika.get(kst_id)
        c.kvst_order = self.request.params.get('kvst_order')

