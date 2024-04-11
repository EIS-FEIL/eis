from eis.lib.baseresource import *
from .feedbackbase import FeedbackBaseController
_ = i18n._

log = logging.getLogger(__name__)

class GruppidetulemusedController(FeedbackBaseController, BaseResourceController):
    "Gruppide tulemuste sakk"
    _permission = 'avalikadmin,testiadmin,aineopetaja'
    _SEARCH_FORM = forms.avalik.tulemused.KlassidForm
    _INDEX_TEMPLATE = 'avalik/ktulemused/gruppidetulemused.mako'
    _LIST_TEMPLATE = 'avalik/ktulemused/gruppidetulemused_list.mako'
    _actions = 'index,download'
    # automaatse tagasisidevormi genereerimisel võib olla vaja see salvestada
    _kohteelvaade_readonly = False
    _tvliik = model.Tagasisidevorm.LIIK_GRUPPIDETULEMUSED
    
    def _get_fr(self, test, lang, kursus):
        c = self.c
        fr = eis.lib.feedbackreport.FeedbackReport.init_gruppidetulemused(self, test, lang, kursus, c.testimiskord)
        return fr
