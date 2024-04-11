from eis.lib.baseresource import *
_ = i18n._
import eis.handlers.avalik.nimekirjad.tugiisik as tugiisik
log = logging.getLogger(__name__)

class TugiisikController(tugiisik.TugiisikController):
    """Tugiisiku määramine
    """
    _INDEX_TEMPLATE = 'avalik/nimekirjad/tugiisik.mako'
    def _after_create(self, none_id):
        if not self.has_errors():
            self.success()
        c = self.c
        return HTTPFound(location=self.url('nimekirjad_avaldus_testid', id=c.sooritaja.kasutaja_id, testiliik=c.test.testiliik_kood))

    def _create(self):            
        """Tugiisiku määramine
        """
        for tos in self.c.sooritaja.sooritused:
            self._set_tugik(tos)
        model.Session.commit()
    
    def __before__(self):
        c = self.c
        sooritaja_id = self.request.matchdict.get('sooritaja_id')
        c.sooritaja = model.Sooritaja.get(sooritaja_id)
        c.test = c.sooritaja.test

    def _perm_params(self):
        c = self.c
        testiliik = self.request.params.get('testiliik')
        if testiliik:
            return {'testiliik': testiliik, 'koht_id': c.user.koht_id}
