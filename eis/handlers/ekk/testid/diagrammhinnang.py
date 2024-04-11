# -*- coding: utf-8 -*- 

from eis.lib.base import *
_ = i18n._
from eis.model import sa
from eis.lib.feedbackdgm import FeedbackDgmHinnang
log = logging.getLogger(__name__)

class DiagrammhinnangController(BaseController):
    _authorize = False
    
    def index(self):
        encoded_params = self.request.params.get('data')
        dgm = FeedbackDgmHinnang(self, None)
        filedata = dgm.draw_params(encoded_params, 300)
        return Response(filedata, content_type='image/png')
