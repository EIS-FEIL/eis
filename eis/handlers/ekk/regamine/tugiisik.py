from eis.lib.baseresource import *
_ = i18n._
import eis.handlers.avalik.nimekirjad.tugiisik as tugiisik
log = logging.getLogger(__name__)

class TugiisikController(tugiisik.TugiisikController):
    """Tugiisiku määramine
    """
    _permission = 'regamine'
    _INDEX_TEMPLATE = 'ekk/regamine/tugiisik.mako'
    _get_is_readonly = False
    _actions = 'index,create'

    def _after_create(self, none_id):
        if self.has_errors():
            return self._index_d()
        else:
            return HTTPFound(location=self.url('regamine_erivajadus', id=self.c.sooritus.id))
    
    def __before__(self):
        c = self.c
        sooritus_id = self.request.matchdict.get('sooritus_id')
        c.sooritus = model.Sooritus.get(sooritus_id)
        c.sooritaja = c.sooritus.sooritaja
        c.test = c.sooritaja.test
        c.testimiskord = c.sooritaja.testimiskord

    def _perm_params(self):
        pass
