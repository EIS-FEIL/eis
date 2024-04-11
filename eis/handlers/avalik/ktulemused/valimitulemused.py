from eis.lib.baseresource import *
from .feedbackbase import FeedbackBaseController
_ = i18n._

log = logging.getLogger(__name__)

class ValimitulemusedController(FeedbackBaseController, BaseResourceController):
    "Valimi koondtulemus"
    _permission = 'avalikadmin,testiadmin,aineopetaja'
    _MODEL = model.Sooritaja
    _SEARCH_FORM = forms.avalik.tulemused.GruppForm
    _INDEX_TEMPLATE = 'avalik/ktulemused/valimitulemused.mako'
    _LIST_TEMPLATE = 'avalik/ktulemused/gruppidetulemused_list.mako'
    _actions = 'index,download'

    _tvliik = model.Tagasisidevorm.LIIK_VALIM

    def _search(self, q):
        "Otsing ilma klasside ja õpetajateta"
        c = self.c
        res = self._get_tagasiside(None, [], [], c.kursus, valimis=True)
        if c.pdf or c.xls:
            return res
        else:
            c.tagasiside_html = res
    
    def _get_fr(self, test, lang, kursus):
        c = self.c
        fr = eis.lib.feedbackreport.FeedbackReport.init_valim(self, test, lang, kursus, c.testimiskord)
        return fr
