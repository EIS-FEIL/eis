"Arvutusprotsessiga genereeritud faili allalaadimine"
from eis.lib.baseresource import *
log = logging.getLogger(__name__)
_ = i18n._

class ProtsessifailController(BaseController):
    _authorize = False
    _actions = 'download'
    _MODEL = model.Arvutusprotsess
            
    def download(self):
        c = self.c
        id = self.request.matchdict.get('id')
        rcd = model.Arvutusprotsess.get(id)
        if not rcd or not rcd.has_file:
            raise NotFound(_("Kirjet ei leitud"))
        if rcd.kasutaja_id != c.user.id and not c.user.on_admin:
            raise NotFound(_("Teise kasutaja genereeritud fail"))
        return utils.download(rcd.filedata, rcd.filename, rcd.mimetype)

        
