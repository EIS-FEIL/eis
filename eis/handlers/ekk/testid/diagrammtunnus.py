from eis.lib.base import *
_ = i18n._
from eis.model import sa
from eis.lib.feedbackdgm import get_feedbackdgm
log = logging.getLogger(__name__)

class DiagrammtunnusController(BaseController):
    _authorize = False
    
    def index(self):
        params = self.request.params
        encoded_params = params.get('data')
        dname = params.get('dname') or 'tunnused2'
        width = int(params.get('width') or 900)
        dgm = get_feedbackdgm(dname)(self, None)
        filedata = dgm.draw_params(encoded_params, width)
        return Response(filedata, content_type='image/png')
