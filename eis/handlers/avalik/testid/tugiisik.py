from eis.lib.baseresource import *
_ = i18n._
import eis.handlers.avalik.nimekirjad.tugiisik as tugiisik
log = logging.getLogger(__name__)

class TugiisikController(tugiisik.TugiisikController):
    """Tugiisiku määramine
    """
    _permission = 'omanimekirjad'
    _INDEX_TEMPLATE = 'avalik/nimekirjad/tugiisik.mako'

    def _create(self):            
        """Tugiisiku määramine
        """
        for tos in self.c.sooritaja.sooritused:
            self._set_tugik(tos)
        model.Session.commit()
    
    def _after_create(self, none_id):
        c = self.c
        if self.has_errors():
            return self._index_d()
        else:
            self.success()
            return HTTPFound(location=self.url('test_nimekiri_kanne', nimekiri_id=c.nimekiri.id, id=c.sooritaja.id, test_id=c.test.id, testiruum_id=c.testiruum_id))

    def __before__(self):
        self.c.test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(self.c.test_id)
        self.c.testiruum_id = self.request.matchdict.get('testiruum_id')
        nimekiri_id = self.request.matchdict.get('nimekiri_id')
        self.c.nimekiri = model.Nimekiri.get(nimekiri_id)
        sooritaja_id = self.request.matchdict.get('sooritaja_id')
        self.c.sooritaja = model.Sooritaja.get(sooritaja_id)
        assert self.c.sooritaja.nimekiri_id == self.c.nimekiri.id and self.c.sooritaja.test_id == self.c.test.id, 'vale sooritaja'
        
    def _perm_params(self):
        return {'obj':self.c.nimekiri}


