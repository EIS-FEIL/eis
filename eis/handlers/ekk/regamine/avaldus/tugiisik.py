from eis.lib.baseresource import *
_ = i18n._
import eis.handlers.ekk.regamine.tugiisik as tugiisik
log = logging.getLogger(__name__)

class TugiisikController(tugiisik.TugiisikController):
    """Tugiisiku määramine
    """
    _INDEX_TEMPLATE = 'ekk/regamine/tugiisik.mako'

    def _create(self):            
        """Tugiisiku määramine
        """
        c = self.c
        params = self.request.params
        for testiosa in self.c.test.testiosad:
            tkid = params.get('tkid_%s' % testiosa.id) or None
            if tkid:
                tkid = int(tkid)
                if tkid == c.sooritaja.kasutaja_id:
                    self.error(_("Sooritaja ei saa ise enda tugiisik olla"))
                    model.Session.rollback()
                    return
            tos = c.sooritaja.get_sooritus(testiosa.id)
            tos.tugiisik_kasutaja_id = tkid
            tos.set_erivajadused(tkid and True or None)            
        model.Session.commit()

    def _after_create(self, none_id):
        if not self.has_errors():
            self.success()
        c = self.c
        return HTTPFound(location=self.url('regamine_avaldus_testid', id=c.sooritaja.kasutaja_id, testiliik=c.test.testiliik_kood))
    
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
