from eis.lib.baseresource import *
from .feedbackbase import FeedbackBaseController
_ = i18n._

log = logging.getLogger(__name__)

class OsalejatetulemusedController(FeedbackBaseController, BaseResourceController):
    "Õpilaste tulemuste tabel"
    _permission = 'avalikadmin,testiadmin,aineopetaja'
    _MODEL = model.Sooritaja
    _SEARCH_FORM = forms.avalik.tulemused.GruppForm
    _INDEX_TEMPLATE = 'avalik/ktulemused/osalejatetulemused.mako'
    _LIST_TEMPLATE = 'avalik/ktulemused/gruppidetulemused_list.mako'
    _actions = 'index,download'
    # automaatse tagasisidevormi genereerimisel võib olla vaja see salvestada
    _kohteelvaade_readonly = False
    _tvliik = model.Tagasisidevorm.LIIK_OSALEJATETULEMUSED
    
    def _get_fr(self, test, lang, kursus):
        c = self.c
        fr = eis.lib.feedbackreport.FeedbackReport.init_osalejatetulemused(self, test, lang, kursus, c.testimiskord)
        return fr
