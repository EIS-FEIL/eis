from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class YlesandeainedController(BaseResourceController):

    _permission = 'ylesanded'
    def new(self):
        params = self.request.params
        self.c.yaine_seq = int(params.get('seq'))
        self.c.yaine = NewItem()
        self.c.aste_kood = params.get('aste')
        self.h.rqexp(True) # et kuvaks tärne
        return self.render_to_response('/ekk/ylesanded/yldandmed.ylesandeaine.mako')
